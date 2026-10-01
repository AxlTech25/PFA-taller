from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.core.deps import ESCRITURA_PEDIDOS, LECTURA_PEDIDOS, ip_de, require_roles
from app.db.session import get_db
from app.models.entities import Usuario
from app.schemas.pedido import PedidoCreado, PedidoCreate, PedidoOut
from app.services import pedidos as servicio

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


@router.get("", response_model=list[PedidoOut])
def listar(
    db: Session = Depends(get_db),
    actor: Usuario = Depends(require_roles(*LECTURA_PEDIDOS)),
    limite: int = Query(default=100, ge=1, le=200),
) -> list:
    return servicio.listar_pedidos(db, actor, limite)


@router.post("", response_model=PedidoCreado, status_code=status.HTTP_201_CREATED)
def crear(
    datos: PedidoCreate,
    request: Request,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(require_roles(*ESCRITURA_PEDIDOS)),
) -> dict:
    pedido = servicio.crear_pedido(db, datos, actor, ip_de(request))
    cuerpo = servicio.salida_pedido(db, pedido, actor.rol)
    cuerpo["mensaje"] = "Pedido registrado correctamente"
    return cuerpo
