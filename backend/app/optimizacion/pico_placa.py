"""Restricción vehicular por último dígito (RN-006, D.S. N.º 033-2012-MTC).

Calendario operativo de días hábiles usado por la heurística del Sprint 3.
Sábado y domingo no restringen. No es el texto íntegro del decreto: es la
regla de último dígito que el backlog pide aplicar al generar la ruta.
"""

from datetime import date

# weekday(): lunes = 0 … domingo = 6
RESTRICCION_POR_DIA: dict[int, frozenset[int]] = {
    0: frozenset({1, 2}),
    1: frozenset({3, 4}),
    2: frozenset({5, 6}),
    3: frozenset({7, 8}),
    4: frozenset({9, 0}),
}


def ultimo_digito(placa: str) -> int | None:
    digitos = [caracter for caracter in placa if caracter.isdigit()]
    if not digitos:
        return None
    return int(digitos[-1])


def placa_restringida(placa: str, fecha: date) -> bool:
    digito = ultimo_digito(placa)
    if digito is None:
        return False
    return digito in RESTRICCION_POR_DIA.get(fecha.weekday(), frozenset())
