"""US-009 · Preferencias de horario del cliente (RF-009, RN-020, matriz del doc 08)."""

from dataclasses import replace
from datetime import UTC, datetime, time
from time import perf_counter

import pytest
from app.models.entities import Cliente, LogAuditoria, Pedido, PreferenciaCliente
from app.optimizacion.evaluacion import (
    PENALIZACION_PREFERENCIA_MIN,
    Plan,
    costo_verde,
    minutos_fuera_preferencia,
    simular,
    vecino_mas_cercano,
)
from app.optimizacion.heuristica import plan_desde_vecino
from app.optimizacion.metaheuristica import evolucionar
from app.optimizacion.reoptimizacion import TOPE_REOPTIMIZACION_S
from app.services import preferencias
from app.services.reoptimizacion import _nodo
from sqlalchemy import func, select
from tests.conftest import autenticar, crear_usuario
from tests.test_metaheuristica import FECHA, _factible, _instancia, _pedido, _recurso
from tests.test_reoptimizacion import _escenario, _operador

CORREO_OK = "demo.consentido@distrirapido.example.com"
CORREO_NO = "demo.sin.consentimiento@distrirapido.example.com"
VALIDA = {
    "hora_inicio": "08:00",
    "hora_fin": "12:00",
    "punto_referencia": "frente a la bodega El Ahorro",
    "restricciones_acceso": "Calle angosta: solo moto o camioneta pequeña",
}


def _cliente(db, correo: str) -> Cliente:
    cliente = db.scalar(select(Cliente).where(Cliente.email == correo))
    assert cliente is not None
    return cliente


def _url(cliente: Cliente) -> str:
    return f"/clientes/{cliente.id_cliente}/preferencia"


def _headers(client, db, email: str, rol: str = "OPERADOR") -> dict:
    usuario = crear_usuario(db, email=email, rol=rol)
    return autenticar(client, usuario.email)


def _fichas(db, cliente: Cliente) -> int:
    return db.scalar(
        select(func.count())
        .select_from(PreferenciaCliente)
        .where(PreferenciaCliente.id_cliente == cliente.id_cliente)
    )


def test_preferencia_valida_se_persiste_y_se_consulta(client, db):
    headers = _headers(client, db, "op.pref@distrirapido.example.com")
    cliente = _cliente(db, CORREO_OK)

    vacia = client.get(_url(cliente), headers=headers)
    assert vacia.status_code == 200, vacia.text
    assert vacia.json()["registrada"] is False
    assert vacia.json()["hora_inicio"] is None

    respuesta = client.put(_url(cliente), headers=headers, json=VALIDA)
    assert respuesta.status_code == 200, respuesta.text
    cuerpo = respuesta.json()
    assert cuerpo["registrada"] is True
    assert cuerpo["hora_inicio"] == "08:00:00"
    assert cuerpo["hora_fin"] == "12:00:00"
    assert cuerpo["punto_referencia"] == VALIDA["punto_referencia"]
    assert cuerpo["restricciones_acceso"] == VALIDA["restricciones_acceso"]
    assert cuerpo["mensaje"] == preferencias.MENSAJE_GUARDADA

    ficha = db.scalar(
        select(PreferenciaCliente).where(PreferenciaCliente.id_cliente == cliente.id_cliente)
    )
    assert ficha.hora_inicio_preferida == time(8, 0)
    assert ficha.hora_fin_preferida == time(12, 0)
    leida = client.get(_url(cliente), headers=headers).json()
    assert leida["registrada"] is True
    assert leida["nombre_cliente"] == cliente.nombre

    log = db.scalar(
        select(LogAuditoria).where(LogAuditoria.accion == "crear_preferencia_cliente")
    )
    assert log is not None
    assert log.datos_nuevos["hora_inicio"] == "08:00"


def test_actualizar_mantiene_una_ficha_por_cliente(client, db):
    headers = _headers(client, db, "op.pref.act@distrirapido.example.com")
    cliente = _cliente(db, CORREO_OK)
    assert client.put(_url(cliente), headers=headers, json=VALIDA).status_code == 200
    cambio = {"hora_inicio": "06:00", "hora_fin": "21:00"}
    respuesta = client.put(_url(cliente), headers=headers, json=cambio)
    assert respuesta.status_code == 200, respuesta.text
    assert respuesta.json()["hora_inicio"] == "06:00:00"
    assert respuesta.json()["punto_referencia"] is None
    assert _fichas(db, cliente) == 1
    log = db.scalar(
        select(LogAuditoria).where(LogAuditoria.accion == "actualizar_preferencia_cliente")
    )
    assert log.datos_anteriores == {"hora_inicio": "08:00", "hora_fin": "12:00"}


@pytest.mark.parametrize(
    ("inicio", "fin"),
    [("12:00", "12:00"), ("15:00", "09:30"), ("21:00", "06:00")],
)
def test_horarios_contradictorios_se_rechazan(client, db, inicio, fin):
    headers = _headers(client, db, f"op.contra.{inicio[:2]}@distrirapido.example.com")
    cliente = _cliente(db, CORREO_OK)
    respuesta = client.put(
        _url(cliente), headers=headers, json={**VALIDA, "hora_inicio": inicio, "hora_fin": fin}
    )
    assert respuesta.status_code == 422
    assert respuesta.json()["detail"] == (
        "La hora de inicio debe ser anterior a la hora de fin. Corrija el horario preferido."
    )
    assert _fichas(db, cliente) == 0


def test_contradiccion_no_pisa_la_preferencia_guardada(client, db):
    headers = _headers(client, db, "op.contra.guardada@distrirapido.example.com")
    cliente = _cliente(db, CORREO_OK)
    assert client.put(_url(cliente), headers=headers, json=VALIDA).status_code == 200
    mala = client.put(
        _url(cliente), headers=headers, json={"hora_inicio": "18:00", "hora_fin": "07:00"}
    )
    assert mala.status_code == 422
    assert client.get(_url(cliente), headers=headers).json()["hora_inicio"] == "08:00:00"


def test_horas_obligatorias(client, db):
    headers = _headers(client, db, "op.pref.oblig@distrirapido.example.com")
    cliente = _cliente(db, CORREO_OK)
    respuesta = client.put(_url(cliente), headers=headers, json={"hora_inicio": "08:00"})
    assert respuesta.status_code == 422
    assert respuesta.json()["detail"] == "El campo hora_fin es obligatorio"


def test_sin_consentimiento_no_se_guarda(client, db):
    headers = _headers(client, db, "op.pref.nocons@distrirapido.example.com")
    cliente = _cliente(db, CORREO_NO)
    respuesta = client.put(_url(cliente), headers=headers, json=VALIDA)
    assert respuesta.status_code == 422
    assert "consentimiento" in respuesta.json()["detail"]
    assert _fichas(db, cliente) == 0
    assert db.scalar(
        select(LogAuditoria).where(LogAuditoria.accion == "preferencia_sin_consentimiento")
    )


def test_texto_peligroso_se_rechaza(client, db):
    headers = _headers(client, db, "op.pref.xss@distrirapido.example.com")
    cliente = _cliente(db, CORREO_OK)
    respuesta = client.put(
        _url(cliente),
        headers=headers,
        json={**VALIDA, "restricciones_acceso": "<script>alert(1)</script>"},
    )
    assert respuesta.status_code == 422
    assert _fichas(db, cliente) == 0


def test_texto_largo_se_rechaza(client, db):
    headers = _headers(client, db, "op.pref.largo@distrirapido.example.com")
    cliente = _cliente(db, CORREO_OK)
    respuesta = client.put(
        _url(cliente), headers=headers, json={**VALIDA, "restricciones_acceso": "x" * 501}
    )
    assert respuesta.status_code == 422
    assert "500" in respuesta.json()["detail"]


def test_cliente_inexistente(client, db):
    headers = _headers(client, db, "op.pref.404@distrirapido.example.com")
    url = "/clientes/00000000-0000-4000-8000-000000000000/preferencia"
    assert client.get(url, headers=headers).status_code == 404
    assert client.put(url, headers=headers, json=VALIDA).status_code == 404


def test_admin_registra_y_gerente_solo_lee(client, db):
    cliente = _cliente(db, CORREO_OK)
    admin = _headers(client, db, "admin.pref@distrirapido.example.com", "ADMIN")
    assert client.put(_url(cliente), headers=admin, json=VALIDA).status_code == 200
    gerente = _headers(client, db, "ger.pref@distrirapido.example.com", "GERENTE")
    lectura = client.get(_url(cliente), headers=gerente)
    assert lectura.status_code == 200
    assert lectura.json()["registrada"] is True
    assert client.put(_url(cliente), headers=gerente, json=VALIDA).status_code == 403


@pytest.mark.parametrize("rol", ["AUDITOR", "CONDUCTOR"])
def test_roles_sin_acceso(client, db, rol):
    cliente = _cliente(db, CORREO_OK)
    headers = _headers(client, db, f"{rol.lower()}.pref@distrirapido.example.com", rol)
    assert client.get(_url(cliente), headers=headers).status_code == 403
    assert client.put(_url(cliente), headers=headers, json=VALIDA).status_code == 403


def test_sin_sesion(client, db):
    cliente = _cliente(db, CORREO_OK)
    assert client.get(_url(cliente)).status_code == 401
    assert client.put(_url(cliente), json=VALIDA).status_code == 401


# --- Restricción suave en el motor (RF-009 Ruta Feliz) ---


def _en(hora: int, minuto: int = 0) -> datetime:
    return datetime(FECHA.year, FECHA.month, FECHA.day, hora, minuto, tzinfo=UTC)


def test_minutos_fuera_preferencia():
    franja = (time(9, 0), time(11, 0))
    assert minutos_fuera_preferencia(_en(10), franja) == 0
    assert minutos_fuera_preferencia(_en(9), franja) == 0
    assert minutos_fuera_preferencia(_en(8, 30), franja) == 30
    assert minutos_fuera_preferencia(_en(11, 45), franja) == 45


def _dos_pedidos(preferencia=None):
    cercano = replace(_pedido(0, -12.001, -76.98), preferencia=preferencia)
    lejano = _pedido(1, -12.021, -76.98)
    return cercano, lejano


def test_sin_preferencia_el_costo_no_cambia():
    cercano, lejano = _dos_pedidos()
    inst = _instancia([cercano, lejano], [_recurso(0)])
    ruta = simular(inst.recursos[0], [cercano, lejano], inst)
    costo = costo_verde([ruta], [], inst)
    assert costo["penalizacion_preferencia"] == 0
    assert costo["minutos_fuera_preferencia"] == 0
    assert costo["total"] == pytest.approx(costo["soles"] + costo["co2_kg"])


def test_preferencia_es_suave_y_reordena_la_ruta():
    # Sin preferencia conviene atender primero al cercano (menos km).
    cercano, lejano = _dos_pedidos()
    base = _instancia([cercano, lejano], [_recurso(0)])
    directo = simular(base.recursos[0], [cercano, lejano], base)
    invertido = simular(base.recursos[0], [lejano, cercano], base)
    assert costo_verde([directo], [], base)["total"] < costo_verde([invertido], [], base)["total"]

    # El cercano prefiere recibir desde las 07:15: llegar a las 07:00 penaliza, no se prohíbe.
    cercano, lejano = _dos_pedidos((time(7, 15), time(9, 0)))
    inst = _instancia([cercano, lejano], [_recurso(0)])
    directo = simular(inst.recursos[0], [cercano, lejano], inst)
    invertido = simular(inst.recursos[0], [lejano, cercano], inst)
    assert directo is not None and invertido is not None
    costo_directo = costo_verde([directo], [], inst)
    costo_invertido = costo_verde([invertido], [], inst)
    assert costo_directo["minutos_fuera_preferencia"] == pytest.approx(15)
    assert costo_directo["penalizacion_preferencia"] == pytest.approx(
        15 * PENALIZACION_PREFERENCIA_MIN
    )
    assert costo_invertido["minutos_fuera_preferencia"] < 15
    assert costo_invertido["total"] < costo_directo["total"]

    vecino = plan_desde_vecino(inst)
    assert [p.id_pedido for p in vecino.rutas[0].paradas] == [cercano.id, lejano.id]
    plan = evolucionar(inst, vecino)
    assert plan.factible
    assert [p.id_pedido for p in plan.rutas[0].paradas] == [lejano.id, cercano.id]
    assert plan.comparacion["minutos_fuera_preferencia"] < 15
    assert plan.comparacion["minutos_fuera_preferencia_base"] == pytest.approx(15)


def test_preferencia_imposible_no_deja_pedidos_sin_asignar():
    # Restricción suave: aunque nadie llegue a las 05:00, el pedido se atiende igual.
    cercano, lejano = _dos_pedidos((time(5, 0), time(5, 30)))
    inst = _instancia([cercano, lejano], [_recurso(0)])
    plan = evolucionar(inst, plan_desde_vecino(inst))
    assert plan.factible
    assert plan.sin_asignar == []
    assert plan.comparacion["minutos_fuera_preferencia"] > 0


def test_horarios_por_pedido_y_nodo_de_reoptimizacion(client, db):
    headers = _headers(client, db, "op.pref.motor@distrirapido.example.com")
    cliente = _cliente(db, CORREO_OK)
    assert client.put(_url(cliente), headers=headers, json=VALIDA).status_code == 200
    alta = client.post(
        "/pedidos",
        headers=headers,
        json={
            "id_cliente": str(cliente.id_cliente),
            "direccion": "Av. Próceres de la Independencia 1200",
            "latitud": -12.0025,
            "longitud": -76.9901,
            "peso_kg": 10,
            "volumen_m3": 0.1,
            "ventana_inicio": "2096-03-06T07:00:00Z",
            "ventana_fin": "2096-03-06T18:00:00Z",
            "tipo_producto": "NO_PERECEDERO",
        },
    )
    assert alta.status_code == 201, alta.text
    pedido = db.get(Pedido, alta.json()["id_pedido"])
    horarios = preferencias.horarios_por_pedido(db, [pedido])
    assert horarios == {pedido.id_pedido: (time(8, 0), time(12, 0))}
    assert _nodo(pedido, horarios).preferencia == (time(8, 0), time(12, 0))
    assert _nodo(pedido).preferencia is None
    assert preferencias.horarios_por_pedido(db, []) == {}


# --- Presupuestos de tiempo con preferencias (RN-014 45 s, US-011 30 s) ---


def test_bench_150_pedidos_con_preferencias_en_45_segundos():
    franjas = [(time(7, 0), time(9, 0)), (time(9, 0), time(12, 0)), (time(14, 0), time(17, 0))]
    pedidos = []
    for indice in range(150):
        fila, columna = divmod(indice, 15)
        nodo = _pedido(indice, -12.03 + fila * 0.004, -77.00 + columna * 0.004)
        pedidos.append(replace(nodo, preferencia=franjas[indice % 3]))
    inst = _instancia(pedidos, [_recurso(indice) for indice in range(15)], segundos=45)
    inicio = perf_counter()
    rutas, libres, _ = vecino_mas_cercano(inst)
    plan = evolucionar(inst, Plan(True, "base", rutas, libres), inicio)
    transcurrido = perf_counter() - inicio
    print(
        f"PREF_BENCH segundos={transcurrido:.3f} "
        f"min_fuera={plan.comparacion['minutos_fuera_preferencia']:.1f} "
        f"min_fuera_base={plan.comparacion['minutos_fuera_preferencia_base']:.1f}"
    )
    assert transcurrido <= 45
    assert plan.sin_asignar == []
    assert plan.comparacion["objetivo_verde"] <= plan.comparacion["objetivo_base"] + 1e-6
    _factible(inst, plan)


def test_reoptimizacion_con_preferencia_cabe_en_30_segundos(client, db):
    _, _, ruta, detalles = _escenario(db, "pref30", "70019030", 30)
    cliente = _cliente(db, CORREO_OK)
    db.add(
        PreferenciaCliente(
            id_cliente=cliente.id_cliente,
            hora_inicio_preferida=time(10, 0),
            hora_fin_preferida=time(12, 0),
        )
    )
    detalles[0].estado_entrega = "ENTREGADO"
    db.commit()
    headers = _operador(client, db, "pref30")
    antes = perf_counter()
    respuesta = client.post(
        f"/rutas/{ruta.id_ruta}/reoptimizar", json={"motivo": "CONGESTION"}, headers=headers
    )
    total = perf_counter() - antes
    assert respuesta.status_code == 200, respuesta.text
    cuerpo = respuesta.json()
    print(f"PREF_REOPT paradas=30 calculo_s={cuerpo['segundos']:.4f} peticion_s={total:.4f}")
    assert cuerpo["segundos"] <= TOPE_REOPTIMIZACION_S
    assert total <= TOPE_REOPTIMIZACION_S
