"""RF-10/RES-02 (compensación anual y meta a 3 años), RES-01 (GNV) y RF-06 (créditos)."""

import math
from datetime import date

import pytest
from app.services import compensacion, metas, reporte_pdf
from sqlalchemy import text
from tests.conftest import autenticar, crear_usuario
from tests.test_cobertura_rutas import FECHA
from tests.test_compensacion import _configurar, _plan, cola  # noqa: F401
from tests.test_reporte_pdf import _texto

URL_ANUAL = "/indicadores/compensacion/anual"
URL_GNV = "/indicadores/gnv"
M3_POR_GALON = 0.138 / (0.001026 * 35.3147)

NUEVAS = {
    "factor_captura_arbol_pesimista_kg": 15.0,
    "precio_gnv_m3_soles": 12.5,
    "costo_conversion_gnv_vehiculo_soles": 5000.0,
    "gnv_precio_mercado_m3_soles": 1.68,
    "diesel_mmbtu_galon": 0.138,
    "diesel_co2_kg_mmbtu": 73.96,
    "gnv_mmbtu_scf": 0.001026,
    "gnv_co2_kg_mmbtu": 53.06,
    "precio_credito_carbono_usd_t": 20.44,
    "tipo_cambio_usd_pen": 3.478,
}


def _borrar(db, clave: str) -> None:
    db.execute(text("DELETE FROM configuracion_sistema WHERE clave = :c"), {"c": clave})
    db.commit()


def test_migracion_009_carga_las_claves_con_fuente(db):
    filas = db.execute(
        text("SELECT clave, valor, descripcion FROM configuracion_sistema WHERE clave = ANY(:c)"),
        {"c": list(NUEVAS)},
    ).all()
    leidas = {fila.clave: fila for fila in filas}
    assert set(leidas) == set(NUEVAS)
    for clave, esperado in NUEVAS.items():
        assert float(leidas[clave].valor) == esperado
        assert leidas[clave].descripcion
    assert "UPN" in leidas["factor_captura_arbol_pesimista_kg"].descripcion
    assert "Consigna" in leidas["precio_gnv_m3_soles"].descripcion
    assert "EPA" in leidas["gnv_co2_kg_mmbtu"].descripcion
    assert "Ecosystem" in leidas["precio_credito_carbono_usd_t"].descripcion
    assert "BCRP" in leidas["tipo_cambio_usd_pen"].descripcion


def test_proyeccion_anual_y_escenarios_con_numeros_exactos(db):
    # 10 kg en 7 días calendario (5 con operación): escala 365/7.
    meta = metas.meta_anual(db, 10, 7, 5)
    assert meta["co2_anual_kg"] == 521.4
    assert meta["escala"] == pytest.approx(52.1429)
    assert "5 día(s) con operación" in meta["aviso"]
    assert "No es un año observado" in meta["aviso"]
    epa, pesimista = meta["escenarios"]
    assert epa["factor_kg_arbol_anio"] == 60
    assert epa["arboles_anuales"] == math.ceil(521.428571 / 60) == 9
    assert epa["costo_total_soles"] == 9 * 94
    assert [f["arboles_a_plantar"] for f in epa["plan"]] == [3, 3, 3]
    assert pesimista["factor_kg_arbol_anio"] == 15
    assert pesimista["arboles_anuales"] == 35
    assert pesimista["costo_total_soles"] == 3290
    assert [f["arboles_a_plantar"] for f in pesimista["plan"]] == [12, 12, 11]
    assert [f["arboles_acumulados"] for f in pesimista["plan"]] == [12, 24, 35]
    assert [f["cobertura_pct"] for f in pesimista["plan"]] == [34.5, 69.0, 100]
    assert sum(f["costo_soles"] for f in pesimista["plan"]) == 3290
    # Sin árboles registrados el avance es 0 % y se marca pendiente.
    assert meta["avance"]["arboles_registrados"] == 0
    assert meta["avance"]["estado_registro"] == "PENDIENTE"
    assert meta["avance"]["avance_pct"] == 0


def test_sin_emisiones_no_hay_plan_ni_division_por_cero(db):
    meta = metas.meta_anual(db, 0, 1, 1)
    assert meta["co2_anual_kg"] == 0
    for escenario in meta["escenarios"]:
        assert escenario["arboles_anuales"] == 0
        assert escenario["arboles_por_anio"] == 0
        assert escenario["costo_total_soles"] == 0
        assert escenario["plan"] == []
    assert meta["avance"]["avance_pct"] is None


def test_avance_con_arboles_registrados(db):
    _configurar(db, "arboles_plantados_registrados", "3")
    avance = metas.meta_anual(db, 10, 7, 5)["avance"]
    assert avance["estado_registro"] == "CONFIGURADO"
    assert avance["arboles_registrados"] == 3
    assert avance["avance_pct"] == round(3 * 60 / 521.4286 * 100, 1)
    assert avance["nota"] is None
    _configurar(db, "arboles_plantados_registrados", "-4")
    assert metas.valor_no_negativo(db, "arboles_plantados_registrados") is None
    _configurar(db, "arboles_plantados_registrados", "abc")
    assert metas.valor_no_negativo(db, "arboles_plantados_registrados") is None


def test_factor_pesimista_pendiente_no_inventa(db):
    _borrar(db, "factor_captura_arbol_pesimista_kg")
    pesimista = metas.meta_anual(db, 10, 7, 5)["escenarios"][1]
    assert pesimista["estado_factor"] == "PENDIENTE"
    assert pesimista["arboles_anuales"] is None
    assert pesimista["costo_total_soles"] is None
    assert pesimista["plan"] == []


def test_plan_sin_factor_epa_ni_costo(db):
    _borrar(db, "factor_captura_arbol_kg")
    _borrar(db, "costo_compensacion_arbol_soles")
    meta = metas.meta_anual(db, 10, 7, 5)
    assert meta["avance"]["avance_pct"] is None
    assert meta["escenarios"][0]["arboles_anuales"] is None
    pesimista = meta["escenarios"][1]
    assert pesimista["arboles_anuales"] == 35
    assert pesimista["costo_total_soles"] is None
    assert [f["costo_soles"] for f in pesimista["plan"]] == [None, None, None]


def test_gnv_con_numeros_exactos(db):
    gnv = metas.evaluar_gnv(
        db,
        litros_periodo=100,
        co2_periodo_kg=10,
        dias_calendario=7,
        dias_con_operacion=5,
        vehiculos=2,
    )
    assert gnv["equivalencia_m3_por_galon"] == round(M3_POR_GALON, 4) == 3.8087
    assert gnv["inversion_soles"] == 10000
    galones = 100 * 365 / 7 / 3.785411784
    assert gnv["costo_diesel_anual_soles"] == pytest.approx(galones * 17.5, abs=0.01)
    assert gnv["precio_equilibrio_gnv_m3"] == round(17.5 / M3_POR_GALON, 2) == 4.59
    razon = 53.06 / 73.96
    assert gnv["co2_gnv_anual_kg"] == pytest.approx(10 * 365 / 7 * razon, abs=0.1)
    assert gnv["co2_evitado_periodo_kg"] == pytest.approx(10 * (1 - razon), abs=0.001)
    assert gnv["reduccion_co2_pct"] == 28.3
    consigna, mercado = gnv["escenarios"]
    m3 = galones * M3_POR_GALON
    # Con S/ 12.50 por m³ el GNV es más caro que el diésel: no hay ahorro ni recuperación.
    assert consigna["precio_gnv_m3"] == 12.5
    assert consigna["costo_gnv_anual_soles"] == pytest.approx(m3 * 12.5, abs=0.01)
    assert consigna["ahorro_anual_soles"] < 0
    assert consigna["recuperacion_meses"] is None
    assert consigna["se_recupera"] is False
    assert consigna["roi_3_anios_pct"] < -100
    assert any("precio de equilibrio" in nota for nota in gnv["notas"])
    # Con el precio de mercado sí hay ahorro.
    ahorro = galones * 17.5 - m3 * 1.68
    assert mercado["ahorro_anual_soles"] == pytest.approx(ahorro, abs=0.01)
    assert mercado["recuperacion_meses"] == pytest.approx(10000 / ahorro * 12, abs=0.05)
    assert mercado["roi_3_anios_pct"] == pytest.approx((ahorro * 3 - 10000) / 10000 * 100, abs=0.1)
    assert mercado["se_recupera"] is True


def test_gnv_pendientes_no_se_inventan(db):
    _borrar(db, "gnv_mmbtu_scf")
    gnv = metas.evaluar_gnv(
        db,
        litros_periodo=100,
        co2_periodo_kg=10,
        dias_calendario=7,
        dias_con_operacion=5,
        vehiculos=2,
    )
    assert gnv["estado_equivalencia"] == "PENDIENTE"
    assert gnv["escenarios"] == []
    assert gnv["costo_diesel_anual_soles"] is None
    assert any("equivalencia energética" in nota for nota in gnv["notas"])


def test_gnv_sin_factor_co2_ni_conversion(db):
    _borrar(db, "gnv_co2_kg_mmbtu")
    _borrar(db, "costo_conversion_gnv_vehiculo_soles")
    gnv = metas.evaluar_gnv(
        db,
        litros_periodo=100,
        co2_periodo_kg=10,
        dias_calendario=7,
        dias_con_operacion=5,
        vehiculos=2,
    )
    assert gnv["estado_factor_co2"] == "PENDIENTE"
    assert gnv["co2_evitado_anual_kg"] is None
    assert gnv["inversion_soles"] is None
    assert gnv["escenarios"][1]["ahorro_anual_soles"] > 0
    assert gnv["escenarios"][1]["roi_3_anios_pct"] is None
    assert gnv["escenarios"][1]["recuperacion_meses"] is None
    textos = " ".join(gnv["notas"])
    assert "costo de conversión" in textos
    assert "factor de emisión del GNV" in textos


def test_gnv_sin_precio_de_mercado_y_sin_vehiculos(db):
    _borrar(db, "gnv_precio_mercado_m3_soles")
    gnv = metas.evaluar_gnv(
        db,
        litros_periodo=50,
        co2_periodo_kg=5,
        dias_calendario=1,
        dias_con_operacion=1,
        vehiculos=0,
    )
    assert gnv["escenarios"][1]["estado_precio"] == "PENDIENTE"
    assert gnv["escenarios"][1]["ahorro_anual_soles"] is None
    assert gnv["inversion_soles"] == 0
    assert gnv["escenarios"][0]["roi_3_anios_pct"] is None
    assert any("No hay vehículos" in nota for nota in gnv["notas"])


def test_creditos_de_carbono(db):
    c = metas.creditos(db, 1000, 250)
    assert c["estado"] == "CONFIGURADO"
    assert c["valor_usd"] == 20.44
    assert c["valor_soles"] == round(20.44 * 3.478, 2) == 71.09
    assert c["toneladas_periodo"] == 1
    assert c["ahorro_usd"] == 5.11
    assert c["ahorro_soles"] == round(5.11 * 3.478, 2)
    _borrar(db, "tipo_cambio_usd_pen")
    pendiente = metas.creditos(db, 1000, 250)
    assert pendiente["estado"] == "PENDIENTE"
    assert pendiente["valor_soles"] is None
    assert "tipo_cambio_usd_pen" in pendiente["nota"]


def test_endpoint_anual_coincide_con_el_tablero(client, db, cola):  # noqa: F811
    headers = _plan(client, db, cola, "op.anual@distrirapido.example.com", "70818001")
    tablero = client.get(f"/indicadores?fecha={FECHA}", headers=headers).json()
    respuesta = client.get(f"{URL_ANUAL}?desde={FECHA}&hasta={FECHA}", headers=headers)
    assert respuesta.status_code == 200, respuesta.text
    anual = respuesta.json()
    assert anual["calculable"] is True
    assert anual["dias_calendario"] == 1
    assert anual["dias_con_operacion"] == 1
    assert anual["co2_periodo_kg"] == tablero["co2_kg"]
    assert anual["co2_anual_kg"] == pytest.approx(tablero["co2_kg"] * 365, abs=0.1)
    epa, pesimista = anual["escenarios"]
    assert epa["arboles_anuales"] == math.ceil(anual["co2_anual_kg"] / 60)
    assert pesimista["arboles_anuales"] == math.ceil(anual["co2_anual_kg"] / 15)
    assert pesimista["costo_total_soles"] == pesimista["arboles_anuales"] * 94
    assert anual["aviso"].startswith("Proyección lineal a 365 días")
    assert anual["avance"]["estado_registro"] == "PENDIENTE"


def test_endpoint_gnv_usa_la_flota_del_periodo(client, db, cola):  # noqa: F811
    headers = _plan(client, db, cola, "op.gnv@distrirapido.example.com", "70818002")
    tablero = client.get(f"/indicadores?fecha={FECHA}", headers=headers).json()
    respuesta = client.get(f"{URL_GNV}?desde={FECHA}&hasta={FECHA}", headers=headers)
    assert respuesta.status_code == 200, respuesta.text
    gnv = respuesta.json()
    assert gnv["calculable"] is True
    assert gnv["vehiculos"] >= 1
    assert gnv["inversion_soles"] == 5000 * gnv["vehiculos"]
    assert gnv["litros_periodo"] == pytest.approx(tablero["combustible_l"], abs=0.01)
    assert len(gnv["escenarios"]) == 2
    assert gnv["co2_evitado_anual_kg"] == pytest.approx(
        tablero["co2_kg"] * (1 - 53.06 / 73.96) * 365, abs=0.1
    )


@pytest.mark.parametrize("url", [URL_ANUAL, URL_GNV])
def test_sin_emisiones_no_calcula(client, db, url):
    usuario = crear_usuario(db, email=f"vacio{len(url)}@distrirapido.example.com", rol="GERENTE")
    respuesta = client.get(
        f"{url}?desde=2099-01-01&hasta=2099-01-31", headers=autenticar(client, usuario.email)
    )
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["calculable"] is False
    assert cuerpo["mensaje"] == compensacion.MENSAJE_SIN_DATOS
    assert cuerpo["escenarios"] == []


@pytest.mark.parametrize("url", [URL_ANUAL, URL_GNV])
@pytest.mark.parametrize("rol", ["ADMIN", "GERENTE", "OPERADOR", "AUDITOR"])
def test_roles_con_acceso(client, db, url, rol):
    usuario = crear_usuario(
        db, email=f"{rol.lower()}.{len(url)}.ag@distrirapido.example.com", rol=rol
    )
    respuesta = client.get(
        f"{url}?desde={FECHA}&hasta={FECHA}", headers=autenticar(client, usuario.email)
    )
    assert respuesta.status_code == 200, respuesta.text


@pytest.mark.parametrize("url", [URL_ANUAL, URL_GNV])
def test_conductor_403_anonimo_401_y_periodo_invalido(client, db, url):
    conductor = crear_usuario(
        db, email=f"con{len(url)}.ag@distrirapido.example.com", rol="CONDUCTOR"
    )
    assert (
        client.get(
            f"{url}?desde={FECHA}&hasta={FECHA}", headers=autenticar(client, conductor.email)
        ).status_code
        == 403
    )
    assert client.get(f"{url}?desde={FECHA}&hasta={FECHA}").status_code == 401
    admin = crear_usuario(db, email=f"adm{len(url)}.ag@distrirapido.example.com", rol="ADMIN")
    headers = autenticar(client, admin.email)
    assert (
        client.get(f"{url}?desde=2026-10-20&hasta=2026-10-19", headers=headers).status_code == 422
    )
    assert (
        client.get(f"{url}?desde=2026-10-01&hasta=2026-11-01", headers=headers).status_code == 422
    )


def test_pdf_incluye_creditos_meta_y_gnv(client, db, cola):  # noqa: F811
    headers = _plan(client, db, cola, "op.pdfag@distrirapido.example.com", "70818003")
    dia = date.fromisoformat(FECHA)
    texto = _texto(reporte_pdf.generar_pdf(reporte_pdf.recopilar(db, dia, dia)))
    assert "Créditos de carbono (RF-06)" in texto
    assert "US$ 20.44 por t CO2e" in texto
    assert "S/ 3.478 por US$" in texto
    assert "Meta de cero emisiones netas a 3 años" in texto
    assert "Pesimista (tesis UPN 2024)" in texto
    assert "Plan de plantación" in texto
    assert "Avance hacia la meta" in texto
    assert "Conversión de la flota a GNV (RES-01)" in texto
    assert "Consigna (S/ 12.50 por m3)" in texto or "Consigna (S/ 12.50 por m³)" in texto
    assert "No se recupera" in texto
    assert "53.06 / 73.96" in texto
    # El endpoint entrega el mismo documento con las secciones nuevas.
    pdf = client.get(f"/indicadores/reporte.pdf?desde={FECHA}&hasta={FECHA}", headers=headers)
    assert pdf.status_code == 200
    assert "Meta de cero emisiones netas" in _texto(pdf.content)


def test_pdf_marca_pendiente_si_faltan_parametros(client, db, cola):  # noqa: F811
    _plan(client, db, cola, "op.pdfpend@distrirapido.example.com", "70818004")
    for clave in (
        "precio_credito_carbono_usd_t",
        "gnv_mmbtu_scf",
        "factor_captura_arbol_pesimista_kg",
    ):
        _borrar(db, clave)
    dia = date.fromisoformat(FECHA)
    texto = _texto(reporte_pdf.generar_pdf(reporte_pdf.recopilar(db, dia, dia)))
    assert "Pendiente" in texto
    assert "precio_credito_carbono_usd_t" in texto
    assert "equivalencia energética" in texto
