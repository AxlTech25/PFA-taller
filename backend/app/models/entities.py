import uuid
from datetime import date, datetime, time
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Time,
    text,
)
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

_UUID_V4 = "uuid_generate_v4()"
_AHORA = "CURRENT_TIMESTAMP"
_FK_USUARIO = "usuario.id_usuario"
_FK_RUTA = "ruta.id_ruta"


class Usuario(Base):
    __tablename__ = "usuario"

    id_usuario: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text(_UUID_V4)
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[str] = mapped_column(String(30), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVO")
    intentos_fallidos: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    bloqueado_hasta: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text(_AHORA)
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text(_AHORA)
    )


class Cliente(Base):
    __tablename__ = "cliente"

    id_cliente: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text(_UUID_V4)
    )
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    telefono: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(255))
    consentimiento_datos: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text(_AHORA)
    )


class Vehiculo(Base):
    __tablename__ = "vehiculo"

    id_vehiculo: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text(_UUID_V4)
    )
    placa: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)
    capacidad_kg: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    capacidad_m3: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    consumo_km_l: Mapped[Decimal] = mapped_column(Numeric(8, 3), nullable=False)
    factor_emision_co2: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False)
    anio_fabricacion: Mapped[int] = mapped_column(Integer, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVO")
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text(_AHORA)
    )


class Conductor(Base):
    __tablename__ = "conductor"

    id_conductor: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text(_UUID_V4)
    )
    id_usuario: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey(_FK_USUARIO), unique=True
    )
    dni: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    licencia_categoria: Mapped[str] = mapped_column(String(10), nullable=False)
    anios_experiencia: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    disponibilidad_inicio: Mapped[time] = mapped_column(Time, nullable=False)
    disponibilidad_fin: Mapped[time] = mapped_column(Time, nullable=False)
    lat_punto_partida: Mapped[Decimal | None] = mapped_column(Numeric(10, 7))
    lon_punto_partida: Mapped[Decimal | None] = mapped_column(Numeric(10, 7))
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVO")
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text(_AHORA)
    )


class Pedido(Base):
    __tablename__ = "pedido"

    id_pedido: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text(_UUID_V4)
    )
    id_cliente: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cliente.id_cliente"), nullable=False
    )
    direccion: Mapped[str | None] = mapped_column(String(255))
    punto_referencia: Mapped[str | None] = mapped_column(String(255))
    latitud: Mapped[Decimal] = mapped_column(Numeric(10, 7), nullable=False)
    longitud: Mapped[Decimal] = mapped_column(Numeric(10, 7), nullable=False)
    peso_kg: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    volumen_m3: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    ventana_inicio: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ventana_fin: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    prioridad: Mapped[str] = mapped_column(String(20), nullable=False, default="ESTANDAR")
    tipo_producto: Mapped[str] = mapped_column(String(30), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDIENTE")
    georreferencia_aproximada: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text(_AHORA)
    )


class LogAuditoria(Base):
    __tablename__ = "log_auditoria"

    id_log: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text(_UUID_V4)
    )
    id_usuario: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey(_FK_USUARIO)
    )
    accion: Mapped[str] = mapped_column(String(100), nullable=False)
    tabla_afectada: Mapped[str | None] = mapped_column(String(50))
    registro_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    datos_anteriores: Mapped[dict | None] = mapped_column(JSONB)
    datos_nuevos: Mapped[dict | None] = mapped_column(JSONB)
    ip_origen: Mapped[str | None] = mapped_column(INET)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text(_AHORA)
    )


class JobOptimizacion(Base):
    __tablename__ = "job_optimizacion"

    id_job: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text(_UUID_V4)
    )
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="ENCOLADO")
    id_usuario: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey(_FK_USUARIO)
    )
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    mensaje: Mapped[str | None] = mapped_column(Text)
    resultado: Mapped[dict | None] = mapped_column(JSONB)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text(_AHORA)
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text(_AHORA)
    )


class Ruta(Base):
    __tablename__ = "ruta"

    id_ruta: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text(_UUID_V4)
    )
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="BORRADOR")
    distancia_total_km: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    tiempo_total_min: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    combustible_estimado_l: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    co2_estimado_kg: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    minutos_conduccion: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    id_job: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("job_optimizacion.id_job")
    )
    generada_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text(_AHORA)
    )


class AsignacionRuta(Base):
    __tablename__ = "asignacion_ruta"

    id_asignacion: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text(_UUID_V4)
    )
    id_ruta: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey(_FK_RUTA), unique=True, nullable=False
    )
    id_vehiculo: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vehiculo.id_vehiculo"), nullable=False
    )
    id_conductor: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conductor.id_conductor"), nullable=False
    )
    asignada_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text(_AHORA)
    )


class DetalleRuta(Base):
    __tablename__ = "detalle_ruta"

    id_detalle: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text(_UUID_V4)
    )
    id_ruta: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey(_FK_RUTA), nullable=False
    )
    id_pedido: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pedido.id_pedido"), nullable=False
    )
    secuencia: Mapped[int] = mapped_column(Integer, nullable=False)
    eta: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    estado_entrega: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDIENTE")


class DescansoRuta(Base):
    __tablename__ = "descanso_ruta"

    id_descanso: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text(_UUID_V4)
    )
    id_ruta: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey(_FK_RUTA), nullable=False
    )
    despues_de_secuencia: Mapped[int] = mapped_column(Integer, nullable=False)
    duracion_min: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    motivo: Mapped[str] = mapped_column(String(80), nullable=False, default="LEY_30224")
