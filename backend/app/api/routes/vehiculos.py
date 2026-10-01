import uuid

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.core.deps import EDICION_FLOTA, ESCRITURA_FLOTA, LECTURA_FLOTA, ip_de, require_roles
from app.db.session import get_db
from app.models.entities import Usuario
from app.schemas.vehiculo import VehiculoCreado, VehiculoCreate, VehiculoOut, VehiculoUpdate
from app.services import vehiculos as servicio

router = APIRouter(prefix="/vehiculos", tags=["Flota"])


@router.get("", response_model=list[VehiculoOut])
def listar(
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles(*LECTURA_FLOTA)),
    limite: int = Query(default=100, ge=1, le=200),
) -> list:
    return servicio.listar_vehiculos(db, limite)


@router.get("/{id_vehiculo}", response_model=VehiculoOut)
def obtener(
    id_vehiculo: uuid.UUID,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles(*LECTURA_FLOTA)),
) -> object:
    return servicio.obtener_vehiculo(db, id_vehiculo)


@router.post("", response_model=VehiculoCreado, status_code=status.HTTP_201_CREATED)
def crear(
    datos: VehiculoCreate,
    request: Request,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(require_roles(*ESCRITURA_FLOTA)),
) -> dict:
    vehiculo = servicio.crear_vehiculo(db, datos, actor, ip_de(request))
    cuerpo = VehiculoOut.model_validate(vehiculo).model_dump()
    cuerpo["mensaje"] = "Vehículo registrado correctamente"
    return cuerpo


@router.put("/{id_vehiculo}", response_model=VehiculoOut)
def actualizar(
    id_vehiculo: uuid.UUID,
    datos: VehiculoUpdate,
    request: Request,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(require_roles(*EDICION_FLOTA)),
) -> object:
    return servicio.actualizar_vehiculo(db, id_vehiculo, datos, actor, ip_de(request))
