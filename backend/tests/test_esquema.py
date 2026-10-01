import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError


def test_postgis_y_tablas_del_modelo(db):
    version = db.execute(text("SELECT postgis_version()")).scalar_one()
    assert version
    tablas = set(db.execute(text(
        "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
    )).scalars())
    esperadas = {
        "usuario",
        "cliente",
        "preferencia_cliente",
        "vehiculo",
        "conductor",
        "pedido",
        "ruta",
        "asignacion_ruta",
        "detalle_ruta",
        "zona_restriccion",
        "emision_co2",
        "reporte",
        "incidencia",
        "configuracion_sistema",
        "log_auditoria",
    }
    assert esperadas <= tablas


def test_indice_gist_de_zonas(db):
    definicion = db.execute(text(
        """
        SELECT indexdef FROM pg_indexes
        WHERE tablename = 'zona_restriccion' AND indexname = 'idx_zona_geometria'
        """
    )).scalar_one()
    assert "gist" in definicion.lower()


def test_placa_unica_en_postgresql(db):
    db.execute(text(
        """
        INSERT INTO vehiculo (
            placa, tipo, capacidad_kg, capacidad_m3, consumo_km_l,
            factor_emision_co2, anio_fabricacion
        ) VALUES ('UNI001', 'CAMIONETA', 1000, 8, 12.5, 0.2700, 2020)
        """
    ))
    db.commit()
    with pytest.raises(IntegrityError):
        db.execute(text(
            """
            INSERT INTO vehiculo (
                placa, tipo, capacidad_kg, capacidad_m3, consumo_km_l,
                factor_emision_co2, anio_fabricacion
            ) VALUES ('UNI001', 'FURGON', 800, 6, 10, 0.2500, 2019)
            """
        ))
        db.commit()
    db.rollback()


def test_parametros_iniciales(db):
    claves = set(db.execute(text("SELECT clave FROM configuracion_sistema")).scalars())
    assert "tiempo_max_optimizacion_s" in claves
    assert "tiempo_max_reoptimizacion_s" in claves
    assert "precio_diesel_galon" in claves
    assert "costo_mantenimiento_km" in claves
