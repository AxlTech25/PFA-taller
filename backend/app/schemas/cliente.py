import uuid

from pydantic import BaseModel, ConfigDict


class ClienteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_cliente: uuid.UUID
    nombre: str
    telefono: str | None = None
    email: str | None = None
    consentimiento_datos: bool
