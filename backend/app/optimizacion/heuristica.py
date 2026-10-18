"""Heurística constructiva del vecino más cercano (inicio de ENB-001 / US-010).

No es el algoritmo genético ni Tabú del enabler completo. Arma un plan factible
de demostración: capacidad, ventana, pico y placa, punto de partida del
conductor, jornada de 8 h y descanso de 1 h cada 4 h de conducción.
"""

import time
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.models.entities import Conductor, Pedido, Vehiculo
from app.optimizacion.jornada import EstadoJornada
from app.optimizacion.pico_placa import placa_restringida

SERVICIO_MIN = 10
DEPOSITO_SJL = (-12.0100, -76.9800)

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


def distancia_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    from math import asin, cos, radians, sin, sqrt

    radio = 6371.0
    phi1, phi2 = radians(lat1), radians(lat2)
    d_phi = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    a = sin(d_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(d_lon / 2) ** 2
    return 2 * radio * asin(sqrt(a))


def pedidos_del_dia(db: Session, fecha: date) -> list[Pedido]:
    from sqlalchemy import func

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


def _armar_ruta(
    vehiculo: Vehiculo,
    conductor: Conductor,
    candidatos: list[Pedido],
    fecha: date,
    velocidad: float,
    congestion: float,
    limite: float,
) -> tuple[RutaPlan | None, bool]:
    jornada = EstadoJornada()
    lat, lon = _origen(conductor)
    reloj = datetime.combine(fecha, conductor.disponibilidad_inicio, tzinfo=UTC)
    fin = datetime.combine(fecha, conductor.disponibilidad_fin, tzinfo=UTC)
    carga_kg = 0.0
    carga_m3 = 0.0
    paradas: list[ParadaPlan] = []
    distancia = 0.0
    pendientes = list(candidatos)
    cortado = False
    reloj_inicial = reloj

    while pendientes:
        if time.perf_counter() >= limite:
            cortado = True
            break
        elegido: tuple | None = None
        for pedido in pendientes:
            peso = float(pedido.peso_kg)
            volumen = float(pedido.volumen_m3)
            if carga_kg + peso > float(vehiculo.capacidad_kg) + 1e-6:
                continue
            if carga_m3 + volumen > float(vehiculo.capacidad_m3) + 1e-6:
                continue
            km = distancia_km(lat, lon, float(pedido.latitud), float(pedido.longitud))
            minutos = (km / velocidad) * 60.0 * congestion
            if not jornada.puede_conducir(minutos):
                continue
            llegada, _proyectado = jornada.proyectar(reloj, minutos)
            if llegada > pedido.ventana_fin or llegada > fin:
                continue
            espera = 0.0
            if llegada < pedido.ventana_inicio:
                espera = (pedido.ventana_inicio - llegada).total_seconds() / 60.0
            clave = (0 if pedido.prioridad == "EXPRESS" else 1, km, str(pedido.id_pedido))
            if elegido is None or clave < elegido[0]:
                elegido = (clave, pedido, km, minutos, espera)
        if elegido is None:
            break
        _, pedido, km, minutos, espera = elegido
        llegada, proyectado = jornada.proyectar(reloj, minutos)
        jornada.adoptar(proyectado)
        reloj = llegada
        if espera:
            reloj = jornada.esperar(reloj, espera)
        reloj += timedelta(minutes=SERVICIO_MIN)
        jornada.registrar_parada()
        paradas.append(
            ParadaPlan(
                id_pedido=pedido.id_pedido,
                lat=float(pedido.latitud),
                lon=float(pedido.longitud),
                minutos_conduccion=minutos,
                eta=reloj,
                km=km,
            )
        )
        distancia += km
        carga_kg += float(pedido.peso_kg)
        carga_m3 += float(pedido.volumen_m3)
        lat, lon = float(pedido.latitud), float(pedido.longitud)
        pendientes = [item for item in pendientes if item.id_pedido != pedido.id_pedido]

    if not paradas:
        return None, cortado
    minutos_reloj = (reloj - reloj_inicial).total_seconds() / 60.0
    consumo = float(vehiculo.consumo_km_l)
    return (
        RutaPlan(
            id_vehiculo=vehiculo.id_vehiculo,
            id_conductor=conductor.id_conductor,
            paradas=paradas,
            descansos=list(jornada.descansos),
            distancia_km=distancia,
            minutos_conduccion=jornada.minutos_conduccion,
            minutos_reloj=minutos_reloj,
            combustible_l=distancia / consumo if consumo else 0,
            co2_kg=distancia * float(vehiculo.factor_emision_co2),
        ),
        cortado,
    )


def generar_plan(db: Session, fecha: date) -> Plan:
    velocidad = max(_parametro(db, "velocidad_urbana_km_h", 25), 1)
    congestion = max(_parametro(db, "factor_congestion", 1), 0.1)
    presupuesto = _parametro(db, "tiempo_max_optimizacion_s", 45)
    limite = time.perf_counter() + presupuesto

    pedidos = pedidos_del_dia(db, fecha)
    if not pedidos:
        return Plan(False, MENSAJE_SIN_PEDIDOS)

    activos = list(
        db.scalars(
            select(Vehiculo).where(Vehiculo.estado == "ACTIVO").order_by(Vehiculo.placa)
        ).all()
    )
    habilitados = [vehiculo for vehiculo in activos if not placa_restringida(vehiculo.placa, fecha)]
    excluidos = len(activos) - len(habilitados)
    conductores = _conductores_libres(db, fecha)
    if not habilitados and excluidos:
        return Plan(False, MENSAJE_PLACA, sin_asignar=[pedido.id_pedido for pedido in pedidos])
    if not habilitados or not conductores:
        return Plan(False, MENSAJE_SIN_FLOTA, sin_asignar=[pedido.id_pedido for pedido in pedidos])

    if time.perf_counter() >= limite:
        return Plan(False, MENSAJE_TIEMPO, sin_asignar=[pedido.id_pedido for pedido in pedidos])

    libres = list(pedidos)
    rutas: list[RutaPlan] = []
    cortado = False
    pares = zip(habilitados, conductores, strict=False)
    for vehiculo, conductor in pares:
        if time.perf_counter() >= limite:
            cortado = True
            break
        ruta, corto_ruta = _armar_ruta(
            vehiculo, conductor, libres, fecha, velocidad, congestion, limite
        )
        cortado = cortado or corto_ruta
        if ruta is None:
            continue
        rutas.append(ruta)
        asignados = {parada.id_pedido for parada in ruta.paradas}
        libres = [pedido for pedido in libres if pedido.id_pedido not in asignados]

    sin_asignar = [pedido.id_pedido for pedido in libres]
    if cortado and not rutas:
        return Plan(False, MENSAJE_TIEMPO, sin_asignar=sin_asignar)
    if not rutas:
        return Plan(False, MENSAJE_SIN_FACTIBLE, sin_asignar=sin_asignar)

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
    return Plan(True, mensaje, rutas, sin_asignar)
