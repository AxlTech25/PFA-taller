"""Carga inicial de usuarios de demostración.

Las contraseñas salen de variables de entorno. Si están vacías, ese usuario
no se crea. Los vehículos de demostración los inserta la migración Alembic.
"""

import logging
import time

from sqlalchemy import select, text

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import SessionLocal, engine
from app.models.entities import Usuario

logger = logging.getLogger("ecologistica.seed")


def wait_for_db(intentos: int = 30) -> None:
    ultimo_error: Exception | None = None
    for _ in range(intentos):
        try:
            with engine.connect() as conexion:
                conexion.execute(text("SELECT 1"))
            return
        except Exception as exc:  # noqa: BLE001
            ultimo_error = exc
            time.sleep(1)
    raise RuntimeError("No se pudo conectar a la base de datos") from ultimo_error


def _asegurar_usuario(db, email: str, password: str, rol: str) -> None:
    if not password:
        logger.warning("Contraseña vacía: no se creó el usuario %s", email)
        return
    if len(password) < 8:
        logger.warning("Contraseña demasiado corta: no se creó el usuario %s", email)
        return
    existente = db.scalar(select(Usuario).where(Usuario.email == email.lower()))
    if existente is not None:
        return
    db.add(
        Usuario(
            email=email.lower(),
            password_hash=hash_password(password),
            rol=rol,
            estado="ACTIVO",
            intentos_fallidos=0,
        )
    )
    logger.info("Usuario de demostración creado: %s (%s)", email, rol)


def cargar() -> None:
    if not settings.seed_on_startup:
        logger.info("SEED_ON_STARTUP desactivado: no hay carga inicial")
        return
    with SessionLocal() as db:
        _asegurar_usuario(db, settings.seed_admin_email, settings.seed_admin_password, "ADMIN")
        _asegurar_usuario(
            db, settings.seed_operador_email, settings.seed_operador_password, "OPERADOR"
        )
        _asegurar_usuario(
            db, settings.seed_gerente_email, settings.seed_gerente_password, "GERENTE"
        )
        db.commit()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    cargar()


if __name__ == "__main__":
    main()
