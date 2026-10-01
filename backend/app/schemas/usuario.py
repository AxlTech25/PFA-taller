import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

RolUsuario = Literal["ADMIN", "GERENTE", "OPERADOR", "CONDUCTOR", "AUDITOR"]
EstadoAlta = Literal["ACTIVO", "INACTIVO"]
EstadoUsuario = Literal["ACTIVO", "INACTIVO", "BLOQUEADO"]


class UsuarioCreate(BaseModel):
    email: EmailStr
    password: str
    rol: RolUsuario
    estado: EstadoAlta = "ACTIVO"

    @field_validator("email")
    @classmethod
    def normalizar_email(cls, valor: str) -> str:
        return valor.strip().lower()

    @field_validator("password")
    @classmethod
    def clave_valida(cls, valor: str) -> str:
        if len(valor) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        if len(valor) > 128:
            raise ValueError("La contraseña es demasiado larga")
        return valor


class UsuarioUpdate(BaseModel):
    rol: RolUsuario | None = None
    estado: EstadoUsuario | None = None

    def hay_cambios(self) -> bool:
        return self.rol is not None or self.estado is not None


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_usuario: uuid.UUID
    email: str
    rol: str
    estado: str
    intentos_fallidos: int
    bloqueado_hasta: datetime | None = None


class UsuarioCreado(UsuarioOut):
    mensaje: str
