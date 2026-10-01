from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.entities import Usuario, Vehiculo
from app.schemas.vehiculo import VehiculoCreate, VehiculoUpdate
from app.services.auditoria import registrar
from app.services.integridad import mensaje_integridad
from app.services.sanitizacion import EntradaRechazada, rechazar_entrada, revisar_texto


def _numero(valor: float) -> Decimal:
    return Decimal(str(valor))


def _foto(vehiculo: Vehiculo) -> dict:
    return {
        "placa": vehiculo.placa,
        "tipo": vehiculo.tipo,
        "estado": vehiculo.estado,
        "factor_emision_co2": float(vehiculo.factor_emision_co2),
        "capacidad_kg": float(vehiculo.capacidad_kg),
    }


def listar_vehiculos(db: Session, limite: int) -> list[Vehiculo]:
    return list(db.scalars(select(Vehiculo).order_by(Vehiculo.placa).limit(limite)).all())


def obtener_vehiculo(db: Session, id_vehiculo) -> Vehiculo:
    vehiculo = db.get(Vehiculo, id_vehiculo)
    if vehiculo is None:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return vehiculo


def crear_vehiculo(
    db: Session, datos: VehiculoCreate, actor: Usuario, ip: str | None
) -> Vehiculo:
    try:
        revisar_texto(datos.placa, "placa")
    except EntradaRechazada as exc:
        rechazar_entrada(db, id_usuario=actor.id_usuario, ip=ip, campo=exc.campo, tabla="vehiculo")

    vehiculo = Vehiculo(
        placa=datos.placa,
        tipo=datos.tipo,
        capacidad_kg=_numero(datos.capacidad_kg),
        capacidad_m3=_numero(datos.capacidad_m3),
        consumo_km_l=_numero(datos.consumo_km_l),
        factor_emision_co2=_numero(datos.factor_emision_co2),
        anio_fabricacion=datos.anio_fabricacion,
        estado=datos.estado,
    )
    db.add(vehiculo)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        mensaje = mensaje_integridad(exc) or "No se pudo registrar el vehículo"
        raise HTTPException(status_code=409, detail=mensaje) from exc
    db.refresh(vehiculo)
    registrar(
        db,
        id_usuario=actor.id_usuario,
        accion="crear_vehiculo",
        tabla="vehiculo",
        registro_id=vehiculo.id_vehiculo,
        ip=ip,
        nuevos=_foto(vehiculo),
    )
    db.commit()
    return vehiculo


def actualizar_vehiculo(
    db: Session, id_vehiculo, datos: VehiculoUpdate, actor: Usuario, ip: str | None
) -> Vehiculo:
    if not datos.hay_cambios():
        raise HTTPException(
            status_code=422, detail="Debe indicar el estado o el factor de emisión"
        )
    vehiculo = obtener_vehiculo(db, id_vehiculo)
    anteriores = _foto(vehiculo)
    if datos.estado is not None:
        vehiculo.estado = datos.estado
    if datos.factor_emision_co2 is not None:
        vehiculo.factor_emision_co2 = _numero(datos.factor_emision_co2)
    db.commit()
    db.refresh(vehiculo)
    registrar(
        db,
        id_usuario=actor.id_usuario,
        accion="actualizar_vehiculo",
        tabla="vehiculo",
        registro_id=vehiculo.id_vehiculo,
        ip=ip,
        anteriores=anteriores,
        nuevos=_foto(vehiculo),
    )
    db.commit()
    return vehiculo
