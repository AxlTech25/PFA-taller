import uuid
from datetime import date, datetime

from pydantic import BaseModel


class ParadaOut(BaseModel):
    secuencia: int
    id_pedido: uuid.UUID
    nombre_cliente: str | None = None
    eta: datetime | None = None
    latitud: float | None = None
    longitud: float | None = None
    punto_referencia: str | None = None
    minutos_tramo: float | None = None
    nivel_congestion: str | None = None


class DescansoOut(BaseModel):
    despues_de_secuencia: int
    duracion_min: int
    motivo: str


class RutaOut(BaseModel):
    id_ruta: uuid.UUID
    fecha: date
    estado: str
    distancia_total_km: float | None = None
    tiempo_total_min: float | None = None
    minutos_conduccion: float | None = None
    combustible_estimado_l: float | None = None
    co2_estimado_kg: float | None = None
    placa: str | None = None
    conductor: str | None = None
    id_conductor: uuid.UUID | None = None
    origen_lat: float | None = None
    origen_lon: float | None = None
    descansos: list[DescansoOut]
    paradas: list[ParadaOut]
    comparacion: dict | None = None
    mensaje: str | None = None


class SolicitudOptimizacion(BaseModel):
    fecha: date


class JobOut(BaseModel):
    id_job: uuid.UUID
    estado: str
    fecha: date
    mensaje: str | None = None
    algoritmo: str | None = None
    comparacion: dict | None = None
    rutas: list[RutaOut]


class IndicadoresOut(BaseModel):
    fecha: date
    hay_datos: bool
    mensaje: str | None = None
    rutas: int = 0
    km: float = 0
    co2_kg: float = 0
    combustible_l: float = 0
    soles_combustible: float = 0
    soles_mantenimiento: float = 0
    soles_ahorrados: float = 0
    co2_ahorrado_kg: float = 0
    arboles: float | None = None
    nota_arboles: str | None = None
    cumplimiento_ventanas_pct: float = 0
    mejora_porcentaje: float | None = None
