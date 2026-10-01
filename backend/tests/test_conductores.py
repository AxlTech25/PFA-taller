from app.models.entities import Conductor, LogAuditoria
from sqlalchemy import func, select
from tests.conftest import autenticar, crear_usuario


def _alta(**cambios: object) -> dict:
    datos: dict = {
        "nombre": "Luis Ramos",
        "dni": "45678912",
        "licencia_categoria": "A-IIIb",
        "anios_experiencia": 6,
        "disponibilidad_inicio": "06:00",
        "disponibilidad_fin": "14:00",
        "lat_punto_partida": -12.01,
        "lon_punto_partida": -76.98,
    }
    datos.update(cambios)
    return datos


def test_operador_registra_conductor_activo(client, db):
    operador = crear_usuario(db, email="op.conductor@distrirapido.example.com")
    headers = autenticar(client, operador.email)
    alta = client.post("/conductores", headers=headers, json=_alta())
    assert alta.status_code == 201
    cuerpo = alta.json()
    assert cuerpo["mensaje"] == "Conductor registrado correctamente"
    assert cuerpo["estado"] == "ACTIVO"
    assert cuerpo["dni"] == "45678912"
    listado = client.get("/conductores", headers=headers)
    assert listado.status_code == 200
    assert any(item["dni"] == "45678912" for item in listado.json())
    db.expire_all()
    evento = db.scalar(select(LogAuditoria).where(LogAuditoria.accion == "crear_conductor"))
    assert evento is not None
    assert evento.datos_nuevos["dni"] == "45678912"


def test_dni_duplicado_y_horario_invalido(client, db):
    operador = crear_usuario(db, email="op.dni@distrirapido.example.com")
    headers = autenticar(client, operador.email)
    assert client.post("/conductores", headers=headers, json=_alta()).status_code == 201
    duplicado = client.post("/conductores", headers=headers, json=_alta(nombre="Otra Persona"))
    assert duplicado.status_code == 409
    assert duplicado.json()["detail"] == "El DNI ya se encuentra registrado"
    horario = client.post(
        "/conductores",
        headers=headers,
        json=_alta(dni="12345678", disponibilidad_inicio="18:00", disponibilidad_fin="08:00"),
    )
    assert horario.status_code == 422
    assert "hora" in horario.json()["detail"].lower()
    antes = db.scalar(select(func.count()).select_from(Conductor))
    inyeccion = client.post(
        "/conductores",
        headers=headers,
        json=_alta(dni="87654321", nombre="<script>alert(1)</script>"),
    )
    assert inyeccion.status_code == 422
    db.expire_all()
    assert db.scalar(select(func.count()).select_from(Conductor)) == antes
    evento = db.scalar(select(LogAuditoria).where(LogAuditoria.accion == "entrada_rechazada"))
    assert evento is not None
    assert evento.tabla_afectada == "conductor"


def test_conductor_solo_ve_su_ficha_y_no_registra(client, db):
    operador = crear_usuario(db, email="op.ver@distrirapido.example.com")
    propio = crear_usuario(db, email="yo.conductor@distrirapido.example.com", rol="CONDUCTOR")
    ajeno = crear_usuario(db, email="otro.conductor@distrirapido.example.com", rol="CONDUCTOR")
    headers = autenticar(client, operador.email)
    creado = client.post("/conductores", headers=headers, json=_alta()).json()
    client.post("/conductores", headers=headers, json=_alta(dni="11112222", nombre="Ana Pérez"))
    ficha = db.get(Conductor, creado["id_conductor"])
    ficha.id_usuario = propio.id_usuario
    db.commit()
    mio = client.get("/conductores", headers=autenticar(client, propio.email))
    assert mio.status_code == 200
    assert len(mio.json()) == 1
    assert mio.json()[0]["dni"] == "45678912"
    vacio = client.get("/conductores", headers=autenticar(client, ajeno.email))
    assert vacio.json() == []
    denegado = client.post(
        "/conductores",
        headers=autenticar(client, propio.email),
        json=_alta(dni="33334444"),
    )
    assert denegado.status_code == 403


def test_auditor_recibe_conductor_sin_datos_personales(client, db):
    operador = crear_usuario(db, email="op.anon@distrirapido.example.com")
    auditor = crear_usuario(db, email="auditor.cond@distrirapido.example.com", rol="AUDITOR")
    client.post(
        "/conductores",
        headers=autenticar(client, operador.email),
        json=_alta(),
    )
    listado = client.get("/conductores", headers=autenticar(client, auditor.email))
    assert listado.status_code == 200
    fila = listado.json()[0]
    assert fila["dni"] is None
    assert fila["lat_punto_partida"] is None
    assert fila["nombre"] == "Conductor"
