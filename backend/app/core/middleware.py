import hashlib

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.compresion import codificar

_SIN_CACHE = {"/health"}


class SecurityHeadersMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers["X-Content-Type-Options"] = "nosniff"
                headers["X-Frame-Options"] = "DENY"
                headers["Referrer-Policy"] = "no-referrer"
                headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
            await send(message)

        await self.app(scope, receive, send_wrapper)


def _etag(cuerpo: bytes) -> str:
    digest = hashlib.sha256(cuerpo).hexdigest()[:32]
    return f'W/"{digest}"'


def _coincide(if_none_match: str, etag: str) -> bool:
    if not if_none_match:
        return False
    for parte in if_none_match.split(","):
        candidato = parte.strip()
        if candidato == "*" or candidato == etag:
            return True
    return False


def _vary(headers: MutableHeaders) -> None:
    extra = "Accept-Encoding, Authorization"
    previo = headers.get("vary")
    headers["Vary"] = f"{previo}, {extra}" if previo else extra


class RespuestaEficienteMiddleware:
    """ETag, Cache-Control y compresión de las respuestas HTTP de la API."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        inicio: Message | None = None
        cuerpo = bytearray()
        enviado = False

        async def capturar(message: Message) -> None:
            nonlocal inicio, enviado
            if message["type"] == "http.response.start":
                inicio = message
                return
            if message["type"] != "http.response.body":
                await send(message)
                return
            cuerpo.extend(message.get("body", b""))
            if message.get("more_body", False):
                return
            enviado = True
            await _emitir(scope, inicio, bytes(cuerpo), send)

        await self.app(scope, receive, capturar)
        if inicio is not None and not enviado:
            await _emitir(scope, inicio, bytes(cuerpo), send)


async def _emitir(scope: Scope, inicio: Message | None, cuerpo: bytes, send: Send) -> None:
    if inicio is None:
        return
    headers = MutableHeaders(scope=inicio)
    metodo = scope.get("method", "GET")
    ruta = scope.get("path", "")
    peticion = MutableHeaders(scope=scope)
    if metodo == "GET" and ruta not in _SIN_CACHE and int(inicio["status"]) == 200:
        etag = _etag(cuerpo)
        headers["ETag"] = etag
        headers["Cache-Control"] = "private, max-age=30, must-revalidate"
        _vary(headers)
        if _coincide(peticion.get("if-none-match", ""), etag):
            inicio["status"] = 304
            headers["Content-Length"] = "0"
            if "content-encoding" in headers:
                del headers["content-encoding"]
            await send(inicio)
            await send({"type": "http.response.body", "body": b""})
            return
    elif metodo == "GET" and ruta in _SIN_CACHE:
        headers["Cache-Control"] = "no-store"

    acepta = peticion.get("accept-encoding", "")
    comprimido, algoritmo = codificar(cuerpo, acepta)
    if algoritmo:
        headers["Content-Encoding"] = algoritmo
        _vary(headers)
    headers["Content-Length"] = str(len(comprimido))
    await send(inicio)
    await send({"type": "http.response.body", "body": comprimido})
