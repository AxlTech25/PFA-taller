import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

CodigoAlerta = Literal["CONGESTION", "VENTANA", "DESCANSO", "INCIDENCIA"]


class AlertaModo(BaseModel):
    codigo: CodigoAlerta
    secuencia: int | None = None
    texto: str


class ParadaModo(BaseModel):
    secuencia: int
    id_detalle: uuid.UUID = Field(
        description=(
            "Identificador del detalle de ruta. US-018 lo usará para persistir "
            "ENTREGADO o FALLIDO. Este contrato no escribe ese estado."
        )
    )
    cliente: str
    direccion: str | None = None
    punto_referencia: str | None = None
    eta: datetime | None = None
    estado_entrega: str
    nivel_congestion: str | None = None


class JornadaModo(BaseModel):
    hay_ruta: bool
    fecha: date
    mensaje: str | None = None
    id_ruta: uuid.UUID | None = None
    placa: str | None = None
    paradas: list[ParadaModo]
    alertas: list[AlertaModo]
