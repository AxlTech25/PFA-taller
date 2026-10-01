import uuid
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator

from app.schemas.comun import validar_anio

TipoVehiculo = Literal["CAMIONETA", "FURGON", "MOTO"]
EstadoVehiculo = Literal["ACTIVO", "MANTENIMIENTO", "INACTIVO"]


class VehiculoCreate(BaseModel):
    placa: str
    tipo: TipoVehiculo
    capacidad_kg: float
    capacidad_m3: float
    consumo_km_l: float
    factor_emision_co2: float
    anio_fabricacion: int
    estado: EstadoVehiculo = "ACTIVO"

    @field_validator("placa")
    @classmethod
    def normalizar_placa(cls, valor: str) -> str:
        placa = valor.strip().upper().replace(" ", "")
        if not placa:
            raise ValueError("La placa es obligatoria")
        if len(placa) > 10:
            raise ValueError("La placa no puede superar 10 caracteres")
        return placa

    @field_validator("capacidad_kg", "capacidad_m3")
    @classmethod
    def capacidad_positiva(cls, valor: float) -> float:
        if valor <= 0:
            raise ValueError("Datos de capacidad inválidos")
        return valor

    @field_validator("consumo_km_l")
    @classmethod
    def consumo_positivo(cls, valor: float) -> float:
        if valor <= 0:
            raise ValueError("El consumo debe ser mayor a cero")
        return valor

    @field_validator("factor_emision_co2")
    @classmethod
    def factor_positivo(cls, valor: float) -> float:
        if valor <= 0:
            raise ValueError("El factor de emisión debe ser mayor a cero")
        return valor

    @field_validator("anio_fabricacion")
    @classmethod
    def anio_valido(cls, valor: int) -> int:
        return validar_anio(valor)


class VehiculoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_vehiculo: uuid.UUID
    placa: str
    tipo: str
    capacidad_kg: float
    capacidad_m3: float
    consumo_km_l: float
    factor_emision_co2: float
    anio_fabricacion: int
    estado: str


class VehiculoUpdate(BaseModel):
    estado: EstadoVehiculo | None = None
    factor_emision_co2: float | None = None

    @field_validator("factor_emision_co2")
    @classmethod
    def factor_positivo(cls, valor: float | None) -> float | None:
        if valor is not None and valor <= 0:
            raise ValueError("El factor de emisión debe ser mayor a cero")
        return valor

    def hay_cambios(self) -> bool:
        return self.estado is not None or self.factor_emision_co2 is not None


class VehiculoCreado(VehiculoOut):
    mensaje: str
