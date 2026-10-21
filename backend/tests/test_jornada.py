from datetime import UTC, datetime

import pytest
from app.optimizacion.jornada import (
    JORNADA_MAX_MIN,
    MENSAJE_JORNADA,
    EstadoJornada,
    descansos_requeridos,
)
from app.optimizacion.pico_placa import placa_restringida


def test_cuatro_horas_insertan_un_descanso():
    estado = EstadoJornada()
    reloj = datetime(2026, 10, 20, 6, 0, tzinfo=UTC)
    reloj = estado.conducir(reloj, 240)
    assert len(estado.descansos) == 1
    assert estado.descansos[0].duracion_min == 60
    assert estado.minutos_conduccion == 240
    assert reloj == datetime(2026, 10, 20, 11, 0, tzinfo=UTC)
    assert descansos_requeridos(240) == 1


def test_cinco_horas_siguen_siendo_factibles_con_descanso():
    estado = EstadoJornada()
    estado.conducir(datetime(2026, 10, 20, 6, tzinfo=UTC), 300)
    assert estado.minutos_conduccion == 300
    assert len(estado.descansos) == 1
    assert descansos_requeridos(300) == 1
    assert descansos_requeridos(100) == 0


def test_mas_de_ocho_horas_incumple_la_ley():
    estado = EstadoJornada()
    with pytest.raises(ValueError, match="30224"):
        estado.conducir(datetime(2026, 10, 20, 6, tzinfo=UTC), JORNADA_MAX_MIN + 1)
    assert MENSAJE_JORNADA.startswith("Incumplimiento")


def test_pico_y_placa_por_ultimo_digito():
    lunes = datetime(2026, 10, 19).date()
    martes = datetime(2026, 10, 20).date()
    domingo = datetime(2026, 10, 18).date()
    assert lunes.weekday() == 0
    assert placa_restringida("DMO-101", lunes) is True
    assert placa_restringida("DMO-102", lunes) is True
    assert placa_restringida("DMO-101", martes) is False
    assert placa_restringida("DMO-101", domingo) is False
    assert placa_restringida("SIN-DIGITO", lunes) is False
