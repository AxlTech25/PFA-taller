import re

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.services.auditoria import registrar

PATRON_PELIGROSO = re.compile(
    r"(<\s*script\b|</\s*script\b|javascript\s*:|onerror\s*=|onload\s*=|<\s*iframe\b|"
    r"\bunion\s+select\b|;\s*drop\s+table\b|'\s*or\s+'1'\s*=\s*'1)",
    re.IGNORECASE,
)


class EntradaRechazada(Exception):
    def __init__(self, campo: str) -> None:
        self.campo = campo
        super().__init__(campo)


def revisar_texto(valor: str | None, campo: str) -> str | None:
    if valor is None:
        return None
    if PATRON_PELIGROSO.search(valor):
        raise EntradaRechazada(campo)
    return valor


def exigir_textos_seguros(
    db: Session,
    *,
    id_usuario,
    ip: str | None,
    tabla: str,
    campos: list[tuple[str | None, str]],
) -> None:
    for valor, campo in campos:
        try:
            revisar_texto(valor, campo)
        except EntradaRechazada as exc:
            rechazar_entrada(
                db,
                id_usuario=id_usuario,
                ip=ip,
                campo=exc.campo,
                tabla=tabla,
            )


def rechazar_entrada(
    db: Session,
    *,
    id_usuario,
    ip: str | None,
    campo: str,
    tabla: str,
) -> None:
    registrar(
        db,
        id_usuario=id_usuario,
        accion="entrada_rechazada",
        tabla=tabla,
        registro_id=None,
        ip=ip,
        nuevos={"motivo": "patron_no_permitido", "campo": campo},
    )
    db.commit()
    raise HTTPException(status_code=422, detail="La entrada contiene un patrón no permitido")
