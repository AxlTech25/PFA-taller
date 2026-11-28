"""RF-10, RES-01, RES-02 y RF-06 · proyección anual, meta a 3 años, GNV y créditos.

Funciones de cálculo puras sobre los totales del período. No importan
`reporte_pdf` para que éste pueda usarlas sin dependencias circulares.

Fórmulas (todas parten de las cifras del tablero, RN-016 y RN-017):
- Proyección anual: valor del período × 365 / días calendario del período
  (promedio por día calendario, así se conserva la proporción de días con
  operación). No es un año observado.
- Árboles anuales = ceil(CO₂ anual / factor de captura). Costo = árboles × costo
  por árbol. Plan a 3 años: se plantan N/3 árboles por año (redondeo hacia
  arriba en los dos primeros años); cada árbol captura el factor desde el año
  en que se planta (el factor de la EPA ya es un promedio de 10 años). Se
  supone que las emisiones anuales no cambian.
- GNV: galones de diésel = litros / 3.785411784. Energía = galones × 0.138
  mmBtu/gal. m³ de GNV equivalentes = energía / (0.001026 mmBtu/scf × 35.3147
  scf/m³). Ahorro anual = costo del diésel − m³ × precio del GNV. Inversión =
  S/ 5,000 × vehículos con ruta. Recuperación (meses) = inversión / ahorro anual
  × 12. ROI a 3 años = (3 × ahorro anual − inversión) / inversión. CO₂ del GNV =
  CO₂ del período × (53.06 / 73.96), la razón de factores EPA por unidad de
  energía; el CO₂ evitado es la diferencia. Supone el mismo rendimiento
  energético del motor con diésel y con GNV.
- Créditos: toneladas × US$ por t CO₂e × tipo de cambio.
Los parámetros salen de `configuracion_sistema`; si falta uno (o no es un
número > 0) el resultado que lo necesita queda PENDIENTE y no se inventa.
"""

from __future__ import annotations

import math

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.optimizacion.evaluacion import LITROS_POR_GALON
from app.services import indicadores

DIAS_ANIO = 365
ANIOS_META = 3
PIES3_POR_M3 = 35.3147  # 1 m³ = 35.3147 ft³ (1 ft = 0.3048 m)
CLAVE_FACTOR = "factor_captura_arbol_kg"
CLAVE_FACTOR_PESIMISTA = "factor_captura_arbol_pesimista_kg"
CLAVE_COSTO_ARBOL = "costo_compensacion_arbol_soles"
CLAVE_ARBOLES_REGISTRADOS = "arboles_plantados_registrados"
CLAVE_PRECIO_DIESEL = "precio_diesel_galon"
CLAVE_PRECIO_GNV = "precio_gnv_m3_soles"
CLAVE_PRECIO_GNV_MERCADO = "gnv_precio_mercado_m3_soles"
CLAVE_CONVERSION = "costo_conversion_gnv_vehiculo_soles"
CLAVE_DIESEL_MMBTU = "diesel_mmbtu_galon"
CLAVE_DIESEL_CO2 = "diesel_co2_kg_mmbtu"
CLAVE_GNV_MMBTU = "gnv_mmbtu_scf"
CLAVE_GNV_CO2 = "gnv_co2_kg_mmbtu"
CLAVE_CREDITO_USD = "precio_credito_carbono_usd_t"
CLAVE_TIPO_CAMBIO = "tipo_cambio_usd_pen"
PRECIO_DIESEL_DEFECTO = 17.50  # consigna RES-01; igual que reporte_pdf

PENDIENTE = "PENDIENTE"
CONFIGURADO = "CONFIGURADO"
AVISO_PROYECCION = (
    "Proyección lineal a 365 días a partir de {dias_op} día(s) con operación dentro de "
    "{dias_cal} día(s) calendario del período. No es un año observado: con pocos días la "
    "cifra anual puede variar mucho."
)
AVISO_GNV_CARO = (
    "Con el precio de la consigna el GNV cuesta más que el diésel por unidad de energía "
    "(precio de equilibrio: S/ {equilibrio:.2f} por m³), por eso no hay ahorro. El precio "
    "de mercado en Lima es mucho menor. Los valores son configurables."
)
ESCENARIOS_ARBOL = (
    ("EPA (referencia)", CLAVE_FACTOR, "US EPA, árbol urbano, promedio de 10 años"),
    (
        "Pesimista (tesis UPN 2024)",
        CLAVE_FACTOR_PESIMISTA,
        "Tesis UPN 2024, Los Olivos, i-Tree Eco (~15,1 kg/árbol/año)",
    ),
)
ESCENARIOS_GNV = (
    ("Consigna (S/ 12.50 por m³)", CLAVE_PRECIO_GNV, "Consigna del proyecto, RES-01"),
    (
        "Mercado Lima (referencial)",
        CLAVE_PRECIO_GNV_MERCADO,
        "Osinergmin Facilito vía El Comercio, 21/11/2026",
    ),
)


def _r(valor: float | None, decimales: int = 2) -> float | None:
    return None if valor is None else round(valor, decimales)


def valor_no_negativo(db: Session, clave: str) -> float | None:
    """Número ≥ 0 de `configuracion_sistema`; None si falta o no es válido."""
    valor = db.execute(
        text("SELECT valor FROM configuracion_sistema WHERE clave = :clave"), {"clave": clave}
    ).scalar()
    if valor is None:
        return None
    try:
        numero = float(valor)
    except ValueError:
        return None
    if numero != numero or numero < 0 or numero == float("inf"):
        return None
    return numero


def _estado(valor: float | None) -> str:
    return CONFIGURADO if valor is not None else PENDIENTE


def proyeccion(co2_periodo_kg: float, dias_calendario: int, dias_con_operacion: int) -> dict:
    escala = DIAS_ANIO / max(dias_calendario, 1)
    return {
        "dias_calendario": dias_calendario,
        "dias_con_operacion": dias_con_operacion,
        "co2_periodo_kg": round(co2_periodo_kg, 3),
        "co2_anual_kg": round(co2_periodo_kg * escala, 1),
        "escala": round(escala, 4),
        "aviso": AVISO_PROYECCION.format(dias_op=dias_con_operacion, dias_cal=dias_calendario),
    }


def plan_tres_anios(arboles: int, factor: float, costo_arbol: float | None, co2_anual: float):
    """Árboles por año para llegar a la neutralidad en `ANIOS_META` años."""
    por_anio = math.ceil(arboles / ANIOS_META)
    filas = []
    acumulado = 0
    for anio in range(1, ANIOS_META + 1):
        plantar = por_anio if anio < ANIOS_META else max(arboles - acumulado, 0)
        acumulado += plantar
        capturado = acumulado * factor
        filas.append(
            {
                "anio": anio,
                "arboles_a_plantar": plantar,
                "arboles_acumulados": acumulado,
                "cobertura_pct": round(min(capturado / co2_anual * 100, 100), 1),
                "costo_soles": _r(plantar * costo_arbol) if costo_arbol is not None else None,
            }
        )
    return filas


def escenarios_arboles(db: Session, co2_anual_kg: float) -> list[dict]:
    costo_arbol = indicadores.valor_positivo(db, CLAVE_COSTO_ARBOL)
    salida = []
    for nombre, clave, fuente in ESCENARIOS_ARBOL:
        factor = indicadores.valor_positivo(db, clave)
        # Sin emisiones no hay nada que compensar: 0 árboles y sin plan.
        arboles = math.ceil(co2_anual_kg / factor) if factor is not None else None
        costo = _r(arboles * costo_arbol) if arboles is not None and costo_arbol else None
        plan = (
            plan_tres_anios(arboles, factor, costo_arbol, co2_anual_kg)
            if arboles and factor is not None
            else []
        )
        salida.append(
            {
                "nombre": nombre,
                "clave_factor": clave,
                "fuente": fuente,
                "factor_kg_arbol_anio": factor,
                "estado_factor": _estado(factor),
                "arboles_anuales": arboles,
                "costo_por_arbol_soles": costo_arbol,
                "estado_costo": _estado(costo_arbol),
                "costo_total_soles": costo,
                "arboles_por_anio": math.ceil(arboles / ANIOS_META)
                if arboles is not None
                else None,
                "plan": plan,
            }
        )
    return salida


def avance_meta(db: Session, co2_anual_kg: float) -> dict:
    """Avance hacia la neutralidad con los árboles registrados por la empresa."""
    factor = indicadores.valor_positivo(db, CLAVE_FACTOR)
    registrados = valor_no_negativo(db, CLAVE_ARBOLES_REGISTRADOS)
    if factor is None or co2_anual_kg <= 0:
        pct = None
    else:
        pct = round(min((registrados or 0) * factor / co2_anual_kg * 100, 100), 1)
    return {
        "arboles_registrados": int(registrados) if registrados is not None else 0,
        "estado_registro": CONFIGURADO if registrados is not None else PENDIENTE,
        "avance_pct": pct,
        "nota": (
            None
            if registrados is not None
            else "Pendiente: la empresa aún no registra árboles plantados "
            f"(clave {CLAVE_ARBOLES_REGISTRADOS}); el avance se muestra en 0 %."
        ),
    }


def meta_anual(
    db: Session, co2_periodo_kg: float, dias_calendario: int, dias_con_operacion: int
) -> dict:
    base = proyeccion(co2_periodo_kg, dias_calendario, dias_con_operacion)
    return {
        **base,
        "anios_meta": ANIOS_META,
        "escenarios": escenarios_arboles(db, base["co2_anual_kg"]),
        "avance": avance_meta(db, base["co2_anual_kg"]),
    }


def _parametros_gnv(db: Session) -> dict[str, float | None]:
    claves = (
        CLAVE_PRECIO_DIESEL,
        CLAVE_CONVERSION,
        CLAVE_DIESEL_MMBTU,
        CLAVE_DIESEL_CO2,
        CLAVE_GNV_MMBTU,
        CLAVE_GNV_CO2,
    )
    valores = {clave: indicadores.valor_positivo(db, clave) for clave in claves}
    if valores[CLAVE_PRECIO_DIESEL] is None:
        valores[CLAVE_PRECIO_DIESEL] = PRECIO_DIESEL_DEFECTO
    return valores


def metros3_por_galon(diesel_mmbtu_gal: float, gnv_mmbtu_scf: float) -> float:
    """m³ de GNV con la misma energía que un galón de diésel."""
    return diesel_mmbtu_gal / (gnv_mmbtu_scf * PIES3_POR_M3)


def evaluar_gnv(
    db: Session,
    *,
    litros_periodo: float,
    co2_periodo_kg: float,
    dias_calendario: int,
    dias_con_operacion: int,
    vehiculos: int,
) -> dict:
    p = _parametros_gnv(db)
    escala = DIAS_ANIO / max(dias_calendario, 1)
    faltan = [
        clave
        for clave in (CLAVE_CONVERSION, CLAVE_DIESEL_MMBTU, CLAVE_GNV_MMBTU)
        if p[clave] is None
    ]
    base: dict = {
        "vehiculos": vehiculos,
        "dias_calendario": dias_calendario,
        "dias_con_operacion": dias_con_operacion,
        "litros_periodo": round(litros_periodo, 2),
        "aviso_proyeccion": AVISO_PROYECCION.format(
            dias_op=dias_con_operacion, dias_cal=dias_calendario
        ),
        "precio_diesel_galon": p[CLAVE_PRECIO_DIESEL],
        "costo_conversion_vehiculo": p[CLAVE_CONVERSION],
        "estado_conversion": _estado(p[CLAVE_CONVERSION]),
        "anios_roi": ANIOS_META,
        "equivalencia_m3_por_galon": None,
        "estado_equivalencia": PENDIENTE,
        "inversion_soles": None,
        "costo_diesel_anual_soles": None,
        "co2_diesel_anual_kg": round(co2_periodo_kg * escala, 1),
        "co2_gnv_anual_kg": None,
        "co2_evitado_periodo_kg": None,
        "co2_evitado_anual_kg": None,
        "reduccion_co2_pct": None,
        "estado_factor_co2": _estado(p[CLAVE_GNV_CO2] if p[CLAVE_DIESEL_CO2] is not None else None),
        "gnv_m3_anual": None,
        "precio_equilibrio_gnv_m3": None,
        "escenarios": [],
        "notas": [],
    }
    if not vehiculos:
        base["notas"].append("No hay vehículos con placa y ruta en el período.")
    if CLAVE_CONVERSION in faltan:
        base["notas"].append(f"Pendiente: costo de conversión (clave {CLAVE_CONVERSION}).")
    if CLAVE_DIESEL_MMBTU in faltan or CLAVE_GNV_MMBTU in faltan:
        base["notas"].append(
            "Pendiente: equivalencia energética diésel-GNV "
            f"(claves {CLAVE_DIESEL_MMBTU} y {CLAVE_GNV_MMBTU})."
        )
        return base

    m3_galon = metros3_por_galon(p[CLAVE_DIESEL_MMBTU], p[CLAVE_GNV_MMBTU])
    galones_anual = litros_periodo * escala / LITROS_POR_GALON
    m3_anual = galones_anual * m3_galon
    costo_diesel = galones_anual * p[CLAVE_PRECIO_DIESEL]
    inversion = p[CLAVE_CONVERSION] * vehiculos if p[CLAVE_CONVERSION] is not None else None
    base.update(
        equivalencia_m3_por_galon=round(m3_galon, 4),
        estado_equivalencia=CONFIGURADO,
        gnv_m3_anual=round(m3_anual, 1),
        inversion_soles=_r(inversion),
        costo_diesel_anual_soles=_r(costo_diesel),
        precio_equilibrio_gnv_m3=round(p[CLAVE_PRECIO_DIESEL] / m3_galon, 2),
    )
    if p[CLAVE_GNV_CO2] is not None and p[CLAVE_DIESEL_CO2] is not None:
        razon = p[CLAVE_GNV_CO2] / p[CLAVE_DIESEL_CO2]
        evitado_periodo = co2_periodo_kg * (1 - razon)
        base.update(
            co2_gnv_anual_kg=round(co2_periodo_kg * escala * razon, 1),
            co2_evitado_periodo_kg=round(evitado_periodo, 3),
            co2_evitado_anual_kg=round(evitado_periodo * escala, 1),
            reduccion_co2_pct=round((1 - razon) * 100, 1),
        )
    else:
        base["notas"].append(
            f"Pendiente: factor de emisión del GNV (claves {CLAVE_GNV_CO2} y {CLAVE_DIESEL_CO2})."
        )
    for nombre, clave, fuente in ESCENARIOS_GNV:
        precio = indicadores.valor_positivo(db, clave)
        fila: dict = {
            "nombre": nombre,
            "clave_precio": clave,
            "fuente": fuente,
            "precio_gnv_m3": precio,
            "estado_precio": _estado(precio),
            "costo_gnv_anual_soles": None,
            "ahorro_anual_soles": None,
            "recuperacion_meses": None,
            "roi_3_anios_pct": None,
            "ahorro_3_anios_soles": None,
            "se_recupera": None,
        }
        if precio is not None:
            costo_gnv = m3_anual * precio
            ahorro = costo_diesel - costo_gnv
            fila.update(
                costo_gnv_anual_soles=_r(costo_gnv),
                ahorro_anual_soles=_r(ahorro),
                ahorro_3_anios_soles=_r(ahorro * ANIOS_META),
            )
            if inversion:
                fila["se_recupera"] = ahorro > 0 and inversion / ahorro * 12 <= ANIOS_META * 12
                fila["recuperacion_meses"] = _r(inversion / ahorro * 12, 1) if ahorro > 0 else None
                fila["roi_3_anios_pct"] = _r((ahorro * ANIOS_META - inversion) / inversion * 100, 1)
        base["escenarios"].append(fila)
    consigna = base["escenarios"][0]
    if consigna["ahorro_anual_soles"] is not None and consigna["ahorro_anual_soles"] <= 0:
        base["notas"].append(AVISO_GNV_CARO.format(equilibrio=base["precio_equilibrio_gnv_m3"]))
    return base


def creditos(db: Session, co2_kg: float, co2_evitado_kg: float) -> dict:
    precio = indicadores.valor_positivo(db, CLAVE_CREDITO_USD)
    cambio = indicadores.valor_positivo(db, CLAVE_TIPO_CAMBIO)
    completo = precio is not None and cambio is not None

    def valor(kg: float) -> tuple[float | None, float | None]:
        if not completo:
            return None, None
        usd = kg / 1000 * precio
        return round(usd, 2), round(usd * cambio, 2)

    usd, soles = valor(co2_kg)
    usd_ev, soles_ev = valor(max(co2_evitado_kg, 0))
    return {
        "precio_usd_t": precio,
        "tipo_cambio": cambio,
        "estado": CONFIGURADO if completo else PENDIENTE,
        "toneladas_periodo": round(co2_kg / 1000, 4),
        "valor_usd": usd,
        "valor_soles": soles,
        "toneladas_evitadas": round(max(co2_evitado_kg, 0) / 1000, 4),
        "ahorro_usd": usd_ev,
        "ahorro_soles": soles_ev,
        "nota": (
            None
            if completo
            else "Pendiente: precio del crédito o tipo de cambio no configurados "
            f"(claves {CLAVE_CREDITO_USD} y {CLAVE_TIPO_CAMBIO})."
        ),
    }
