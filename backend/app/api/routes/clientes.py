import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.deps import (
    ESCRITURA_PREFERENCIAS,
    LECTURA_CLIENTES,
    LECTURA_PREFERENCIAS,
    ip_de,
    require_roles,
)
from app.db.session import get_db
from app.models.entities import Usuario
from app.schemas.cliente import ClienteOut, PreferenciaIn, PreferenciaOut
from app.schemas.pagina import Pagina
from app.services import pedidos as servicio
from app.services import preferencias

router = APIRouter(prefix="/clientes", tags=["Pedidos"])

_ERRORES = {
    401: {"description": "No autenticado"},
    403: {"description": "Rol sin acceso a preferencias de cliente (RF-009)"},
    404: {"description": "Cliente no encontrado"},
}


@router.get(
    "",
    response_model=Pagina[ClienteOut],
    summary="Catálogo de demostración",
    description=(
        "Catálogo de demostración, sin altas. Lista los clientes sembrados para "
        "registrar pedidos (US-008). No existe un módulo de registro de clientes."
    ),
)
def listar(
    db: Annotated[Session, Depends(get_db)],
    actor: Annotated[Usuario, Depends(require_roles(*LECTURA_CLIENTES))],
    page: Annotated[int, Query(ge=1)] = 1,
    limite: Annotated[int, Query(ge=1, le=50)] = 12,
) -> dict:
    return servicio.listar_clientes(db, actor, page, limite)


@router.get(
    "/{id_cliente}/preferencia",
    response_model=PreferenciaOut,
    summary="Preferencias de entrega del cliente (US-009)",
    description=(
        "Ficha de preferencias del cliente: horario preferido, punto de referencia y "
        "restricción de acceso (RF-009). Admin, Gerente y Operador."
    ),
    responses=_ERRORES,
)
def consultar_preferencia(
    id_cliente: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    _actor: Annotated[Usuario, Depends(require_roles(*LECTURA_PREFERENCIAS))],
) -> dict:
    return preferencias.consultar(db, id_cliente)


@router.put(
    "/{id_cliente}/preferencia",
    response_model=PreferenciaOut,
    summary="Registrar o actualizar preferencias de entrega (US-009)",
    description=(
        "Guarda la ficha del cliente (una por cliente). Rechaza hora_inicio ≥ hora_fin y "
        "clientes sin consentimiento (RN-020). El horario entra al motor como restricción "
        "suave. Admin y Operador."
    ),
    responses={**_ERRORES, 422: {"description": "Horario contradictorio o sin consentimiento"}},
)
def guardar_preferencia(
    id_cliente: uuid.UUID,
    datos: PreferenciaIn,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    actor: Annotated[Usuario, Depends(require_roles(*ESCRITURA_PREFERENCIAS))],
) -> dict:
    return preferencias.guardar(db, id_cliente, datos, actor, ip_de(request))
