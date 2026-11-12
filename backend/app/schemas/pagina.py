from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Pagina(BaseModel, Generic[T]):
    """Bloque de un listado. El tamaño de página operativo es 12."""

    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int
