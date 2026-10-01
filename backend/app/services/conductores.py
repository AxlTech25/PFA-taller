from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.entities import Conductor, Usuario
from app.schemas.conductor import ConductorCreate
from app.services.auditoria import registrar
from app.services.integridad import mensaje_integridad
from app.services.sanitizacion import exigir_textos_seguros


def _numero(valor: float | None) -> float | None:
    if valor is None:
        return None
    return float(valor)


def _decimal(valor: float) -> Decimal:
    return Decimal(str(valor))


def salida_conductor(conductor: Conductor, rol: str) -> dict:
    anonimo = rol == "AUDITOR"
    return {
        "id_conductor": conductor.id_conductor,
        "nombre": "Conductor" if anonimo else conductor.nombre,
        "dni": None if anonimo else conductor.dni,
        "licencia_categoria": conductor.licencia_categoria,
        "anios_experiencia": conductor.anios_experiencia,
        "disponibilidad_inicio": conductor.disponibilidad_inicio,
        "disponibilidad_fin": conductor.disponibilidad_fin,
        "lat_punto_partida": None if anonimo else _numero(conductor.lat_punto_partida),
        "lon_punto_partida": None if anonimo else _numero(conductor.lon_punto_partida),
        "estado": conductor.estado,
    }


def listar_conductores(db: Session, actor: Usuario, limite: int) -> list[dict]:
    consulta = select(Conductor).order_by(Conductor.nombre)
    if actor.rol == "CONDUCTOR":
        consulta = consulta.where(Conductor.id_usuario == actor.id_usuario)
    filas = list(db.scalars(consulta.limit(limite)).all())
    return [salida_conductor(fila, actor.rol) for fila in filas]


def crear_conductor(
    db: Session, datos: ConductorCreate, actor: Usuario, ip: str | None
) -> Conductor:
    exigir_textos_seguros(
        db,
        id_usuario=actor.id_usuario,
        ip=ip,
        tabla="conductor",
        campos=[
            (datos.nombre, "nombre"),
            (datos.dni, "dni"),
            (datos.licencia_categoria, "licencia_categoria"),
        ],
    )
    conductor = Conductor(
        nombre=datos.nombre,
        dni=datos.dni,
        licencia_categoria=datos.licencia_categoria,
        anios_experiencia=datos.anios_experiencia,
        disponibilidad_inicio=datos.disponibilidad_inicio,
        disponibilidad_fin=datos.disponibilidad_fin,
        lat_punto_partida=_decimal(datos.lat_punto_partida),
        lon_punto_partida=_decimal(datos.lon_punto_partida),
        estado="ACTIVO",
    )
    db.add(conductor)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        mensaje = mensaje_integridad(exc) or "No se pudo registrar el conductor"
        raise HTTPException(status_code=409, detail=mensaje) from exc
    db.refresh(conductor)
    registrar(
        db,
        id_usuario=actor.id_usuario,
        accion="crear_conductor",
        tabla="conductor",
        registro_id=conductor.id_conductor,
        ip=ip,
        nuevos={
            "dni": conductor.dni,
            "nombre": conductor.nombre,
            "estado": conductor.estado,
        },
    )
    db.commit()
    return conductor
