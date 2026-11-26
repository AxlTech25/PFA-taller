"""US-017 · Plan de compensación de carbono del período (RF-010, RN-018).

El CO₂ emitido sale del mismo cálculo del tablero y del reporte PDF (RN-016:
km planificados × factor de emisión del vehículo). Los árboles necesarios usan
el factor de captura `factor_captura_arbol_kg` de `configuracion_sistema`
(RN-018) y el costo usa `costo_compensacion_arbol_soles`. Ninguno de los dos
está ratificado: mientras falten, el plan los devuelve como PENDIENTE y no
muestra cifras inventadas. Los proyectos locales son los que nombra RF-010.
"""

from __future__ import annotations

import math
from datetime import date

from sqlalchemy.orm import Session

from app.services import indicadores, reporte_pdf

CLAVE_FACTOR = "factor_captura_arbol_kg"
CLAVE_COSTO = "costo_compensacion_arbol_soles"
PENDIENTE = "PENDIENTE"
CONFIGURADO = "CONFIGURADO"
MENSAJE_SIN_DATOS = (
    "No es posible calcular la compensación: no hay datos de emisiones en el período."
)
NOTA_FACTOR = (
    "Pendiente: el factor de captura por árbol (RN-018) no está ratificado en la "
    f"configuración (clave {CLAVE_FACTOR}). No se muestra una cantidad inventada."
)
NOTA_COSTO = (
    "Pendiente: el costo por árbol de la compensación no está definido en la "
    f"configuración (clave {CLAVE_COSTO}). No se muestra un monto inventado."
)
# RF-010 (documento 06) y US-017: proyectos locales a sugerir. Solo el nombre;
# el sistema no tiene datos verificados de costos ni de capacidad de cada uno.
PROYECTOS = ("Lomas de Lima", "Parque Zonal Huáscar", "Árboles para Lima")


def _sin_datos(desde: date, hasta: date) -> dict:
    return {
        "desde": desde,
        "hasta": hasta,
        "calculable": False,
        "mensaje": MENSAJE_SIN_DATOS,
        "dias_con_operacion": 0,
        "rutas": 0,
        "co2_emitido_kg": 0,
        "factor_captura_arbol_kg": None,
        "estado_factor": None,
        "arboles_necesarios": None,
        "costo_por_arbol_soles": None,
        "estado_costo": None,
        "costo_estimado_soles": None,
        "notas": [],
        "proyectos": [],
    }


def plan(db: Session, desde: date, hasta: date) -> dict:
    datos = reporte_pdf.recopilar(db, desde, hasta)
    co2 = round(datos.total("co2_kg"), 3)
    if not datos.dias or co2 <= 0:
        return _sin_datos(desde, hasta)

    factor = indicadores.valor_positivo(db, CLAVE_FACTOR)
    costo_arbol = indicadores.valor_positivo(db, CLAVE_COSTO)
    # Árboles enteros: no se planta una fracción. Se redondea hacia arriba para cubrir el CO₂.
    arboles = math.ceil(co2 / factor) if factor is not None else None
    costo = (
        round(arboles * costo_arbol, 2) if arboles is not None and costo_arbol is not None else None
    )
    notas = []
    if factor is None:
        notas.append(NOTA_FACTOR)
    if costo_arbol is None:
        notas.append(NOTA_COSTO)
    return {
        "desde": desde,
        "hasta": hasta,
        "calculable": True,
        "mensaje": None,
        "dias_con_operacion": len(datos.dias),
        "rutas": len(datos.rutas),
        "co2_emitido_kg": co2,
        "factor_captura_arbol_kg": factor,
        "estado_factor": CONFIGURADO if factor is not None else PENDIENTE,
        "arboles_necesarios": arboles,
        "costo_por_arbol_soles": costo_arbol,
        "estado_costo": CONFIGURADO if costo_arbol is not None else PENDIENTE,
        "costo_estimado_soles": costo,
        "notas": notas,
        "proyectos": [{"nombre": nombre} for nombre in PROYECTOS],
    }
