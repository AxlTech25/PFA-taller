"""Codificación Brotli o Gzip de cuerpos HTTP mayores a 1 KiB."""

import gzip

try:
    import brotli
except ImportError:  # pragma: no cover - el entorno de CI instala el paquete
    brotli = None

UMBRAL_BYTES = 1024


def negociar(accept_encoding: str) -> str | None:
    """Prefiere Brotli y, si el cliente no lo anuncia, usa Gzip."""

    pedidos = [parte.split(";", 1)[0].strip().lower() for parte in accept_encoding.split(",")]
    if "br" in pedidos and brotli is not None:
        return "br"
    if "gzip" in pedidos:
        return "gzip"
    return None


def codificar(cuerpo: bytes, accept_encoding: str) -> tuple[bytes, str | None]:
    if len(cuerpo) < UMBRAL_BYTES:
        return cuerpo, None
    algoritmo = negociar(accept_encoding)
    if algoritmo == "br" and brotli is not None:
        return brotli.compress(cuerpo, quality=5), "br"
    if algoritmo == "gzip":
        return gzip.compress(cuerpo, compresslevel=5), "gzip"
    return cuerpo, None
