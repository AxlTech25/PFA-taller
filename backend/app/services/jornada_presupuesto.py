"""Ruta de 12 paradas para medir ENB-008.

No sustituye la jornada de tres paradas del conductor de demostración.
Usa otro usuario, el mismo vehículo DMO-101 y el cliente con consentimiento.
No rellena kilómetros, CO₂ ni árboles: el presupuesto mide la sesión de la
lista, no indicadores de gerencia.
"""

from datetime import UTC, datetime, time
from decimal import Decimal

from sqlalchemy import delete, select
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

CORREO = "conductor.presupuesto@distrirapido.example.com"
DNI = "70015012"
PLACA = "DMO-101"
CORREO_CLIENTE = "demo.consentido@distrirapido.example.com"
PARADAS = 12


def _referencia(numero: int) -> str:
    return f"manzana-{numero:02d}"


def _marcar(fecha, hora: int, minuto: int) -> datetime:
    return datetime(fecha.year, fecha.month, fecha.day, hora, minuto, tzinfo=UTC)


def _catalogo(db: Session) -> tuple[Cliente, Vehiculo] | None:
    cliente = db.scalar(select(Cliente).where(Cliente.email == CORREO_CLIENTE))
    vehiculo = db.scalar(select(Vehiculo).where(Vehiculo.placa == PLACA))
    if cliente is None or vehiculo is None:
        return None
    return cliente, vehiculo


def _conductor(db: Session, usuario: Usuario) -> Conductor | None:
    propio = db.scalar(select(Conductor).where(Conductor.id_usuario == usuario.id_usuario))
    por_dni = db.scalar(select(Conductor).where(Conductor.dni == DNI))
    if por_dni is None and propio is not None:
        return None
    if por_dni is not None and por_dni.id_usuario not in (None, usuario.id_usuario):
        return None
    if por_dni is None:
        por_dni = Conductor(
            id_usuario=usuario.id_usuario,
            dni=DNI,
            nombre="Conductor de presupuesto",
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


def _limpiar(db: Session, conductor: Conductor) -> None:
    rutas = list(
        db.scalars(
            select(Ruta.id_ruta)
            .join(AsignacionRuta, AsignacionRuta.id_ruta == Ruta.id_ruta)
            .where(AsignacionRuta.id_conductor == conductor.id_conductor)
        ).all()
    )
    if rutas:
        db.execute(delete(Incidencia).where(Incidencia.id_ruta.in_(rutas)))
        db.execute(delete(DetalleRuta).where(DetalleRuta.id_ruta.in_(rutas)))
        db.execute(delete(AsignacionRuta).where(AsignacionRuta.id_ruta.in_(rutas)))
        db.execute(delete(Ruta).where(Ruta.id_ruta.in_(rutas)))
    refs = [_referencia(numero) for numero in range(1, PARADAS + 1)]
    db.execute(delete(Pedido).where(Pedido.punto_referencia.in_(refs)))
    db.flush()


def _parada(numero: int, fecha) -> dict:
    # 15 min entre paradas desde las 08:00. La última queda fuera de su ventana.
    minutos = (numero - 1) * 15
    hora, minuto = divmod(8 * 60 + minutos, 60)
    fuera = numero == PARADAS
    inicio = (hora, max(minuto - 20, 0)) if not fuera else (hora, 0)
    fin = (hora, minuto + 30) if not fuera else (hora, max(minuto - 5, 0))
    if fin[1] >= 60:
        fin = (fin[0] + 1, fin[1] - 60)
    return {
        "referencia": _referencia(numero),
        "direccion": f"Calle {numero}, San Juan de Lurigancho",
        "latitud": Decimal("-12.0100000") + Decimal(numero % 4) * Decimal("0.0040000"),
        "longitud": Decimal("-76.9900000") - Decimal(numero % 3) * Decimal("0.0040000"),
        "eta": (hora, minuto),
        "ventana_inicio": inicio,
        "ventana_fin": fin,
    }


def asegurar_jornada_presupuesto(db: Session, usuario: Usuario) -> bool:
    catalogo = _catalogo(db)
    if catalogo is None:
        return False
    cliente, vehiculo = catalogo
    conductor = _conductor(db, usuario)
    if conductor is None:
        return False
    _limpiar(db, conductor)
    fecha = fecha_operativa()
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
    for numero in range(1, PARADAS + 1):
        spec = _parada(numero, fecha)
        pedido = Pedido(
            id_cliente=cliente.id_cliente,
            direccion=spec["direccion"],
            punto_referencia=spec["referencia"],
            latitud=spec["latitud"],
            longitud=spec["longitud"],
            peso_kg=Decimal("4.00"),
            volumen_m3=Decimal("0.050"),
            ventana_inicio=_marcar(fecha, *spec["ventana_inicio"]),
            ventana_fin=_marcar(fecha, *spec["ventana_fin"]),
            prioridad="ESTANDAR",
            tipo_producto="NO_PERECEDERO",
            estado="ASIGNADO",
            georreferencia_aproximada=True,
        )
        db.add(pedido)
        db.flush()
        db.add(
            DetalleRuta(
                id_ruta=ruta.id_ruta,
                id_pedido=pedido.id_pedido,
                secuencia=numero,
                eta=_marcar(fecha, *spec["eta"]),
                estado_entrega="PENDIENTE",
            )
        )
    db.flush()
    return True
