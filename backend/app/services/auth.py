from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import func, or_, select
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


def _reloj(db: Session) -> datetime:
    marca = db.scalar(select(func.clock_timestamp()))
    if not isinstance(marca, datetime):
        return datetime.now(UTC)
    if marca.tzinfo is None:
        return marca.replace(tzinfo=UTC)
    return marca.astimezone(UTC)


def _bloqueo_vigente(db: Session, usuario: Usuario) -> bool:
    """El vencimiento lo decide PostgreSQL, no un datetime mal etiquetado."""
    if usuario.estado != "BLOQUEADO":
        return False
    vigente = db.scalar(
        select(
            or_(
                Usuario.bloqueado_hasta.is_(None),
                Usuario.bloqueado_hasta > func.clock_timestamp(),
            )
        ).where(Usuario.id_usuario == usuario.id_usuario)
    )
    return bool(vigente)


def _error_bloqueo(db: Session, usuario: Usuario) -> HTTPException:
    if usuario.bloqueado_hasta is None:
        return HTTPException(status_code=423, detail=MENSAJE_BLOQUEO_MANUAL)
    segundos = db.scalar(
        select(func.extract("epoch", Usuario.bloqueado_hasta - func.clock_timestamp())).where(
            Usuario.id_usuario == usuario.id_usuario
        )
    )
    restante = max(int(segundos or 1), 1)
    return HTTPException(
        status_code=423,
        detail=MENSAJE_BLOQUEO,
        headers={"Retry-After": str(restante)},
    )


def autenticar(db: Session, datos: LoginRequest, ip: str | None) -> TokenResponse:
    usuario = db.scalar(
        select(Usuario).where(Usuario.email == datos.email).with_for_update()
    )
    if usuario is None:
        raise HTTPException(status_code=401, detail=MENSAJE_CREDENCIALES)

    if usuario.estado == "INACTIVO":
        raise HTTPException(status_code=403, detail="La cuenta está inactiva")
    if _bloqueo_vigente(db, usuario):
        raise _error_bloqueo(db, usuario)
    if usuario.estado == "BLOQUEADO":
        usuario.estado = "ACTIVO"
        usuario.intentos_fallidos = 0
        usuario.bloqueado_hasta = None

    if not verify_password(datos.password, usuario.password_hash):
        ahora = _reloj(db)
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
            raise _error_bloqueo(db, usuario)
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
    usuario.actualizado_en = _reloj(db)
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
