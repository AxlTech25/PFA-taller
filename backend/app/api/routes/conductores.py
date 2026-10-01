from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.core.deps import ESCRITURA_CONDUCTORES, LECTURA_CONDUCTORES, ip_de, require_roles
from app.db.session import get_db
from app.models.entities import Usuario
from app.schemas.conductor import ConductorCreado, ConductorCreate, ConductorOut
from app.services import conductores as servicio

router = APIRouter(prefix="/conductores", tags=["Conductores"])


@router.get("", response_model=list[ConductorOut])
def listar(
    db: Session = Depends(get_db),
    actor: Usuario = Depends(require_roles(*LECTURA_CONDUCTORES)),
    limite: int = Query(default=100, ge=1, le=200),
) -> list:
    return servicio.listar_conductores(db, actor, limite)


@router.post("", response_model=ConductorCreado, status_code=status.HTTP_201_CREATED)
def crear(
    datos: ConductorCreate,
    request: Request,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(require_roles(*ESCRITURA_CONDUCTORES)),
) -> dict:
    conductor = servicio.crear_conductor(db, datos, actor, ip_de(request))
    cuerpo = servicio.salida_conductor(conductor, actor.rol)
    cuerpo["mensaje"] = "Conductor registrado correctamente"
    return cuerpo
