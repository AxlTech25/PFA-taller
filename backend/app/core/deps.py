import uuid
from collections.abc import Callable

from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token, ip_valida
from app.db.session import get_db
from app.models.entities import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

LECTURA_FLOTA = ("ADMIN", "GERENTE", "OPERADOR", "CONDUCTOR", "AUDITOR")
ESCRITURA_FLOTA = ("ADMIN", "OPERADOR")


def ip_de(request: Request) -> str | None:
    host = request.client.host if request.client else None
    return ip_valida(host)


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    if not token:
        raise HTTPException(status_code=401, detail="No autenticado")
    payload = decode_token(token)
    try:
        user_id = uuid.UUID(payload.get("sub", ""))
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Token inválido o expirado") from exc
    user = db.get(Usuario, user_id)
    if user is None or user.estado != "ACTIVO":
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    return user


def require_roles(*roles: str) -> Callable:
    def _dependencia(user: Usuario = Depends(get_current_user)) -> Usuario:
        if user.rol not in roles:
            raise HTTPException(
                status_code=403,
                detail="No tiene permiso para realizar esta acción",
            )
        return user

    return _dependencia
