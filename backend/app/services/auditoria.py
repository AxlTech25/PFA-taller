import uuid

from sqlalchemy.orm import Session

from app.models.entities import LogAuditoria


def registrar(
    db: Session,
    *,
    id_usuario: uuid.UUID | None,
    accion: str,
    tabla: str | None,
    registro_id: uuid.UUID | None,
    ip: str | None,
    anteriores: dict | None = None,
    nuevos: dict | None = None,
) -> None:
    db.add(
        LogAuditoria(
            id_usuario=id_usuario,
            accion=accion,
            tabla_afectada=tabla,
            registro_id=registro_id,
            datos_anteriores=anteriores,
            datos_nuevos=nuevos,
            ip_origen=ip,
        )
    )
