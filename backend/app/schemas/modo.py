import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

CodigoAlerta = Literal["CONGESTION", "VENTANA", "DESCANSO", "INCIDENCIA", "REOPTIMIZACION"]


class AlertaModo(BaseModel):
    codigo: CodigoAlerta
    secuencia: int | None = None
    texto: str


class ParadaModo(BaseModel):
    secuencia: int
    id_detalle: uuid.UUID = Field(
        description=(
            "Identificador del detalle de ruta. Se envía a "
            "POST /modo/paradas/{id_detalle}/confirmacion para registrar "
            "ENTREGADO o FALLIDO (US-018)."
        )
    )
    cliente: str
    direccion: str | None = None
    punto_referencia: str | None = None
    eta: datetime | None = None
    estado_entrega: str
    motivo_fallo: str | None = None
    nivel_congestion: str | None = None


class JornadaModo(BaseModel):
    hay_ruta: bool
    fecha: date
    mensaje: str | None = None
    id_ruta: uuid.UUID | None = None
    placa: str | None = None
    paradas: list[ParadaModo]
    alertas: list[AlertaModo]


class PuntoModo(BaseModel):
    secuencia: int
    latitud: float
    longitud: float
    cliente: str


class MapaModo(BaseModel):
    """Coordenadas opcionales. La lista de paradas no las necesita."""

    hay_ruta: bool
    placa: str | None = None
    puntos: list[PuntoModo]


ResultadoEntrega = Literal["ENTREGADO", "FALLIDO"]
MOTIVO_MAXIMO = 250
MENSAJE_MOTIVO = "Indique el motivo cuando la entrega es fallida."


class ConfirmacionEntregaIn(BaseModel):
    resultado: ResultadoEntrega = Field(
        description="ENTREGADO o FALLIDO. Otros estados no se aceptan aquí."
    )
    motivo: str | None = Field(
        default=None,
        max_length=MOTIVO_MAXIMO,
        description="Obligatorio si el resultado es FALLIDO. Se ignora si es ENTREGADO.",
    )

    @field_validator("motivo")
    @classmethod
    def _recortar(cls, valor: str | None) -> str | None:
        if valor is None:
            return None
        limpio = " ".join(valor.split())
        return limpio or None

    @model_validator(mode="after")
    def _motivo_si_falla(self) -> "ConfirmacionEntregaIn":
        if self.resultado == "FALLIDO" and not self.motivo:
            raise ValueError(MENSAJE_MOTIVO)
        if self.resultado == "ENTREGADO":
            self.motivo = None
        return self


class ConfirmacionEntregaOut(BaseModel):
    id_detalle: uuid.UUID
    secuencia: int
    estado_entrega: ResultadoEntrega
    motivo_fallo: str | None = None
    confirmada_en: datetime
    mensaje: str
