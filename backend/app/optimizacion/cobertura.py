"""Cobertura de Lima Este (US-008 B, RN-005)."""

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

MENSAJE_FUERA_COBERTURA = (
    "El pedido está fuera de la cobertura de Lima Este "
    "(San Juan de Lurigancho, El Agustino, Santa Anita y Ate)."
)

_CONSULTA = text(
    """
    SELECT nombre
    FROM distrito_cobertura
    WHERE activo
      AND ST_Covers(
            geometria,
            ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)
          )
    ORDER BY nombre
    LIMIT 1
    """
)


def distrito_en(db: Session, latitud: float, longitud: float) -> str | None:
    return db.execute(_CONSULTA, {"lat": latitud, "lon": longitud}).scalar()


def exigir_cobertura(db: Session, latitud: float, longitud: float) -> str:
    nombre = distrito_en(db, latitud, longitud)
    if not nombre:
        raise HTTPException(status_code=422, detail=MENSAJE_FUERA_COBERTURA)
    return nombre
