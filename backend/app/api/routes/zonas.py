from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import LECTURA_RUTAS, require_roles
from app.db.session import get_db
from app.models.entities import Usuario
from app.schemas.zona import ListadoZonas
from app.services import zonas as servicio

router = APIRouter(prefix="/rutas", tags=["Mapa"])


@router.get(
    "/zonas-restriccion",
    response_model=ListadoZonas,
    summary="Zonas de restricción activas",
    description=(
        "Polígonos para el overlay del mapa (US-013). "
        "Las filas cuyo nombre empieza por DEMO son ilustrativas: "
        "no son el catastro del INEI ni el límite oficial de una reserva o de una zona de riesgo."
    ),
)
def listar(
    db: Annotated[Session, Depends(get_db)],
    _actor: Annotated[Usuario, Depends(require_roles(*LECTURA_RUTAS))],
) -> dict:
    return servicio.listar(db)
