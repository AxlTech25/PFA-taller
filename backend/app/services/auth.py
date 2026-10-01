from datetime import UTC, datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.models.entities import Usuario
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auditoria import registrar

MENSAJE_CREDENCIALES = "Credenciales inválidas"


def autenticar(db: Session, datos: LoginRequest, ip: str | None) -> TokenResponse:
    usuario = db.scalar(select(Usuario).where(Usuario.email == datos.email))
    if usuario is None:
        raise HTTPException(status_code=401, detail=MENSAJE_CREDENCIALES)

    ahora = datetime.now(UTC)
    if usuario.estado == "BLOQUEADO":
        raise HTTPException(status_code=403, detail="La cuenta está bloqueada")
    if usuario.estado != "ACTIVO":
        raise HTTPException(status_code=403, detail="La cuenta está inactiva")

    if not verify_password(datos.password, usuario.password_hash):
        usuario.intentos_fallidos += 1
        usuario.actualizado_en = ahora
        registrar(
            db,
            id_usuario=usuario.id_usuario,
            accion="login_fallido",
            tabla="usuario",
            registro_id=usuario.id_usuario,
            ip=ip,
            nuevos={"intentos_fallidos": usuario.intentos_fallidos},
        )
        db.commit()
        raise HTTPException(status_code=401, detail=MENSAJE_CREDENCIALES)

    usuario.intentos_fallidos = 0
    usuario.actualizado_en = ahora
    token = create_access_token(
        user_id=usuario.id_usuario, email=usuario.email, rol=usuario.rol
    )
    registrar(
        db,
        id_usuario=usuario.id_usuario,
        accion="login",
        tabla="usuario",
        registro_id=usuario.id_usuario,
        ip=ip,
        nuevos={"rol": usuario.rol},
    )
    db.commit()
    return TokenResponse(
        access_token=token,
        id_usuario=usuario.id_usuario,
        email=usuario.email,
        rol=usuario.rol,
    )
