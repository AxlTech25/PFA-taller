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
from app.services import auditoria, indicadores

MAX_DIAS = 31
TIPO_REPORTE = "SOSTENIBILIDAD_PDF"
LIMA = ZoneInfo("America/Lima")
MENSAJE_RANGO = "La fecha final no puede ser anterior a la inicial."
MENSAJE_LARGO = f"El período del reporte no puede superar {MAX_DIAS} días."
NOTA_ARBOLES_PDF = (
    "Pendiente: el factor de captura por árbol (RN-018) no está ratificado en la "
    "configuración. El reporte no muestra un equivalente inventado."
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

    def total(self, clave: str) -> float:
        return sum(float(dia[clave]) for dia in self.dias)

    @property
    def costo_local(self) -> float:
        return self.total("soles_combustible") + self.total("soles_mantenimiento")


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
    return datos


def _soles(valor: float) -> str:
    return f"S/ {valor:,.2f}"


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
