from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import LECTURA_CLIENTES, require_roles
from app.db.session import get_db
from app.models.entities import Usuario
from app.schemas.cliente import ClienteOut
from app.services import pedidos as servicio

router = APIRouter(prefix="/clientes", tags=["Pedidos"])


@router.get(
    "",
    response_model=list[ClienteOut],
    summary="Catálogo de demostración",
    description=(
        "Catálogo de demostración, sin altas. Lista los clientes sembrados para "
        "registrar pedidos (US-008). No existe un módulo de registro de clientes."
    ),
)
def listar(
    db: Session = Depends(get_db),
    actor: Usuario = Depends(require_roles(*LECTURA_CLIENTES)),
    limite: int = Query(default=100, ge=1, le=200),
) -> list:
    return servicio.listar_clientes(db, actor, limite)
