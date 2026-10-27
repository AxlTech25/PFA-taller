from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db

router = APIRouter(tags=["Salud"])


@router.get(
    "/health",
    responses={503: {"description": "Base de datos no disponible"}},
)
def health(db: Annotated[Session, Depends(get_db)]) -> dict:
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Base de datos no disponible") from exc
    return {"status": "ok", "servicio": "ecologistica-api"}
