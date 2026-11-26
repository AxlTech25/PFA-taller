"""Re-optimización de las paradas que faltan en una ruta activa (US-011, RN-014, RN-015).

Solo se toca la ruta afectada. Las paradas con resultado (ENTREGADO o FALLIDO)
quedan fijas en su lugar y desde la última de ellas se vuelve a ordenar el resto.
Las restricciones son las del plan inicial (`evaluacion._cabe`): capacidad,
ventana, jornada de 8 h con descansos de la Ley N.º 30224 y la reserva ecológica
como restricción dura (RN-013). La zona de riesgo se penaliza en el costo (RN-012).

El presupuesto es `tiempo_max_reoptimizacion_s` y nunca pasa de 30 s (RN-014).
Si se acaba, se devuelve la mejor secuencia completa encontrada hasta ese momento;
si no hubo ninguna, no hay solución y se conserva la ruta anterior.
"""

import copy
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from uuid import UUID

from app.optimizacion.evaluacion import (
    Instancia,
    PedidoNodo,
    Recurso,
    RutaPlan,
    _adoptar,
    _cabe,
    _cerrar,
    _Cursor,
    _cursor,
    costo_verde,
    distancia_km,
)

TOPE_REOPTIMIZACION_S = 30.0
# 2-opt completo hasta este tamaño; por encima solo se usa la construcción.
DOS_OPT_MAXIMO = 40

Reloj = Callable[[], float]


@dataclass
class ResultadoReoptimizacion:
    factible: bool
    ruta: RutaPlan | None = None
    orden: list[UUID] = field(default_factory=list)
    sin_ubicar: list[UUID] = field(default_factory=list)
    cortado: bool = False
    segundos: float = 0.0
    estrategia: str = ""
    costo_inicial: float | None = None
    costo_final: float | None = None


def presupuesto(valor_configurado: float | None) -> float:
    """RN-014: el parámetro es configurable, pero el tope de 30 s no se puede superar."""

    if valor_configurado is None:
        return TOPE_REOPTIMIZACION_S
    return min(max(float(valor_configurado), 0.0), TOPE_REOPTIMIZACION_S)


def _forzar(cursor: _Cursor, pedido: PedidoNodo, inst: Instancia) -> None:
    """Suma una parada ya resuelta sin exigir ventana: el conductor ya pasó por ahí."""

    km = distancia_km(cursor.lat, cursor.lon, pedido.lat, pedido.lon)
    minutos = (km / inst.velocidad) * 60.0 * inst.congestion
    try:
        _, proyectado = cursor.jornada.proyectar(cursor.reloj, minutos)
    except ValueError:
        proyectado = copy.deepcopy(cursor.jornada)
        proyectado.minutos_conduccion += minutos
    _adoptar(cursor, pedido, (km, minutos, 0.0, proyectado), inst)


def prefijo(recurso: Recurso, fijas: list[PedidoNodo], inst: Instancia) -> _Cursor:
    cursor = _cursor(recurso)
    for pedido in fijas:
        _forzar(cursor, pedido, inst)
    return cursor


def _simular(
    base: _Cursor, recurso: Recurso, secuencia: list[PedidoNodo], inst: Instancia
) -> _Cursor | None:
    cursor = copy.deepcopy(base)
    for pedido in secuencia:
        cabe = _cabe(cursor, pedido, recurso, inst)
        if cabe is None:
            return None
        _adoptar(cursor, pedido, cabe, inst)
    return cursor


def _costo(cursor: _Cursor, recurso: Recurso, inst: Instancia) -> float:
    ruta = _cerrar(recurso, cursor)
    if ruta is None:
        return 0.0
    return float(costo_verde([ruta], [], inst)["total"])


class _Busqueda:
    def __init__(
        self,
        base: _Cursor,
        recurso: Recurso,
        inst: Instancia,
        reloj: Reloj,
    ) -> None:
        self.base = base
        self.recurso = recurso
        self.inst = inst
        self.reloj = reloj
        self.mejor: list[PedidoNodo] | None = None
        self.mejor_costo = float("inf")
        self.estrategia = ""
        self.cortado = False

    def queda_tiempo(self) -> bool:
        if self.reloj() >= self.inst.limite:
            self.cortado = True
            return False
        return True

    def proponer(self, secuencia: list[PedidoNodo], estrategia: str) -> bool:
        cursor = _simular(self.base, self.recurso, secuencia, self.inst)
        if cursor is None:
            return False
        costo = _costo(cursor, self.recurso, self.inst)
        if costo + 1e-6 < self.mejor_costo:
            self.mejor = list(secuencia)
            self.mejor_costo = costo
            self.estrategia = estrategia
            return True
        return False


def _insercion_mas_barata(
    busqueda: _Busqueda, orden: list[PedidoNodo], nuevos: list[PedidoNodo]
) -> list[PedidoNodo] | None:
    """Conserva el orden que el conductor conoce e inserta cada pedido nuevo donde cuesta menos."""

    actual = list(orden)
    for pedido in nuevos:
        elegido: tuple[float, list[PedidoNodo]] | None = None
        for posicion in range(len(actual) + 1):
            if not busqueda.queda_tiempo():
                return None
            candidata = actual[:posicion] + [pedido] + actual[posicion:]
            cursor = _simular(busqueda.base, busqueda.recurso, candidata, busqueda.inst)
            if cursor is None:
                continue
            costo = _costo(cursor, busqueda.recurso, busqueda.inst)
            if elegido is None or costo < elegido[0]:
                elegido = (costo, candidata)
        if elegido is None:
            return None
        actual = elegido[1]
    return actual


def _vecino(busqueda: _Busqueda, candidatos: list[PedidoNodo]) -> tuple[list[PedidoNodo], list]:
    cursor = copy.deepcopy(busqueda.base)
    pendientes = list(candidatos)
    orden: list[PedidoNodo] = []
    while pendientes and busqueda.queda_tiempo():
        elegido = None
        for pedido in pendientes:
            cabe = _cabe(cursor, pedido, busqueda.recurso, busqueda.inst)
            if cabe is None:
                continue
            clave = (0 if pedido.express else 1, cabe[0], str(pedido.id))
            if elegido is None or clave < elegido[0]:
                elegido = (clave, pedido, cabe)
        if elegido is None:
            break
        _, pedido, cabe = elegido
        _adoptar(cursor, pedido, cabe, busqueda.inst)
        orden.append(pedido)
        pendientes = [item for item in pendientes if item.id != pedido.id]
    return orden, pendientes


def _dos_opt(busqueda: _Busqueda) -> None:
    if busqueda.mejor is None or len(busqueda.mejor) > DOS_OPT_MAXIMO:
        return
    hubo = True
    while hubo:
        hubo = False
        secuencia = busqueda.mejor
        n = len(secuencia)
        for inicio in range(n):
            for fin in range(inicio + 1, n):
                if not busqueda.queda_tiempo():
                    return
                candidata = (
                    secuencia[:inicio] + secuencia[inicio : fin + 1][::-1] + secuencia[fin + 1 :]
                )
                etiqueta = busqueda.estrategia.split("+")[0] + "+2-opt"
                if busqueda.proponer(candidata, etiqueta):
                    hubo = True
                    break
            if hubo:
                break


def reoptimizar(
    recurso: Recurso,
    fijas: list[PedidoNodo],
    pendientes: list[PedidoNodo],
    nuevos: list[PedidoNodo],
    inst: Instancia,
    reloj: Reloj = time.perf_counter,
    inicio: float | None = None,
) -> ResultadoReoptimizacion:
    """Ordena `pendientes + nuevos` después de las `fijas` sin pasar `inst.limite`."""

    arranque = reloj() if inicio is None else inicio
    base = prefijo(recurso, fijas, inst)
    busqueda = _Busqueda(base, recurso, inst, reloj)
    candidatos = list(pendientes) + list(nuevos)

    costo_inicial = None
    if busqueda.queda_tiempo():
        anterior = _simular(base, recurso, list(pendientes), inst)
        if anterior is not None and pendientes:
            costo_inicial = _costo(anterior, recurso, inst)
    if busqueda.queda_tiempo():
        insertada = _insercion_mas_barata(busqueda, pendientes, nuevos)
        if insertada is not None:
            busqueda.proponer(insertada, "orden_anterior_con_insercion")
    sin_ubicar: list[PedidoNodo] = []
    if busqueda.queda_tiempo():
        orden, sin_ubicar = _vecino(busqueda, candidatos)
        if not sin_ubicar:
            busqueda.proponer(orden, "vecino_mas_cercano")
    if busqueda.mejor is not None and busqueda.queda_tiempo():
        _dos_opt(busqueda)

    segundos = reloj() - arranque
    if busqueda.mejor is None:
        faltan = sin_ubicar or candidatos
        return ResultadoReoptimizacion(
            factible=False,
            sin_ubicar=[pedido.id for pedido in faltan],
            cortado=busqueda.cortado,
            segundos=segundos,
            costo_inicial=costo_inicial,
        )
    final = _simular(base, recurso, busqueda.mejor, inst)
    ruta = _cerrar(recurso, final) if final is not None else None
    return ResultadoReoptimizacion(
        factible=ruta is not None,
        ruta=ruta,
        orden=[pedido.id for pedido in busqueda.mejor],
        cortado=busqueda.cortado,
        segundos=segundos,
        estrategia=busqueda.estrategia,
        costo_inicial=costo_inicial,
        costo_final=busqueda.mejor_costo,
    )
