import uuid

from pydantic import BaseModel, Field


class ZonaOut(BaseModel):
    id_zona: uuid.UUID
    nombre: str
    tipo: str
    severidad: str
    es_demostracion: bool
    geometria: dict


class ListadoZonas(BaseModel):
    advertencia: str
    zonas: list[ZonaOut] = Field(default_factory=list)


class ZonaCruzadaOut(BaseModel):
    id_zona: uuid.UUID
    nombre: str
    tipo: str
    severidad: str
