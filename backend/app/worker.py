"""Proceso independiente del motor (ENB-006). No forma parte del request de FastAPI.

Arranque: ``python -m app.worker``
"""

import time
import uuid
from datetime import UTC, datetime

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import SessionLocal, engine
from app.models.entities import JobOptimizacion
from app.optimizacion.cola import ColaNoDisponible, tomar
from app.optimizacion.heuristica import generar_plan
from app.optimizacion.persistencia import persistir_plan
from app.seed import wait_for_db

MENSAJE_FALLO = "No se pudo calcular la ruta. Se conserva el estado anterior."


def procesar_job(db: Session, id_job: uuid.UUID) -> None:
    job = db.get(JobOptimizacion, id_job)
    if job is None or job.estado not in {"ENCOLADO", "EN_PROCESO"}:
        return
    job.estado = "EN_PROCESO"
    job.actualizado_en = datetime.now(UTC)
    db.commit()
    try:
        plan = generar_plan(db, job.fecha)
        if plan.factible:
            identificadores = persistir_plan(db, job, plan)
            job.estado = "COMPLETADO"
            job.resultado = {
                "id_rutas": identificadores,
                "pedidos_sin_asignar": [str(item) for item in plan.sin_asignar],
            }
        else:
            job.estado = "FALLIDO"
            job.resultado = {
                "id_rutas": [],
                "pedidos_sin_asignar": [str(item) for item in plan.sin_asignar],
            }
        job.mensaje = plan.mensaje
        job.actualizado_en = datetime.now(UTC)
        db.commit()
    except Exception:
        db.rollback()
        job = db.get(JobOptimizacion, id_job)
        if job is None:
            return
        job.estado = "FALLIDO"
        job.mensaje = MENSAJE_FALLO
        job.actualizado_en = datetime.now(UTC)
        db.commit()


def iteracion(db: Session) -> bool:
    try:
        identificador = tomar(timeout=1)
    except ColaNoDisponible:
        return False
    if not identificador:
        return False
    procesar_job(db, uuid.UUID(identificador))
    return True


def _esperar_esquema() -> None:
    wait_for_db()
    for _ in range(60):
        try:
            with engine.connect() as conexion:
                conexion.execute(text("SELECT 1 FROM job_optimizacion LIMIT 0"))
            return
        except Exception:
            time.sleep(1)
    raise SystemExit("El esquema de optimización no está listo. Ejecute las migraciones.")


def main() -> None:
    _esperar_esquema()
    while True:
        with SessionLocal() as db:
            try:
                trabajo = iteracion(db)
            except Exception:
                time.sleep(2)
                continue
        if not trabajo:
            time.sleep(1)


if __name__ == "__main__":
    main()
