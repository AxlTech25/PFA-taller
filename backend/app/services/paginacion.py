"""Paginación de listados. El cliente pide bloques de 12 filas, no la tabla completa."""

import math

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

TAMANO_PAGINA = 12
LIMITE_MAXIMO = 50


def normalizar(page: int, limite: int) -> tuple[int, int]:
    pagina = page if page >= 1 else 1
    if 1 <= limite <= LIMITE_MAXIMO:
        return pagina, limite
    return pagina, TAMANO_PAGINA


def _total(db: Session, consulta: Select) -> int:
    origen = consulta.order_by(None).subquery()
    return int(db.scalar(select(func.count()).select_from(origen)) or 0)


def _meta(total: int, pagina: int, tamano: int) -> dict:
    paginas = math.ceil(total / tamano) if total else 0
    return {
        "total": total,
        "page": pagina,
        "page_size": tamano,
        "total_pages": paginas,
    }


def paginar_entidades(db: Session, consulta: Select, page: int, limite: int) -> dict:
    pagina, tamano = normalizar(page, limite)
    total = _total(db, consulta)
    filas = list(db.scalars(consulta.offset((pagina - 1) * tamano).limit(tamano)).all())
    return {"items": filas, **_meta(total, pagina, tamano)}


def paginar_filas(db: Session, consulta: Select, page: int, limite: int) -> tuple[list, dict]:
    pagina, tamano = normalizar(page, limite)
    total = _total(db, consulta)
    filas = list(db.execute(consulta.offset((pagina - 1) * tamano).limit(tamano)).all())
    return filas, _meta(total, pagina, tamano)
