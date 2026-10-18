"""Inicio del tablero (Hito 3). US-014 queda para el Sprint 5."""

import pytest
from tests.conftest import autenticar, crear_usuario
from tests.test_cobertura_rutas import (
    FECHA,
    ColaFalsa,
    _conductor,
    _operador,
    _pedido,
    _procesar,
)


@pytest.fixture
def cola(monkeypatch):
    falsa = ColaFalsa()
    monkeypatch.setattr("app.optimizacion.cola.obtener_cliente", lambda: falsa)
    return falsa


def test_periodo_sin_rutas(client, db):
    headers, _ = _operador(client, db, "op.ind@distrirapido.example.com")
    respuesta = client.get(f"/indicadores?fecha={FECHA}", headers=headers)
    assert respuesta.status_code == 200, respuesta.text
    cuerpo = respuesta.json()
    assert cuerpo["hay_datos"] is False
    assert cuerpo["mensaje"] == "Sin datos de operación para el período seleccionado."
    assert cuerpo["km"] == 0
    assert cuerpo["arboles"] is None
    assert "RN-018" in cuerpo["nota_arboles"]


def test_indicadores_del_plan_y_conductor_sin_acceso(client, db, cola):
    headers, _ = _operador(client, db, "op.ind2@distrirapido.example.com")
    _conductor(db, dni="70801080")
    _pedido(client, headers, db)
    alta = client.post("/optimizaciones", headers=headers, json={"fecha": FECHA})
    assert alta.status_code == 202
    _procesar(db, cola)
    respuesta = client.get(f"/indicadores?fecha={FECHA}", headers=headers)
    assert respuesta.status_code == 200, respuesta.text
    cuerpo = respuesta.json()
    assert cuerpo["hay_datos"] is True
    assert cuerpo["mensaje"] is None
    assert cuerpo["rutas"] == 1
    assert cuerpo["km"] > 0
    assert cuerpo["co2_kg"] > 0
    assert cuerpo["combustible_l"] > 0
    assert cuerpo["soles_combustible"] > 0
    assert cuerpo["soles_mantenimiento"] > 0
    assert cuerpo["cumplimiento_ventanas_pct"] == 100
    assert cuerpo["arboles"] is None
    assert "RN-018" in cuerpo["nota_arboles"]
    assert cuerpo["mejora_porcentaje"] is not None
    conductor = crear_usuario(db, email="con.ind@distrirapido.example.com", rol="CONDUCTOR")
    prohibido = client.get(
        f"/indicadores?fecha={FECHA}",
        headers=autenticar(client, conductor.email),
    )
    assert prohibido.status_code == 403
