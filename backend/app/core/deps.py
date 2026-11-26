import uuid
from collections.abc import Callable

from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token, ip_valida
from app.db.session import get_db
from app.models.entities import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

ROLES = ("ADMIN", "GERENTE", "OPERADOR", "CONDUCTOR", "AUDITOR")
LECTURA_FLOTA = ROLES
ESCRITURA_FLOTA = ("ADMIN", "OPERADOR")
EDICION_FLOTA = ("ADMIN", "GERENTE", "OPERADOR")
LECTURA_USUARIOS = ("ADMIN", "GERENTE")
ESCRITURA_USUARIOS = ("ADMIN",)
LECTURA_CONDUCTORES = ROLES
ESCRITURA_CONDUCTORES = ("ADMIN", "OPERADOR")
LECTURA_PEDIDOS = ROLES
ESCRITURA_PEDIDOS = ("ADMIN", "OPERADOR")
LECTURA_CLIENTES = ("ADMIN", "GERENTE", "OPERADOR", "AUDITOR")
LECTURA_RUTAS = ("ADMIN", "GERENTE", "OPERADOR", "AUDITOR")
ESCRITURA_RUTAS = ("ADMIN", "OPERADOR")
# US-011: la matriz de permisos deja a gerencia ejecutar la re-optimización.
REOPTIMIZACION_RUTAS = ("ADMIN", "GERENTE", "OPERADOR")
# US-016 / RF-006: Admin, Gerente y Operador generan; Auditor tiene lectura.
REPORTES_SOSTENIBILIDAD = ("ADMIN", "GERENTE", "OPERADOR", "AUDITOR")
# US-017 / RF-010: el documento 08 da lectura del plan a Admin, Gerente, Operador y Auditor.
PLAN_COMPENSACION = ("ADMIN", "GERENTE", "OPERADOR", "AUDITOR")


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
