from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.models.entities import Usuario
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auditoria import registrar

MENSAJE_CREDENCIALES = "Credenciales inválidas"
MENSAJE_BLOQUEO = "La cuenta está bloqueada temporalmente. Intente nuevamente en 15 minutos."
MENSAJE_BLOQUEO_MANUAL = "La cuenta está bloqueada"
INTENTOS_PARA_BLOQUEO = 3
MINUTOS_BLOQUEO = 15


def _instante(valor: datetime) -> datetime:
    if valor.tzinfo is None:
        return valor.replace(tzinfo=UTC)
    return valor


def _bloqueo_vigente(usuario: Usuario, ahora: datetime) -> bool:
    if usuario.estado != "BLOQUEADO":
        return False
    if usuario.bloqueado_hasta is None:
        return True
    return _instante(usuario.bloqueado_hasta) > ahora


def _error_bloqueo(usuario: Usuario, ahora: datetime) -> HTTPException:
    if usuario.bloqueado_hasta is None:
        return HTTPException(status_code=423, detail=MENSAJE_BLOQUEO_MANUAL)
    restante = int((_instante(usuario.bloqueado_hasta) - ahora).total_seconds())
    return HTTPException(
        status_code=423,
        detail=MENSAJE_BLOQUEO,
        headers={"Retry-After": str(max(restante, 1))},
    )


def autenticar(db: Session, datos: LoginRequest, ip: str | None) -> TokenResponse:
    usuario = db.scalar(select(Usuario).where(Usuario.email == datos.email))
    if usuario is None:
        raise HTTPException(status_code=401, detail=MENSAJE_CREDENCIALES)

    ahora = datetime.now(UTC)
    if usuario.estado == "INACTIVO":
        raise HTTPException(status_code=403, detail="La cuenta está inactiva")
    if _bloqueo_vigente(usuario, ahora):
        raise _error_bloqueo(usuario, ahora)
    if usuario.estado == "BLOQUEADO":
        usuario.estado = "ACTIVO"
        usuario.intentos_fallidos = 0
        usuario.bloqueado_hasta = None

    if not verify_password(datos.password, usuario.password_hash):
        usuario.intentos_fallidos += 1
        usuario.actualizado_en = ahora
        if usuario.intentos_fallidos >= INTENTOS_PARA_BLOQUEO:
            usuario.estado = "BLOQUEADO"
            usuario.bloqueado_hasta = ahora + timedelta(minutes=MINUTOS_BLOQUEO)
            registrar(
                db,
                id_usuario=usuario.id_usuario,
                accion="bloqueo_cuenta",
                tabla="usuario",
                registro_id=usuario.id_usuario,
                ip=ip,
                nuevos={
                    "intentos_fallidos": usuario.intentos_fallidos,
                    "bloqueado_hasta": usuario.bloqueado_hasta.isoformat(),
                },
            )
            db.commit()
            raise _error_bloqueo(usuario, ahora)
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
    usuario.bloqueado_hasta = None
    usuario.estado = "ACTIVO"
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
