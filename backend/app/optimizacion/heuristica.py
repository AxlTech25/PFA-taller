"""Carga del día y heurística del vecino más cercano (inicio de ENB-001 / US-010).

El algoritmo genético del Sprint 4 reutiliza esta carga y esta heurística como
línea base. La construcción sigue siendo: capacidad, ventana, pico y placa,
punto de partida, jornada de 8 h y descanso de 1 h cada 4 h de conducción.
"""

import hashlib
import time
from datetime import UTC, date, datetime
from uuid import UUID

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.models.entities import Conductor, Pedido, Vehiculo
from app.optimizacion.evaluacion import (
    DEPOSITO_SJL,
    LITROS_POR_GALON,
    Instancia,
    PedidoNodo,
    Plan,
    Recurso,
    vecino_mas_cercano,
)
from app.optimizacion.pico_placa import placa_restringida

MENSAJE_SIN_PEDIDOS = (
    "No hay pedidos pendientes para esa fecha. "
    "Registre entregas en Lima Este antes de optimizar."
)
MENSAJE_SIN_FLOTA = (
    "No hay flota disponible para la fecha. Agregue vehículos activos y conductores, "
    "o libere la operación del día."
)
MENSAJE_PLACA = (
    "No hay vehículos disponibles: la restricción de placa (D.S. N.º 033-2012-MTC) "
    "excluye la flota activa para esa fecha. Agregue vehículos o elija otro día."
)
MENSAJE_SIN_FACTIBLE = (
    "No hay solución factible con la flota activa. Agregue vehículos o relaje "
    "ventanas y el peso de los pedidos. Se conserva el estado anterior."
)
MENSAJE_TIEMPO = (
    "Se alcanzó el tiempo límite de optimización. Se conserva el estado anterior. "
    "Agregue vehículos o relaje ventanas."
)
MENSAJE_PLAN = (
    "Plan en borrador generado con la heurística del vecino más cercano. "
    "Confirme la ruta para asignar los pedidos. Esta heurística no es el algoritmo genético final."
)


def _parametro(db: Session, clave: str, defecto: float) -> float:
    valor = db.execute(
        text("SELECT valor FROM configuracion_sistema WHERE clave = :clave"),
        {"clave": clave},
    ).scalar()
    if valor is None:
        return defecto
    return float(valor)


def _origen(conductor: Conductor) -> tuple[float, float]:
    if conductor.lat_punto_partida is not None and conductor.lon_punto_partida is not None:
        return float(conductor.lat_punto_partida), float(conductor.lon_punto_partida)
    return DEPOSITO_SJL


def pedidos_del_dia(db: Session, fecha: date) -> list[Pedido]:
    ocupados = set(
        db.execute(
            text(
                """
                SELECT d.id_pedido
                FROM detalle_ruta d
                JOIN ruta r ON r.id_ruta = d.id_ruta
                WHERE r.fecha = :fecha AND r.estado <> 'CANCELADA'
                """
            ),
            {"fecha": fecha},
        ).scalars()
    )
    filas = list(
        db.scalars(
            select(Pedido)
            .where(Pedido.estado == "PENDIENTE")
            .where(func.date(Pedido.ventana_inicio) <= fecha)
            .where(func.date(Pedido.ventana_fin) >= fecha)
            .order_by(Pedido.creado_en)
        ).all()
    )
    return [fila for fila in filas if fila.id_pedido not in ocupados]


def _conductores_libres(db: Session, fecha: date) -> list[Conductor]:
    ocupados = set(
        db.execute(
            text(
                """
                SELECT a.id_conductor
                FROM asignacion_ruta a
                JOIN ruta r ON r.id_ruta = a.id_ruta
                WHERE r.fecha = :fecha AND r.estado <> 'CANCELADA'
                """
            ),
            {"fecha": fecha},
        ).scalars()
    )
    filas = list(
        db.scalars(
            select(Conductor)
            .where(Conductor.estado == "ACTIVO")
            .order_by(Conductor.nombre)
        ).all()
    )
    return [fila for fila in filas if fila.id_conductor not in ocupados]


def _semilla(fecha: date, identificadores: list[UUID]) -> int:
    texto = fecha.isoformat() + "|" + ",".join(sorted(str(item) for item in identificadores))
    return int(hashlib.sha256(texto.encode()).hexdigest()[:8], 16)


def _mensaje_base(excluidos: int, sin_asignar: list[UUID], cortado: bool) -> str:
    mensaje = MENSAJE_PLAN
    if excluidos:
        mensaje += (
            f" Se excluyeron {excluidos} vehículo(s) por restricción de placa "
            "(D.S. N.º 033-2012-MTC)."
        )
    if sin_asignar:
        mensaje += f" Quedaron {len(sin_asignar)} pedido(s) sin asignar."
    if cortado:
        mensaje += (
            " El cálculo se detuvo al alcanzar el tiempo límite y devolvió el mejor plan factible."
        )
    return mensaje


def preparar(db: Session, fecha: date) -> Instancia | Plan:
    velocidad = max(_parametro(db, "velocidad_urbana_km_h", 25), 1)
    congestion = max(_parametro(db, "factor_congestion", 1), 0.1)
    presupuesto = _parametro(db, "tiempo_max_optimizacion_s", 45)
    precio_galon = _parametro(db, "precio_diesel_galon", 17.50)
    costo_km = _parametro(db, "costo_mantenimiento_km", 1.20)
    limite = time.perf_counter() + presupuesto

    pedidos = pedidos_del_dia(db, fecha)
    if not pedidos:
        return Plan(False, MENSAJE_SIN_PEDIDOS)

    identificadores = [pedido.id_pedido for pedido in pedidos]
    activos = list(
        db.scalars(
            select(Vehiculo).where(Vehiculo.estado == "ACTIVO").order_by(Vehiculo.placa)
        ).all()
    )
    habilitados = [vehiculo for vehiculo in activos if not placa_restringida(vehiculo.placa, fecha)]
    excluidos = len(activos) - len(habilitados)
    conductores = _conductores_libres(db, fecha)
    if not habilitados and excluidos:
        return Plan(False, MENSAJE_PLACA, sin_asignar=identificadores)
    if not habilitados or not conductores:
        return Plan(False, MENSAJE_SIN_FLOTA, sin_asignar=identificadores)
    if time.perf_counter() >= limite:
        return Plan(False, MENSAJE_TIEMPO, sin_asignar=identificadores)

    nodos = [
        PedidoNodo(
            id=pedido.id_pedido,
            lat=float(pedido.latitud),
            lon=float(pedido.longitud),
            peso=float(pedido.peso_kg),
            volumen=float(pedido.volumen_m3),
            ventana_inicio=pedido.ventana_inicio,
            ventana_fin=pedido.ventana_fin,
            express=pedido.prioridad == "EXPRESS",
        )
        for pedido in pedidos
    ]
    recursos: list[Recurso] = []
    for vehiculo, conductor in zip(habilitados, conductores, strict=False):
        lat, lon = _origen(conductor)
        recursos.append(
            Recurso(
                id_vehiculo=vehiculo.id_vehiculo,
                id_conductor=conductor.id_conductor,
                placa=vehiculo.placa,
                capacidad_kg=float(vehiculo.capacidad_kg),
                capacidad_m3=float(vehiculo.capacidad_m3),
                consumo_km_l=float(vehiculo.consumo_km_l),
                factor_co2=float(vehiculo.factor_emision_co2),
                origen_lat=lat,
                origen_lon=lon,
                inicio=datetime.combine(fecha, conductor.disponibilidad_inicio, tzinfo=UTC),
                fin=datetime.combine(fecha, conductor.disponibilidad_fin, tzinfo=UTC),
            )
        )
    return Instancia(
        fecha=fecha,
        pedidos=nodos,
        recursos=recursos,
        velocidad=velocidad,
        congestion=congestion,
        limite=limite,
        precio_litro=precio_galon / LITROS_POR_GALON,
        costo_km=costo_km,
        excluidos=excluidos,
        semilla=_semilla(fecha, identificadores),
    )


def plan_desde_vecino(inst: Instancia) -> Plan:
    rutas, sin_asignar, cortado = vecino_mas_cercano(inst)
    if cortado and not rutas:
        return Plan(False, MENSAJE_TIEMPO, sin_asignar=sin_asignar)
    if not rutas:
        return Plan(False, MENSAJE_SIN_FACTIBLE, sin_asignar=sin_asignar)
    return Plan(
        True,
        _mensaje_base(inst.excluidos, sin_asignar, cortado),
        rutas,
        sin_asignar,
        algoritmo="vecino_mas_cercano",
    )


def generar_plan(db: Session, fecha: date) -> Plan:
    """Línea base del Sprint 3. El worker del Sprint 4 usa la metaheurística."""

    preparado = preparar(db, fecha)
    if isinstance(preparado, Plan):
        return preparado
    return plan_desde_vecino(preparado)
