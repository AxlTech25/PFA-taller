from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy.orm import Session

from app.core.deps import (
    LECTURA_RUTAS,
    PLAN_COMPENSACION,
    REPORTES_SOSTENIBILIDAD,
    ip_de,
    require_roles,
)
from app.db.session import get_db
from app.models.entities import Usuario
from app.schemas.ruta import IndicadoresOut, PlanCompensacionOut
from app.services import compensacion, reporte_pdf
from app.services import indicadores as servicio

router = APIRouter(prefix="/indicadores", tags=["Sostenibilidad"])


@router.get(
    "",
    response_model=IndicadoresOut,
    summary="Indicadores del día (tablero iniciado)",
    description=(
        "Inicio del dashboard del Hito 3. Resume km, CO₂, combustible, soles y "
        "cumplimiento de ventanas del último plan del día. US-014 se cierra en el Sprint 5. "
        "El equivalente en árboles espera el factor RN-018."
    ),
)
def consultar(
    db: Annotated[Session, Depends(get_db)],
    _actor: Annotated[Usuario, Depends(require_roles(*LECTURA_RUTAS))],
    fecha: Annotated[date, Query()],
) -> dict:
    return servicio.consultar(db, fecha)


@router.get(
    "/reporte.pdf",
    summary="Reporte PDF de sostenibilidad del período (US-016)",
    description=(
        "RF-006. PDF con emisiones por ruta (RN-016), combustible, costos locales (RN-017), "
        "ahorro frente al vecino más cercano y cumplimiento de ventanas, con las mismas cifras "
        "del tablero. Período de hasta 31 días. Sin rutas en el período responde 404 y no genera "
        "archivo. El equivalente en árboles (RN-018) queda pendiente mientras el factor no esté "
        "ratificado."
    ),
    response_class=Response,
    responses={
        200: {"content": {"application/pdf": {}}, "description": "Reporte PDF"},
        403: {"description": "Solo ADMIN, GERENTE, OPERADOR o AUDITOR"},
        404: {"description": "Sin datos de operación para el período seleccionado"},
        422: {"description": "Período inválido o mayor a 31 días"},
    },
)
def reporte(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    actor: Annotated[Usuario, Depends(require_roles(*REPORTES_SOSTENIBILIDAD))],
    desde: Annotated[date, Query(description="Primer día del período (AAAA-MM-DD)")],
    hasta: Annotated[date, Query(description="Último día del período (AAAA-MM-DD)")],
) -> Response:
    contenido = reporte_pdf.reporte(db, desde, hasta, actor, ip_de(request))
    return Response(
        content=contenido,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{reporte_pdf.nombre_archivo(desde, hasta)}"'
            ),
            "Cache-Control": "no-store",
        },
    )


@router.get(
    "/compensacion",
    response_model=PlanCompensacionOut,
    summary="Plan de compensación de carbono del período (US-017)",
    description=(
        "RF-010. Suma el CO₂ emitido del período con el mismo cálculo del tablero (RN-016), "
        "estima los árboles necesarios con el factor RN-018 y el costo con "
        "`costo_compensacion_arbol_soles`, y sugiere Lomas de Lima, Parque Zonal Huáscar y "
        "«Árboles para Lima». Si un factor no está configurado se devuelve PENDIENTE, sin "
        "cifras inventadas. Sin emisiones: `calculable=false` con el aviso. Hasta 31 días."
    ),
    responses={
        403: {"description": "Solo ADMIN, GERENTE, OPERADOR o AUDITOR"},
        422: {"description": "Período inválido o mayor a 31 días"},
    },
)
def plan_compensacion(
    db: Annotated[Session, Depends(get_db)],
    _actor: Annotated[Usuario, Depends(require_roles(*PLAN_COMPENSACION))],
    desde: Annotated[date, Query(description="Primer día del período (AAAA-MM-DD)")],
    hasta: Annotated[date, Query(description="Último día del período (AAAA-MM-DD)")],
) -> dict:
    return compensacion.plan(db, desde, hasta)
