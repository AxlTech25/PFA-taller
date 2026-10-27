"""Evaluación compartida del VRPTW + Green VRP.

La usa la heurística del vecino más cercano (Sprint 3) y el algoritmo
genético (Sprint 4). Las restricciones duras son las mismas: capacidad,
ventana, punto de partida, pico y placa (ya filtrado al armar la flota),
jornada de 8 h y descanso de la Ley N.º 30224.
"""

import time
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from math import asin, cos, radians, sin, sqrt
from uuid import UUID

from app.optimizacion.jornada import EstadoJornada

SERVICIO_MIN = 10
# 1 galón estadounidense. RN-017 publica el diésel en S/ por galón.
LITROS_POR_GALON = 3.785411784
# RN-011: cada puesto después del primero en un pedido Exprés desempata
# hacia las primeras posiciones, sin volver blanda la ventana ni la capacidad.
PENALIZACION_EXPRESS = 50.0
DEPOSITO_SJL = (-12.0100, -76.9800)


def distancia_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radio = 6371.0
    phi1, phi2 = radians(lat1), radians(lat2)
    d_phi = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    a = sin(d_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(d_lon / 2) ** 2
    return 2 * radio * asin(sqrt(a))


@dataclass
class ParadaPlan:
    id_pedido: UUID
    lat: float
    lon: float
    minutos_conduccion: float
    eta: datetime
    km: float


@dataclass
class RutaPlan:
    id_vehiculo: UUID
    id_conductor: UUID
    paradas: list[ParadaPlan]
    descansos: list
    distancia_km: float
    minutos_conduccion: float
    minutos_reloj: float
    combustible_l: float
    co2_kg: float


@dataclass
class Plan:
    factible: bool
    mensaje: str
    rutas: list[RutaPlan] = field(default_factory=list)
    sin_asignar: list[UUID] = field(default_factory=list)
    algoritmo: str = "vecino_mas_cercano"
    comparacion: dict | None = None


@dataclass
class PedidoNodo:
    id: UUID
    lat: float
    lon: float
    peso: float
    volumen: float
    ventana_inicio: datetime
    ventana_fin: datetime
    express: bool


@dataclass
class Recurso:
    id_vehiculo: UUID
    id_conductor: UUID
    placa: str
    capacidad_kg: float
    capacidad_m3: float
    consumo_km_l: float
    factor_co2: float
    origen_lat: float
    origen_lon: float
    inicio: datetime
    fin: datetime


@dataclass
class Instancia:
    fecha: date
    pedidos: list[PedidoNodo]
    recursos: list[Recurso]
    velocidad: float
    congestion: float
    limite: float
    precio_litro: float
    costo_km: float
    excluidos: int
    semilla: int


@dataclass
class _Cursor:
    jornada: EstadoJornada
    lat: float
    lon: float
    reloj: datetime
    reloj_inicial: datetime
    carga_kg: float = 0
    carga_m3: float = 0
    distancia: float = 0
    paradas: list[ParadaPlan] = field(default_factory=list)


def _cursor(recurso: Recurso) -> _Cursor:
    return _Cursor(
        jornada=EstadoJornada(),
        lat=recurso.origen_lat,
        lon=recurso.origen_lon,
        reloj=recurso.inicio,
        reloj_inicial=recurso.inicio,
    )


def _cabe(cursor: _Cursor, pedido: PedidoNodo, recurso: Recurso, inst: Instancia) -> tuple | None:
    if cursor.carga_kg + pedido.peso > recurso.capacidad_kg + 1e-6:
        return None
    if cursor.carga_m3 + pedido.volumen > recurso.capacidad_m3 + 1e-6:
        return None
    km = distancia_km(cursor.lat, cursor.lon, pedido.lat, pedido.lon)
    minutos = (km / inst.velocidad) * 60.0 * inst.congestion
    if not cursor.jornada.puede_conducir(minutos):
        return None
    llegada, proyectado = cursor.jornada.proyectar(cursor.reloj, minutos)
    if llegada > pedido.ventana_fin or llegada > recurso.fin:
        return None
    espera = 0.0
    if llegada < pedido.ventana_inicio:
        espera = (pedido.ventana_inicio - llegada).total_seconds() / 60.0
    return km, minutos, espera, proyectado


def _adoptar(cursor: _Cursor, pedido: PedidoNodo, elegido: tuple) -> None:
    km, minutos, espera, proyectado = elegido
    llegada, _ = cursor.jornada.proyectar(cursor.reloj, minutos)
    cursor.jornada.adoptar(proyectado)
    cursor.reloj = llegada
    if espera:
        cursor.reloj = cursor.jornada.esperar(cursor.reloj, espera)
    cursor.reloj += timedelta(minutes=SERVICIO_MIN)
    cursor.jornada.registrar_parada()
    cursor.paradas.append(
        ParadaPlan(
            id_pedido=pedido.id,
            lat=pedido.lat,
            lon=pedido.lon,
            minutos_conduccion=minutos,
            eta=cursor.reloj,
            km=km,
        )
    )
    cursor.distancia += km
    cursor.carga_kg += pedido.peso
    cursor.carga_m3 += pedido.volumen
    cursor.lat = pedido.lat
    cursor.lon = pedido.lon


def _cerrar(recurso: Recurso, cursor: _Cursor) -> RutaPlan | None:
    if not cursor.paradas:
        return None
    minutos_reloj = (cursor.reloj - cursor.reloj_inicial).total_seconds() / 60.0
    consumo = recurso.consumo_km_l
    return RutaPlan(
        id_vehiculo=recurso.id_vehiculo,
        id_conductor=recurso.id_conductor,
        paradas=list(cursor.paradas),
        descansos=list(cursor.jornada.descansos),
        distancia_km=cursor.distancia,
        minutos_conduccion=cursor.jornada.minutos_conduccion,
        minutos_reloj=minutos_reloj,
        combustible_l=cursor.distancia / consumo if consumo else 0,
        co2_kg=cursor.distancia * recurso.factor_co2,
    )


def _elegir_cercano(
    cursor: _Cursor,
    pendientes: list[PedidoNodo],
    recurso: Recurso,
    inst: Instancia,
) -> tuple | None:
    elegido: tuple | None = None
    for pedido in pendientes:
        cabe = _cabe(cursor, pedido, recurso, inst)
        if cabe is None:
            continue
        km = cabe[0]
        clave = (0 if pedido.express else 1, km, str(pedido.id))
        if elegido is None or clave < elegido[0]:
            elegido = (clave, pedido, cabe)
    return elegido


def _armar_por_cercania(
    recurso: Recurso,
    candidatos: list[PedidoNodo],
    inst: Instancia,
) -> tuple[RutaPlan | None, list[PedidoNodo], bool]:
    cursor = _cursor(recurso)
    pendientes = list(candidatos)
    cortado = False
    while pendientes:
        if time.perf_counter() >= inst.limite:
            cortado = True
            break
        elegido = _elegir_cercano(cursor, pendientes, recurso, inst)
        if elegido is None:
            break
        _, pedido, cabe = elegido
        _adoptar(cursor, pedido, cabe)
        pendientes = [item for item in pendientes if item.id != pedido.id]
    return _cerrar(recurso, cursor), pendientes, cortado


def vecino_mas_cercano(inst: Instancia) -> tuple[list[RutaPlan], list[UUID], bool]:
    libres = list(inst.pedidos)
    rutas: list[RutaPlan] = []
    cortado = False
    for recurso in inst.recursos:
        if time.perf_counter() >= inst.limite:
            cortado = True
            break
        ruta, libres, corto = _armar_por_cercania(recurso, libres, inst)
        cortado = cortado or corto
        if ruta is not None:
            rutas.append(ruta)
    return rutas, [pedido.id for pedido in libres], cortado


def _tomar_en_orden(
    recurso: Recurso,
    orden: list[PedidoNodo],
    inst: Instancia,
) -> tuple[RutaPlan | None, list[PedidoNodo]]:
    cursor = _cursor(recurso)
    pendientes = list(orden)
    while True:
        if time.perf_counter() >= inst.limite:
            break
        colocado = False
        for indice, pedido in enumerate(pendientes):
            cabe = _cabe(cursor, pedido, recurso, inst)
            if cabe is None:
                continue
            _adoptar(cursor, pedido, cabe)
            del pendientes[indice]
            colocado = True
            break
        if not colocado:
            break
    return _cerrar(recurso, cursor), pendientes


def decodificar(orden: list[int], inst: Instancia) -> tuple[list[RutaPlan], list[UUID], bool]:
    pendientes = [inst.pedidos[indice] for indice in orden]
    rutas: list[RutaPlan] = []
    cortado = False
    for recurso in inst.recursos:
        if time.perf_counter() >= inst.limite:
            cortado = True
            break
        ruta, pendientes = _tomar_en_orden(recurso, pendientes, inst)
        if ruta is not None:
            rutas.append(ruta)
    return rutas, [pedido.id for pedido in pendientes], cortado


def _recurso_de(inst: Instancia, id_vehiculo: UUID) -> Recurso:
    for recurso in inst.recursos:
        if recurso.id_vehiculo == id_vehiculo:
            return recurso
    raise KeyError(id_vehiculo)


def _pedidos_de(inst: Instancia) -> dict[UUID, PedidoNodo]:
    return {pedido.id: pedido for pedido in inst.pedidos}


def simular(recurso: Recurso, secuencia: list[PedidoNodo], inst: Instancia) -> RutaPlan | None:
    cursor = _cursor(recurso)
    for pedido in secuencia:
        cabe = _cabe(cursor, pedido, recurso, inst)
        if cabe is None:
            return None
        _adoptar(cursor, pedido, cabe)
    return _cerrar(recurso, cursor)


def costo_verde(rutas: list[RutaPlan], sin_asignar: list[UUID], inst: Instancia) -> dict:
    express = {pedido.id for pedido in inst.pedidos if pedido.express}
    soles = 0.0
    co2 = 0.0
    km = 0.0
    litros = 0.0
    penal = 0.0
    for ruta in rutas:
        soles += ruta.combustible_l * inst.precio_litro + ruta.distancia_km * inst.costo_km
        co2 += ruta.co2_kg
        km += ruta.distancia_km
        litros += ruta.combustible_l
        for puesto, parada in enumerate(ruta.paradas):
            if parada.id_pedido in express and puesto > 0:
                penal += PENALIZACION_EXPRESS * puesto
    total = len(sin_asignar) * 1_000_000 + soles + co2 + penal
    return {
        "total": total,
        "soles": soles,
        "co2_kg": co2,
        "distancia_km": km,
        "combustible_l": litros,
        "penalizacion_express": penal,
        "sin_asignar": len(sin_asignar),
    }


def _reverso_mejor(
    recurso: Recurso,
    secuencia: list[PedidoNodo],
    inst: Instancia,
    mejor_total: float,
) -> tuple[list[PedidoNodo], RutaPlan, float] | None:
    n = len(secuencia)
    for inicio in range(n):
        for fin in range(inicio + 1, n):
            candidata = (
                secuencia[:inicio] + secuencia[inicio : fin + 1][::-1] + secuencia[fin + 1 :]
            )
            simulada = simular(recurso, candidata, inst)
            if simulada is None:
                continue
            total = costo_verde([simulada], [], inst)["total"]
            if total + 1e-6 < mejor_total:
                return candidata, simulada, total
    return None


def _optimizar_secuencia(
    recurso: Recurso,
    secuencia: list[PedidoNodo],
    actual: RutaPlan,
    inst: Instancia,
    mejor_total: float,
) -> RutaPlan:
    hubo = True
    while hubo and time.perf_counter() < inst.limite:
        hubo = False
        hallazgo = _reverso_mejor(recurso, secuencia, inst, mejor_total)
        if hallazgo is None:
            break
        secuencia, actual, mejor_total = hallazgo
        hubo = True
    return actual


def mejorar_orden_local(
    rutas: list[RutaPlan],
    sin_asignar: list[UUID],
    inst: Instancia,
) -> tuple[list[RutaPlan], list[UUID]]:
    """2-opt dentro de cada ruta. No cambia la asignación, solo el orden factible."""

    catalogo = _pedidos_de(inst)
    mejoradas: list[RutaPlan] = []
    for ruta in rutas:
        if time.perf_counter() >= inst.limite:
            mejoradas.append(ruta)
            continue
        recurso = _recurso_de(inst, ruta.id_vehiculo)
        secuencia = [catalogo[parada.id_pedido] for parada in ruta.paradas]
        if len(secuencia) > 16:
            mejoradas.append(ruta)
            continue
        mejor_total = costo_verde([ruta], [], inst)["total"]
        mejoradas.append(_optimizar_secuencia(recurso, secuencia, ruta, inst, mejor_total))
    return mejoradas, sin_asignar
