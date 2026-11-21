"""Jornada del modo conductor (US-015).

El conductor autenticado solo recibe la ruta CONFIRMADA o EN_EJECUCION
asignada a su ficha en el día civil de Lima (UTC−5, sin horario de verano).
No hay identificador de otro conductor en la consulta.

US-018 (Sprint 6) persistirá ENTREGADO o FALLIDO sobre `id_detalle`,
auditará la acción y responderá 403 si el detalle no es de este conductor.
Este módulo no escribe `estado_entrega`.
"""

from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import (
    AsignacionRuta,
    Cliente,
    Conductor,
    DescansoRuta,
    DetalleRuta,
    Incidencia,
    Pedido,
    Ruta,
    Usuario,
    Vehiculo,
)
from app.optimizacion.congestion import nivel_congestion
from app.optimizacion.heuristica import _parametro

# Perú no observa horario de verano: el día operativo es UTC−5 todo el año.
ZONA_LIMA = timezone(timedelta(hours=-5))
MENSAJE_SIN_RUTA = "No tiene una ruta confirmada para hoy."
ESTADOS_DEL_DIA = ("CONFIRMADA", "EN_EJECUCION")

_TEXTO_INCIDENCIA = {
    "NUEVO_PEDIDO": "Hay un pedido nuevo pendiente de revisar en la ruta.",
    "CANCELACION": "Hay una cancelación pendiente en la ruta.",
    "ACCIDENTE_TRANSITO": "Hay un accidente de tránsito reportado en la ruta.",
    "AVERIA_VEHICULO": "Hay una avería de vehículo reportada.",
    "CONGESTION": "Hay congestión reportada en la ruta.",
}


def fecha_operativa(momento: datetime | None = None) -> date:
    actual = momento if momento is not None else datetime.now(ZONA_LIMA)
    if actual.tzinfo is None:
        actual = actual.replace(tzinfo=ZONA_LIMA)
    return actual.astimezone(ZONA_LIMA).date()


def _vacia(fecha: date) -> dict:
    return {
        "hay_ruta": False,
        "fecha": fecha,
        "mensaje": MENSAJE_SIN_RUTA,
        "id_ruta": None,
        "placa": None,
        "paradas": [],
        "alertas": [],
    }


def _ruta_del_dia(db: Session, id_usuario: UUID, fecha: date) -> tuple[Ruta, str] | None:
    fila = db.execute(
        select(Ruta, Vehiculo.placa)
        .join(AsignacionRuta, AsignacionRuta.id_ruta == Ruta.id_ruta)
        .join(Vehiculo, Vehiculo.id_vehiculo == AsignacionRuta.id_vehiculo)
        .join(Conductor, Conductor.id_conductor == AsignacionRuta.id_conductor)
        .where(
            Conductor.id_usuario == id_usuario,
            Ruta.fecha == fecha,
            Ruta.estado.in_(ESTADOS_DEL_DIA),
        )
        .order_by(AsignacionRuta.asignada_en.desc())
        .limit(1)
    ).first()
    if fila is None:
        return None
    return fila[0], fila[1]


def _alerta_congestion(secuencia: int, nivel: str) -> dict | None:
    if nivel == "ROJO":
        texto = f"Parada {secuencia}: semáforo rojo en la llegada estimada."
    elif nivel == "AMARILLO":
        texto = f"Parada {secuencia}: semáforo amarillo en la llegada estimada."
    else:
        return None
    return {"codigo": "CONGESTION", "secuencia": secuencia, "texto": texto}


def _alerta_ventana(
    secuencia: int,
    eta: datetime | None,
    inicio: datetime,
    fin: datetime,
) -> dict | None:
    if eta is None or inicio <= eta <= fin:
        return None
    return {
        "codigo": "VENTANA",
        "secuencia": secuencia,
        "texto": f"Parada {secuencia}: la llegada estimada queda fuera de la ventana del cliente.",
    }


def _paradas(db: Session, id_ruta: UUID, factor: float) -> tuple[list[dict], list[dict]]:
    filas = db.execute(
        select(DetalleRuta, Pedido, Cliente.nombre)
        .join(Pedido, Pedido.id_pedido == DetalleRuta.id_pedido)
        .join(Cliente, Cliente.id_cliente == Pedido.id_cliente)
        .where(DetalleRuta.id_ruta == id_ruta)
        .order_by(DetalleRuta.secuencia)
    ).all()
    paradas: list[dict] = []
    alertas: list[dict] = []
    for detalle, pedido, nombre in filas:
        nivel = nivel_congestion(factor, detalle.eta)
        paradas.append(
            {
                "secuencia": detalle.secuencia,
                "id_detalle": detalle.id_detalle,
                "cliente": nombre or "Cliente",
                "direccion": pedido.direccion,
                "punto_referencia": pedido.punto_referencia,
                "eta": detalle.eta,
                "estado_entrega": detalle.estado_entrega,
                "nivel_congestion": nivel,
            }
        )
        congestion = _alerta_congestion(detalle.secuencia, nivel)
        if congestion is not None:
            alertas.append(congestion)
        ventana = _alerta_ventana(
            detalle.secuencia, detalle.eta, pedido.ventana_inicio, pedido.ventana_fin
        )
        if ventana is not None:
            alertas.append(ventana)
    return paradas, alertas


def _texto_incidencia(incidencia: Incidencia) -> str:
    if incidencia.descripcion and incidencia.descripcion.strip():
        return incidencia.descripcion.strip()[:180]
    return _TEXTO_INCIDENCIA.get(incidencia.tipo, "Hay un aviso pendiente en la ruta.")


def _alertas_incidencia(db: Session, id_ruta: UUID) -> list[dict]:
    avisos = db.scalars(
        select(Incidencia)
        .where(Incidencia.id_ruta == id_ruta, Incidencia.estado == "PENDIENTE")
        .order_by(Incidencia.reportada_en)
    ).all()
    return [
        {"codigo": "INCIDENCIA", "secuencia": None, "texto": _texto_incidencia(aviso)}
        for aviso in avisos
    ]


def _alertas_descanso(db: Session, id_ruta: UUID) -> list[dict]:
    descansos = db.scalars(
        select(DescansoRuta)
        .where(DescansoRuta.id_ruta == id_ruta)
        .order_by(DescansoRuta.despues_de_secuencia)
    ).all()
    alertas = []
    for descanso in descansos:
        if descanso.despues_de_secuencia > 0:
            texto = (
                f"Después de la parada {descanso.despues_de_secuencia} hay un descanso "
                f"de {descanso.duracion_min} min (Ley N.º 30224)."
            )
            secuencia = descanso.despues_de_secuencia
        else:
            texto = (
                f"La jornada incluye un descanso de {descanso.duracion_min} min (Ley N.º 30224)."
            )
            secuencia = None
        alertas.append({"codigo": "DESCANSO", "secuencia": secuencia, "texto": texto})
    return alertas


def jornada(db: Session, actor: Usuario) -> dict:
    fecha = fecha_operativa()
    encontrada = _ruta_del_dia(db, actor.id_usuario, fecha)
    if encontrada is None:
        return _vacia(fecha)
    ruta, placa = encontrada
    factor = max(_parametro(db, "factor_congestion", 1.0), 0.1)
    paradas, alertas_parada = _paradas(db, ruta.id_ruta, factor)
    alertas = (
        _alertas_incidencia(db, ruta.id_ruta)
        + alertas_parada
        + _alertas_descanso(db, ruta.id_ruta)
    )
    return {
        "hay_ruta": True,
        "fecha": fecha,
        "mensaje": None,
        "id_ruta": ruta.id_ruta,
        "placa": placa,
        "paradas": paradas,
        "alertas": alertas,
    }


def _vacio_mapa() -> dict:
    return {"hay_ruta": False, "placa": None, "puntos": []}


def mapa(db: Session, actor: Usuario) -> dict:
    """Puntos de la misma jornada. Se pide solo si el conductor abre el mapa."""

    encontrada = _ruta_del_dia(db, actor.id_usuario, fecha_operativa())
    if encontrada is None:
        return _vacio_mapa()
    ruta, placa = encontrada
    filas = db.execute(
        select(DetalleRuta.secuencia, Pedido.latitud, Pedido.longitud, Cliente.nombre)
        .join(Pedido, Pedido.id_pedido == DetalleRuta.id_pedido)
        .join(Cliente, Cliente.id_cliente == Pedido.id_cliente)
        .where(DetalleRuta.id_ruta == ruta.id_ruta)
        .order_by(DetalleRuta.secuencia)
    ).all()
    return {
        "hay_ruta": True,
        "placa": placa,
        "puntos": [
            {
                "secuencia": secuencia,
                "latitud": float(latitud),
                "longitud": float(longitud),
                "cliente": nombre or "Cliente",
            }
            for secuencia, latitud, longitud, nombre in filas
        ],
    }
