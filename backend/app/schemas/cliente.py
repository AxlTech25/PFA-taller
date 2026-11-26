import uuid
from datetime import time

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class ClienteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_cliente: uuid.UUID
    nombre: str
    telefono: str | None = None
    email: str | None = None
    consentimiento_datos: bool


MENSAJE_HORARIO_CONTRADICTORIO = (
    "La hora de inicio debe ser anterior a la hora de fin. Corrija el horario preferido."
)


def _texto(valor: str | None, maximo: int) -> str | None:
    if valor is None:
        return None
    limpio = valor.strip()
    if not limpio:
        return None
    if len(limpio) > maximo:
        raise ValueError(f"El texto no puede superar {maximo} caracteres")
    return limpio


class PreferenciaIn(BaseModel):
    """US-009 / RF-009: horario preferido, punto de referencia y restricción de acceso."""

    hora_inicio: time
    hora_fin: time
    punto_referencia: str | None = None
    restricciones_acceso: str | None = None

    @field_validator("hora_inicio", "hora_fin")
    @classmethod
    def sin_zona(cls, valor: time) -> time:
        return valor.replace(tzinfo=None, microsecond=0)

    @field_validator("punto_referencia")
    @classmethod
    def punto_valido(cls, valor: str | None) -> str | None:
        return _texto(valor, 255)

    @field_validator("restricciones_acceso")
    @classmethod
    def restricciones_validas(cls, valor: str | None) -> str | None:
        return _texto(valor, 500)

    @model_validator(mode="after")
    def horario_ordenado(self) -> "PreferenciaIn":
        if self.hora_inicio >= self.hora_fin:
            raise ValueError(MENSAJE_HORARIO_CONTRADICTORIO)
        return self


class PreferenciaOut(BaseModel):
    id_cliente: uuid.UUID
    nombre_cliente: str
    registrada: bool
    hora_inicio: time | None = None
    hora_fin: time | None = None
    punto_referencia: str | None = None
    restricciones_acceso: str | None = None
    mensaje: str | None = None
