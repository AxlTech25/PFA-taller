from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.entities import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate
from app.services.auditoria import registrar
from app.services.integridad import mensaje_integridad
from app.services.sanitizacion import exigir_textos_seguros


def listar_usuarios(db: Session, limite: int) -> list[Usuario]:
    return list(db.scalars(select(Usuario).order_by(Usuario.email).limit(limite)).all())


def crear_usuario(db: Session, datos: UsuarioCreate, actor: Usuario, ip: str | None) -> Usuario:
    exigir_textos_seguros(
        db,
        id_usuario=actor.id_usuario,
        ip=ip,
        tabla="usuario",
        campos=[(datos.email, "email"), (datos.rol, "rol")],
    )
    usuario = Usuario(
        email=datos.email,
        password_hash=hash_password(datos.password),
        rol=datos.rol,
        estado=datos.estado,
        intentos_fallidos=0,
    )
    db.add(usuario)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        mensaje = mensaje_integridad(exc) or "No se pudo registrar el usuario"
        raise HTTPException(status_code=409, detail=mensaje) from exc
    db.refresh(usuario)
    registrar(
        db,
        id_usuario=actor.id_usuario,
        accion="crear_usuario",
        tabla="usuario",
        registro_id=usuario.id_usuario,
        ip=ip,
        nuevos={"email": usuario.email, "rol": usuario.rol, "estado": usuario.estado},
    )
    db.commit()
    return usuario


def actualizar_usuario(
    db: Session, id_usuario, datos: UsuarioUpdate, actor: Usuario, ip: str | None
) -> Usuario:
    if not datos.hay_cambios():
        raise HTTPException(status_code=422, detail="Debe indicar el rol o el estado")
    usuario = db.get(Usuario, id_usuario)
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if actor.id_usuario == usuario.id_usuario and datos.estado in {"INACTIVO", "BLOQUEADO"}:
        raise HTTPException(
            status_code=409, detail="No puede bloquear ni desactivar su propia cuenta"
        )
    anteriores = {"rol": usuario.rol, "estado": usuario.estado}
    if datos.rol is not None:
        usuario.rol = datos.rol
    if datos.estado is not None:
        usuario.estado = datos.estado
        if datos.estado == "ACTIVO":
            usuario.intentos_fallidos = 0
            usuario.bloqueado_hasta = None
    db.commit()
    db.refresh(usuario)
    registrar(
        db,
        id_usuario=actor.id_usuario,
        accion="actualizar_usuario",
        tabla="usuario",
        registro_id=usuario.id_usuario,
        ip=ip,
        anteriores=anteriores,
        nuevos={"rol": usuario.rol, "estado": usuario.estado},
    )
    db.commit()
    return usuario
