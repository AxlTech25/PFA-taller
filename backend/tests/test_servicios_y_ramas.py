"""Ramas que el informe de cobertura dejaba fuera: servicios, worker y helpers extraídos."""

import time
import uuid
from datetime import UTC, date, datetime
from types import SimpleNamespace

import pytest
from app.core.deps import get_current_user, ip_de
from app.core.security import create_access_token
from app.db.session import get_db
from app.main import app
from app.optimizacion.cobertura import exigir_cobertura
from app.optimizacion.cola import ColaNoDisponible
from app.optimizacion.evaluacion import (
    DEPOSITO_SJL,
    ParadaPlan,
    RutaPlan,
    _armar_por_cercania,
    _optimizar_secuencia,
    _recurso_de,
    _reverso_mejor,
    _tomar_en_orden,
    decodificar,
    mejorar_orden_local,
    simular,
    vecino_mas_cercano,
)
from app.optimizacion.heuristica import MENSAJE_PLAN, _mensaje_base, _origen, _parametro
from app.optimizacion.metaheuristica import _adoptar_si_mejora, _evaluar, _mensaje
from app.services.indicadores import (
    _ahorros,
    _cumplimiento,
    _equivalente_arboles,
    _factor_arboles,
    _rutas_del_dia,
)
from app.services.integridad import mensaje_integridad
from app.services.rutas import _comparacion_de, _float, _minutos_tramo, _origen_conductor, _parada
from app.worker import _esperar_esquema, iteracion, main, procesar_job
from fastapi import HTTPException
from sqlalchemy import text
from tests.conftest import autenticar, crear_usuario
from tests.test_metaheuristica import _instancia, _pedido, _recurso


class _Consulta:
    def __init__(self, valor):
        self.valor = valor

    def execute(self, *_args, **_kwargs):
        return self

    def scalar(self):
        return self.valor


def test_sin_clave_de_unicidad_y_textos_de_respaldo():
    assert mensaje_integridad(SimpleNamespace(orig=SimpleNamespace())) is None
    assert "placa" in mensaje_integridad(_error("", "vehiculo_placa_key"))
    assert "DNI" in mensaje_integridad(_error("", "conductor_dni_key"))
    assert "correo" in mensaje_integridad(_error("", "usuario_email_key"))
    assert "placa" in mensaje_integridad(_error("duplicate key vehiculo_placa", None))
    assert "placa" in mensaje_integridad(_error("placa repetida", ""))
    assert "DNI" in mensaje_integridad(_error("duplicate conductor_dni", None))
    assert "DNI" in mensaje_integridad(_error("dni repetido", ""))
    assert "correo" in mensaje_integridad(_error("usuario_email duplicado", None))
    assert mensaje_integridad(_error("otro conflicto", "ajena")) is None


class _Orig:
    def __init__(self, texto, nombre):
        self._texto = texto
        self.diag = SimpleNamespace(constraint_name=nombre)

    def __str__(self) -> str:
        return self._texto


def _error(texto, nombre):
    return SimpleNamespace(orig=_Orig(texto, nombre))


def test_cobertura_exige_distrito_o_422(monkeypatch):
    monkeypatch.setattr("app.optimizacion.cobertura.distrito_en", lambda *_args: None)
    with pytest.raises(HTTPException) as exc:
        exigir_cobertura(None, 0, 0)
    assert exc.value.status_code == 422
    monkeypatch.setattr("app.optimizacion.cobertura.distrito_en", lambda *_args: "Ate")
    assert exigir_cobertura(None, -12.0, -76.9) == "Ate"


def test_factor_ahorros_cumplimiento_y_arboles(db):
    assert _factor_arboles(_Consulta(None)) is None
    assert _factor_arboles(_Consulta("no-numero")) is None
    assert _factor_arboles(_Consulta("0")) is None
    assert _factor_arboles(_Consulta("-1")) is None
    assert _factor_arboles(_Consulta("2.5")) == 2.5
    db.execute(
        text(
            "INSERT INTO configuracion_sistema (clave, valor, unidad, descripcion) "
            "VALUES ('factor_captura_arbol_kg', '10', 'kg', 'prueba')"
        )
    )
    assert _factor_arboles(db) == 10

    assert _ahorros(None) == (0.0, 0.0, None)
    assert _ahorros(SimpleNamespace(resultado=None)) == (0.0, 0.0, None)
    assert _ahorros(SimpleNamespace(resultado={})) == (0.0, 0.0, None)
    soles, co2, mejora = _ahorros(
        SimpleNamespace(
            resultado={
                "comparacion": {
                    "soles_base": 1,
                    "soles": 8,
                    "co2_base_kg": 1,
                    "co2_kg": 4,
                    "mejora_porcentaje": 3,
                }
            }
        )
    )
    assert (soles, co2, mejora) == (0.0, 0.0, 3)
    assert _equivalente_arboles(None, 4) is None
    assert _equivalente_arboles(2, 0) is None
    assert _equivalente_arboles(2, 5) == 2.5

    class _Db:
        def scalars(self, _consulta):
            return self

        def all(self):
            return [
                SimpleNamespace(id_pedido="falta", eta=None),
                SimpleNamespace(id_pedido="sin-eta", eta=None),
                SimpleNamespace(id_pedido="ok", eta=datetime(2026, 11, 2, 9, tzinfo=UTC)),
                SimpleNamespace(id_pedido="tarde", eta=datetime(2026, 11, 2, 18, tzinfo=UTC)),
            ]

        def get(self, _modelo, identificador):
            if identificador == "falta":
                return None
            if identificador == "sin-eta":
                return SimpleNamespace(
                    ventana_inicio=datetime(2026, 11, 2, 8, tzinfo=UTC),
                    ventana_fin=datetime(2026, 11, 2, 12, tzinfo=UTC),
                )
            if identificador == "ok":
                return SimpleNamespace(
                    ventana_inicio=datetime(2026, 11, 2, 8, tzinfo=UTC),
                    ventana_fin=datetime(2026, 11, 2, 12, tzinfo=UTC),
                )
            return SimpleNamespace(
                ventana_inicio=datetime(2026, 11, 2, 8, tzinfo=UTC),
                ventana_fin=datetime(2026, 11, 2, 12, tzinfo=UTC),
            )

    assert _cumplimiento(_Db(), []) == 0
    assert _cumplimiento(_Db(), [SimpleNamespace(id_ruta="r")]) == 50
    job, rutas = _rutas_del_dia(db, date(1999, 1, 1))
    assert job is None
    assert rutas == []


def test_helpers_de_ruta_para_auditor_y_tramos():
    assert _float(None) is None
    assert _float("1.5") == 1.5
    assert _origen_conductor(None, False) == (None, None)
    conductor = SimpleNamespace(lat_punto_partida=None, lon_punto_partida=-76.9)
    assert _origen_conductor(conductor, False) == DEPOSITO_SJL
    assert _origen_conductor(conductor, True) == (None, None)
    puesto = SimpleNamespace(lat_punto_partida=-12.2, lon_punto_partida=-77.0)
    assert _origen_conductor(puesto, False) == (-12.2, -77.0)

    minutos, previo = _minutos_tramo((None, None), -12.0, -77.0, 25, 1)
    assert minutos is None
    assert previo == (None, None)
    minutos, previo = _minutos_tramo((-12.01, -76.98), -12.02, -76.99, 25, 1.1)
    assert minutos is not None and minutos > 0
    assert previo == (-12.02, -76.99)

    ruta = SimpleNamespace(id_job=None)
    assert _comparacion_de(SimpleNamespace(), ruta) is None
    ruta = SimpleNamespace(id_job=uuid.uuid4())

    class _Vacio:
        def get(self, *_args):
            return None

    assert _comparacion_de(_Vacio(), ruta) is None
    sin_resultado = SimpleNamespace(get=lambda *_a: SimpleNamespace(resultado=None))
    assert _comparacion_de(sin_resultado, ruta) is None
    con_ficha = SimpleNamespace(
        get=lambda *_a: SimpleNamespace(resultado={"comparacion": {"km": 1}})
    )
    assert _comparacion_de(con_ficha, ruta) == {"km": 1}

    class _Pedidos:
        def get(self, modelo, identificador):
            nombre = getattr(modelo, "__name__", "")
            if nombre == "Pedido" and identificador == "p1":
                return SimpleNamespace(
                    id_cliente="c1",
                    latitud=-12.02,
                    longitud=-76.99,
                    punto_referencia="bodega",
                )
            if nombre == "Cliente":
                return SimpleNamespace(nombre="Ana")
            return None

    detalle = SimpleNamespace(id_pedido="p1", secuencia=1, eta=None)
    parada, _ = _parada(_Pedidos(), detalle, True, (None, None), 25, 1)
    assert parada["latitud"] is None
    assert parada["nombre_cliente"] == "Ana"
    parada, previo = _parada(_Pedidos(), detalle, False, (-12.01, -76.98), 25, 1)
    assert parada["punto_referencia"] == "bodega"
    assert parada["minutos_tramo"] is not None
    assert previo[0] == -12.02
    detalle_vacio = SimpleNamespace(id_pedido="no", secuencia=2, eta=None)
    parada, _ = _parada(_Pedidos(), detalle_vacio, False, (-12.01, -76.98), 25, 1)
    assert parada["nombre_cliente"] is None


def test_parametros_origen_y_mensaje_de_la_heuristica():
    assert _parametro(_Consulta(None), "clave", 4) == 4
    assert _parametro(_Consulta("1.5"), "clave", 4) == 1.5
    assert _origen(SimpleNamespace(lat_punto_partida=None, lon_punto_partida=None)) == DEPOSITO_SJL
    con_partida = SimpleNamespace(lat_punto_partida=-12.2, lon_punto_partida=-77.1)
    assert _origen(con_partida) == (-12.2, -77.1)
    assert _mensaje_base(0, [], False) == MENSAJE_PLAN
    texto = _mensaje_base(2, [uuid.uuid4()], True)
    assert "excluyeron" in texto
    assert "sin asignar" in texto
    assert "tiempo límite" in texto


def test_mensaje_evaluacion_y_adopcion_del_genetico(monkeypatch):
    inst = SimpleNamespace(excluidos=0)
    assert "iguala" in _mensaje(inst, 0.01, False, 0)
    completo = _mensaje(SimpleNamespace(excluidos=2), 12, True, 3)
    assert "12.0 %" in completo
    assert "excluyeron" in completo
    assert "sin asignar" in completo
    assert "tiempo límite" in completo

    incumbente = ([], [], {"total": 9})
    assert _evaluar(SimpleNamespace(limite=0), incumbente, [0]) == (9,)
    monkeypatch.setattr(
        "app.optimizacion.metaheuristica.decodificar",
        lambda *_args: ([], [], False),
    )
    monkeypatch.setattr(
        "app.optimizacion.metaheuristica.costo_verde",
        lambda *_args: {"total": 4},
    )
    assert _evaluar(SimpleNamespace(limite=time.perf_counter() + 30), incumbente, [0]) == (4,)

    puntero = SimpleNamespace(fitness=SimpleNamespace(values=(50.0,)))
    nuevo, valor, delta = _adoptar_si_mejora(SimpleNamespace(), puntero, incumbente, 10)
    assert nuevo is incumbente and valor == 10 and delta == 1

    monkeypatch.setattr(
        "app.optimizacion.metaheuristica.mejorar_orden_local",
        lambda rutas, libres, _inst: (rutas, libres),
    )
    class _Individuo(list):
        def __init__(self, valor: float):
            super().__init__([0])
            self.fitness = SimpleNamespace(values=(valor,))

    puntero = _Individuo(1.0)
    monkeypatch.setattr(
        "app.optimizacion.metaheuristica.costo_verde",
        lambda *_args: {"total": 20},
    )
    nuevo, valor, delta = _adoptar_si_mejora(SimpleNamespace(), puntero, incumbente, 5)
    assert delta == 1 and valor == 5 and nuevo is incumbente
    monkeypatch.setattr(
        "app.optimizacion.metaheuristica.costo_verde",
        lambda *_args: {"total": 3},
    )
    nuevo, valor, delta = _adoptar_si_mejora(SimpleNamespace(), puntero, incumbente, 5)
    assert delta == 0 and valor == 3
    assert nuevo[2]["total"] == 3


def test_cortes_por_tiempo_y_secuencias_del_optimizador():
    inst = _instancia(
        [_pedido(0, -12.02, -76.99), _pedido(1, -12.03, -77.0)],
        [_recurso(0)],
    )
    rutas, libres, _ = vecino_mas_cercano(inst)
    assert rutas
    inst.limite = 0
    assert mejorar_orden_local(rutas, libres, inst)[0] == rutas
    assert vecino_mas_cercano(inst)[2] is True
    assert decodificar([0, 1], inst)[2] is True
    _ruta, _pendientes, cortado = _armar_por_cercania(inst.recursos[0], list(inst.pedidos), inst)
    assert cortado is True
    _tomar_en_orden(inst.recursos[0], list(inst.pedidos), inst)

    with pytest.raises(KeyError):
        _recurso_de(inst, uuid.UUID(int=9))

    pesado = _pedido(4, -12.05, -77.02)
    pesado.peso = 50_000
    otro = _pedido(5, -12.06, -77.03)
    otro.peso = 50_000
    imposible = _instancia([pesado, otro], [_recurso(1)])
    assert simular(imposible.recursos[0], [pesado], imposible) is None
    assert _reverso_mejor(imposible.recursos[0], [pesado, otro], imposible, 1e9) is None

    inst = _instancia([_pedido(i, -12.02 - i * 0.01, -76.99) for i in range(2)], [_recurso(2)])
    rutas, _libres, _ = vecino_mas_cercano(inst)
    ruta = rutas[0]
    recurso = _recurso_de(inst, ruta.id_vehiculo)
    catalogo = {pedido.id: pedido for pedido in inst.pedidos}
    secuencia = [catalogo[parada.id_pedido] for parada in ruta.paradas]
    assert _optimizar_secuencia(recurso, secuencia, ruta, inst, 0) is ruta

    pedido = inst.pedidos[0]
    parada = ParadaPlan(pedido.id, pedido.lat, pedido.lon, 1, pedido.ventana_inicio, 0.1)
    larga = RutaPlan(
        id_vehiculo=inst.recursos[0].id_vehiculo,
        id_conductor=inst.recursos[0].id_conductor,
        paradas=[parada] * 17,
        descansos=[],
        distancia_km=1,
        minutos_conduccion=1,
        minutos_reloj=1,
        combustible_l=1,
        co2_kg=1,
    )
    assert mejorar_orden_local([larga], [], inst)[0] == [larga]


class _Job:
    def __init__(self, estado="ENCOLADO"):
        self.estado = estado
        self.fecha = date(2026, 11, 2)
        self.mensaje = ""
        self.resultado = None
        self.actualizado_en = None


class _DbJob:
    def __init__(self, job):
        self.job = job
        self.lecturas = 0
        self.commits = 0
        self.rollbacks = 0

    def get(self, *_args):
        self.lecturas += 1
        if self.lecturas > 1 and self.job is None:
            return None
        return self.job

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


def test_worker_ignora_descarta_y_marca_fallido(monkeypatch):
    assert procesar_job(_DbJob(None), uuid.uuid4()) is None
    job = _Job("COMPLETADO")
    assert procesar_job(_DbJob(job), uuid.uuid4()) is None

    base = _DbJob(_Job())

    def _plan(_db, _fecha):
        return SimpleNamespace(factible=False, sin_asignar=[uuid.uuid4()], mensaje="sin flota")

    monkeypatch.setattr("app.worker.generar_plan", _plan)
    procesar_job(base, uuid.uuid4())
    assert base.job.estado == "FALLIDO"
    assert base.job.mensaje == "sin flota"
    assert base.job.resultado["id_rutas"] == []

    roto = _DbJob(_Job())

    def _revienta(_db, _fecha):
        roto.job = None
        raise RuntimeError("se fue")

    monkeypatch.setattr("app.worker.generar_plan", _revienta)
    assert procesar_job(roto, uuid.uuid4()) is None
    assert roto.rollbacks == 1


def _tomar_caido(timeout=1):
    assert timeout == 1
    raise ColaNoDisponible("no")


def test_worker_cola_esquema_y_bucle(monkeypatch, db):
    monkeypatch.setattr("app.worker.tomar", _tomar_caido)
    assert iteracion(db) is False

    visto = {}

    def _toma(timeout=1):
        assert timeout == 1
        return str(uuid.uuid4())

    def _procesa(_db, identificador):
        visto["id"] = identificador

    monkeypatch.setattr("app.worker.tomar", _toma)
    monkeypatch.setattr("app.worker.procesar_job", _procesa)
    assert iteracion(db) is True
    assert visto["id"]

    _esperar_esquema()

    fases = {"n": 0}

    def _iteracion(_db):
        fases["n"] += 1
        if fases["n"] == 1:
            raise RuntimeError("transitorio")
        if fases["n"] == 2:
            return False
        raise SystemExit(0)

    monkeypatch.setattr("app.worker._esperar_esquema", lambda: None)
    monkeypatch.setattr("app.worker.iteracion", _iteracion)
    monkeypatch.setattr("app.worker.time.sleep", lambda _segundos: None)
    with pytest.raises(SystemExit):
        main()
    assert fases["n"] == 3


def test_el_worker_aborta_si_el_esquema_no_llega(monkeypatch):
    monkeypatch.setattr("app.worker.wait_for_db", lambda: None)
    monkeypatch.setattr("app.worker.time.sleep", lambda _segundos: None)

    class _Roto:
        def __enter__(self):
            raise RuntimeError("sin tabla")

        def __exit__(self, *_args):
            return False

    monkeypatch.setattr("app.worker.engine.connect", lambda: _Roto())
    with pytest.raises(SystemExit, match="migraciones"):
        _esperar_esquema()


def test_token_ip_y_salud(client, db):
    with pytest.raises(HTTPException):
        get_current_user(None, db)
    token = create_access_token(user_id=uuid.uuid4(), email="nadie@example.com", rol="ADMIN")
    with pytest.raises(HTTPException) as exc:
        get_current_user(token, db)
    assert exc.value.status_code == 401

    usuario = crear_usuario(db, email="inactivo.token@distrirapido.example.com", rol="OPERADOR")
    usuario.estado = "INACTIVO"
    db.commit()
    token = create_access_token(user_id=usuario.id_usuario, email=usuario.email, rol=usuario.rol)
    with pytest.raises(HTTPException):
        get_current_user(token, db)

    from app.core import deps

    original = deps.decode_token
    deps.decode_token = lambda _token: {"sub": "no-es-uuid"}
    try:
        with pytest.raises(HTTPException):
            get_current_user("token", db)
    finally:
        deps.decode_token = original

    assert ip_de(SimpleNamespace(client=None)) is None
    assert ip_de(SimpleNamespace(client=SimpleNamespace(host="no-es-ip"))) is None
    assert ip_de(SimpleNamespace(client=SimpleNamespace(host="127.0.0.1"))) == "127.0.0.1"

    anterior = app.dependency_overrides[get_db]

    def override():
        class _Roto:
            def execute(self, *_args, **_kwargs):
                raise RuntimeError("caida")

        yield _Roto()

    app.dependency_overrides[get_db] = override
    try:
        respuesta = client.get("/health")
    finally:
        app.dependency_overrides[get_db] = anterior
    assert respuesta.status_code == 503
    assert respuesta.json()["detail"] == "Base de datos no disponible"

    admin = crear_usuario(db, email="adm.ruta.ausente@distrirapido.example.com", rol="ADMIN")
    headers = autenticar(client, admin.email)
    faltante = client.post(f"/rutas/{uuid.uuid4()}/confirmar", headers=headers)
    assert faltante.status_code == 404
    listado = client.get("/rutas", headers=headers)
    assert listado.status_code == 200
