"""Cola Redis de trabajos de optimización (ENB-006).

La API solo encola. El proceso `python -m app.worker` consume la cola.
"""

from typing import NoReturn

import redis

from app.core.config import settings

NOMBRE_COLA = "ecologistica:optimizacion"
MENSAJE_COLA = (
    "La cola de optimización no está disponible. "
    "Intente nuevamente cuando Redis responda."
)


class ColaNoDisponible(Exception):
    pass


def obtener_cliente() -> redis.Redis:
    return redis.Redis.from_url(
        settings.redis_url,
        socket_connect_timeout=0.5,
        socket_timeout=2,
        decode_responses=True,
    )


def _traducir(exc: Exception) -> NoReturn:
    raise ColaNoDisponible(MENSAJE_COLA) from exc


def disponible() -> bool:
    try:
        return bool(obtener_cliente().ping())
    except (redis.RedisError, OSError):
        return False


def encolar(id_job: str) -> None:
    try:
        cliente = obtener_cliente()
        cliente.ping()
        cliente.lpush(NOMBRE_COLA, id_job)
    except (redis.RedisError, OSError) as exc:
        _traducir(exc)


def tomar(timeout: int = 5) -> str | None:
    try:
        fila = obtener_cliente().brpop(NOMBRE_COLA, timeout=timeout)
    except (redis.RedisError, OSError) as exc:
        _traducir(exc)
    if not fila:
        return None
    return str(fila[1])
