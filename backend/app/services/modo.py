"""Jornada del modo conductor (US-015).

El conductor autenticado solo recibe la ruta CONFIRMADA o EN_EJECUCION
asignada a su ficha en el día civil de Lima (UTC−5, sin horario de verano).
No hay identificador de otro conductor en la consulta.

US-018: `confirmar_parada` registra ENTREGADO o FALLIDO sobre `id_detalle`,
guarda quién y cuándo, lo audita y responde 403 si el detalle pertenece a la
ruta de otro conductor.
"""

from datetime import UTC, date, datetime, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import (
    AsignacionRuta,
    Cliente,
    Conductor,
    DescansoRuta,
    DetalleRuta,
    Incidencia,
    LogAuditoria,
    Pedido,
    Ruta,
    Usuario,
    Vehiculo,
)
from app.optimizacion.congestion import nivel_congestion
from app.optimizacion.heuristica import _parametro
from app.services.auditoria import registrar
from app.services.sanitizacion import exigir_textos_seguros

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
                "motivo_fallo": detalle.motivo_fallo,
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


def _alerta_reoptimizacion(db: Session, id_ruta: UUID) -> list[dict]:
    """Aviso in-app al conductor cuando el operador re-optimizó su ruta (US-011, RF-007)."""

    momento = db.scalar(
        select(LogAuditoria.creado_en)
        .where(
            LogAuditoria.accion == "reoptimizar_ruta",
            LogAuditoria.tabla_afectada == "ruta",
            LogAuditoria.registro_id == id_ruta,
        )
        .order_by(LogAuditoria.creado_en.desc())
        .limit(1)
    )
    if momento is None:
        return []
    hora = momento.astimezone(ZONA_LIMA).strftime("%H:%M")
    return [
        {
            "codigo": "REOPTIMIZACION",
            "secuencia": None,
            "texto": (
                f"La ruta se re-optimizó a las {hora} (hora de Lima). "
                "Revise el nuevo orden de las paradas pendientes."
            ),
        }
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
        _alerta_reoptimizacion(db, ruta.id_ruta)
        + _alertas_incidencia(db, ruta.id_ruta)
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


ESTADOS_CONFIRMABLES = ("PENDIENTE", "REPROGRAMADO")
MENSAJE_PARADA_NO_ENCONTRADA = "Parada no encontrada"
MENSAJE_PARADA_AJENA = "La parada pertenece a la ruta de otro conductor"
MENSAJE_RUTA_NO_ACTIVA = "La ruta de esta parada no está confirmada ni en ejecución"
_TEXTO_RESULTADO = {"ENTREGADO": "entregada", "FALLIDO": "fallida"}


def _conductor_de_ruta(db: Session, id_ruta: UUID) -> UUID | None:
    return db.scalar(
        select(Conductor.id_usuario)
        .join(AsignacionRuta, AsignacionRuta.id_conductor == Conductor.id_conductor)
        .where(AsignacionRuta.id_ruta == id_ruta)
        .order_by(AsignacionRuta.asignada_en.desc())
        .limit(1)
    )


def confirmar_parada(
    db: Session,
    actor: Usuario,
    id_detalle: UUID,
    resultado: str,
    motivo: str | None,
    ip: str | None,
) -> dict:
    """Registra ENTREGADO o FALLIDO en una parada del propio conductor.

    404 si la parada no existe, 403 si es de otro conductor, 409 si la ruta no
    está activa o la parada ya tiene resultado. La fila se bloquea para que
    dos confirmaciones simultáneas no ganen las dos.
    """

    detalle = db.scalar(
        select(DetalleRuta).where(DetalleRuta.id_detalle == id_detalle).with_for_update()
    )
    if detalle is None:
        raise HTTPException(status_code=404, detail=MENSAJE_PARADA_NO_ENCONTRADA)
    if _conductor_de_ruta(db, detalle.id_ruta) != actor.id_usuario:
        registrar(
            db,
            id_usuario=actor.id_usuario,
            accion="confirmacion_entrega_denegada",
            tabla="detalle_ruta",
            registro_id=detalle.id_detalle,
            ip=ip,
        )
        db.commit()
        raise HTTPException(status_code=403, detail=MENSAJE_PARADA_AJENA)
    ruta = db.get(Ruta, detalle.id_ruta)
    if ruta is None or ruta.estado not in ESTADOS_DEL_DIA:
        raise HTTPException(status_code=409, detail=MENSAJE_RUTA_NO_ACTIVA)
    if detalle.estado_entrega not in ESTADOS_CONFIRMABLES:
        raise HTTPException(
            status_code=409,
            detail=f"La parada ya fue registrada como {detalle.estado_entrega}",
        )
    exigir_textos_seguros(
        db,
        id_usuario=actor.id_usuario,
        ip=ip,
        tabla="detalle_ruta",
        campos=[(motivo, "motivo")],
    )

    anterior = detalle.estado_entrega
    momento = datetime.now(UTC)
    detalle.estado_entrega = resultado
    detalle.motivo_fallo = motivo if resultado == "FALLIDO" else None
    detalle.confirmada_por = actor.id_usuario
    detalle.confirmada_en = momento
    if resultado == "ENTREGADO":
        pedido = db.get(Pedido, detalle.id_pedido)
        if pedido is not None:
            pedido.estado = "ENTREGADO"
    if ruta.estado == "CONFIRMADA":
        ruta.estado = "EN_EJECUCION"
    registrar(
        db,
        id_usuario=actor.id_usuario,
        accion="confirmar_entrega",
        tabla="detalle_ruta",
        registro_id=detalle.id_detalle,
        ip=ip,
        anteriores={"estado_entrega": anterior},
        nuevos={"estado_entrega": resultado, "motivo_fallo": detalle.motivo_fallo},
    )
    db.commit()
    return {
        "id_detalle": detalle.id_detalle,
        "secuencia": detalle.secuencia,
        "estado_entrega": resultado,
        "motivo_fallo": detalle.motivo_fallo,
        "confirmada_en": momento,
        "mensaje": f"Parada {detalle.secuencia} registrada como {_TEXTO_RESULTADO[resultado]}.",
    }
