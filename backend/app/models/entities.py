import uuid
from datetime import datetime, time
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Time, text
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Usuario(Base):
    __tablename__ = "usuario"

    id_usuario: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[str] = mapped_column(String(30), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVO")
    intentos_fallidos: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    bloqueado_hasta: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )


class Cliente(Base):
    __tablename__ = "cliente"

    id_cliente: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    telefono: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(255))
    consentimiento_datos: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )


class Vehiculo(Base):
    __tablename__ = "vehiculo"

    id_vehiculo: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
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
        DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )


class Conductor(Base):
    __tablename__ = "conductor"

    id_conductor: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    id_usuario: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuario.id_usuario"), unique=True
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
        DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )


class Pedido(Base):
    __tablename__ = "pedido"

    id_pedido: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
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
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )


class LogAuditoria(Base):
    __tablename__ = "log_auditoria"

    id_log: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    id_usuario: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuario.id_usuario")
    )
    accion: Mapped[str] = mapped_column(String(100), nullable=False)
    tabla_afectada: Mapped[str | None] = mapped_column(String(50))
    registro_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    datos_anteriores: Mapped[dict | None] = mapped_column(JSONB)
    datos_nuevos: Mapped[dict | None] = mapped_column(JSONB)
    ip_origen: Mapped[str | None] = mapped_column(INET)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
