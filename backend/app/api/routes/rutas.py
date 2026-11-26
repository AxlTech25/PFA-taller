from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.deps import (
    ESCRITURA_RUTAS,
    LECTURA_RUTAS,
    REOPTIMIZACION_RUTAS,
    ip_de,
    require_roles,
)
from app.db.session import get_db
from app.models.entities import Usuario
from app.schemas.pagina import Pagina
from app.schemas.ruta import (
    PedidoDisponibleOut,
    ReoptimizacionIn,
    ReoptimizacionOut,
    RutaOut,
)
from app.services import reoptimizacion as reoptimizacion
from app.services import rutas as servicio

router = APIRouter(prefix="/rutas", tags=["Optimización"])


@router.get("", response_model=Pagina[RutaOut], summary="Listar rutas generadas")
def listar(
    db: Annotated[Session, Depends(get_db)],
    actor: Annotated[Usuario, Depends(require_roles(*LECTURA_RUTAS))],
    fecha: Annotated[date | None, Query()] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    limite: Annotated[int, Query(ge=1, le=50)] = 12,
) -> dict:
    return servicio.listar_rutas(db, actor, fecha, page, limite)


@router.post(
    "/{id_ruta}/alternativa-segura",
    response_model=RutaOut,
    summary="Ruta alternativa más segura",
    description=(
        "Recalcula el trazado del borrador para rodear las zonas de riesgo (RN-012) "
        "sin atravesar reservas ecológicas (RN-013). "
        "El resultado es un desvío geométrico, no un recorrido callejero ni un límite oficial."
    ),
)
def alternativa(
    id_ruta: UUID,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    actor: Annotated[Usuario, Depends(require_roles(*ESCRITURA_RUTAS))],
) -> dict:
    return servicio.alternativa(db, id_ruta, actor, ip_de(request))


@router.post(
    "/{id_ruta}/confirmar",
    response_model=RutaOut,
    summary="Confirmar una ruta en borrador",
    description=(
        "Rechaza la ruta si el trazado atraviesa una reserva ecológica (RN-013). "
        "Rechaza la asignación si la conducción del conductor en el día supera 8 horas "
        "(Ley N.º 30224). Si hay 4 horas continuas sin descanso, inserta 1 hora."
    ),
)
def confirmar(
    id_ruta: UUID,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    actor: Annotated[Usuario, Depends(require_roles(*ESCRITURA_RUTAS))],
) -> dict:
    return servicio.confirmar(db, id_ruta, actor, ip_de(request))


@router.post(
    "/{id_ruta}/reoptimizar",
    response_model=ReoptimizacionOut,
    summary="Re-optimizar las paradas pendientes de una ruta activa",
    description=(
        "US-011 (RF-007, RN-014, RN-015). Recalcula solo esta ruta CONFIRMADA o EN_EJECUCION "
        "ante un pedido nuevo, una cancelación, una parada fallida, un accidente o vía "
        "bloqueada, o congestión. Las paradas ENTREGADO o FALLIDO se conservan. La reserva "
        "ecológica es restricción dura (RN-013) y la zona de riesgo se penaliza (RN-012). "
        "El cálculo usa `tiempo_max_reoptimizacion_s`, con tope de 30 s; al llegar al tope "
        "devuelve la mejor secuencia completa hallada. Sin solución, conserva la ruta, "
        "registra el evento como SIN_SOLUCION y responde 422."
    ),
    responses={
        403: {"description": "Solo ADMIN, GERENTE u OPERADOR"},
        404: {"description": "La ruta no existe"},
        409: {"description": "La ruta no está activa o no quedan paradas pendientes"},
        422: {"description": "Datos inválidos o sin solución factible dentro del tope"},
    },
)
def reoptimizar(
    id_ruta: UUID,
    datos: ReoptimizacionIn,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    actor: Annotated[Usuario, Depends(require_roles(*REOPTIMIZACION_RUTAS))],
) -> dict:
    return reoptimizacion.reoptimizar_ruta(db, id_ruta, datos, actor, ip_de(request))


@router.get(
    "/{id_ruta}/pedidos-disponibles",
    response_model=list[PedidoDisponibleOut],
    summary="Pedidos pendientes que pueden sumarse a la ruta",
    description="Pedidos PENDIENTE de la fecha de la ruta que no están en otra ruta (máx. 50).",
)
def disponibles(
    id_ruta: UUID,
    db: Annotated[Session, Depends(get_db)],
    _actor: Annotated[Usuario, Depends(require_roles(*REOPTIMIZACION_RUTAS))],
) -> list[dict]:
    return reoptimizacion.pedidos_disponibles(db, id_ruta)
