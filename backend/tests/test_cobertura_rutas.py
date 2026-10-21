from datetime import date, time
from decimal import Decimal
from uuid import UUID

import pytest
from app.models.entities import (
    AsignacionRuta,
    Conductor,
    DescansoRuta,
    JobOptimizacion,
    Pedido,
    Ruta,
    Vehiculo,
)
from app.worker import iteracion, procesar_job
from sqlalchemy import func, select, text
from tests.conftest import autenticar, crear_usuario

FECHA = "2026-10-20"
DIA = date(2026, 10, 20)


class ColaFalsa:
    def __init__(self, viva: bool = True, falla_al_encolar: bool = False):
        self.viva = viva
        self.falla_al_encolar = falla_al_encolar
        self.items: list[str] = []

    def ping(self):
        if not self.viva:
            raise ConnectionError("redis caído")
        return True

    def lpush(self, _clave, valor):
        self.ping()
        if self.falla_al_encolar:
            raise ConnectionError("redis se cayó al encolar")
        self.items.insert(0, valor)
        return len(self.items)

    def brpop(self, clave, timeout=0):
        self.ping()
        if not self.items:
            return None
        return (clave, self.items.pop())


@pytest.fixture
def cola(monkeypatch):
    falsa = ColaFalsa()
    monkeypatch.setattr("app.optimizacion.cola.obtener_cliente", lambda: falsa)
    return falsa


def _operador(client, db, email="op.ruta@distrirapido.example.com"):
    usuario = crear_usuario(db, email=email)
    return autenticar(client, usuario.email), usuario


def _conductor(db, **cambios) -> Conductor:
    datos = {
        "dni": "70801020",
        "nombre": "Rosa Quispe",
        "licencia_categoria": "A-IIIb",
        "disponibilidad_inicio": time(6, 0),
        "disponibilidad_fin": time(20, 0),
        "lat_punto_partida": Decimal("-12.0100"),
        "lon_punto_partida": Decimal("-76.9800"),
        "estado": "ACTIVO",
    }
    datos.update(cambios)
    fila = Conductor(**datos)
    db.add(fila)
    db.commit()
    db.refresh(fila)
    return fila


def _pedido(client, headers, db, **cambios) -> dict:
    cliente = db.execute(
        text("SELECT id_cliente FROM cliente WHERE email = :email"),
        {"email": "demo.consentido@distrirapido.example.com"},
    ).scalar_one()
    cuerpo = {
        "id_cliente": str(cliente),
        "direccion": "Av. Próceres de la Independencia 1200",
        "latitud": -12.0025,
        "longitud": -76.9901,
        "peso_kg": 25,
        "volumen_m3": 0.4,
        "ventana_inicio": f"{FECHA}T08:00:00Z",
        "ventana_fin": f"{FECHA}T18:00:00Z",
        "prioridad": "ESTANDAR",
        "tipo_producto": "NO_PERECEDERO",
    }
    cuerpo.update(cambios)
    respuesta = client.post("/pedidos", headers=headers, json=cuerpo)
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def _procesar(db, cola_falsa: ColaFalsa) -> None:
    assert iteracion(db) is True
    assert cola_falsa.items == []


def test_punto_de_referencia_marca_georreferencia_aproximada(client, db):
    headers, _ = _operador(client, db, "op.ref@distrirapido.example.com")
    creado = _pedido(
        client,
        headers,
        db,
        punto_referencia="frente a la bodega El Ahorro",
    )
    assert creado["georreferencia_aproximada"] is True
    assert creado["distrito"] == "San Juan de Lurigancho"
    assert creado["punto_referencia"] == "frente a la bodega El Ahorro"
    assert creado["estado"] == "PENDIENTE"


def test_fuera_de_cobertura_no_crea_el_pedido(client, db):
    headers, _ = _operador(client, db, "op.fuera@distrirapido.example.com")
    antes = db.scalar(select(func.count()).select_from(Pedido))
    respuesta = client.post(
        "/pedidos",
        headers=headers,
        json={
            "id_cliente": str(
                db.execute(
                    text("SELECT id_cliente FROM cliente WHERE consentimiento_datos IS TRUE")
                ).scalar_one()
            ),
            "latitud": -12.1219,
            "longitud": -77.03,
            "peso_kg": 10,
            "volumen_m3": 0.2,
            "ventana_inicio": f"{FECHA}T08:00:00Z",
            "ventana_fin": f"{FECHA}T12:00:00Z",
            "tipo_producto": "NO_PERECEDERO",
        },
    )
    assert respuesta.status_code == 422
    assert "Lima Este" in respuesta.json()["detail"]
    db.expire_all()
    assert db.scalar(select(func.count()).select_from(Pedido)) == antes


def test_job_asincrono_y_heuristica_en_borrador(client, db, cola):
    headers, _ = _operador(client, db)
    _conductor(db)
    primero = _pedido(client, headers, db)
    segundo = _pedido(
        client,
        headers,
        db,
        latitud=-12.02,
        longitud=-76.97,
        prioridad="EXPRESS",
        punto_referencia="frente al mercado de Canto Grande",
    )
    antes = db.scalar(select(func.count()).select_from(Ruta))
    alta = client.post("/optimizaciones", headers=headers, json={"fecha": FECHA})
    assert alta.status_code == 202
    cuerpo = alta.json()
    assert cuerpo["estado"] == "ENCOLADO"
    assert "cola" in cuerpo["mensaje"].lower()
    assert db.scalar(select(func.count()).select_from(Ruta)) == antes
    consulta = client.get(f"/optimizaciones/{cuerpo['id_job']}", headers=headers)
    assert consulta.json()["estado"] == "ENCOLADO"
    _procesar(db, cola)
    listo = client.get(f"/optimizaciones/{cuerpo['id_job']}", headers=headers)
    assert listo.status_code == 200
    plan = listo.json()
    assert plan["estado"] == "COMPLETADO"
    assert "algoritmo genético" in plan["mensaje"]
    assert "vecino más cercano" in plan["mensaje"]
    assert plan["algoritmo"] == "algoritmo_genetico"
    assert plan["comparacion"]["linea_base"] == "vecino_mas_cercano"
    assert plan["comparacion"]["mejora_porcentaje"] >= 0
    assert len(plan["rutas"]) == 1
    ruta = plan["rutas"][0]
    assert ruta["estado"] == "BORRADOR"
    assert ruta["placa"] == "DMO-101"
    assert [parada["id_pedido"] for parada in ruta["paradas"]][0] == segundo["id_pedido"]
    assert len(ruta["paradas"]) == 2
    assert ruta["descansos"] == []
    pedidos = client.get("/pedidos", headers=headers).json()
    estados = {item["id_pedido"]: item["estado"] for item in pedidos}
    assert estados[primero["id_pedido"]] == "PENDIENTE"
    assert estados[segundo["id_pedido"]] == "PENDIENTE"
    confirmada = client.post(f"/rutas/{ruta['id_ruta']}/confirmar", headers=headers)
    assert confirmada.status_code == 200, confirmada.text
    assert confirmada.json()["estado"] == "CONFIRMADA"
    assert "30224" in confirmada.json()["mensaje"]
    db.expire_all()
    assert db.get(Pedido, primero["id_pedido"]).estado == "ASIGNADO"


def test_redis_caido_responde_503_sin_job(client, db, monkeypatch):
    headers, _ = _operador(client, db, "op.redis@distrirapido.example.com")
    falsa = ColaFalsa(viva=False)
    monkeypatch.setattr("app.optimizacion.cola.obtener_cliente", lambda: falsa)
    antes = db.scalar(select(func.count()).select_from(JobOptimizacion))
    respuesta = client.post("/optimizaciones", headers=headers, json={"fecha": FECHA})
    assert respuesta.status_code == 503
    assert "Redis" in respuesta.json()["detail"]
    db.expire_all()
    assert db.scalar(select(func.count()).select_from(JobOptimizacion)) == antes
    assert falsa.items == []


def test_fallo_al_encolar_borra_el_job(client, db, monkeypatch):
    headers, _ = _operador(client, db, "op.cola@distrirapido.example.com")
    monkeypatch.setattr(
        "app.optimizacion.cola.obtener_cliente",
        lambda: ColaFalsa(falla_al_encolar=True),
    )
    antes = db.scalar(select(func.count()).select_from(JobOptimizacion))
    respuesta = client.post("/optimizaciones", headers=headers, json={"fecha": FECHA})
    assert respuesta.status_code == 503
    db.expire_all()
    assert db.scalar(select(func.count()).select_from(JobOptimizacion)) == antes


def test_pico_y_placa_excluye_la_flota_demo(client, db, cola):
    headers, _ = _operador(client, db, "op.placa@distrirapido.example.com")
    _conductor(db, dni="70801021")
    _pedido(
        client,
        headers,
        db,
        ventana_inicio="2026-10-19T08:00:00Z",
        ventana_fin="2026-10-19T18:00:00Z",
    )
    antes = db.scalar(select(func.count()).select_from(Ruta))
    alta = client.post("/optimizaciones", headers=headers, json={"fecha": "2026-10-19"})
    assert alta.status_code == 202
    _procesar(db, cola)
    plan = client.get(f"/optimizaciones/{alta.json()['id_job']}", headers=headers).json()
    assert plan["estado"] == "FALLIDO"
    assert "033-2012-MTC" in plan["mensaje"]
    assert plan["rutas"] == []
    assert db.scalar(select(func.count()).select_from(Ruta)) == antes


def test_sin_flota_conserva_el_estado(client, db, cola):
    headers, _ = _operador(client, db, "op.flota@distrirapido.example.com")
    db.execute(text("UPDATE vehiculo SET estado = 'MANTENIMIENTO'"))
    db.commit()
    _pedido(client, headers, db)
    alta = client.post("/optimizaciones", headers=headers, json={"fecha": FECHA})
    _procesar(db, cola)
    plan = client.get(f"/optimizaciones/{alta.json()['id_job']}", headers=headers).json()
    assert plan["estado"] == "FALLIDO"
    assert "flota" in plan["mensaje"].lower()
    assert db.scalar(select(func.count()).select_from(Ruta)) == 0


def test_tiempo_limite_no_deja_rutas(client, db, cola):
    headers, _ = _operador(client, db, "op.tiempo@distrirapido.example.com")
    _conductor(db, dni="70801022")
    _pedido(client, headers, db)
    db.execute(
        text(
            "UPDATE configuracion_sistema SET valor = '0' "
            "WHERE clave = 'tiempo_max_optimizacion_s'"
        )
    )
    db.commit()
    alta = client.post("/optimizaciones", headers=headers, json={"fecha": FECHA})
    _procesar(db, cola)
    plan = client.get(f"/optimizaciones/{alta.json()['id_job']}", headers=headers).json()
    assert plan["estado"] == "FALLIDO"
    assert "tiempo límite" in plan["mensaje"]
    assert db.scalar(select(func.count()).select_from(Ruta)) == 0


def test_capacidad_insuficiente_no_asigna(client, db, cola):
    headers, _ = _operador(client, db, "op.peso@distrirapido.example.com")
    _conductor(db, dni="70801023")
    db.execute(text("UPDATE vehiculo SET estado = 'INACTIVO' WHERE tipo <> 'MOTO'"))
    db.commit()
    _pedido(client, headers, db, peso_kg=80, volumen_m3=0.1)
    alta = client.post("/optimizaciones", headers=headers, json={"fecha": FECHA})
    _procesar(db, cola)
    plan = client.get(f"/optimizaciones/{alta.json()['id_job']}", headers=headers).json()
    assert plan["estado"] == "FALLIDO"
    assert "factible" in plan["mensaje"].lower()


def test_tramo_largo_inserta_descanso_de_una_hora(client, db, cola):
    headers, _ = _operador(client, db, "op.descanso@distrirapido.example.com")
    _conductor(
        db,
        dni="70801024",
        lat_punto_partida=Decimal("-11.9100"),
        lon_punto_partida=Decimal("-77.0200"),
    )
    db.execute(
        text("UPDATE configuracion_sistema SET valor = '4' WHERE clave = 'velocidad_urbana_km_h'")
    )
    db.commit()
    _pedido(client, headers, db, latitud=-12.045, longitud=-76.925, peso_kg=20)
    alta = client.post("/optimizaciones", headers=headers, json={"fecha": FECHA})
    _procesar(db, cola)
    plan = client.get(f"/optimizaciones/{alta.json()['id_job']}", headers=headers).json()
    assert plan["estado"] == "COMPLETADO", plan["mensaje"]
    ruta = plan["rutas"][0]
    assert ruta["minutos_conduccion"] > 240
    assert ruta["minutos_conduccion"] <= 480
    assert len(ruta["descansos"]) == 1
    assert ruta["descansos"][0]["duracion_min"] == 60


def test_confirmacion_rechaza_jornada_de_mas_de_ocho_horas(client, db):
    headers, usuario = _operador(client, db, "op.ley@distrirapido.example.com")
    conductor = _conductor(db, dni="70801025")
    vehiculo = db.scalar(select(Vehiculo).where(Vehiculo.placa == "DMO-102"))
    ruta = Ruta(
        fecha=DIA,
        estado="BORRADOR",
        minutos_conduccion=Decimal("500"),
        distancia_total_km=Decimal("10"),
    )
    db.add(ruta)
    db.flush()
    db.add(
        AsignacionRuta(
            id_ruta=ruta.id_ruta,
            id_vehiculo=vehiculo.id_vehiculo,
            id_conductor=conductor.id_conductor,
        )
    )
    db.commit()
    respuesta = client.post(f"/rutas/{ruta.id_ruta}/confirmar", headers=headers)
    assert respuesta.status_code == 422
    assert "30224" in respuesta.json()["detail"]
    db.expire_all()
    assert db.get(Ruta, ruta.id_ruta).estado == "BORRADOR"
    assert usuario.email.startswith("op.ley")


def test_confirmacion_inserta_descanso_si_faltaba(client, db):
    headers, _ = _operador(client, db, "op.ins@distrirapido.example.com")
    conductor = _conductor(db, dni="70801026")
    vehiculo = db.scalar(select(Vehiculo).where(Vehiculo.placa == "DMO-201"))
    ruta = Ruta(fecha=DIA, estado="BORRADOR", minutos_conduccion=Decimal("300"))
    db.add(ruta)
    db.flush()
    db.add(
        AsignacionRuta(
            id_ruta=ruta.id_ruta,
            id_vehiculo=vehiculo.id_vehiculo,
            id_conductor=conductor.id_conductor,
        )
    )
    db.commit()
    respuesta = client.post(f"/rutas/{ruta.id_ruta}/confirmar", headers=headers)
    assert respuesta.status_code == 200, respuesta.text
    assert "descanso" in respuesta.json()["mensaje"].lower()
    assert len(respuesta.json()["descansos"]) == 1
    db.expire_all()
    assert db.scalar(select(func.count()).select_from(DescansoRuta)) == 1


def test_suma_de_rutas_del_dia_no_puede_pasar_de_ocho_horas(client, db):
    headers, _ = _operador(client, db, "op.suma@distrirapido.example.com")
    conductor = _conductor(db, dni="70801027")
    vehiculo = db.scalar(select(Vehiculo).where(Vehiculo.placa == "DMO-102"))
    previa = Ruta(fecha=DIA, estado="CONFIRMADA", minutos_conduccion=Decimal("300"))
    nueva = Ruta(fecha=DIA, estado="BORRADOR", minutos_conduccion=Decimal("200"))
    db.add_all([previa, nueva])
    db.flush()
    db.add(
        AsignacionRuta(
            id_ruta=previa.id_ruta,
            id_vehiculo=vehiculo.id_vehiculo,
            id_conductor=conductor.id_conductor,
        )
    )
    db.add(
        AsignacionRuta(
            id_ruta=nueva.id_ruta,
            id_vehiculo=vehiculo.id_vehiculo,
            id_conductor=conductor.id_conductor,
        )
    )
    db.commit()
    respuesta = client.post(f"/rutas/{nueva.id_ruta}/confirmar", headers=headers)
    assert respuesta.status_code == 422
    assert "30224" in respuesta.json()["detail"]
    db.expire_all()
    assert db.get(Ruta, nueva.id_ruta).estado == "BORRADOR"


def test_roles_de_optimizacion_y_openapi(client, db, cola):
    operador_headers, _ = _operador(client, db, "op.rol@distrirapido.example.com")
    gerente = crear_usuario(db, email="ger.ruta@distrirapido.example.com", rol="GERENTE")
    conductor = crear_usuario(db, email="con.ruta@distrirapido.example.com", rol="CONDUCTOR")
    assert (
        client.post(
            "/optimizaciones",
            headers=autenticar(client, gerente.email),
            json={"fecha": FECHA},
        ).status_code
        == 403
    )
    assert (
        client.post(
            "/optimizaciones",
            headers=autenticar(client, conductor.email),
            json={"fecha": FECHA},
        ).status_code
        == 403
    )
    assert client.get("/rutas", headers=autenticar(client, conductor.email)).status_code == 403
    especificacion = client.get("/openapi.json").json()
    assert "/optimizaciones" in especificacion["paths"]
    assert "/rutas/{id_ruta}/confirmar" in especificacion["paths"]
    descripcion = especificacion["paths"]["/clientes"]["get"]["description"].lower()
    assert "demostración" in descripcion
    assert "sin altas" in descripcion
    faltante = client.get(
        "/optimizaciones/00000000-0000-0000-0000-000000000000",
        headers=operador_headers,
    )
    assert faltante.status_code == 404
    assert cola.items == []


def test_worker_marca_fallido_si_el_calculo_revienta(client, db, cola, monkeypatch):
    headers, _ = _operador(client, db, "op.fallo@distrirapido.example.com")
    alta = client.post("/optimizaciones", headers=headers, json={"fecha": FECHA})
    id_job = alta.json()["id_job"]

    def _revienta(_db, _fecha):
        raise RuntimeError("fallo de prueba")

    monkeypatch.setattr("app.worker.generar_plan", _revienta)
    procesar_job(db, UUID(id_job))
    db.expire_all()
    job = db.get(JobOptimizacion, id_job)
    assert job.estado == "FALLIDO"
    assert "estado anterior" in job.mensaje
    assert db.scalar(select(func.count()).select_from(Ruta)) == 0


def test_tomar_vacio_no_procesa(db, cola):
    assert iteracion(db) is False
