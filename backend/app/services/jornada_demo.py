"""Ruta confirmada de hoy para el usuario conductor de demostración.

La carga inicial la llama solo si SEED_CONDUCTOR_PASSWORD está definida.
Reutiliza el cliente con consentimiento y la unidad DMO-101. No inventa
kilómetros, CO₂ ni el factor de árboles: esos campos de la ruta quedan vacíos.
Cada arranque deja la misma ruta en la fecha operativa, sin duplicar paradas.
"""

import logging
from datetime import UTC, datetime, time
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import (
    AsignacionRuta,
    Cliente,
    Conductor,
    DetalleRuta,
    Incidencia,
    Pedido,
    Ruta,
    Usuario,
    Vehiculo,
)
from app.services.modo import fecha_operativa

logger = logging.getLogger("ecologistica.jornada")

DNI_DEMO = "70015015"
PLACA_DEMO = "DMO-101"
CORREO_CLIENTE = "demo.consentido@distrirapido.example.com"
DESCRIPCION_AVISO = (
    "Aviso de demostración: revisar el tramo de Av. Próceres de la Independencia."
)

# Coordenadas dentro de la envolvente operativa de San Juan de Lurigancho.
# La hora es la marca UTC que ya usa el semáforo (no se convierte a Lima).
PARADAS = (
    {
        "referencia": "frente a la bodega El Ahorro",
        "direccion": "Av. Próceres de la Independencia 2450",
        "latitud": Decimal("-12.0025000"),
        "longitud": Decimal("-76.9901000"),
        "peso": Decimal("8.00"),
        "volumen": Decimal("0.200"),
        "eta": (8, 15),
        "ventana_inicio": (7, 0),
        "ventana_fin": (10, 0),
    },
    {
        "referencia": "paradero del mercado",
        "direccion": "Jr. Los Jardines 180",
        "latitud": Decimal("-12.0200000"),
        "longitud": Decimal("-76.9700000"),
        "peso": Decimal("6.00"),
        "volumen": Decimal("0.100"),
        "eta": (10, 40),
        "ventana_inicio": (10, 0),
        "ventana_fin": (12, 0),
    },
    {
        "referencia": "al costado del grifo",
        "direccion": "Av. El Sol 510",
        "latitud": Decimal("-11.9800000"),
        "longitud": Decimal("-76.9950000"),
        "peso": Decimal("4.00"),
        "volumen": Decimal("0.050"),
        "eta": (12, 20),
        "ventana_inicio": (11, 0),
        "ventana_fin": (12, 0),
    },
)


def _marcar(fecha, hora: int, minuto: int) -> datetime:
    return datetime(fecha.year, fecha.month, fecha.day, hora, minuto, tzinfo=UTC)


def _catalogo(db: Session) -> tuple[Cliente, Vehiculo] | None:
    cliente = db.scalar(select(Cliente).where(Cliente.email == CORREO_CLIENTE))
    vehiculo = db.scalar(select(Vehiculo).where(Vehiculo.placa == PLACA_DEMO))
    if cliente is None or vehiculo is None:
        logger.warning("Faltan el cliente o el vehículo de demostración para la jornada")
        return None
    return cliente, vehiculo


def _conductor(db: Session, usuario: Usuario) -> Conductor | None:
    propio = db.scalar(select(Conductor).where(Conductor.id_usuario == usuario.id_usuario))
    por_dni = db.scalar(select(Conductor).where(Conductor.dni == DNI_DEMO))
    if por_dni is None and propio is not None:
        logger.warning("El usuario de demostración ya tiene otra ficha de conductor")
        return None
    if por_dni is not None and por_dni.id_usuario not in (None, usuario.id_usuario):
        logger.warning("El DNI de demostración está vinculado a otro usuario")
        return None
    if por_dni is None:
        por_dni = Conductor(
            id_usuario=usuario.id_usuario,
            dni=DNI_DEMO,
            nombre="Conductor de demostración",
            licencia_categoria="A-IIb",
            anios_experiencia=4,
            disponibilidad_inicio=time(8, 0),
            disponibilidad_fin=time(17, 0),
            lat_punto_partida=Decimal("-12.0100000"),
            lon_punto_partida=Decimal("-76.9800000"),
            estado="ACTIVO",
        )
        db.add(por_dni)
        db.flush()
        return por_dni
    por_dni.id_usuario = usuario.id_usuario
    por_dni.estado = "ACTIVO"
    return por_dni


def _pedido(db: Session, cliente: Cliente, spec: dict, fecha) -> Pedido:
    pedido = db.scalar(select(Pedido).where(Pedido.punto_referencia == spec["referencia"]))
    if pedido is None:
        pedido = Pedido(
            id_cliente=cliente.id_cliente,
            direccion=spec["direccion"],
            punto_referencia=spec["referencia"],
            latitud=spec["latitud"],
            longitud=spec["longitud"],
            peso_kg=spec["peso"],
            volumen_m3=spec["volumen"],
            ventana_inicio=_marcar(fecha, *spec["ventana_inicio"]),
            ventana_fin=_marcar(fecha, *spec["ventana_fin"]),
            prioridad="ESTANDAR",
            tipo_producto="NO_PERECEDERO",
            estado="ASIGNADO",
            georreferencia_aproximada=True,
        )
        db.add(pedido)
        db.flush()
        return pedido
    pedido.direccion = spec["direccion"]
    pedido.ventana_inicio = _marcar(fecha, *spec["ventana_inicio"])
    pedido.ventana_fin = _marcar(fecha, *spec["ventana_fin"])
    pedido.estado = "ASIGNADO"
    return pedido


def _ruta_demo(db: Session, conductor: Conductor, vehiculo: Vehiculo, fecha) -> Ruta:
    ruta = db.scalar(
        select(Ruta)
        .join(DetalleRuta, DetalleRuta.id_ruta == Ruta.id_ruta)
        .join(Pedido, Pedido.id_pedido == DetalleRuta.id_pedido)
        .join(AsignacionRuta, AsignacionRuta.id_ruta == Ruta.id_ruta)
        .where(
            Pedido.punto_referencia == PARADAS[0]["referencia"],
            AsignacionRuta.id_conductor == conductor.id_conductor,
        )
        .limit(1)
    )
    if ruta is None:
        ruta = Ruta(fecha=fecha, estado="CONFIRMADA")
        db.add(ruta)
        db.flush()
        db.add(
            AsignacionRuta(
                id_ruta=ruta.id_ruta,
                id_vehiculo=vehiculo.id_vehiculo,
                id_conductor=conductor.id_conductor,
            )
        )
        return ruta
    ruta.fecha = fecha
    ruta.estado = "CONFIRMADA"
    return ruta


def _detalle(db: Session, ruta: Ruta, pedido: Pedido, secuencia: int, eta: datetime) -> None:
    detalle = db.scalar(
        select(DetalleRuta).where(
            DetalleRuta.id_ruta == ruta.id_ruta,
            DetalleRuta.id_pedido == pedido.id_pedido,
        )
    )
    if detalle is None:
        db.add(
            DetalleRuta(
                id_ruta=ruta.id_ruta,
                id_pedido=pedido.id_pedido,
                secuencia=secuencia,
                eta=eta,
                estado_entrega="PENDIENTE",
            )
        )
        return
    detalle.secuencia = secuencia
    detalle.eta = eta


def _aviso(db: Session, ruta: Ruta) -> None:
    aviso = db.scalar(
        select(Incidencia).where(
            Incidencia.id_ruta == ruta.id_ruta,
            Incidencia.descripcion == DESCRIPCION_AVISO,
        )
    )
    if aviso is None:
        db.add(
            Incidencia(
                tipo="CONGESTION",
                origen="MANUAL",
                id_ruta=ruta.id_ruta,
                descripcion=DESCRIPCION_AVISO,
                estado="PENDIENTE",
            )
        )
        return
    aviso.estado = "PENDIENTE"
    aviso.tipo = "CONGESTION"


def asegurar_jornada_demo(db: Session, usuario: Usuario) -> bool:
    catalogo = _catalogo(db)
    if catalogo is None:
        return False
    cliente, vehiculo = catalogo
    conductor = _conductor(db, usuario)
    if conductor is None:
        return False
    fecha = fecha_operativa()
    ruta = _ruta_demo(db, conductor, vehiculo, fecha)
    for secuencia, spec in enumerate(PARADAS, start=1):
        pedido = _pedido(db, cliente, spec, fecha)
        _detalle(db, ruta, pedido, secuencia, _marcar(fecha, *spec["eta"]))
    _aviso(db, ruta)
    db.flush()
    return True
