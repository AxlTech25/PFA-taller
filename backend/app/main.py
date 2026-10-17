from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import (
    auth,
    clientes,
    conductores,
    health,
    optimizaciones,
    pedidos,
    rutas,
    usuarios,
    vehiculos,
)
from app.core.config import settings
from app.core.errores import traducir_validacion
from app.core.middleware import SecurityHeadersMiddleware

app = FastAPI(
    title="EcoLogística Lima",
    version="1.0.0-MVP",
    description=(
        "API del Sprint 3: cobertura de Lima Este, jornada de 8 horas, "
        "worker de optimización y heurística de rutas sobre PostgreSQL + PostGIS."
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
app.include_router(optimizaciones.router)
app.include_router(rutas.router)


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
