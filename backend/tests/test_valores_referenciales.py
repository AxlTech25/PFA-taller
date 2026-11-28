"""Valores referenciales de compensación y ciclo de vida (migración 008)."""

from datetime import date

from app.services import compensacion, indicadores, reporte_pdf
from sqlalchemy import text
from tests.test_reporte_pdf import _texto

VALORES = {
    "factor_captura_arbol_kg": 60.0,
    "costo_compensacion_arbol_soles": 94.0,
    "depreciacion_anual_vehiculo_soles": 23988.0,
    "seguro_anual_vehiculo_soles": 8072.0,
    "soat_anual_vehiculo_soles": 150.0,
    "sueldo_anual_conductor_soles": 18000.0,
}


def test_migracion_carga_los_valores_investigados(db):
    filas = db.execute(
        text(
            "SELECT clave, valor, unidad, descripcion FROM configuracion_sistema "
            "WHERE clave = ANY(:claves)"
        ),
        {"claves": list(VALORES)},
    ).all()
    leidas = {fila.clave: fila for fila in filas}
    assert set(leidas) == set(VALORES)
    for clave, esperado in VALORES.items():
        assert float(leidas[clave].valor) == esperado
        assert leidas[clave].descripcion
    assert "EPA" in leidas["factor_captura_arbol_kg"].descripcion
    assert "SERPAR" in leidas["costo_compensacion_arbol_soles"].descripcion
    assert "Hilux" in leidas["depreciacion_anual_vehiculo_soles"].descripcion
    assert "6,73" in leidas["seguro_anual_vehiculo_soles"].descripcion
    assert "Positiva" in leidas["soat_anual_vehiculo_soles"].descripcion
    assert "1,500" in leidas["sueldo_anual_conductor_soles"].descripcion


def test_prorrateo_de_un_dia_y_de_una_semana():
    assert reporte_pdf.prorratear(23988, 1, 1) == 65.72
    assert reporte_pdf.prorratear(8072, 1, 1) == 22.12
    assert reporte_pdf.prorratear(150, 1, 1) == 0.41
    assert reporte_pdf.prorratear(18000, 1, 1) == 49.32
    # 7 días, 2 vehículos.
    assert reporte_pdf.prorratear(23988, 7, 2) == 920.09
    assert reporte_pdf.prorratear(8072, 7, 2) == 309.61
    assert reporte_pdf.prorratear(150, 7, 2) == 5.75
    assert reporte_pdf.prorratear(18000, 7, 2) == 690.41


def test_costo_ciclo_vida_completo_y_pendiente(db):
    ciclo = reporte_pdf.costo_ciclo_vida(db, date(2026, 11, 1), date(2026, 11, 1), {"ABC-123"})
    assert ciclo.completo is True
    assert ciclo.vehiculos == 1
    assert ciclo.dias_periodo == 1
    assert ciclo.depreciacion_anual == 23988
    assert ciclo.total_anual_por_vehiculo == 50210
    assert ciclo.depreciacion_periodo == 65.72
    assert ciclo.seguro_periodo == 22.12
    assert ciclo.soat_periodo == 0.41
    assert ciclo.sueldo_periodo == 49.32
    assert ciclo.total_periodo == 137.57

    semana = reporte_pdf.costo_ciclo_vida(db, date(2026, 11, 1), date(2026, 11, 7), {"A", "B"})
    assert semana.dias_periodo == 7
    assert semana.vehiculos == 2
    assert semana.depreciacion_periodo == 920.09
    assert semana.seguro_periodo == 309.61
    assert semana.soat_periodo == 5.75
    assert semana.sueldo_periodo == 690.41
    assert semana.total_periodo == 1925.86

    db.execute(text("DELETE FROM configuracion_sistema WHERE clave = 'soat_anual_vehiculo_soles'"))
    db.commit()
    incompleto = reporte_pdf.costo_ciclo_vida(db, date(2026, 11, 1), date(2026, 11, 1), {"ABC-123"})
    assert incompleto.completo is False
    assert incompleto.soat_anual is None
    assert incompleto.soat_periodo is None
    assert incompleto.total_periodo is None


def test_pdf_declara_fuentes_y_marca_pendiente_si_falta_un_valor(db):
    datos = reporte_pdf.DatosReporte(
        desde=date(2026, 11, 2), hasta=date(2026, 11, 8), precio_galon=17.5, costo_km=1.2
    )
    datos.ciclo = reporte_pdf.costo_ciclo_vida(db, datos.desde, datos.hasta, {"AAA-001", "BBB-002"})
    texto = _texto(reporte_pdf.generar_pdf(datos))
    assert "Costo de ciclo de vida (supuestos referenciales)" in texto
    assert "Vehículos con ruta en el período: 2" in texto
    assert "Días calendario del período: 7" in texto
    assert "S/ 23,988.00 / año" in texto
    assert "S/ 1,925.86" in texto
    assert "Grupo Pana" in texto
    assert "Positiva" in texto
    assert "Interbank" in texto
    assert "SERPAR" not in texto  # esa fuente es del plan de compensación, no del ciclo
    assert "consigna" in texto and "proyecto" in texto

    db.execute(
        text(
            "DELETE FROM configuracion_sistema WHERE clave IN "
            "('depreciacion_anual_vehiculo_soles', 'seguro_anual_vehiculo_soles')"
        )
    )
    db.commit()
    datos.ciclo = reporte_pdf.costo_ciclo_vida(db, datos.desde, datos.hasta, {"AAA-001"})
    texto = _texto(reporte_pdf.generar_pdf(datos))
    assert "Pendiente" in texto
    assert datos.ciclo.completo is False


def test_sin_claves_la_compensacion_vuelve_a_pendiente(db):
    db.execute(
        text(
            "DELETE FROM configuracion_sistema WHERE clave IN "
            "('factor_captura_arbol_kg', 'costo_compensacion_arbol_soles')"
        )
    )
    db.commit()
    assert indicadores.valor_positivo(db, "factor_captura_arbol_kg") is None
    assert indicadores.valor_positivo(db, "costo_compensacion_arbol_soles") is None
    # Las notas de pendiente se conservan por si se revierte la migración.
    assert "no está ratificado" in compensacion.NOTA_FACTOR
    assert "no está definido" in compensacion.NOTA_COSTO
