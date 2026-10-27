from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import LECTURA_RUTAS, require_roles
from app.db.session import get_db
from app.models.entities import Usuario
from app.schemas.ruta import IndicadoresOut
from app.services import indicadores as servicio

router = APIRouter(prefix="/indicadores", tags=["Sostenibilidad"])


@router.get(
    "",
    response_model=IndicadoresOut,
    summary="Indicadores del día (tablero iniciado)",
    description=(
        "Inicio del dashboard del Hito 3. Resume km, CO₂, combustible, soles y "
        "cumplimiento de ventanas del último plan del día. US-014 se cierra en el Sprint 5. "
        "El equivalente en árboles espera el factor RN-018."
    ),
)
def consultar(
    db: Annotated[Session, Depends(get_db)],
    _actor: Annotated[Usuario, Depends(require_roles(*LECTURA_RUTAS))],
    fecha: Annotated[date, Query()],
) -> dict:
    return servicio.consultar(db, fecha)
