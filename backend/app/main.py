from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import auth, clientes, conductores, health, pedidos, usuarios, vehiculos
from app.core.config import settings
from app.core.errores import traducir_validacion
from app.core.middleware import SecurityHeadersMiddleware

app = FastAPI(
    title="EcoLogística Lima",
    version="1.0.0-MVP",
    description=(
        "API del Sprint 2: usuarios y roles, bloqueo de cuenta, flota, "
        "conductores y alta de pedidos sobre PostgreSQL + PostGIS."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityHeadersMiddleware)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(vehiculos.router)
app.include_router(conductores.router)
app.include_router(clientes.router)
app.include_router(pedidos.router)


@app.exception_handler(RequestValidationError)
async def errores_de_validacion(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": traducir_validacion(exc)})


@app.get("/", tags=["Salud"])
def raiz() -> dict:
    return {
        "nombre": "EcoLogística Lima",
        "version": "1.0.0-MVP",
        "docs": "/docs",
    }
