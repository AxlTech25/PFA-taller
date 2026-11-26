"""Preferencias de entrega del cliente (US-009 / RF-009).

Una ficha por cliente (UNIQUE en `preferencia_cliente.id_cliente`, 1:0..1).
El horario preferido entra al motor como restricción suave: la ventana del
pedido sigue siendo la restricción dura (RN-004) y la preferencia solo suma
una penalización por minuto de llegada fuera del horario preferido.
"""

import uuid
from datetime import time

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.entities import Cliente, PreferenciaCliente, Usuario
from app.schemas.cliente import PreferenciaIn
from app.services.auditoria import registrar
from app.services.integridad import mensaje_integridad
from app.services.pedidos import MENSAJE_CONSENTIMIENTO
from app.services.sanitizacion import exigir_textos_seguros

MENSAJE_GUARDADA = (
    "Preferencia guardada. El horario se usará como restricción suave en las próximas "
    "optimizaciones."
)
MENSAJE_SIN_PREFERENCIA = "El cliente aún no tiene preferencias de entrega registradas."


def _cliente(db: Session, id_cliente: uuid.UUID) -> Cliente:
    cliente = db.get(Cliente, id_cliente)
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


def _salida(cliente: Cliente, ficha: PreferenciaCliente | None, mensaje: str | None) -> dict:
    if ficha is None:
        return {
            "id_cliente": cliente.id_cliente,
            "nombre_cliente": cliente.nombre,
            "registrada": False,
            "mensaje": mensaje or MENSAJE_SIN_PREFERENCIA,
        }
    return {
        "id_cliente": cliente.id_cliente,
        "nombre_cliente": cliente.nombre,
        "registrada": True,
        "hora_inicio": ficha.hora_inicio_preferida,
        "hora_fin": ficha.hora_fin_preferida,
        "punto_referencia": ficha.punto_referencia,
        "restricciones_acceso": ficha.restricciones_acceso,
        "mensaje": mensaje,
    }


def _ficha(db: Session, id_cliente: uuid.UUID) -> PreferenciaCliente | None:
    return db.scalar(
        select(PreferenciaCliente).where(PreferenciaCliente.id_cliente == id_cliente)
    )


def consultar(db: Session, id_cliente: uuid.UUID) -> dict:
    cliente = _cliente(db, id_cliente)
    return _salida(cliente, _ficha(db, id_cliente), None)


def _texto_hora(valor: time | None) -> str | None:
    return valor.strftime("%H:%M") if valor is not None else None


def guardar(
    db: Session,
    id_cliente: uuid.UUID,
    datos: PreferenciaIn,
    actor: Usuario,
    ip: str | None,
) -> dict:
    exigir_textos_seguros(
        db,
        id_usuario=actor.id_usuario,
        ip=ip,
        tabla="preferencia_cliente",
        campos=[
            (datos.punto_referencia, "punto_referencia"),
            (datos.restricciones_acceso, "restricciones_acceso"),
        ],
    )
    cliente = _cliente(db, id_cliente)
    if not cliente.consentimiento_datos:
        # RN-020: sin consentimiento no se almacenan datos del cliente.
        registrar(
            db,
            id_usuario=actor.id_usuario,
            accion="preferencia_sin_consentimiento",
            tabla="preferencia_cliente",
            registro_id=None,
            ip=ip,
            nuevos={"id_cliente": str(cliente.id_cliente)},
        )
        db.commit()
        raise HTTPException(status_code=422, detail=MENSAJE_CONSENTIMIENTO)

    ficha = _ficha(db, id_cliente)
    anteriores = None
    accion = "crear_preferencia_cliente"
    if ficha is None:
        ficha = PreferenciaCliente(id_cliente=id_cliente)
        db.add(ficha)
    else:
        accion = "actualizar_preferencia_cliente"
        anteriores = {
            "hora_inicio": _texto_hora(ficha.hora_inicio_preferida),
            "hora_fin": _texto_hora(ficha.hora_fin_preferida),
        }
    ficha.hora_inicio_preferida = datos.hora_inicio
    ficha.hora_fin_preferida = datos.hora_fin
    ficha.punto_referencia = datos.punto_referencia
    ficha.restricciones_acceso = datos.restricciones_acceso
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        mensaje = mensaje_integridad(exc) or "No se pudo guardar la preferencia"
        raise HTTPException(status_code=409, detail=mensaje) from exc
    registrar(
        db,
        id_usuario=actor.id_usuario,
        accion=accion,
        tabla="preferencia_cliente",
        registro_id=ficha.id_preferencia,
        ip=ip,
        anteriores=anteriores,
        nuevos={
            "id_cliente": str(id_cliente),
            "hora_inicio": _texto_hora(datos.hora_inicio),
            "hora_fin": _texto_hora(datos.hora_fin),
            "con_punto_referencia": datos.punto_referencia is not None,
            "con_restricciones_acceso": datos.restricciones_acceso is not None,
        },
    )
    db.commit()
    db.refresh(ficha)
    return _salida(cliente, ficha, MENSAJE_GUARDADA)


def horarios_por_pedido(db: Session, pedidos: list) -> dict[uuid.UUID, tuple[time, time]]:
    """Horario preferido de cada pedido según la ficha de su cliente (para el motor)."""

    clientes = {pedido.id_cliente for pedido in pedidos}
    if not clientes:
        return {}
    filas = db.execute(
        select(
            PreferenciaCliente.id_cliente,
            PreferenciaCliente.hora_inicio_preferida,
            PreferenciaCliente.hora_fin_preferida,
        ).where(PreferenciaCliente.id_cliente.in_(clientes))
    ).all()
    horarios = {
        fila.id_cliente: (fila.hora_inicio_preferida, fila.hora_fin_preferida)
        for fila in filas
        if fila.hora_inicio_preferida is not None
        and fila.hora_fin_preferida is not None
        and fila.hora_inicio_preferida < fila.hora_fin_preferida
    }
    return {
        pedido.id_pedido: horarios[pedido.id_cliente]
        for pedido in pedidos
        if pedido.id_cliente in horarios
    }
