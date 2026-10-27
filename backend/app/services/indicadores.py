"""Tablero iniciado del Hito 3 (US-014 no se cierra: sigue en el Sprint 5).

Agrega el último trabajo completado del día. Los soles usan RN-017
(S/ 17.50 por galón y S/ 1.20 por km). El equivalente en árboles queda
vacío mientras `factor_captura_arbol_kg` no esté ratificado.
"""

from datetime import date

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.models.entities import DetalleRuta, JobOptimizacion, Pedido, Ruta
from app.optimizacion.evaluacion import LITROS_POR_GALON
from app.optimizacion.heuristica import _parametro

MENSAJE_VACIO = "Sin datos de operación para el período seleccionado."
NOTA_ARBOLES = (
    "El factor de captura por árbol (RN-018) todavía no está ratificado "
    "en la configuración. No se muestra un equivalente inventado."
)


def _factor_arboles(db: Session) -> float | None:
    valor = db.execute(
        text("SELECT valor FROM configuracion_sistema WHERE clave = :clave"),
        {"clave": "factor_captura_arbol_kg"},
    ).scalar()
    if valor is None:
        return None
    try:
        factor = float(valor)
    except ValueError:
        return None
    if factor <= 0:
        return None
    return factor


def _sin_datos(fecha: date) -> dict:
    return {
        "fecha": fecha,
        "hay_datos": False,
        "mensaje": MENSAJE_VACIO,
        "rutas": 0,
        "km": 0,
        "co2_kg": 0,
        "combustible_l": 0,
        "soles_combustible": 0,
        "soles_mantenimiento": 0,
        "soles_ahorrados": 0,
        "co2_ahorrado_kg": 0,
        "arboles": None,
        "nota_arboles": NOTA_ARBOLES,
        "cumplimiento_ventanas_pct": 0,
        "mejora_porcentaje": None,
    }


def _rutas_del_dia(db: Session, fecha: date) -> tuple[JobOptimizacion | None, list[Ruta]]:
    job = db.scalar(
        select(JobOptimizacion)
        .where(JobOptimizacion.fecha == fecha, JobOptimizacion.estado == "COMPLETADO")
        .order_by(JobOptimizacion.actualizado_en.desc())
    )
    if job is not None:
        rutas = list(db.scalars(select(Ruta).where(Ruta.id_job == job.id_job)).all())
    else:
        rutas = list(
            db.scalars(select(Ruta).where(Ruta.fecha == fecha, Ruta.estado != "CANCELADA")).all()
        )
    return job, rutas


def _ahorros(job: JobOptimizacion | None) -> tuple[float, float, float | None]:
    comparacion = (job.resultado or {}).get("comparacion") if job and job.resultado else None
    if not comparacion:
        return 0.0, 0.0, None
    soles = max(float(comparacion.get("soles_base", 0)) - float(comparacion.get("soles", 0)), 0)
    co2 = max(float(comparacion.get("co2_base_kg", 0)) - float(comparacion.get("co2_kg", 0)), 0)
    return soles, co2, float(comparacion.get("mejora_porcentaje", 0))


def _cumplimiento(db: Session, rutas: list[Ruta]) -> float:
    cumplidas = 0
    totales = 0
    for ruta in rutas:
        detalles = list(
            db.scalars(select(DetalleRuta).where(DetalleRuta.id_ruta == ruta.id_ruta)).all()
        )
        for detalle in detalles:
            pedido = db.get(Pedido, detalle.id_pedido)
            if pedido is None or detalle.eta is None:
                continue
            totales += 1
            if pedido.ventana_inicio <= detalle.eta <= pedido.ventana_fin:
                cumplidas += 1
    if totales == 0:
        return 0.0
    return cumplidas / totales * 100


def _equivalente_arboles(factor: float | None, co2_ahorrado: float) -> float | None:
    if factor is None or co2_ahorrado <= 0:
        return None
    return round(co2_ahorrado / factor, 2)


def consultar(db: Session, fecha: date) -> dict:
    job, rutas = _rutas_del_dia(db, fecha)
    if not rutas:
        return _sin_datos(fecha)

    precio_litro = _parametro(db, "precio_diesel_galon", 17.50) / LITROS_POR_GALON
    costo_km = _parametro(db, "costo_mantenimiento_km", 1.20)
    km = sum(float(ruta.distancia_total_km or 0) for ruta in rutas)
    co2 = sum(float(ruta.co2_estimado_kg or 0) for ruta in rutas)
    litros = sum(float(ruta.combustible_estimado_l or 0) for ruta in rutas)
    soles_ahorrados, co2_ahorrado, mejora = _ahorros(job)
    pct = _cumplimiento(db, rutas)
    arboles = _equivalente_arboles(_factor_arboles(db), co2_ahorrado)
    return {
        "fecha": fecha,
        "hay_datos": True,
        "mensaje": None,
        "rutas": len(rutas),
        "km": round(km, 2),
        "co2_kg": round(co2, 3),
        "combustible_l": round(litros, 2),
        "soles_combustible": round(litros * precio_litro, 2),
        "soles_mantenimiento": round(km * costo_km, 2),
        "soles_ahorrados": round(soles_ahorrados, 2),
        "co2_ahorrado_kg": round(co2_ahorrado, 3),
        "arboles": arboles,
        "nota_arboles": None if arboles is not None else NOTA_ARBOLES,
        "cumplimiento_ventanas_pct": round(pct, 1),
        "mejora_porcentaje": None if mejora is None else round(mejora, 2),
    }
