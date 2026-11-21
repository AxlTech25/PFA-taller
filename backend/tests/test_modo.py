from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal

import pytest
from app.models.entities import (
    AsignacionRuta,
    Cliente,
    Conductor,
    DescansoRuta,
    DetalleRuta,
    Incidencia,
    Pedido,
    Ruta,
    Vehiculo,
)
from app.services.jornada_demo import (
    DESCRIPCION_AVISO,
    DNI_DEMO,
    PARADAS,
    PLACA_DEMO,
    asegurar_jornada_demo,
)
from app.services.jornada_presupuesto import PARADAS as PARADAS_PRESUPUESTO
from app.services.jornada_presupuesto import asegurar_jornada_presupuesto
from app.services.modo import fecha_operativa
from sqlalchemy import func, select, text
from tests.conftest import autenticar, crear_usuario

TOPE_BYTES = 150 * 1024


def test_fecha_operativa_usa_el_dia_civil_de_lima():
    # 22/11 02:30 UTC sigue siendo 21/11 en Lima (UTC−5, sin horario de verano).
    assert fecha_operativa(datetime(2026, 11, 22, 2, 30, tzinfo=UTC)) == date(2026, 11, 21)
    assert fecha_operativa(datetime(2026, 11, 21, 5, 0, tzinfo=UTC)) == date(2026, 11, 21)
    assert fecha_operativa(datetime(2026, 11, 21, 4, 59, tzinfo=UTC)) == date(2026, 11, 20)
    assert fecha_operativa(datetime(2026, 11, 21, 23, 30)) == date(2026, 11, 21)


def _cliente(db) -> Cliente:
    cliente = db.scalar(
        select(Cliente).where(Cliente.email == "demo.consentido@distrirapido.example.com")
    )
    assert cliente is not None
    return cliente


def _vehiculo(db, placa: str = "DMO-101") -> Vehiculo:
    vehiculo = db.scalar(select(Vehiculo).where(Vehiculo.placa == placa))
    assert vehiculo is not None
    return vehiculo


def _marcar(dia: date, hora: int, minuto: int) -> datetime:
    return datetime(dia.year, dia.month, dia.day, hora, minuto, tzinfo=UTC)


def _conductor(db, usuario, dni: str) -> Conductor:
    fila = Conductor(
        id_usuario=usuario.id_usuario,
        dni=dni,
        nombre=f"Conductor {dni}",
        licencia_categoria="A-IIb",
        anios_experiencia=2,
        disponibilidad_inicio=time(8, 0),
        disponibilidad_fin=time(17, 0),
        lat_punto_partida=Decimal("-12.0100000"),
        lon_punto_partida=Decimal("-76.9800000"),
        estado="ACTIVO",
    )
    db.add(fila)
    db.flush()
    return fila


def _pedido(db, cliente, dia: date, referencia: str, inicio: tuple[int, int], fin: tuple[int, int]):
    pedido = Pedido(
        id_cliente=cliente.id_cliente,
        direccion=f"Calle {referencia}",
        punto_referencia=referencia,
        latitud=Decimal("-12.0100000"),
        longitud=Decimal("-76.9800000"),
        peso_kg=Decimal("5.00"),
        volumen_m3=Decimal("0.100"),
        ventana_inicio=_marcar(dia, *inicio),
        ventana_fin=_marcar(dia, *fin),
        prioridad="ESTANDAR",
        tipo_producto="NO_PERECEDERO",
        estado="ASIGNADO",
        georreferencia_aproximada=True,
    )
    db.add(pedido)
    db.flush()
    return pedido


def _ruta(
    db,
    conductor,
    vehiculo,
    dia: date,
    paradas: list[tuple[Pedido, datetime | None]],
    *,
    estado: str = "CONFIRMADA",
    asignada_en: datetime | None = None,
) -> Ruta:
    ruta = Ruta(fecha=dia, estado=estado)
    db.add(ruta)
    db.flush()
    db.add(
        AsignacionRuta(
            id_ruta=ruta.id_ruta,
            id_vehiculo=vehiculo.id_vehiculo,
            id_conductor=conductor.id_conductor,
            asignada_en=asignada_en or datetime.now(UTC),
        )
    )
    for secuencia, (pedido, eta) in enumerate(paradas, start=1):
        db.add(
            DetalleRuta(
                id_ruta=ruta.id_ruta,
                id_pedido=pedido.id_pedido,
                secuencia=secuencia,
                eta=eta,
                estado_entrega="PENDIENTE",
            )
        )
    db.flush()
    return ruta


def test_conductor_ve_su_ruta_y_no_la_de_otro(client, db):
    dia = fecha_operativa()
    cliente = _cliente(db)
    vehiculo = _vehiculo(db)
    propio = crear_usuario(db, email="propio.modo@distrirapido.example.com", rol="CONDUCTOR")
    ajeno = crear_usuario(db, email="ajeno.modo@distrirapido.example.com", rol="CONDUCTOR")
    ficha_propia = _conductor(db, propio, "70015001")
    ficha_ajena = _conductor(db, ajeno, "70015002")
    pedido_propio = _pedido(db, cliente, dia, "propia-modo", (8, 0), (12, 0))
    pedido_ajeno = _pedido(db, cliente, dia, "ajena-modo", (8, 0), (12, 0))
    ruta_propia = _ruta(
        db,
        ficha_propia,
        vehiculo,
        dia,
        [(pedido_propio, _marcar(dia, 9, 0))],
    )
    _ruta(db, ficha_ajena, _vehiculo(db, "DMO-102"), dia, [(pedido_ajeno, _marcar(dia, 9, 30))])
    respuesta = client.get("/modo/jornada", headers=autenticar(client, propio.email))
    assert respuesta.status_code == 200, respuesta.text
    cuerpo = respuesta.json()
    assert cuerpo["hay_ruta"] is True
    assert cuerpo["id_ruta"] == str(ruta_propia.id_ruta)
    assert cuerpo["placa"] == "DMO-101"
    assert [parada["punto_referencia"] for parada in cuerpo["paradas"]] == ["propia-modo"]
    assert "ajena-modo" not in respuesta.text
    assert "latitud" not in respuesta.text
    assert "co2" not in respuesta.text
    assert "combustible" not in respuesta.text
    assert "arboles" not in respuesta.text
    con_query = client.get(
        f"/modo/jornada?id_ruta={cuerpo['id_ruta']}",
        headers=autenticar(client, ajeno.email),
    )
    assert con_query.status_code == 200
    assert con_query.json()["paradas"][0]["punto_referencia"] == "ajena-modo"


def test_sin_ruta_confirmada_hoy(client, db):
    dia = fecha_operativa()
    usuario = crear_usuario(db, email="vacio.modo@distrirapido.example.com", rol="CONDUCTOR")
    ficha = _conductor(db, usuario, "70015003")
    pedido = _pedido(db, _cliente(db), dia, "borrador-modo", (8, 0), (12, 0))
    _ruta(db, ficha, _vehiculo(db), dia, [(pedido, _marcar(dia, 9, 0))], estado="BORRADOR")
    ayer = dia - timedelta(days=1)
    pedido_ayer = _pedido(db, _cliente(db), ayer, "ayer-modo", (8, 0), (12, 0))
    _ruta(db, ficha, _vehiculo(db), ayer, [(pedido_ayer, _marcar(ayer, 9, 0))])
    respuesta = client.get("/modo/jornada", headers=autenticar(client, usuario.email))
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["hay_ruta"] is False
    assert cuerpo["mensaje"] == "No tiene una ruta confirmada para hoy."
    assert cuerpo["paradas"] == []
    assert cuerpo["fecha"] == dia.isoformat()


def test_en_ejecucion_cuenta_y_la_mas_reciente_gana(client, db):
    dia = fecha_operativa()
    usuario = crear_usuario(db, email="activa.modo@distrirapido.example.com", rol="CONDUCTOR")
    ficha = _conductor(db, usuario, "70015004")
    cliente = _cliente(db)
    vehiculo = _vehiculo(db)
    base = datetime.now(UTC)
    temprana = _pedido(db, cliente, dia, "temprana-modo", (8, 0), (12, 0))
    reciente = _pedido(db, cliente, dia, "reciente-modo", (8, 0), (12, 0))
    _ruta(
        db,
        ficha,
        vehiculo,
        dia,
        [(temprana, _marcar(dia, 9, 0))],
        estado="CONFIRMADA",
        asignada_en=base,
    )
    nueva = _ruta(
        db,
        ficha,
        _vehiculo(db, "DMO-102"),
        dia,
        [(reciente, _marcar(dia, 11, 0))],
        estado="EN_EJECUCION",
        asignada_en=base + timedelta(minutes=5),
    )
    borrador = _pedido(db, cliente, dia, "tarde-borrador", (8, 0), (12, 0))
    _ruta(
        db,
        ficha,
        vehiculo,
        dia,
        [(borrador, _marcar(dia, 15, 0))],
        estado="BORRADOR",
        asignada_en=base + timedelta(hours=1),
    )
    cuerpo = client.get("/modo/jornada", headers=autenticar(client, usuario.email)).json()
    assert cuerpo["id_ruta"] == str(nueva.id_ruta)
    assert cuerpo["placa"] == "DMO-102"
    assert cuerpo["paradas"][0]["punto_referencia"] == "reciente-modo"


def test_alertas_de_semaforo_ventana_descanso_e_incidencia(client, db):
    dia = fecha_operativa()
    usuario = crear_usuario(db, email="alerta.modo@distrirapido.example.com", rol="CONDUCTOR")
    ficha = _conductor(db, usuario, "70015005")
    cliente = _cliente(db)
    en_punta = _pedido(db, cliente, dia, "punta-modo", (7, 0), (11, 0))
    fuera = _pedido(db, cliente, dia, "fuera-modo", (11, 0), (12, 0))
    sin_hora = _pedido(db, cliente, dia, "sin-hora-modo", (13, 0), (16, 0))
    ruta = _ruta(
        db,
        ficha,
        _vehiculo(db),
        dia,
        [
            (en_punta, _marcar(dia, 8, 15)),
            (fuera, _marcar(dia, 12, 20)),
            (sin_hora, None),
        ],
    )
    db.add(
        DescansoRuta(
            id_ruta=ruta.id_ruta,
            despues_de_secuencia=1,
            duracion_min=60,
            motivo="LEY_30224",
        )
    )
    db.add(DescansoRuta(id_ruta=ruta.id_ruta, despues_de_secuencia=0, duracion_min=60))
    ahora = datetime.now(UTC)
    db.add(
        Incidencia(
            tipo="CONGESTION",
            origen="MANUAL",
            id_ruta=ruta.id_ruta,
            descripcion="  Congestión reportada en el tramo de la ruta.  ",
            estado="PENDIENTE",
            reportada_en=ahora,
        )
    )
    db.add(
        Incidencia(
            tipo="AVERIA_VEHICULO",
            origen="MANUAL",
            id_ruta=ruta.id_ruta,
            descripcion=None,
            estado="PENDIENTE",
            reportada_en=ahora + timedelta(seconds=1),
        )
    )
    db.add(
        Incidencia(
            tipo="ACCIDENTE_TRANSITO",
            origen="MANUAL",
            id_ruta=ruta.id_ruta,
            descripcion="Ya resuelto",
            estado="DESCARTADA",
        )
    )
    db.commit()
    cuerpo = client.get("/modo/jornada", headers=autenticar(client, usuario.email)).json()
    textos = [alerta["texto"] for alerta in cuerpo["alertas"]]
    assert textos[0] == "Congestión reportada en el tramo de la ruta."
    assert "Hay una avería de vehículo reportada." in textos
    assert "Ya resuelto" not in textos
    assert "Parada 1: semáforo amarillo en la llegada estimada." in textos
    assert "Parada 2: la llegada estimada queda fuera de la ventana del cliente." in textos
    assert any("Después de la parada 1 hay un descanso de 60 min" in texto for texto in textos)
    assert any("La jornada incluye un descanso de 60 min" in texto for texto in textos)
    assert cuerpo["paradas"][0]["nivel_congestion"] == "AMARILLO"
    assert cuerpo["paradas"][1]["nivel_congestion"] == "VERDE"
    assert cuerpo["paradas"][2]["nivel_congestion"] == "VERDE"
    assert cuerpo["paradas"][2]["eta"] is None
    codigos = {alerta["codigo"] for alerta in cuerpo["alertas"]}
    assert codigos == {"INCIDENCIA", "CONGESTION", "VENTANA", "DESCANSO"}


def test_semaforo_rojo_usa_el_factor_configurado(client, db):
    dia = fecha_operativa()
    usuario = crear_usuario(db, email="rojo.modo@distrirapido.example.com", rol="CONDUCTOR")
    ficha = _conductor(db, usuario, "70015006")
    pedido = _pedido(db, _cliente(db), dia, "rojo-modo", (10, 0), (16, 0))
    _ruta(db, ficha, _vehiculo(db), dia, [(pedido, _marcar(dia, 11, 0))])
    db.execute(
        text(
            "UPDATE configuracion_sistema SET valor = '1.35' "
            "WHERE clave = 'factor_congestion'"
        )
    )
    db.commit()
    cuerpo = client.get("/modo/jornada", headers=autenticar(client, usuario.email)).json()
    assert cuerpo["paradas"][0]["nivel_congestion"] == "ROJO"
    assert cuerpo["alertas"][0]["texto"] == "Parada 1: semáforo rojo en la llegada estimada."


def test_doce_paradas_siguen_bajo_el_presupuesto(client, db):
    dia = fecha_operativa()
    usuario = crear_usuario(db, email="doce.modo@distrirapido.example.com", rol="CONDUCTOR")
    ficha = _conductor(db, usuario, "70015007")
    cliente = _cliente(db)
    paradas = []
    for numero in range(1, 13):
        pedido = _pedido(db, cliente, dia, f"doce-{numero}", (8, 0), (18, 0))
        pedido.direccion = f"Av. de la demostración {numero}, San Juan de Lurigancho"
        paradas.append((pedido, _marcar(dia, 9, numero)))
    _ruta(db, ficha, _vehiculo(db), dia, paradas)
    respuesta = client.get("/modo/jornada", headers=autenticar(client, usuario.email))
    assert respuesta.status_code == 200
    assert len(respuesta.json()["paradas"]) == 12
    assert len(respuesta.content) <= TOPE_BYTES


def test_sin_ficha_y_sin_sesion(client, db):
    usuario = crear_usuario(db, email="sinficha.modo@distrirapido.example.com", rol="CONDUCTOR")
    respuesta = client.get("/modo/jornada", headers=autenticar(client, usuario.email))
    assert respuesta.status_code == 200
    assert respuesta.json()["hay_ruta"] is False
    assert client.get("/modo/jornada").status_code == 401


@pytest.mark.parametrize("rol", ["ADMIN", "GERENTE", "OPERADOR", "AUDITOR"])
def test_otros_roles_reciben_403(client, db, rol):
    usuario = crear_usuario(db, email=f"{rol.lower()}.modo@distrirapido.example.com", rol=rol)
    respuesta = client.get("/modo/jornada", headers=autenticar(client, usuario.email))
    assert respuesta.status_code == 403


def test_no_hay_escritura_de_entrega(client, db):
    usuario = crear_usuario(db, email="escritura.modo@distrirapido.example.com", rol="CONDUCTOR")
    headers = autenticar(client, usuario.email)
    respuesta = client.post(
        "/modo/jornada",
        headers=headers,
        json={"estado_entrega": "ENTREGADO"},
    )
    assert respuesta.status_code == 405
    contrato = client.get("/openapi.json").json()["paths"]["/modo/jornada"]
    assert "post" not in contrato
    assert "US-018" in contrato["get"]["description"]
    assert "id_detalle" in contrato["get"]["description"]


def test_jornada_demo_es_idempotente_y_cae_en_hoy(client, db):
    usuario = crear_usuario(db, email="demo.modo@distrirapido.example.com", rol="CONDUCTOR")
    assert asegurar_jornada_demo(db, usuario) is True
    assert asegurar_jornada_demo(db, usuario) is True
    claves = [spec["referencia"] for spec in PARADAS]
    referencias = set(
        db.scalars(select(Pedido.punto_referencia).where(Pedido.punto_referencia.in_(claves))).all()
    )
    assert referencias == set(claves)
    rutas = db.scalar(
        select(func.count())
        .select_from(Ruta)
        .join(AsignacionRuta, AsignacionRuta.id_ruta == Ruta.id_ruta)
        .join(Conductor, Conductor.id_conductor == AsignacionRuta.id_conductor)
        .where(Conductor.dni == DNI_DEMO)
    )
    assert rutas == 1
    avisos = db.scalar(
        select(func.count())
        .select_from(Incidencia)
        .where(Incidencia.descripcion == DESCRIPCION_AVISO)
    )
    assert avisos == 1
    ruta = db.scalar(
        select(Ruta)
        .join(AsignacionRuta, AsignacionRuta.id_ruta == Ruta.id_ruta)
        .join(Conductor, Conductor.id_conductor == AsignacionRuta.id_conductor)
        .where(Conductor.dni == DNI_DEMO)
    )
    ruta.fecha = fecha_operativa() - timedelta(days=1)
    db.flush()
    assert asegurar_jornada_demo(db, usuario) is True
    db.expire_all()
    assert db.get(Ruta, ruta.id_ruta).fecha == fecha_operativa()
    cuerpo = client.get("/modo/jornada", headers=autenticar(client, usuario.email)).json()
    assert cuerpo["hay_ruta"] is True
    assert cuerpo["placa"] == PLACA_DEMO
    assert len(cuerpo["paradas"]) == 3
    assert cuerpo["paradas"][0]["estado_entrega"] == "PENDIENTE"
    assert cuerpo["paradas"][0]["cliente"] == "Bodega El Ahorro"
    textos = " ".join(alerta["texto"] for alerta in cuerpo["alertas"])
    assert "semáforo amarillo" in textos
    assert "fuera de la ventana" in textos
    assert DESCRIPCION_AVISO in textos
    assert "distancia_total_km" not in cuerpo
    assert "co2_estimado_kg" not in cuerpo


def test_sin_catalogo_demo_no_crea_conductor(db, monkeypatch):
    monkeypatch.setattr("app.services.jornada_demo.PLACA_DEMO", "NO-EXISTE")
    usuario = crear_usuario(db, email="sin.catalogo@distrirapido.example.com", rol="CONDUCTOR")
    assert asegurar_jornada_demo(db, usuario) is False
    assert db.scalar(select(Conductor).where(Conductor.id_usuario == usuario.id_usuario)) is None


def test_no_reemplaza_otra_ficha_ni_otro_dni(db):
    usuario = crear_usuario(db, email="otra.ficha@distrirapido.example.com", rol="CONDUCTOR")
    _conductor(db, usuario, "70015008")
    assert asegurar_jornada_demo(db, usuario) is False
    dueno = crear_usuario(db, email="dueno.dni@distrirapido.example.com", rol="CONDUCTOR")
    _conductor(db, dueno, DNI_DEMO)
    nuevo = crear_usuario(db, email="nuevo.dni@distrirapido.example.com", rol="CONDUCTOR")
    assert asegurar_jornada_demo(db, nuevo) is False


def test_mapa_opcional_y_ruta_de_doce_paradas(client, db):
    usuario = crear_usuario(db, email="presupuesto.modo@distrirapido.example.com", rol="CONDUCTOR")
    assert asegurar_jornada_presupuesto(db, usuario) is True
    assert asegurar_jornada_presupuesto(db, usuario) is True
    headers = autenticar(client, usuario.email)
    jornada = client.get("/modo/jornada", headers=headers)
    assert jornada.status_code == 200, jornada.text
    cuerpo = jornada.json()
    assert len(cuerpo["paradas"]) == PARADAS_PRESUPUESTO
    assert "latitud" not in jornada.text
    assert len(jornada.content) <= TOPE_BYTES
    mapa = client.get("/modo/mapa", headers=headers)
    assert mapa.status_code == 200, mapa.text
    puntos = mapa.json()["puntos"]
    assert len(puntos) == PARADAS_PRESUPUESTO
    assert puntos[0]["secuencia"] == 1
    assert "latitud" in puntos[0]
    ajeno = crear_usuario(db, email="ajeno.mapa@distrirapido.example.com", rol="CONDUCTOR")
    ajeno_mapa = client.get("/modo/mapa", headers=autenticar(client, ajeno.email))
    assert ajeno_mapa.json()["hay_ruta"] is False
    operador = crear_usuario(db, email="op.mapa@distrirapido.example.com", rol="OPERADOR")
    operador_mapa = client.get("/modo/mapa", headers=autenticar(client, operador.email))
    assert operador_mapa.status_code == 403
