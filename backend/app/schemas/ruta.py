import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from app.schemas.zona import ZonaCruzadaOut


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
    estado_entrega: str | None = None


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
    trazado: list[list[float]] | None = None
    evita_riesgo: bool = False
    zonas_cruzadas: list[ZonaCruzadaOut] = Field(default_factory=list)
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


MotivoReoptimizacion = Literal[
    "NUEVO_PEDIDO",
    "CANCELACION",
    "PARADA_FALLIDA",
    "ACCIDENTE_TRANSITO",
    "CONGESTION",
]
MENSAJE_SIN_AGREGAR = "Indique al menos un pedido nuevo para agregar."
MENSAJE_SIN_CANCELAR = "Indique al menos un pedido para cancelar."
MENSAJE_REPETIDO = "Un pedido no puede agregarse y cancelarse a la vez."


class ReoptimizacionIn(BaseModel):
    motivo: MotivoReoptimizacion = Field(
        description=(
            "Evento que dispara la re-optimización (RN-015). NUEVO_PEDIDO exige `agregar`; "
            "CANCELACION exige `cancelar`. ACCIDENTE_TRANSITO cubre una vía o zona bloqueada."
        )
    )
    descripcion: str | None = Field(default=None, max_length=255)
    agregar: list[uuid.UUID] = Field(default_factory=list, max_length=20)
    cancelar: list[uuid.UUID] = Field(default_factory=list, max_length=20)

    @field_validator("descripcion")
    @classmethod
    def _recortar(cls, valor: str | None) -> str | None:
        if valor is None:
            return None
        limpio = " ".join(valor.split())
        return limpio or None

    @model_validator(mode="after")
    def _coherente(self) -> "ReoptimizacionIn":
        self.agregar = list(dict.fromkeys(self.agregar))
        self.cancelar = list(dict.fromkeys(self.cancelar))
        if self.motivo == "NUEVO_PEDIDO" and not self.agregar:
            raise ValueError(MENSAJE_SIN_AGREGAR)
        if self.motivo == "CANCELACION" and not self.cancelar:
            raise ValueError(MENSAJE_SIN_CANCELAR)
        if set(self.agregar) & set(self.cancelar):
            raise ValueError(MENSAJE_REPETIDO)
        return self


class ReoptimizacionOut(BaseModel):
    mensaje: str
    segundos: float = Field(description="Tiempo medido del cálculo (perf_counter), en segundos.")
    presupuesto_s: float = Field(description="Tope aplicado: tiempo_max_reoptimizacion_s ≤ 30 s.")
    cortado: bool = Field(description="True si se usó la mejor solución hallada al llegar al tope.")
    estrategia: str
    paradas_fijas: int
    paradas_reordenadas: int
    agregadas: int
    canceladas: int
    distancia_antes_km: float | None = None
    distancia_despues_km: float | None = None
    ruta: RutaOut


class PedidoDisponibleOut(BaseModel):
    id_pedido: uuid.UUID
    nombre_cliente: str | None = None
    punto_referencia: str | None = None
    peso_kg: float
    prioridad: str
