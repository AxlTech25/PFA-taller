from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.deps import ESCRITURA_RUTAS, LECTURA_RUTAS, ip_de, require_roles
from app.db.session import get_db
from app.models.entities import Usuario
from app.schemas.ruta import RutaOut
from app.services import rutas as servicio

router = APIRouter(prefix="/rutas", tags=["Optimización"])


@router.get("", response_model=list[RutaOut], summary="Listar rutas generadas")
def listar(
    db: Session = Depends(get_db),
    actor: Usuario = Depends(require_roles(*LECTURA_RUTAS)),
    fecha: date | None = Query(default=None),
) -> list:
    return servicio.listar_rutas(db, actor, fecha)


@router.post(
    "/{id_ruta}/confirmar",
    response_model=RutaOut,
    summary="Confirmar una ruta en borrador",
    description=(
        "Rechaza la asignación si la conducción del conductor en el día supera 8 horas "
        "(Ley N.º 30224). Si hay 4 horas continuas sin descanso, inserta 1 hora."
    ),
)
def confirmar(
    id_ruta: UUID,
    request: Request,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(require_roles(*ESCRITURA_RUTAS)),
) -> dict:
    return servicio.confirmar(db, id_ruta, actor, ip_de(request))
