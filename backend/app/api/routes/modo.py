from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_roles
from app.db.session import get_db
from app.models.entities import Usuario
from app.schemas.modo import JornadaModo, MapaModo
from app.services import modo as servicio

router = APIRouter(prefix="/modo", tags=["Modo conductor"])

_DESCRIPCION = (
    "Jornada del conductor autenticado (US-015). Devuelve solo la ruta CONFIRMADA "
    "o EN_EJECUCION asignada a su ficha en el día civil de Lima (UTC−5, sin horario "
    "de verano): secuencia, hora estimada y alertas. No incluye el tablero de gerencia "
    "ni coordenadas. Un conductor no puede consultar la ruta de otro: no se acepta "
    "un identificador ajeno. Cada parada trae id_detalle para la acción de confirmar. "
    "Persistir ENTREGADO o FALLIDO, auditar y responder 403 si el detalle es de otro "
    "conductor es US-018; este endpoint no escribe."
)


@router.get(
    "/jornada",
    response_model=JornadaModo,
    summary="Ruta confirmada del conductor",
    description=_DESCRIPCION,
)
def consultar_jornada(
    db: Annotated[Session, Depends(get_db)],
    actor: Annotated[Usuario, Depends(require_roles("CONDUCTOR"))],
) -> dict:
    return servicio.jornada(db, actor)


@router.get(
    "/mapa",
    response_model=MapaModo,
    summary="Puntos opcionales del mapa del conductor",
    description=(
        "Coordenadas de la misma ruta que GET /modo/jornada. No forma parte de la "
        "consulta inicial: el modo conductor pide este recurso solo si la persona "
        "abre el mapa. Misma autorización: solo el conductor y solo su ficha."
    ),
)
def consultar_mapa(
    db: Annotated[Session, Depends(get_db)],
    actor: Annotated[Usuario, Depends(require_roles("CONDUCTOR"))],
) -> dict:
    return servicio.mapa(db, actor)
