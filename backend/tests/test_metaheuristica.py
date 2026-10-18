"""ENB-001 / US-010: el genético no empeora al vecino y cabe en 45 s."""

import time
from datetime import UTC, date, datetime, timedelta
from uuid import UUID

from app.optimizacion.congestion import nivel_congestion
from app.optimizacion.evaluacion import (
    Instancia,
    PedidoNodo,
    Plan,
    Recurso,
    costo_verde,
    simular,
    vecino_mas_cercano,
)
from app.optimizacion.jornada import JORNADA_MAX_MIN
from app.optimizacion.metaheuristica import evolucionar
from app.optimizacion.pico_placa import placa_restringida

FECHA = date(2026, 11, 2)


def _recurso(indice: int, digito: str = "5") -> Recurso:
    inicio = datetime(FECHA.year, FECHA.month, FECHA.day, 6, 0, tzinfo=UTC)
    return Recurso(
        id_vehiculo=UUID(int=1_000 + indice),
        id_conductor=UUID(int=2_000 + indice),
        placa=f"LIM-10{digito}",
        capacidad_kg=800,
        capacidad_m3=8,
        consumo_km_l=12,
        factor_co2=0.25,
        origen_lat=-12.01,
        origen_lon=-76.98,
        inicio=inicio,
        fin=inicio + timedelta(hours=14),
    )


def _pedido(indice: int, lat: float, lon: float, *, express: bool = False) -> PedidoNodo:
    inicio = datetime(FECHA.year, FECHA.month, FECHA.day, 7, 0, tzinfo=UTC)
    return PedidoNodo(
        id=UUID(int=indice + 1),
        lat=lat,
        lon=lon,
        peso=12,
        volumen=0.2,
        ventana_inicio=inicio,
        ventana_fin=inicio + timedelta(hours=12),
        express=express,
    )


def _instancia(
    pedidos: list[PedidoNodo],
    recursos: list[Recurso],
    segundos: float = 45,
) -> Instancia:
    return Instancia(
        fecha=FECHA,
        pedidos=pedidos,
        recursos=recursos,
        velocidad=25,
        congestion=1.1,
        limite=time.perf_counter() + segundos,
        precio_litro=17.50 / 3.785411784,
        costo_km=1.20,
        excluidos=0,
        semilla=20261102,
    )


def _cruce() -> Instancia:
    # El vecino entra al punto más cercano y cruza; el 2-opt del genético no.
    puntos = ((0.01, 0.0), (0.011, 0.001), (0.012, -0.001), (0.002, 0.012))
    pedidos = [_pedido(i, -12.01 + lat, -76.98 + lon) for i, (lat, lon) in enumerate(puntos)]
    return _instancia(pedidos, [_recurso(0)])


def _forzar(inst: Instancia) -> Plan:
    rutas, libres, _ = vecino_mas_cercano(inst)
    assert rutas, "la línea base del cruce tiene que ser factible"
    return evolucionar(inst, Plan(True, "base", rutas, libres, algoritmo="vecino_mas_cercano"))


def test_semaforo_de_congestion():
    punta = datetime(2026, 11, 2, 8, 0, tzinfo=UTC)
    valle = datetime(2026, 11, 2, 11, 0, tzinfo=UTC)
    assert nivel_congestion(1.0, valle) == "VERDE"
    assert nivel_congestion(1.0, punta) == "AMARILLO"
    assert nivel_congestion(1.2, valle) == "AMARILLO"
    assert nivel_congestion(1.2, punta) == "ROJO"
    assert nivel_congestion(1.4, valle) == "ROJO"
    assert nivel_congestion(1.0, None) == "VERDE"


def test_el_genetico_mejora_el_cruce_y_queda_a_quince_por_ciento():
    inst = _cruce()
    base_rutas, libres, _ = vecino_mas_cercano(inst)
    base = costo_verde(base_rutas, libres, inst)
    plan = _forzar(inst)
    actual = costo_verde(plan.rutas, plan.sin_asignar, inst)
    assert plan.algoritmo == "algoritmo_genetico"
    assert plan.comparacion["generaciones"] >= 1
    assert actual["total"] < base["total"]
    assert plan.comparacion["mejora_porcentaje"] > 0
    assert plan.comparacion["segundos"] <= 45

    referencia = _optimo(inst)
    assert actual["total"] <= referencia * 1.15


def _optimo(inst: Instancia) -> float:
    from itertools import permutations

    recurso = inst.recursos[0]
    mejor = None
    for orden in permutations(inst.pedidos):
        ruta = simular(recurso, list(orden), inst)
        if ruta is None:
            continue
        total = costo_verde([ruta], [], inst)["total"]
        if mejor is None or total < mejor:
            mejor = total
    assert mejor is not None
    return mejor


def test_bench_150_pedidos_15_vehiculos_en_45_segundos():
    assert FECHA.weekday() == 0
    pedidos = []
    for indice in range(150):
        fila, columna = divmod(indice, 15)
        lat = -12.03 + fila * 0.004
        lon = -77.00 + columna * 0.004
        pedidos.append(_pedido(indice, lat, lon, express=indice % 11 == 0))
    recursos = [_recurso(indice, "5") for indice in range(15)]
    for recurso in recursos:
        assert not placa_restringida(recurso.placa, FECHA)
    inst = _instancia(pedidos, recursos, segundos=45)
    inicio = time.perf_counter()
    base_rutas, libres, _ = vecino_mas_cercano(inst)
    plan = evolucionar(
        inst,
        Plan(True, "base", base_rutas, libres, algoritmo="vecino_mas_cercano"),
        inicio,
    )
    transcurrido = time.perf_counter() - inicio
    assert transcurrido <= 45
    assert plan.comparacion["segundos"] <= 45
    assert plan.sin_asignar == []
    assert plan.comparacion["objetivo_verde"] <= plan.comparacion["objetivo_base"] + 1e-6
    _factible(inst, plan)


def _factible(inst: Instancia, plan: Plan) -> None:
    vistos: set[UUID] = set()
    catalogo = {pedido.id: pedido for pedido in inst.pedidos}
    recursos = {recurso.id_vehiculo: recurso for recurso in inst.recursos}
    for ruta in plan.rutas:
        recurso = recursos[ruta.id_vehiculo]
        assert not placa_restringida(recurso.placa, inst.fecha)
        assert ruta.minutos_conduccion <= JORNADA_MAX_MIN + 1e-6
        peso = 0.0
        volumen = 0.0
        secuencia = []
        for parada in ruta.paradas:
            assert parada.id_pedido not in vistos
            vistos.add(parada.id_pedido)
            pedido = catalogo[parada.id_pedido]
            peso += pedido.peso
            volumen += pedido.volumen
            secuencia.append(pedido)
        assert peso <= recurso.capacidad_kg + 1e-6
        assert volumen <= recurso.capacidad_m3 + 1e-6
        assert simular(recurso, secuencia, inst) is not None
    assert vistos == set(catalogo)
