import re
import uuid
from datetime import time

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

DNI_PERU = re.compile(r"^\d{8}$")


class ConductorCreate(BaseModel):
    nombre: str
    dni: str
    licencia_categoria: str
    anios_experiencia: int = 0
    disponibilidad_inicio: time
    disponibilidad_fin: time
    lat_punto_partida: float
    lon_punto_partida: float

    @field_validator("nombre")
    @classmethod
    def nombre_valido(cls, valor: str) -> str:
        nombre = valor.strip()
        if not nombre:
            raise ValueError("El nombre es obligatorio")
        if len(nombre) > 150:
            raise ValueError("El nombre no puede superar 150 caracteres")
        return nombre

    @field_validator("dni")
    @classmethod
    def dni_valido(cls, valor: str) -> str:
        dni = valor.strip()
        if not DNI_PERU.fullmatch(dni):
            raise ValueError("El DNI debe tener 8 dígitos")
        return dni

    @field_validator("licencia_categoria")
    @classmethod
    def licencia_valida(cls, valor: str) -> str:
        licencia = valor.strip().upper()
        if not licencia:
            raise ValueError("La categoría de licencia es obligatoria")
        if len(licencia) > 10:
            raise ValueError("La categoría de licencia no puede superar 10 caracteres")
        return licencia

    @field_validator("anios_experiencia")
    @classmethod
    def experiencia_valida(cls, valor: int) -> int:
        if valor < 0:
            raise ValueError("Los años de experiencia no pueden ser negativos")
        return valor

    @field_validator("lat_punto_partida")
    @classmethod
    def latitud_valida(cls, valor: float) -> float:
        if valor < -90 or valor > 90:
            raise ValueError("La latitud del punto de partida no es válida")
        return valor

    @field_validator("lon_punto_partida")
    @classmethod
    def longitud_valida(cls, valor: float) -> float:
        if valor < -180 or valor > 180:
            raise ValueError("La longitud del punto de partida no es válida")
        return valor

    @model_validator(mode="after")
    def horario_valido(self) -> "ConductorCreate":
        if self.disponibilidad_inicio >= self.disponibilidad_fin:
            raise ValueError("La hora de inicio debe ser menor que la hora de fin")
        return self


class ConductorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_conductor: uuid.UUID
    nombre: str
    dni: str | None = None
    licencia_categoria: str
    anios_experiencia: int
    disponibilidad_inicio: time
    disponibilidad_fin: time
    lat_punto_partida: float | None = None
    lon_punto_partida: float | None = None
    estado: str


class ConductorCreado(ConductorOut):
    mensaje: str
