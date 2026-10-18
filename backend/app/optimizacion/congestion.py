"""Semáforo de congestión para el mapa (inicio de US-012).

El factor sale de `configuracion_sistema.factor_congestion` (Sprint 3).
La hora punta de Lima, 07:00–09:00 y 17:00–20:00, sube un nivel. El reloj
es el mismo que usa el motor (marca UTC de la ventana, sin convertir a
America/Lima): así el semáforo coincide con el ETA guardado.
"""

from datetime import datetime


def nivel_congestion(factor: float, eta: datetime | None) -> str:
    hora = eta.hour if eta is not None else None
    punta = hora is not None and (7 <= hora < 9 or 17 <= hora < 20)
    if factor >= 1.35 or (punta and factor >= 1.15):
        return "ROJO"
    if factor >= 1.15 or punta:
        return "AMARILLO"
    return "VERDE"
