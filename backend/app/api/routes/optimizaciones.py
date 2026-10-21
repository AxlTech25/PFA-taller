from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.deps import ESCRITURA_RUTAS, LECTURA_RUTAS, ip_de, require_roles
from app.db.session import get_db
from app.models.entities import Usuario
from app.schemas.ruta import JobOut, SolicitudOptimizacion
from app.services import rutas as servicio

router = APIRouter(prefix="/optimizaciones", tags=["Optimización"])


@router.post(
    "",
    response_model=JobOut,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Encolar generación de rutas",
    description=(
        "Encola un trabajo para el worker de optimización y responde de inmediato. "
        "El algoritmo genético no corre en esta petición. Consulte GET /optimizaciones/{id_job}."
    ),
    responses={503: {"description": "Redis no está disponible"}},
)
def solicitar(
    datos: SolicitudOptimizacion,
    request: Request,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(require_roles(*ESCRITURA_RUTAS)),
) -> dict:
    job = servicio.solicitar(db, actor, datos.fecha, ip_de(request))
    return servicio.salida_job(db, job, actor.rol)


@router.get(
    "/{id_job}",
    response_model=JobOut,
    summary="Consultar un trabajo de optimización",
)
def consultar(
    id_job: UUID,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(require_roles(*LECTURA_RUTAS)),
) -> dict:
    job = servicio.obtener_job(db, id_job)
    return servicio.salida_job(db, job, actor.rol)
