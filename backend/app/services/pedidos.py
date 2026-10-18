from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.entities import Cliente, Pedido, Usuario
from app.optimizacion.cobertura import MENSAJE_FUERA_COBERTURA, distrito_en
from app.schemas.pedido import PedidoCreate
from app.services.auditoria import registrar
from app.services.integridad import mensaje_integridad
from app.services.sanitizacion import exigir_textos_seguros

MENSAJE_CONSENTIMIENTO = (
    "El cliente no ha otorgado el consentimiento para el tratamiento de sus datos. "
    "Solicite el consentimiento explícito."
)


def _decimal(valor: float) -> Decimal:
    return Decimal(str(valor))


def _float(valor) -> float | None:
    if valor is None:
        return None
    return float(valor)


def listar_clientes(db: Session, actor: Usuario, limite: int) -> list[dict]:
    filas = list(db.scalars(select(Cliente).order_by(Cliente.nombre).limit(limite)).all())
    anonimo = actor.rol == "AUDITOR"
    return [
        {
            "id_cliente": fila.id_cliente,
            "nombre": fila.nombre,
            "telefono": None if anonimo else fila.telefono,
            "email": None if anonimo else fila.email,
            "consentimiento_datos": fila.consentimiento_datos,
        }
        for fila in filas
    ]


def _nombre_cliente(db: Session, id_cliente) -> str | None:
    cliente = db.get(Cliente, id_cliente)
    return cliente.nombre if cliente else None


def salida_pedido(db: Session, pedido: Pedido, rol: str) -> dict:
    anonimo = rol == "AUDITOR"
    return {
        "id_pedido": pedido.id_pedido,
        "id_cliente": pedido.id_cliente,
        "nombre_cliente": _nombre_cliente(db, pedido.id_cliente),
        "direccion": None if anonimo else pedido.direccion,
        "punto_referencia": None if anonimo else pedido.punto_referencia,
        "latitud": None if anonimo else _float(pedido.latitud),
        "longitud": None if anonimo else _float(pedido.longitud),
        "peso_kg": float(pedido.peso_kg),
        "volumen_m3": float(pedido.volumen_m3),
        "ventana_inicio": pedido.ventana_inicio,
        "ventana_fin": pedido.ventana_fin,
        "prioridad": pedido.prioridad,
        "tipo_producto": pedido.tipo_producto,
        "estado": pedido.estado,
        "georreferencia_aproximada": pedido.georreferencia_aproximada,
        "distrito": None
        if anonimo
        else distrito_en(db, float(pedido.latitud), float(pedido.longitud)),
    }


def listar_pedidos(db: Session, actor: Usuario, limite: int) -> list[dict]:
    if actor.rol == "CONDUCTOR":
        return []
    filas = list(
        db.scalars(select(Pedido).order_by(Pedido.creado_en.desc()).limit(limite)).all()
    )
    return [salida_pedido(db, fila, actor.rol) for fila in filas]


def crear_pedido(db: Session, datos: PedidoCreate, actor: Usuario, ip: str | None) -> Pedido:
    exigir_textos_seguros(
        db,
        id_usuario=actor.id_usuario,
        ip=ip,
        tabla="pedido",
        campos=[
            (datos.direccion, "direccion"),
            (datos.punto_referencia, "punto_referencia"),
        ],
    )
    cliente = db.get(Cliente, datos.id_cliente)
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    if not cliente.consentimiento_datos:
        registrar(
            db,
            id_usuario=actor.id_usuario,
            accion="pedido_sin_consentimiento",
            tabla="pedido",
            registro_id=None,
            ip=ip,
            nuevos={"id_cliente": str(cliente.id_cliente)},
        )
        db.commit()
        raise HTTPException(status_code=422, detail=MENSAJE_CONSENTIMIENTO)

    distrito = distrito_en(db, datos.latitud, datos.longitud)
    if distrito is None:
        registrar(
            db,
            id_usuario=actor.id_usuario,
            accion="pedido_fuera_cobertura",
            tabla="pedido",
            registro_id=None,
            ip=ip,
            nuevos={"latitud": datos.latitud, "longitud": datos.longitud},
        )
        db.commit()
        raise HTTPException(status_code=422, detail=MENSAJE_FUERA_COBERTURA)

    aproximada = datos.punto_referencia is not None
    pedido = Pedido(
        id_cliente=datos.id_cliente,
        direccion=datos.direccion,
        punto_referencia=datos.punto_referencia,
        latitud=_decimal(datos.latitud),
        longitud=_decimal(datos.longitud),
        peso_kg=_decimal(datos.peso_kg),
        volumen_m3=_decimal(datos.volumen_m3),
        ventana_inicio=datos.ventana_inicio,
        ventana_fin=datos.ventana_fin,
        prioridad=datos.prioridad,
        tipo_producto=datos.tipo_producto,
        estado="PENDIENTE",
        georreferencia_aproximada=aproximada,
    )
    db.add(pedido)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        mensaje = mensaje_integridad(exc) or "No se pudo registrar el pedido"
        raise HTTPException(status_code=409, detail=mensaje) from exc
    db.refresh(pedido)
    registrar(
        db,
        id_usuario=actor.id_usuario,
        accion="crear_pedido",
        tabla="pedido",
        registro_id=pedido.id_pedido,
        ip=ip,
        nuevos={
            "id_cliente": str(pedido.id_cliente),
            "estado": pedido.estado,
            "peso_kg": float(pedido.peso_kg),
            "distrito": distrito,
            "georreferencia_aproximada": pedido.georreferencia_aproximada,
        },
    )
    db.commit()
    return pedido
