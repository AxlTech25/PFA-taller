import pytest
from app.core.config import Settings
from pydantic import ValidationError


def test_database_url_explicita_tiene_prioridad(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@db:5432/app")
    cfg = Settings(_env_file=None)
    assert cfg.database_url == "postgresql+psycopg://u:p@db:5432/app"


def test_la_clave_de_postgres_sale_del_entorno(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("POSTGRES_USER", "ecologistica")
    monkeypatch.setenv("POSTGRES_PASSWORD", "clave demo")
    monkeypatch.setenv("POSTGRES_HOST", "localhost")
    monkeypatch.setenv("POSTGRES_PORT", "5432")
    monkeypatch.setenv("POSTGRES_DB", "ecologistica")
    cfg = Settings(_env_file=None)
    assert cfg.database_url == (
        "postgresql+psycopg://ecologistica:clave+demo@localhost:5432/ecologistica"
    )


def test_sin_clave_no_arma_la_conexion(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("POSTGRES_PASSWORD", "")
    monkeypatch.setenv("POSTGRES_USER", "ecologistica")
    monkeypatch.setenv("POSTGRES_HOST", "localhost")
    monkeypatch.setenv("POSTGRES_PORT", "5432")
    monkeypatch.setenv("POSTGRES_DB", "ecologistica")
    with pytest.raises(ValidationError, match="POSTGRES_PASSWORD"):
        Settings(_env_file=None)
