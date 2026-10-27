"""Algoritmo genético VRPTW + Green VRP (ENB-001 / US-010, DEAP).

Corre en el worker, no en el request. Parte de la heurística del vecino más
cercano, la educa con 2-opt y evoluciona permutaciones hasta el presupuesto
de `tiempo_max_optimizacion_s` (RN-014, tope 45 s). Si no mejora el costo
verde, se conserva el plan base: nunca se devuelve una solución peor.

`random` siembra esa búsqueda con la semilla del plan. No genera secretos,
tokens ni claves: el uso es no criptográfico (python:S2245, revisión Safe).
"""

import random
import time
from datetime import date

from deap import base, creator, tools
from sqlalchemy.orm import Session

from app.optimizacion.evaluacion import (
    Instancia,
    Plan,
    costo_verde,
    decodificar,
    mejorar_orden_local,
)
from app.optimizacion.heuristica import plan_desde_vecino, preparar

POBLACION = 16
GENERACIONES_TOPE = 40
ESTANCAMIENTO = 8


def _tipos() -> None:
    if not hasattr(creator, "AptitudVerde"):
        creator.create("AptitudVerde", base.Fitness, weights=(-1.0,))
        creator.create("Individuo", list, fitness=creator.AptitudVerde)


def _mensaje(inst: Instancia, mejora: float, cortado: bool, sin_asignar: int) -> str:
    if mejora > 0.05:
        texto = (
            "Plan en borrador generado con el algoritmo genético (VRPTW + Green VRP, DEAP). "
            "Frente a la heurística del vecino más cercano reduce el costo verde "
            f"un {mejora:.1f} %. "
            "Confirme la ruta para asignar los pedidos."
        )
    else:
        texto = (
            "Plan en borrador generado con el algoritmo genético (VRPTW + Green VRP, DEAP). "
            "El costo verde iguala a la heurística del vecino más cercano. "
            "Confirme la ruta para asignar los pedidos."
        )
    if inst.excluidos:
        texto += (
            f" Se excluyeron {inst.excluidos} vehículo(s) por restricción de placa "
            "(D.S. N.º 033-2012-MTC)."
        )
    if sin_asignar:
        texto += f" Quedaron {sin_asignar} pedido(s) sin asignar."
    if cortado:
        texto += (
            " El cálculo se detuvo al alcanzar el tiempo límite y devolvió el mejor plan factible."
        )
    return texto


def _ficha(
    inst: Instancia,
    rutas,
    sin_asignar,
    segundos: float,
    base: dict,
    generaciones: int,
) -> dict:
    actual = costo_verde(rutas, sin_asignar, inst)
    soles_base = float(base["soles"])
    mejora = 0.0 if soles_base <= 1e-9 else (soles_base - actual["soles"]) / soles_base * 100
    return {
        "algoritmo": "algoritmo_genetico",
        "linea_base": "vecino_mas_cercano",
        "objetivo_verde": round(actual["total"], 4),
        "objetivo_base": round(float(base["total"]), 4),
        "distancia_km": round(actual["distancia_km"], 4),
        "distancia_base_km": round(float(base["distancia_km"]), 4),
        "combustible_l": round(actual["combustible_l"], 4),
        "combustible_base_l": round(float(base["combustible_l"]), 4),
        "co2_kg": round(actual["co2_kg"], 4),
        "co2_base_kg": round(float(base["co2_kg"]), 4),
        "soles": round(actual["soles"], 4),
        "soles_base": round(soles_base, 4),
        "mejora_porcentaje": round(mejora, 4),
        "segundos": round(segundos, 4),
        "generaciones": generaciones,
        "sin_asignar": len(sin_asignar),
    }


def evolucionar(inst: Instancia, base: Plan, inicio: float | None = None) -> Plan:
    """Devuelve el mejor plan factible dentro del presupuesto. No empeora la base."""

    reloj = time.perf_counter() if inicio is None else inicio
    costo_base = costo_verde(base.rutas, base.sin_asignar, inst)
    rutas_local, sin_local = mejorar_orden_local(base.rutas, base.sin_asignar, inst)
    costo_local = costo_verde(rutas_local, sin_local, inst)
    if costo_local["total"] + 1e-6 < costo_base["total"]:
        incumbente = (rutas_local, sin_local, costo_local)
    else:
        incumbente = (base.rutas, base.sin_asignar, costo_base)

    generaciones = 0
    n = len(inst.pedidos)
    if n >= 2 and time.perf_counter() < inst.limite:
        generaciones, incumbente = _generaciones(inst, incumbente)

    rutas, sin_asignar, _costo = incumbente
    segundos = time.perf_counter() - reloj
    cortado = time.perf_counter() >= inst.limite
    ficha = _ficha(inst, rutas, sin_asignar, segundos, costo_base, generaciones)
    return Plan(
        True,
        _mensaje(inst, float(ficha["mejora_porcentaje"]), cortado, len(sin_asignar)),
        list(rutas),
        list(sin_asignar),
        algoritmo="algoritmo_genetico",
        comparacion=ficha,
    )


def _generaciones(inst: Instancia, incumbente: tuple) -> tuple[int, tuple]:
    _tipos()
    estado = random.getstate()
    random.seed(inst.semilla)
    try:
        return _correr(inst, incumbente)
    finally:
        random.setstate(estado)


def _evaluar(inst: Instancia, incumbente: tuple, individuo: list[int]) -> tuple[float]:
    if time.perf_counter() >= inst.limite:
        return (incumbente[2]["total"],)
    rutas, libres, _ = decodificar(list(individuo), inst)
    return (costo_verde(rutas, libres, inst)["total"],)


def _cruzar(caja: base.Toolbox, hijos: list) -> None:
    for izquierda, derecha in zip(hijos[::2], hijos[1::2], strict=False):
        if random.random() < 0.7:
            caja.mate(izquierda, derecha)
            del izquierda.fitness.values
            del derecha.fitness.values


def _mutar(caja: base.Toolbox, hijos: list) -> None:
    for individuo in hijos:
        if random.random() < 0.3:
            caja.mutar(individuo)
            del individuo.fitness.values


def _adoptar_si_mejora(
    inst: Instancia,
    puntero: list,
    incumbente: tuple,
    mejor_valor: float,
) -> tuple[tuple, float, int]:
    if puntero.fitness.values[0] + 1e-6 >= mejor_valor:
        return incumbente, mejor_valor, 1
    rutas, libres, _ = decodificar(list(puntero), inst)
    rutas, libres = mejorar_orden_local(rutas, libres, inst)
    total = costo_verde(rutas, libres, inst)
    if total["total"] + 1e-6 < incumbente[2]["total"]:
        return (rutas, libres, total), total["total"], 0
    return incumbente, mejor_valor, 1


def _generacion(
    inst: Instancia,
    caja: base.Toolbox,
    poblacion: list,
    tam: int,
    incumbente: tuple,
    mejor_valor: float,
    quietud: int,
    generaciones: int,
) -> tuple[list, int, tuple, float, int]:
    generaciones += 1
    hijos = [caja.clone(ind) for ind in caja.seleccionar(poblacion, tam)]
    _cruzar(caja, hijos)
    _mutar(caja, hijos)
    invalidos = [ind for ind in hijos if not ind.fitness.valid]
    for individuo in invalidos:
        individuo.fitness.values = _evaluar(inst, incumbente, individuo)
    poblacion = tools.selBest(poblacion + hijos, tam)
    puntero = tools.selBest(poblacion, 1)[0]
    incumbente, mejor_valor, delta = _adoptar_si_mejora(inst, puntero, incumbente, mejor_valor)
    if delta == 0:
        quietud = 0
    else:
        quietud += 1
    return poblacion, generaciones, incumbente, mejor_valor, quietud


def _correr(inst: Instancia, incumbente: tuple) -> tuple[int, tuple]:
    n = len(inst.pedidos)
    caja = base.Toolbox()
    caja.register("indices", random.sample, range(n), n)
    caja.register("individuo", tools.initIterate, creator.Individuo, caja.indices)
    caja.register("poblacion", tools.initRepeat, list, caja.individuo)
    caja.register("mate", tools.cxOrdered)
    caja.register("mutar", tools.mutShuffleIndexes, indpb=0.15)
    caja.register("seleccionar", tools.selTournament, tournsize=3)

    tam = 8 if n > 40 else POBLACION
    poblacion = caja.poblacion(n=tam)
    for individuo in poblacion:
        individuo.fitness.values = _evaluar(inst, incumbente, individuo)
    mejor_valor = incumbente[2]["total"]
    generaciones = 0
    quietud = 0
    while (
        generaciones < GENERACIONES_TOPE
        and quietud < ESTANCAMIENTO
        and time.perf_counter() < inst.limite
    ):
        poblacion, generaciones, incumbente, mejor_valor, quietud = _generacion(
            inst,
            caja,
            poblacion,
            tam,
            incumbente,
            mejor_valor,
            quietud,
            generaciones,
        )
    return generaciones, incumbente


def generar_plan(db: Session, fecha: date) -> Plan:
    inicio = time.perf_counter()
    preparado = preparar(db, fecha)
    if isinstance(preparado, Plan):
        return preparado
    base = plan_desde_vecino(preparado)
    if not base.factible:
        return base
    return evolucionar(preparado, base, inicio)
