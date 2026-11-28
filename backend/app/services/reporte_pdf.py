"""US-016 · Reporte PDF de sostenibilidad del período (RF-006).

Todas las cifras salen del mismo cálculo del tablero (`services.indicadores`):
km, combustible y CO₂ guardados en cada ruta (RN-016: km × factor del vehículo),
soles con RN-017 (precio del diésel y costo de mantenimiento de
`configuracion_sistema`) y ahorro frente al vecino más cercano del trabajo de
optimización. El equivalente en árboles (RN-018) solo aparece si el factor está
ratificado en la configuración; si no, el reporte lo marca como pendiente.
"""

from __future__ import annotations

import io
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import AsignacionRuta, Reporte, Usuario, Vehiculo
from app.optimizacion.evaluacion import LITROS_POR_GALON
from app.optimizacion.heuristica import _parametro
from app.services import auditoria, indicadores, metas

MAX_DIAS = 31
TIPO_REPORTE = "SOSTENIBILIDAD_PDF"
LIMA = ZoneInfo("America/Lima")
MENSAJE_RANGO = "La fecha final no puede ser anterior a la inicial."
MENSAJE_LARGO = f"El período del reporte no puede superar {MAX_DIAS} días."
NOTA_ARBOLES_PDF = (
    "Pendiente: el factor de captura por árbol (RN-018) no está ratificado en la "
    "configuración. El reporte no muestra un equivalente inventado."
)
# Costo de ciclo de vida: valores anuales por vehículo, en configuracion_sistema.
# Se prorratean a los días calendario del período (año de 365 días) y a las
# placas distintas con ruta en ese período. No se mezclan con el costo local RN-017.
DIAS_ANIO = 365
CLAVE_DEPRECIACION = "depreciacion_anual_vehiculo_soles"
CLAVE_SEGURO = "seguro_anual_vehiculo_soles"
CLAVE_SOAT = "soat_anual_vehiculo_soles"
CLAVE_SUELDO = "sueldo_anual_conductor_soles"
NOTA_CICLO_VIDA = (
    "Supuestos referenciales por vehículo y año, prorrateados a los días calendario "
    "del período (año de 365 días) y a los vehículos con ruta en el período. No son "
    "tarifas contratadas de DistriRápido. Depreciación: 20 % anual sobre S/ 119,941 "
    "(Toyota Hilux 4x2 D/C 2GD M/T SR, lista Grupo Pana US$ 34,490 × tipo de cambio "
    "BCRP S/ 3,478 al 26/11/2026) = S/ 23,988. Seguro: 6,73 % anual (Interbank/Rímac, "
    "pick-up Lima, tarifario dic. 2021, uso particular; no hay tarifa pública de flota) "
    "≈ S/ 8,072. SOAT: S/ 150 (La Positiva, pick-up N1 uso carga, Lima, ago. 2026, "
    "referencial). Sueldo del conductor: S/ 1,500 al mes = S/ 18,000 al año (consigna "
    "del proyecto)."
)

ESTADOS = {
    "BORRADOR": "Borrador",
    "CONFIRMADA": "Confirmada",
    "EN_EJECUCION": "En ejecución",
    "COMPLETADA": "Completada",
}
ANCHOS_DIA = [w * cm for w in (2.3, 1.4, 1.8, 2, 2.6, 2.4, 2.2, 3)]
ANCHOS_RUTA = [w * cm for w in (2.2, 2, 2.6, 1.6, 1.6, 2, 2.6, 2.4)]


@dataclass
class FilaRuta:
    fecha: date
    placa: str
    estado: str
    km: float
    litros: float
    co2_kg: float
    soles_combustible: float
    soles_mantenimiento: float


@dataclass
class DatosReporte:
    desde: date
    hasta: date
    precio_galon: float
    costo_km: float
    dias: list[dict] = field(default_factory=list)
    rutas: list[FilaRuta] = field(default_factory=list)
    cumplimiento_pct: float = 0.0
    factor_arboles: float | None = None
    arboles: float | None = None
    ciclo: CostoCicloVida | None = None
    meta: dict | None = None
    gnv: dict | None = None
    creditos: dict | None = None

    def total(self, clave: str) -> float:
        return sum(float(dia[clave]) for dia in self.dias)

    @property
    def costo_local(self) -> float:
        return self.total("soles_combustible") + self.total("soles_mantenimiento")


@dataclass
class CostoCicloVida:
    """Costo anual por vehículo, prorrateado al período del reporte."""

    vehiculos: int
    dias_periodo: int
    depreciacion_anual: float | None
    seguro_anual: float | None
    soat_anual: float | None
    sueldo_anual: float | None
    depreciacion_periodo: float | None
    seguro_periodo: float | None
    soat_periodo: float | None
    sueldo_periodo: float | None
    total_anual_por_vehiculo: float | None
    total_periodo: float | None
    completo: bool


def prorratear(anual: float, dias: int, vehiculos: int) -> float:
    return round(anual * dias * vehiculos / DIAS_ANIO, 2)


def _linea_ciclo(anual: float | None, dias: int, vehiculos: int) -> float | None:
    if anual is None:
        return None
    return prorratear(anual, dias, vehiculos)


def costo_ciclo_vida(db: Session, desde: date, hasta: date, placas: set[str]) -> CostoCicloVida:
    dias = (hasta - desde).days + 1
    vehiculos = len(placas)
    depreciacion = indicadores.valor_positivo(db, CLAVE_DEPRECIACION)
    seguro = indicadores.valor_positivo(db, CLAVE_SEGURO)
    soat = indicadores.valor_positivo(db, CLAVE_SOAT)
    sueldo = indicadores.valor_positivo(db, CLAVE_SUELDO)
    anuales = (depreciacion, seguro, soat, sueldo)
    completo = all(valor is not None for valor in anuales)
    total_anual = round(sum(anuales), 2) if completo else None  # type: ignore[arg-type]
    lineas = [_linea_ciclo(valor, dias, vehiculos) for valor in anuales]
    total_periodo = round(sum(lineas), 2) if completo else None  # type: ignore[arg-type]
    return CostoCicloVida(
        vehiculos=vehiculos,
        dias_periodo=dias,
        depreciacion_anual=depreciacion,
        seguro_anual=seguro,
        soat_anual=soat,
        sueldo_anual=sueldo,
        depreciacion_periodo=lineas[0],
        seguro_periodo=lineas[1],
        soat_periodo=lineas[2],
        sueldo_periodo=lineas[3],
        total_anual_por_vehiculo=total_anual,
        total_periodo=total_periodo,
        completo=completo,
    )


def validar_periodo(desde: date, hasta: date) -> None:
    if hasta < desde:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, MENSAJE_RANGO)
    if (hasta - desde).days + 1 > MAX_DIAS:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, MENSAJE_LARGO)


def _placa(db: Session, id_ruta) -> str:
    asignacion = db.scalar(select(AsignacionRuta).where(AsignacionRuta.id_ruta == id_ruta))
    vehiculo = db.get(Vehiculo, asignacion.id_vehiculo) if asignacion else None
    return vehiculo.placa if vehiculo else "Sin asignar"


def recopilar(db: Session, desde: date, hasta: date) -> DatosReporte:
    validar_periodo(desde, hasta)
    precio_galon = _parametro(db, "precio_diesel_galon", 17.50)
    costo_km = _parametro(db, "costo_mantenimiento_km", 1.20)
    precio_litro = precio_galon / LITROS_POR_GALON
    datos = DatosReporte(desde=desde, hasta=hasta, precio_galon=precio_galon, costo_km=costo_km)
    todas = []
    dia = desde
    while dia <= hasta:
        resumen = indicadores.consultar(db, dia)
        if resumen["hay_datos"]:
            datos.dias.append(resumen)
            _, rutas = indicadores._rutas_del_dia(db, dia)
            todas.extend(rutas)
            for ruta in rutas:
                km = float(ruta.distancia_total_km or 0)
                litros = float(ruta.combustible_estimado_l or 0)
                datos.rutas.append(
                    FilaRuta(
                        fecha=dia,
                        placa=_placa(db, ruta.id_ruta),
                        estado=ruta.estado,
                        km=round(km, 2),
                        litros=round(litros, 2),
                        co2_kg=round(float(ruta.co2_estimado_kg or 0), 3),
                        soles_combustible=round(litros * precio_litro, 2),
                        soles_mantenimiento=round(km * costo_km, 2),
                    )
                )
        dia += timedelta(days=1)
    if todas:
        datos.cumplimiento_pct = round(indicadores._cumplimiento(db, todas), 1)
        datos.factor_arboles = indicadores._factor_arboles(db)
        datos.arboles = indicadores._equivalente_arboles(
            datos.factor_arboles, datos.total("co2_ahorrado_kg")
        )
    placas = {fila.placa for fila in datos.rutas if fila.placa != "Sin asignar"}
    datos.ciclo = costo_ciclo_vida(db, desde, hasta, placas)
    if datos.dias:
        co2 = datos.total("co2_kg")
        dias_calendario = (hasta - desde).days + 1
        datos.meta = metas.meta_anual(db, co2, dias_calendario, len(datos.dias))
        datos.gnv = metas.evaluar_gnv(
            db,
            litros_periodo=datos.total("combustible_l"),
            co2_periodo_kg=co2,
            dias_calendario=dias_calendario,
            dias_con_operacion=len(datos.dias),
            vehiculos=len(placas),
        )
        datos.creditos = metas.creditos(db, co2, datos.total("co2_ahorrado_kg"))
    return datos


def _soles(valor: float) -> str:
    return f"-S/ {-valor:,.2f}" if valor < 0 else f"S/ {valor:,.2f}"


def _num(valor: float, decimales: int = 2) -> str:
    return f"{valor:,.{decimales}f}"


def _tabla(filas: list[list[str]], anchos: list[float]) -> Table:
    tabla = Table(filas, colWidths=anchos, repeatRows=1)
    tabla.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f5135")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#9aa9a1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eef5f0")]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    return tabla


def _celda(valor: float | None, anual: bool = False) -> str:
    if valor is None:
        return "Pendiente"
    return _soles(valor) + (" / año" if anual else "")


def _bloque_ciclo(datos: DatosReporte, estilos, nota) -> list:
    ciclo = datos.ciclo
    if ciclo is None:
        return []
    filas = [
        ["Concepto", "Anual por vehículo", "Prorrateado al período"],
        [
            "Depreciación (20 % sobre S/ 119,941)",
            _celda(ciclo.depreciacion_anual, True),
            _celda(ciclo.depreciacion_periodo),
        ],
        [
            "Seguro vehicular (6,73 %)",
            _celda(ciclo.seguro_anual, True),
            _celda(ciclo.seguro_periodo),
        ],
        ["SOAT", _celda(ciclo.soat_anual, True), _celda(ciclo.soat_periodo)],
        [
            "Sueldo del conductor",
            _celda(ciclo.sueldo_anual, True),
            _celda(ciclo.sueldo_periodo),
        ],
        [
            "Total",
            _celda(ciclo.total_anual_por_vehiculo, True),
            _celda(ciclo.total_periodo),
        ],
    ]
    return [
        Paragraph("Costo de ciclo de vida (supuestos referenciales)", estilos["Heading2"]),
        Paragraph(
            f"Vehículos con ruta en el período: {ciclo.vehiculos}. "
            f"Días calendario del período: {ciclo.dias_periodo}.",
            estilos["BodyText"],
        ),
        _tabla(filas, [8.5 * cm, 4.5 * cm, 4.5 * cm]),
        Paragraph(NOTA_CICLO_VIDA, nota),
        Spacer(1, 0.3 * cm),
    ]


def _usd(valor: float | None) -> str:
    return "Pendiente" if valor is None else f"US$ {valor:,.2f}"


def _bloque_creditos(datos: DatosReporte, estilos, nota) -> list:
    c = datos.creditos
    if c is None:
        return []
    filas = [
        ["Concepto", "Toneladas CO2e", "US$", "Soles"],
        [
            "Créditos para compensar el CO2 del período",
            _num(c["toneladas_periodo"], 4),
            _usd(c["valor_usd"]),
            _celda(c["valor_soles"]),
        ],
        [
            "Ahorro en créditos por CO2 evitado",
            _num(c["toneladas_evitadas"], 4),
            _usd(c["ahorro_usd"]),
            _celda(c["ahorro_soles"]),
        ],
    ]
    precio = (
        "Pendiente" if c["precio_usd_t"] is None else f"US$ {c['precio_usd_t']:,.2f} por t CO2e"
    )
    cambio = "Pendiente" if c["tipo_cambio"] is None else f"S/ {c['tipo_cambio']:,.3f} por US$"
    return [
        Paragraph("Créditos de carbono (RF-06)", estilos["Heading2"]),
        Paragraph(f"Precio del crédito: {precio}. Tipo de cambio: {cambio}.", estilos["BodyText"]),
        _tabla(filas, [7 * cm, 3.5 * cm, 3.5 * cm, 3.5 * cm]),
        Paragraph(
            c["nota"]
            or "Precio medio de créditos de forestación y reforestación (ARR), Ecosystem "
            "Marketplace, State of the Voluntary Carbon Market 2025 (US$ 20.44 por t CO2e). "
            "Tipo de cambio interbancario venta BCRP del 26/11/2026 (S/ 3.478). "
            "Valor referencial: no es una cotización ni una compra.",
            nota,
        ),
        Spacer(1, 0.3 * cm),
    ]


def _bloque_meta(datos: DatosReporte, estilos, nota) -> list:
    meta = datos.meta
    if meta is None:
        return []
    filas = [["Escenario", "kg/árbol/año", "Árboles al año", "Árboles por año (3 años)", "Costo"]]
    for esc in meta["escenarios"]:
        filas.append(
            [
                esc["nombre"],
                "Pendiente"
                if esc["factor_kg_arbol_anio"] is None
                else _num(esc["factor_kg_arbol_anio"], 0),
                "Pendiente" if esc["arboles_anuales"] is None else f"{esc['arboles_anuales']:,}",
                "Pendiente" if esc["arboles_por_anio"] is None else f"{esc['arboles_por_anio']:,}",
                _celda(esc["costo_total_soles"]),
            ]
        )
    historia = [
        Paragraph("Meta de cero emisiones netas a 3 años (RES-02, RF-10)", estilos["Heading2"]),
        Paragraph(
            f"CO2 anual proyectado: {_num(meta['co2_anual_kg'], 1)} kg (CO2 del período "
            f"{_num(meta['co2_periodo_kg'], 3)} kg × 365 / {meta['dias_calendario']} días). "
            + meta["aviso"],
            estilos["BodyText"],
        ),
        _tabla(filas, [4.6 * cm, 2.4 * cm, 2.9 * cm, 4 * cm, 3.6 * cm]),
        Spacer(1, 0.15 * cm),
    ]
    principal = next((e for e in meta["escenarios"] if e["plan"]), None)
    if principal is not None:
        plan = [["Año", "Árboles a plantar", "Acumulados", "Cobertura del CO2 anual", "Costo"]]
        for fila in principal["plan"]:
            plan.append(
                [
                    f"Año {fila['anio']}",
                    f"{fila['arboles_a_plantar']:,}",
                    f"{fila['arboles_acumulados']:,}",
                    f"{fila['cobertura_pct']:.1f} %",
                    _celda(fila["costo_soles"]),
                ]
            )
        historia += [
            Paragraph(f"Plan de plantación, escenario {principal['nombre']}", estilos["BodyText"]),
            _tabla(plan, [3 * cm, 3.6 * cm, 3 * cm, 4.6 * cm, 3.3 * cm]),
        ]
    avance = meta["avance"]
    pct = "Pendiente" if avance["avance_pct"] is None else f"{avance['avance_pct']:.1f} %"
    historia += [
        Spacer(1, 0.15 * cm),
        Paragraph(
            f"Avance hacia la meta: {avance['arboles_registrados']:,} árboles plantados "
            f"registrados, {pct} del CO2 anual proyectado. " + (avance["nota"] or ""),
            estilos["BodyText"],
        ),
        Paragraph(
            "Árboles = CO2 anual / factor de captura, redondeado hacia arriba. EPA: 60 kg por "
            "árbol urbano al año (promedio de 10 años). Pesimista: 15 kg, tesis UPN 2024 "
            "(Los Olivos, i-Tree Eco), que no aclara si es C o CO2. El costo por árbol es de "
            "SERPAR (S/ 94, 2021). Supone que las emisiones anuales no cambian y que cada "
            "árbol captura el factor desde el año en que se planta.",
            nota,
        ),
        Spacer(1, 0.3 * cm),
    ]
    return historia


def _bloque_gnv(datos: DatosReporte, estilos, nota) -> list:
    g = datos.gnv
    if g is None:
        return []
    historia = [
        Paragraph("Conversión de la flota a GNV (RES-01)", estilos["Heading2"]),
        Paragraph(
            f"Vehículos con ruta en el período: {g['vehiculos']}. Inversión: "
            f"{_celda(g['inversion_soles'])} (S/ 5,000 por vehículo, consigna). Diésel anual "
            f"proyectado: {_celda(g['costo_diesel_anual_soles'])}. " + g["aviso_proyeccion"],
            estilos["BodyText"],
        ),
    ]
    if g["escenarios"]:
        filas = [
            [
                "Escenario",
                "Precio GNV",
                "Ahorro anual",
                "Recuperación",
                "ROI a 3 años",
                "CO2 evitado/año",
            ]
        ]
        evitado = (
            "Pendiente"
            if g["co2_evitado_anual_kg"] is None
            else f"{_num(g['co2_evitado_anual_kg'], 1)} kg"
        )
        for esc in g["escenarios"]:
            if g["inversion_soles"] is None or esc["ahorro_anual_soles"] is None:
                recup = "Pendiente"
            elif g["inversion_soles"] == 0:
                recup = "Sin inversión"
            elif esc["recuperacion_meses"] is None:
                recup = "No se recupera"
            else:
                recup = f"{_num(esc['recuperacion_meses'], 1)} meses"
            roi = (
                "Pendiente" if esc["roi_3_anios_pct"] is None else f"{esc['roi_3_anios_pct']:.1f} %"
            )
            filas.append(
                [
                    esc["nombre"],
                    "Pendiente"
                    if esc["precio_gnv_m3"] is None
                    else f"S/ {_num(esc['precio_gnv_m3'], 2)}/m3",
                    _celda(esc["ahorro_anual_soles"]),
                    recup,
                    roi,
                    evitado,
                ]
            )
        historia.append(_tabla(filas, [4.6 * cm, 2.2 * cm, 2.9 * cm, 2.7 * cm, 2.3 * cm, 2.8 * cm]))
    for texto in g["notas"]:
        historia.append(Paragraph(texto, nota))
    historia += [
        Paragraph(
            "Método: 1 galón de diésel = 0.138 mmBtu y 1 m3 de GNV = 0.001026 mmBtu/scf × "
            "35.3147 scf/m3 (US EPA, GHG Emission Factors Hub 2025, poder calorífico "
            "superior), es decir "
            + (
                "pendiente"
                if g["equivalencia_m3_por_galon"] is None
                else f"{g['equivalencia_m3_por_galon']:.3f} m3 de GNV por galón"
            )
            + ". CO2 del GNV = CO2 del diésel × 53.06 / 73.96 (kg CO2/mmBtu, EPA, factores de "
            "EE. UU.). Supone el mismo rendimiento del motor con diésel y con GNV; no incluye "
            "mantenimiento ni otros costos de la conversión. Precio de mercado: promedio de "
            "Lima, Osinergmin Facilito vía El Comercio, 21/11/2026.",
            nota,
        ),
        Spacer(1, 0.3 * cm),
    ]
    return historia


def generar_pdf(datos: DatosReporte, generado_en: datetime | None = None) -> bytes:
    momento = (generado_en or datetime.now(UTC)).astimezone(LIMA)
    estilos = getSampleStyleSheet()
    nota = ParagraphStyle("nota", parent=estilos["BodyText"], fontSize=8.5, leading=11)
    buffer = io.BytesIO()
    titulo = f"Reporte de sostenibilidad {datos.desde.isoformat()} a {datos.hasta.isoformat()}"
    documento = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=1.6 * cm,
        rightMargin=1.6 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        title=titulo,
        author="EcoLogística Lima",
        subject="Impacto ambiental y económico del período (RF-006)",
        lang="es-PE",
    )
    co2_ahorrado = datos.total("co2_ahorrado_kg")
    if datos.factor_arboles is None:
        arboles = NOTA_ARBOLES_PDF
    elif datos.arboles is None:
        arboles = "sin CO2 evitado en el período, no hay equivalente que mostrar."
    else:
        arboles = f"{_num(datos.arboles)} árboles (factor RN-018 de la configuración)"
    resumen = [
        ["Indicador", "Valor"],
        ["Días con operación", str(len(datos.dias))],
        ["Rutas", str(len(datos.rutas))],
        ["Distancia total", f"{_num(datos.total('km'))} km"],
        ["Combustible estimado", f"{_num(datos.total('combustible_l'))} L"],
        ["Emisiones de CO2 (RN-016)", f"{_num(datos.total('co2_kg'), 3)} kg"],
        ["Costo de combustible (RN-017)", _soles(datos.total("soles_combustible"))],
        ["Costo de mantenimiento (RN-017)", _soles(datos.total("soles_mantenimiento"))],
        ["Costo local total", _soles(datos.costo_local)],
        ["Ahorro frente al vecino más cercano", _soles(datos.total("soles_ahorrados"))],
        ["CO2 evitado frente al vecino más cercano", f"{_num(co2_ahorrado, 3)} kg"],
        ["Cumplimiento de ventanas horarias", f"{_num(datos.cumplimiento_pct, 1)} %"],
    ]
    por_dia = [["Fecha", "Rutas", "km", "CO2 kg", "Costo local", "Ahorro", "Ventanas", "Mejora"]]
    for dia in datos.dias:
        mejora = dia["mejora_porcentaje"]
        por_dia.append(
            [
                dia["fecha"].isoformat(),
                str(dia["rutas"]),
                _num(dia["km"]),
                _num(dia["co2_kg"], 3),
                _soles(dia["soles_combustible"] + dia["soles_mantenimiento"]),
                _soles(dia["soles_ahorrados"]),
                f"{_num(dia['cumplimiento_ventanas_pct'], 1)} %",
                "Sin comparación" if mejora is None else f"{_num(mejora)} %",
            ]
        )
    por_ruta = [["Fecha", "Placa", "Estado", "km", "L", "CO2 kg", "Combustible", "Mant."]]
    for fila in datos.rutas:
        por_ruta.append(
            [
                fila.fecha.isoformat(),
                fila.placa,
                ESTADOS.get(fila.estado, fila.estado),
                _num(fila.km),
                _num(fila.litros),
                _num(fila.co2_kg, 3),
                _soles(fila.soles_combustible),
                _soles(fila.soles_mantenimiento),
            ]
        )
    historia = [
        Paragraph("EcoLogística Lima · Reporte de sostenibilidad", estilos["Title"]),
        Paragraph(
            f"Período: {datos.desde.isoformat()} a {datos.hasta.isoformat()}. "
            f"Generado el {momento:%Y-%m-%d %H:%M} (hora de Lima).",
            estilos["BodyText"],
        ),
        Paragraph(
            f"Costos locales usados: diésel S/ {datos.precio_galon:.2f} por galón y "
            f"mantenimiento S/ {datos.costo_km:.2f} por km (configuración del sistema).",
            estilos["BodyText"],
        ),
        Spacer(1, 0.3 * cm),
        Paragraph("Resumen del período", estilos["Heading2"]),
        _tabla(resumen, [10 * cm, 7.5 * cm]),
        Paragraph(f"Equivalente en árboles: {arboles}", nota),
        Spacer(1, 0.3 * cm),
        Paragraph("Detalle por día", estilos["Heading2"]),
        _tabla(por_dia, ANCHOS_DIA),
        Spacer(1, 0.3 * cm),
        Paragraph("Emisiones por ruta", estilos["Heading2"]),
        _tabla(por_ruta, ANCHOS_RUTA),
        Spacer(1, 0.3 * cm),
        *_bloque_ciclo(datos, estilos, nota),
        *_bloque_creditos(datos, estilos, nota),
        *_bloque_meta(datos, estilos, nota),
        *_bloque_gnv(datos, estilos, nota),
        Paragraph(
            "Método: las emisiones de cada ruta son la distancia planificada por el factor de "
            "emisión del vehículo (RN-016, ISO 14083). El ahorro y el CO2 evitado comparan el "
            "algoritmo con el vecino más cercano del mismo trabajo de optimización. Las cifras "
            "son las mismas del tablero de sostenibilidad.",
            nota,
        ),
    ]
    documento.build(historia)
    return buffer.getvalue()


def nombre_archivo(desde: date, hasta: date) -> str:
    return f"reporte-sostenibilidad-{desde.isoformat()}_{hasta.isoformat()}.pdf"


def reporte(db: Session, desde: date, hasta: date, actor: Usuario, ip: str | None) -> bytes:
    datos = recopilar(db, desde, hasta)
    if not datos.dias:
        raise HTTPException(status.HTTP_404_NOT_FOUND, indicadores.MENSAJE_VACIO)
    contenido = generar_pdf(datos)
    # Se registra quién y qué período; el archivo no se guarda (ruta_archivo vacía).
    registro = Reporte(
        periodo_inicio=desde, periodo_fin=hasta, tipo=TIPO_REPORTE, generado_por=actor.id_usuario
    )
    db.add(registro)
    db.flush()
    auditoria.registrar(
        db,
        id_usuario=actor.id_usuario,
        accion="reporte_pdf",
        tabla="reporte",
        registro_id=registro.id_reporte,
        ip=ip,
        nuevos={
            "desde": desde.isoformat(),
            "hasta": hasta.isoformat(),
            "rutas": len(datos.rutas),
            "bytes": len(contenido),
        },
    )
    db.commit()
    return contenido
