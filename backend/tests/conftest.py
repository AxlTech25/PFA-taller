import os
import re

os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://ecologistica:ecologistica@localhost:5432/ecologistica_test",
)
os.environ.setdefault("JWT_SECRET", "test-secret-not-for-production")
os.environ["SEED_ON_STARTUP"] = "false"
os.environ["JWT_EXPIRE_MINUTES"] = "60"

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import Session, sessionmaker

from app.core.security import hash_password
from app.db.session import engine, get_db
from app.main import app
from app.models.entities import Usuario


def _asegurar_base() -> None:
    destino = make_url(os.environ["DATABASE_URL"])
    nombre = destino.database or ""
    if not re.fullmatch(r"[A-Za-z0-9_]+", nombre):
        raise RuntimeError("Nombre de base de datos de prueba inválido")
    admin = create_engine(destino.set(database="postgres"), isolation_level="AUTOCOMMIT")
    try:
        with admin.connect() as conexion:
            existe = conexion.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :nombre"),
                {"nombre": nombre},
            ).scalar()
            if not existe:
                conexion.execute(text(f'CREATE DATABASE "{nombre}"'))
    finally:
        admin.dispose()


def _migrar() -> None:
    _asegurar_base()
    command.upgrade(Config("alembic.ini"), "head")


_migrar()


@pytest.fixture
def db():
    conexion = engine.connect()
    transaccion = conexion.begin()
    sesion = sessionmaker(bind=conexion, join_transaction_mode="create_savepoint")()
    try:
        yield sesion
    finally:
        sesion.close()
        transaccion.rollback()
        conexion.close()


@pytest.fixture
def client(db: Session):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as cliente:
        yield cliente
    app.dependency_overrides.clear()


def crear_usuario(
    db: Session,
    *,
    email: str,
    password: str = "clave-segura",
    rol: str = "OPERADOR",
    estado: str = "ACTIVO",
) -> Usuario:
    usuario = Usuario(
        email=email.lower(),
        password_hash=hash_password(password),
        rol=rol,
        estado=estado,
        intentos_fallidos=0,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def autenticar(client: TestClient, email: str, password: str = "clave-segura") -> dict[str, str]:
    respuesta = client.post("/auth/login", json={"email": email, "password": password})
    assert respuesta.status_code == 200, respuesta.text
    token = respuesta.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def vehiculo_valido(**cambios: object) -> dict:
    datos: dict = {
        "placa": "ABC123",
        "tipo": "CAMIONETA",
        "capacidad_kg": 1200,
        "capacidad_m3": 8,
        "consumo_km_l": 12.5,
        "factor_emision_co2": 0.27,
        "anio_fabricacion": 2022,
    }
    datos.update(cambios)
    return datos

