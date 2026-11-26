"""US-016 · Reporte PDF de sostenibilidad (RF-006)."""

import io
from datetime import UTC, date, datetime

import pytest
from app.models.entities import LogAuditoria, Reporte
from app.services import reporte_pdf
from pypdf import PdfReader
from sqlalchemy import select, text
from tests.conftest import autenticar, crear_usuario
from tests.test_cobertura_rutas import (
    FECHA,
    ColaFalsa,
    _conductor,
    _operador,
    _pedido,
    _procesar,
)

URL = "/indicadores/reporte.pdf"


@pytest.fixture
def cola(monkeypatch):
    falsa = ColaFalsa()
    monkeypatch.setattr("app.optimizacion.cola.obtener_cliente", lambda: falsa)
    return falsa


def _texto(contenido: bytes) -> str:
    lector = PdfReader(io.BytesIO(contenido))
    return "\n".join(pagina.extract_text() for pagina in lector.pages)


def _plan(client, db, cola, email: str, dni: str) -> dict:
    headers, _ = _operador(client, db, email)
    _conductor(db, dni=dni)
    _pedido(client, headers, db)
    alta = client.post("/optimizaciones", headers=headers, json={"fecha": FECHA})
    assert alta.status_code == 202, alta.text
    _procesar(db, cola)
    return headers


def _soles(valor: float) -> str:
    return f"S/ {valor:,.2f}"


def test_pdf_con_las_cifras_del_tablero_y_arboles_pendientes(client, db, cola):
    headers = _plan(client, db, cola, "op.pdf@distrirapido.example.com", "70816001")
    tablero = client.get(f"/indicadores?fecha={FECHA}", headers=headers).json()
    assert tablero["hay_datos"] is True

    respuesta = client.get(f"{URL}?desde={FECHA}&hasta={FECHA}", headers=headers)
    assert respuesta.status_code == 200, respuesta.text
    assert respuesta.headers["content-type"] == "application/pdf"
    assert (
        respuesta.headers["content-disposition"]
        == f'attachment; filename="reporte-sostenibilidad-{FECHA}_{FECHA}.pdf"'
    )
    assert respuesta.headers["cache-control"] == "no-store"
    assert "etag" not in respuesta.headers
    assert respuesta.content.startswith(b"%PDF-")

    lector = PdfReader(io.BytesIO(respuesta.content))
    assert lector.metadata.title == f"Reporte de sostenibilidad {FECHA} a {FECHA}"
    texto = _texto(respuesta.content)
    assert "Reporte de sostenibilidad" in texto
    assert f"Período: {FECHA} a {FECHA}" in texto
    # Mismas cifras que /indicadores: ningún número se calcula aparte.
    assert f"{tablero['km']:,.2f} km" in texto
    assert f"{tablero['co2_kg']:,.3f} kg" in texto
    assert f"{tablero['combustible_l']:,.2f} L" in texto
    assert _soles(tablero["soles_combustible"]) in texto
    assert _soles(tablero["soles_mantenimiento"]) in texto
    assert _soles(tablero["soles_combustible"] + tablero["soles_mantenimiento"]) in texto
    assert _soles(tablero["soles_ahorrados"]) in texto
    assert f"{tablero['cumplimiento_ventanas_pct']:,.1f} %" in texto
    assert f"{tablero['mejora_porcentaje']:,.2f} %" in texto
    assert "diésel S/ 17.50 por galón" in texto
    assert "mantenimiento S/ 1.20 por km" in texto
    assert "Emisiones por ruta" in texto
    assert "Pendiente: el factor de captura por árbol (RN-018)" in texto
    assert "árboles (factor" not in texto

    registro = db.scalar(select(Reporte).where(Reporte.periodo_inicio == date.fromisoformat(FECHA)))
    assert registro is not None
    assert registro.tipo == "SOSTENIBILIDAD_PDF"
    assert registro.ruta_archivo is None
    log = db.scalar(select(LogAuditoria).where(LogAuditoria.accion == "reporte_pdf"))
    assert log is not None
    assert log.registro_id == registro.id_reporte
    assert log.datos_nuevos["rutas"] == 1


def test_arboles_solo_con_factor_ratificado(client, db, cola):
    headers = _plan(client, db, cola, "op.pdf2@distrirapido.example.com", "70816002")
    db.execute(
        text(
            "INSERT INTO configuracion_sistema (clave, valor, unidad, descripcion) "
            "VALUES ('factor_captura_arbol_kg', '20', 'kg', 'prueba')"
        )
    )
    db.commit()
    tablero = client.get(f"/indicadores?fecha={FECHA}", headers=headers).json()
    texto = _texto(client.get(f"{URL}?desde={FECHA}&hasta={FECHA}", headers=headers).content)
    assert "Pendiente: el factor de captura por árbol (RN-018)" not in texto
    if tablero["arboles"] is None:
        assert "sin CO2 evitado en el período" in texto
    else:
        assert f"{tablero['arboles']:,.2f} árboles (factor RN-018" in texto


def test_periodo_vacio_no_genera_archivo(client, db):
    headers, _ = _operador(client, db, "op.pdf3@distrirapido.example.com")
    respuesta = client.get(f"{URL}?desde=2099-01-01&hasta=2099-01-31", headers=headers)
    assert respuesta.status_code == 404
    assert respuesta.headers["content-type"].startswith("application/json")
    assert respuesta.json()["detail"] == "Sin datos de operación para el período seleccionado."
    assert db.scalar(select(Reporte)) is None


def test_periodo_invalido(client, db):
    headers, _ = _operador(client, db, "op.pdf4@distrirapido.example.com")
    al_reves = client.get(f"{URL}?desde=2026-10-20&hasta=2026-10-19", headers=headers)
    assert al_reves.status_code == 422
    assert al_reves.json()["detail"] == reporte_pdf.MENSAJE_RANGO
    largo = client.get(f"{URL}?desde=2026-10-01&hasta=2026-11-01", headers=headers)
    assert largo.status_code == 422
    assert largo.json()["detail"] == reporte_pdf.MENSAJE_LARGO
    assert client.get(f"{URL}?desde=2026-10-01", headers=headers).status_code == 422


@pytest.mark.parametrize("rol", ["ADMIN", "GERENTE", "AUDITOR"])
def test_roles_con_acceso(client, db, cola, rol):
    _plan(client, db, cola, f"op.pdf.{rol.lower()}@distrirapido.example.com", f"7081610{len(rol)}")
    usuario = crear_usuario(db, email=f"{rol.lower()}.pdf@distrirapido.example.com", rol=rol)
    respuesta = client.get(
        f"{URL}?desde={FECHA}&hasta={FECHA}", headers=autenticar(client, usuario.email)
    )
    assert respuesta.status_code == 200, respuesta.text
    assert respuesta.content.startswith(b"%PDF-")


def test_conductor_recibe_403_y_anonimo_401(client, db):
    conductor = crear_usuario(db, email="con.pdf@distrirapido.example.com", rol="CONDUCTOR")
    prohibido = client.get(
        f"{URL}?desde={FECHA}&hasta={FECHA}", headers=autenticar(client, conductor.email)
    )
    assert prohibido.status_code == 403
    assert client.get(f"{URL}?desde={FECHA}&hasta={FECHA}").status_code == 401


def test_generar_pdf_con_hora_de_lima_y_sin_mejora():
    datos = reporte_pdf.DatosReporte(
        desde=date(2026, 11, 2), hasta=date(2026, 11, 3), precio_galon=17.5, costo_km=1.2
    )
    datos.dias.append(
        {
            "fecha": date(2026, 11, 2),
            "rutas": 1,
            "km": 10.0,
            "co2_kg": 2.5,
            "combustible_l": 1.0,
            "soles_combustible": 4.62,
            "soles_mantenimiento": 12.0,
            "soles_ahorrados": 0.0,
            "co2_ahorrado_kg": 0.0,
            "cumplimiento_ventanas_pct": 50.0,
            "mejora_porcentaje": None,
        }
    )
    datos.factor_arboles = 20.0
    datos.arboles = 3.5
    contenido = reporte_pdf.generar_pdf(datos, datetime(2026, 11, 3, 15, 30, tzinfo=UTC))
    texto = _texto(contenido)
    assert "Generado el 2026-11-03 10:30 (hora de Lima)" in texto
    assert "Sin comparación" in texto
    assert "3.50 árboles (factor RN-018" in texto
    assert "S/ 16.62" in texto
    assert reporte_pdf.nombre_archivo(date(2026, 11, 2), date(2026, 11, 3)) == (
        "reporte-sostenibilidad-2026-11-02_2026-11-03.pdf"
    )
