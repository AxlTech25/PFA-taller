"""Usuarios y una ruta con coordenadas para la auditoría Lighthouse.

Credenciales de prueba, no de producción. La contraseña llega en
AUDITORIA_PASSWORD (el valor de CI es clave-segura). La ruta usa la fecha
local del proceso: el workflow y la medición fijan TZ=UTC, igual que el
navegador, para que la pantalla de rutas pida el mismo día.
"""

from __future__ import annotations

import os
import sys
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.entities import (
    AsignacionRuta,
    Cliente,
    Conductor,
    DetalleRuta,
    Pedido,
    Ruta,
    Usuario,
    Vehiculo,
)

CORREO_ADMIN = os.environ.get("LHCI_ADMIN_EMAIL", "admin.lhci@distrirapido.example.com")
CORREO_CONDUCTOR = os.environ.get(
    "LHCI_CONDUCTOR_EMAIL", "conductor.lhci@distrirapido.example.com"
)
CLAVE = os.environ.get("AUDITORIA_PASSWORD", "clave-segura")
DNI = "LHCI0001"
REFERENCIA = "auditoria-lhci"


def _usuario(db, email: str, rol: str) -> Usuario:
    existente = db.scalar(select(Usuario).where(Usuario.email == email))
    if existente is not None:
        return existente
    if len(CLAVE) < 8:
        raise SystemExit("AUDITORIA_PASSWORD debe tener al menos 8 caracteres")
    usuario = Usuario(
        email=email,
        password_hash=hash_password(CLAVE),
        rol=rol,
        estado="ACTIVO",
        intentos_fallidos=0,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def _ruta_de_hoy(db, actor: Usuario) -> None:
    if db.scalar(select(Conductor).where(Conductor.dni == DNI)) is not None:
        return
    cliente = db.scalar(
        select(Cliente).where(Cliente.email == "demo.consentido@distrirapido.example.com")
    )
    vehiculo = db.scalar(select(Vehiculo).where(Vehiculo.placa == "DMO-101"))
    if cliente is None or vehiculo is None:
        raise SystemExit("Faltan el cliente o el vehículo de demostración. Corra las migraciones.")
    conductor = Conductor(
        id_usuario=actor.id_usuario,
        dni=DNI,
        nombre="Conductor de auditoría",
        licencia_categoria="A-IIb",
        anios_experiencia=5,
        disponibilidad_inicio=time(8, 0),
        disponibilidad_fin=time(17, 0),
        lat_punto_partida=-12.0100000,
        lon_punto_partida=-76.9800000,
        estado="ACTIVO",
    )
    db.add(conductor)
    db.flush()
    ahora = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    pedido = Pedido(
        id_cliente=cliente.id_cliente,
        direccion="Av. Próceres de la Independencia 1000",
        punto_referencia=REFERENCIA,
        latitud=-12.0300000,
        longitud=-77.0000000,
        peso_kg=10,
        volumen_m3=0.05,
        ventana_inicio=ahora,
        ventana_fin=ahora + timedelta(hours=4),
        prioridad="ESTANDAR",
        tipo_producto="NO_PERECEDERO",
        estado="PENDIENTE",
        georreferencia_aproximada=False,
    )
    db.add(pedido)
    db.flush()
    ruta = Ruta(
        fecha=date.today(),
        estado="BORRADOR",
        distancia_total_km=4.2,
        tiempo_total_min=25,
        minutos_conduccion=25,
        combustible_estimado_l=0.4,
        co2_estimado_kg=1.1,
    )
    db.add(ruta)
    db.flush()
    db.add(
        AsignacionRuta(
            id_ruta=ruta.id_ruta,
            id_vehiculo=vehiculo.id_vehiculo,
            id_conductor=conductor.id_conductor,
        )
    )
    db.add(
        DetalleRuta(
            id_ruta=ruta.id_ruta,
            id_pedido=pedido.id_pedido,
            secuencia=1,
            eta=ahora + timedelta(hours=1),
            estado_entrega="PENDIENTE",
        )
    )
    db.commit()


def main() -> None:
    db = SessionLocal()
    try:
        admin = _usuario(db, CORREO_ADMIN, "ADMIN")
        _usuario(db, CORREO_CONDUCTOR, "CONDUCTOR")
        _ruta_de_hoy(db, admin)
    finally:
        db.close()
    print(f"semilla lista para {date.today().isoformat()}")


if __name__ == "__main__":
    main()
