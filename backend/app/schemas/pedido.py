import uuid
from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, field_validator, model_validator

PrioridadPedido = Literal["EXPRESS", "ESTANDAR", "ECONOMICO"]
TipoProducto = Literal["PERECEDERO", "NO_PERECEDERO"]


def _con_zona(valor: datetime) -> datetime:
    if valor.tzinfo is None:
        return valor.replace(tzinfo=UTC)
    return valor


class PedidoCreate(BaseModel):
    id_cliente: uuid.UUID
    direccion: str | None = None
    punto_referencia: str | None = None
    latitud: float
    longitud: float
    peso_kg: float
    volumen_m3: float
    ventana_inicio: datetime
    ventana_fin: datetime
    prioridad: PrioridadPedido = "ESTANDAR"
    tipo_producto: TipoProducto

    @field_validator("direccion", "punto_referencia")
    @classmethod
    def texto_opcional(cls, valor: str | None) -> str | None:
        if valor is None:
            return None
        limpio = valor.strip()
        if not limpio:
            return None
        if len(limpio) > 255:
            raise ValueError("El texto no puede superar 255 caracteres")
        return limpio

    @field_validator("peso_kg")
    @classmethod
    def peso_valido(cls, valor: float) -> float:
        if valor <= 0:
            raise ValueError("El peso debe ser mayor a cero")
        return valor

    @field_validator("volumen_m3")
    @classmethod
    def volumen_valido(cls, valor: float) -> float:
        if valor <= 0:
            raise ValueError("El volumen debe ser mayor a cero")
        return valor

    @field_validator("latitud")
    @classmethod
    def latitud_valida(cls, valor: float) -> float:
        if valor < -90 or valor > 90:
            raise ValueError("La latitud no es válida")
        return valor

    @field_validator("longitud")
    @classmethod
    def longitud_valida(cls, valor: float) -> float:
        if valor < -180 or valor > 180:
            raise ValueError("La longitud no es válida")
        return valor

    @field_validator("ventana_inicio", "ventana_fin")
    @classmethod
    def ventana_con_zona(cls, valor: datetime) -> datetime:
        return _con_zona(valor)

    @model_validator(mode="after")
    def ventana_ordenada(self) -> "PedidoCreate":
        if self.ventana_inicio >= self.ventana_fin:
            raise ValueError("La ventana de inicio debe ser anterior a la ventana de fin")
        return self


class PedidoOut(BaseModel):
    id_pedido: uuid.UUID
    id_cliente: uuid.UUID
    nombre_cliente: str | None = None
    direccion: str | None = None
    punto_referencia: str | None = None
    latitud: float | None = None
    longitud: float | None = None
    peso_kg: float
    volumen_m3: float
    ventana_inicio: datetime
    ventana_fin: datetime
    prioridad: str
    tipo_producto: str
    estado: str


class PedidoCreado(PedidoOut):
    mensaje: str
