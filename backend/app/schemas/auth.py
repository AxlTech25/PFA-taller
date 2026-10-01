import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def normalizar_email(cls, valor: str) -> str:
        return valor.strip().lower()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    id_usuario: uuid.UUID
    email: str
    rol: str


class UsuarioSesion(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_usuario: uuid.UUID
    email: str
    rol: str
    estado: str
