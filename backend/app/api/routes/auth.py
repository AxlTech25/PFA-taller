from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, ip_de
from app.db.session import get_db
from app.models.entities import Usuario
from app.schemas.auth import LoginRequest, TokenResponse, UsuarioSesion
from app.services.auth import autenticar

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={
        401: {"description": "Credenciales inválidas"},
        403: {"description": "Cuenta inactiva"},
        423: {"description": "Cuenta bloqueada temporalmente"},
    },
)
def login(datos: LoginRequest, request: Request, db: Session = Depends(get_db)) -> TokenResponse:
    return autenticar(db, datos, ip_de(request))


@router.get("/me", response_model=UsuarioSesion)
def me(usuario: Usuario = Depends(get_current_user)) -> Usuario:
    return usuario
