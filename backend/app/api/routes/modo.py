from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.deps import ip_de, require_roles
from app.db.session import get_db
from app.models.entities import Usuario
from app.schemas.modo import (
    ConfirmacionEntregaIn,
    ConfirmacionEntregaOut,
    JornadaModo,
    MapaModo,
)
from app.services import modo as servicio

router = APIRouter(prefix="/modo", tags=["Modo conductor"])

_DESCRIPCION = (
    "Jornada del conductor autenticado (US-015). Devuelve solo la ruta CONFIRMADA "
    "o EN_EJECUCION asignada a su ficha en el día civil de Lima (UTC−5, sin horario "
    "de verano): secuencia, hora estimada y alertas. No incluye el tablero de gerencia "
    "ni coordenadas. Un conductor no puede consultar la ruta de otro: no se acepta "
    "un identificador ajeno. Cada parada trae id_detalle para la acción de confirmar "
    "(POST /modo/paradas/{id_detalle}/confirmacion, US-018). Este endpoint no escribe."
)


@router.get(
    "/jornada",
    response_model=JornadaModo,
    summary="Ruta confirmada del conductor",
    description=_DESCRIPCION,
)
def consultar_jornada(
    db: Annotated[Session, Depends(get_db)],
    actor: Annotated[Usuario, Depends(require_roles("CONDUCTOR"))],
) -> dict:
    return servicio.jornada(db, actor)


@router.get(
    "/mapa",
    response_model=MapaModo,
    summary="Puntos opcionales del mapa del conductor",
    description=(
        "Coordenadas de la misma ruta que GET /modo/jornada. No forma parte de la "
        "consulta inicial: el modo conductor pide este recurso solo si la persona "
        "abre el mapa. Misma autorización: solo el conductor y solo su ficha."
    ),
)
def consultar_mapa(
    db: Annotated[Session, Depends(get_db)],
    actor: Annotated[Usuario, Depends(require_roles("CONDUCTOR"))],
) -> dict:
    return servicio.mapa(db, actor)


@router.post(
    "/paradas/{id_detalle}/confirmacion",
    response_model=ConfirmacionEntregaOut,
    summary="Confirmar una parada como entregada o fallida",
    description=(
        "US-018. El conductor autenticado registra ENTREGADO o FALLIDO en una parada "
        "de su ruta CONFIRMADA o EN_EJECUCION. FALLIDO exige motivo. Guarda quién y "
        "cuándo confirmó, y lo deja en el log de auditoría. La primera confirmación "
        "pasa la ruta a EN_EJECUCION."
    ),
    responses={
        403: {"description": "Rol distinto de CONDUCTOR o parada de otro conductor"},
        404: {"description": "La parada no existe"},
        409: {"description": "La parada ya tiene resultado o la ruta no está activa"},
        422: {"description": "Resultado inválido o FALLIDO sin motivo"},
    },
)
def confirmar_parada(
    id_detalle: UUID,
    datos: ConfirmacionEntregaIn,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    actor: Annotated[Usuario, Depends(require_roles("CONDUCTOR"))],
) -> dict:
    return servicio.confirmar_parada(
        db, actor, id_detalle, datos.resultado, datos.motivo, ip_de(request)
    )
