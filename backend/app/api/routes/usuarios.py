import uuid

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.core.deps import ESCRITURA_USUARIOS, LECTURA_USUARIOS, ip_de, require_roles
from app.db.session import get_db
from app.models.entities import Usuario
from app.schemas.usuario import UsuarioCreado, UsuarioCreate, UsuarioOut, UsuarioUpdate
from app.services import usuarios as servicio

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get("", response_model=list[UsuarioOut])
def listar(
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles(*LECTURA_USUARIOS)),
    limite: int = Query(default=100, ge=1, le=200),
) -> list:
    return servicio.listar_usuarios(db, limite)


@router.post("", response_model=UsuarioCreado, status_code=status.HTTP_201_CREATED)
def crear(
    datos: UsuarioCreate,
    request: Request,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(require_roles(*ESCRITURA_USUARIOS)),
) -> dict:
    usuario = servicio.crear_usuario(db, datos, actor, ip_de(request))
    cuerpo = UsuarioOut.model_validate(usuario).model_dump()
    cuerpo["mensaje"] = "Usuario registrado correctamente"
    return cuerpo


@router.patch("/{id_usuario}", response_model=UsuarioOut)
def actualizar(
    id_usuario: uuid.UUID,
    datos: UsuarioUpdate,
    request: Request,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(require_roles(*ESCRITURA_USUARIOS)),
) -> Usuario:
    return servicio.actualizar_usuario(db, id_usuario, datos, actor, ip_de(request))
