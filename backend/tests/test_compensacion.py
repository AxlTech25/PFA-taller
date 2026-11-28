"""US-017 · Plan de compensación de carbono (RF-010, RN-018)."""

import math

import pytest
from app.services import compensacion, indicadores, reporte_pdf
from sqlalchemy import text
from tests.conftest import autenticar, crear_usuario
from tests.test_cobertura_rutas import (
    FECHA,
    ColaFalsa,
    _conductor,
    _operador,
    _pedido,
    _procesar,
)

URL = "/indicadores/compensacion"
PROYECTOS = [
    {"nombre": "Lomas de Lima"},
    {"nombre": "Parque Zonal Huáscar"},
    {"nombre": "Árboles para Lima"},
]


@pytest.fixture
def cola(monkeypatch):
    falsa = ColaFalsa()
    monkeypatch.setattr("app.optimizacion.cola.obtener_cliente", lambda: falsa)
    return falsa


def _plan(client, db, cola, email: str, dni: str) -> dict:
    headers, _ = _operador(client, db, email)
    _conductor(db, dni=dni)
    _pedido(client, headers, db)
    alta = client.post("/optimizaciones", headers=headers, json={"fecha": FECHA})
    assert alta.status_code == 202, alta.text
    _procesar(db, cola)
    return headers


def _configurar(db, clave: str, valor: str) -> None:
    db.execute(
        text(
            "INSERT INTO configuracion_sistema (clave, valor, unidad, descripcion) "
            "VALUES (:clave, :valor, 'prueba', 'prueba') "
            "ON CONFLICT (clave) DO UPDATE SET valor = EXCLUDED.valor"
        ),
        {"clave": clave, "valor": valor},
    )
    db.commit()


def test_plan_con_emisiones_usa_valores_ratificados(client, db, cola):
    headers = _plan(client, db, cola, "op.comp@distrirapido.example.com", "70817001")
    tablero = client.get(f"/indicadores?fecha={FECHA}", headers=headers).json()
    respuesta = client.get(f"{URL}?desde={FECHA}&hasta={FECHA}", headers=headers)
    assert respuesta.status_code == 200, respuesta.text
    plan = respuesta.json()
    assert plan["calculable"] is True
    assert plan["mensaje"] is None
    assert plan["dias_con_operacion"] == 1
    assert plan["rutas"] == tablero["rutas"]
    # Mismo CO₂ que el tablero: no hay un cálculo aparte.
    assert plan["co2_emitido_kg"] == tablero["co2_kg"]
    assert plan["co2_emitido_kg"] > 0
    # Migración 008: EPA 60 kg/árbol y SERPAR S/ 94.
    assert plan["estado_factor"] == "CONFIGURADO"
    assert plan["factor_captura_arbol_kg"] == 60
    esperado = math.ceil(plan["co2_emitido_kg"] / 60)
    assert plan["arboles_necesarios"] == esperado
    assert plan["estado_costo"] == "CONFIGURADO"
    assert plan["costo_por_arbol_soles"] == 94
    assert plan["costo_estimado_soles"] == round(esperado * 94, 2)
    assert plan["notas"] == []
    assert plan["proyectos"] == PROYECTOS


def test_plan_con_factores_configurados(client, db, cola):
    headers = _plan(client, db, cola, "op.comp2@distrirapido.example.com", "70817002")
    # Valores de prueba: el sistema no trae ninguno ratificado.
    _configurar(db, "factor_captura_arbol_kg", "0.5")
    _configurar(db, "costo_compensacion_arbol_soles", "3")
    plan = client.get(f"{URL}?desde={FECHA}&hasta={FECHA}", headers=headers).json()
    esperado = math.ceil(plan["co2_emitido_kg"] / 0.5)
    assert plan["estado_factor"] == "CONFIGURADO"
    assert plan["factor_captura_arbol_kg"] == 0.5
    assert plan["arboles_necesarios"] == esperado
    assert plan["estado_costo"] == "CONFIGURADO"
    assert plan["costo_por_arbol_soles"] == 3
    assert plan["costo_estimado_soles"] == round(esperado * 3, 2)
    assert plan["notas"] == []


def test_costo_pendiente_si_solo_hay_factor(client, db, cola):
    headers = _plan(client, db, cola, "op.comp3@distrirapido.example.com", "70817003")
    db.execute(
        text("DELETE FROM configuracion_sistema WHERE clave = :clave"),
        {"clave": "costo_compensacion_arbol_soles"},
    )
    db.commit()
    _configurar(db, "factor_captura_arbol_kg", "10")
    plan = client.get(f"{URL}?desde={FECHA}&hasta={FECHA}", headers=headers).json()
    assert plan["arboles_necesarios"] == math.ceil(plan["co2_emitido_kg"] / 10)
    assert plan["estado_costo"] == "PENDIENTE"
    assert plan["costo_estimado_soles"] is None
    assert plan["notas"] == [compensacion.NOTA_COSTO]


@pytest.mark.parametrize("valor", ["0", "-2", "abc", "nan", "inf"])
def test_factor_invalido_sigue_pendiente(db, valor):
    _configurar(db, "factor_captura_arbol_kg", valor)
    assert indicadores.valor_positivo(db, "factor_captura_arbol_kg") is None


def test_sin_emisiones_no_calcula(client, db):
    headers, _ = _operador(client, db, "op.comp4@distrirapido.example.com")
    respuesta = client.get(f"{URL}?desde=2099-01-01&hasta=2099-01-31", headers=headers)
    assert respuesta.status_code == 200
    plan = respuesta.json()
    assert plan["calculable"] is False
    assert plan["mensaje"] == compensacion.MENSAJE_SIN_DATOS
    assert plan["arboles_necesarios"] is None
    assert plan["proyectos"] == []


def test_periodo_invalido(client, db):
    headers, _ = _operador(client, db, "op.comp5@distrirapido.example.com")
    al_reves = client.get(f"{URL}?desde=2026-10-20&hasta=2026-10-19", headers=headers)
    assert al_reves.status_code == 422
    assert al_reves.json()["detail"] == reporte_pdf.MENSAJE_RANGO
    largo = client.get(f"{URL}?desde=2026-10-01&hasta=2026-11-01", headers=headers)
    assert largo.status_code == 422
    assert client.get(f"{URL}?desde=2026-10-01", headers=headers).status_code == 422


@pytest.mark.parametrize("rol", ["ADMIN", "GERENTE", "AUDITOR"])
def test_roles_con_lectura(client, db, rol):
    usuario = crear_usuario(db, email=f"{rol.lower()}.comp@distrirapido.example.com", rol=rol)
    respuesta = client.get(
        f"{URL}?desde={FECHA}&hasta={FECHA}", headers=autenticar(client, usuario.email)
    )
    assert respuesta.status_code == 200, respuesta.text


def test_conductor_recibe_403_y_anonimo_401(client, db):
    conductor = crear_usuario(db, email="con.comp@distrirapido.example.com", rol="CONDUCTOR")
    prohibido = client.get(
        f"{URL}?desde={FECHA}&hasta={FECHA}", headers=autenticar(client, conductor.email)
    )
    assert prohibido.status_code == 403
    assert client.get(f"{URL}?desde={FECHA}&hasta={FECHA}").status_code == 401
