from app.models.entities import LogAuditoria
from sqlalchemy import select
from tests.conftest import autenticar, crear_usuario, vehiculo_valido


def test_operador_registra_vehiculo(client, db):
    operador = crear_usuario(db, email="op.flota@distrirapido.example.com")
    headers = autenticar(client, operador.email)
    respuesta = client.post("/vehiculos", headers=headers, json=vehiculo_valido())
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["mensaje"] == "Vehículo registrado correctamente"
    assert cuerpo["placa"] == "ABC123"
    assert cuerpo["estado"] == "ACTIVO"
    db.expire_all()
    evento = db.scalar(select(LogAuditoria).where(LogAuditoria.accion == "crear_vehiculo"))
    assert evento is not None


def test_placa_duplicada_y_capacidad_invalida(client, db):
    operador = crear_usuario(db, email="op.placa@distrirapido.example.com")
    headers = autenticar(client, operador.email)
    alta = client.post("/vehiculos", headers=headers, json=vehiculo_valido(placa="xyz-12"))
    assert alta.status_code == 201
    assert alta.json()["placa"] == "XYZ-12"
    duplicada = client.post("/vehiculos", headers=headers, json=vehiculo_valido(placa="xyz-12"))
    assert duplicada.status_code == 409
    assert duplicada.json()["detail"] == "La placa ya se encuentra registrada"
    invalida = client.post(
        "/vehiculos", headers=headers, json=vehiculo_valido(placa="NEW1", capacidad_kg=-5)
    )
    assert invalida.status_code == 422
    assert invalida.json()["detail"] == "Datos de capacidad inválidos"
    futuro = client.post(
        "/vehiculos",
        headers=headers,
        json=vehiculo_valido(placa="NEW2", anio_fabricacion=2035),
    )
    assert futuro.status_code == 422
    assert futuro.json()["detail"] == "El año de fabricación no es válido"


def test_listado_muestra_la_flota_demo_y_un_conductor_no_registra(client, db):
    operador = crear_usuario(db, email="op.lista@distrirapido.example.com")
    conductor = crear_usuario(db, email="conductor.flota@distrirapido.example.com", rol="CONDUCTOR")
    headers = autenticar(client, operador.email)
    listado = client.get("/vehiculos", headers=headers)
    assert listado.status_code == 200
    placas = {item["placa"] for item in listado.json()}
    assert {"DMO-101", "DMO-102", "DMO-201", "DMO-301"} <= placas
    denegado = client.post(
        "/vehiculos",
        headers=autenticar(client, conductor.email),
        json=vehiculo_valido(placa="NOPE01"),
    )
    assert denegado.status_code == 403
    peligroso = client.post(
        "/vehiculos",
        headers=headers,
        json=vehiculo_valido(placa="<script>"),
    )
    assert peligroso.status_code == 422


def test_operador_actualiza_estado_y_factor_y_deja_auditoria(client, db):
    operador = crear_usuario(db, email="op.edita@distrirapido.example.com")
    headers = autenticar(client, operador.email)
    listado = client.get("/vehiculos", headers=headers).json()
    objetivo = next(item for item in listado if item["placa"] == "DMO-101")
    respuesta = client.put(
        f"/vehiculos/{objetivo['id_vehiculo']}",
        headers=headers,
        json={"estado": "MANTENIMIENTO", "factor_emision_co2": 0.31},
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "MANTENIMIENTO"
    assert respuesta.json()["factor_emision_co2"] == 0.31
    db.expire_all()
    evento = db.scalar(select(LogAuditoria).where(LogAuditoria.accion == "actualizar_vehiculo"))
    assert evento is not None
    assert evento.datos_anteriores["estado"] == "ACTIVO"
    assert evento.datos_nuevos["estado"] == "MANTENIMIENTO"
    assert evento.ip_origen is None or evento.accion == "actualizar_vehiculo"


def test_conductor_no_edita_flota_y_el_registro_no_cambia(client, db):
    operador = crear_usuario(db, email="op.base@distrirapido.example.com")
    conductor = crear_usuario(db, email="conductor.edita@distrirapido.example.com", rol="CONDUCTOR")
    headers = autenticar(client, operador.email)
    listado = client.get("/vehiculos", headers=headers).json()
    objetivo = next(item for item in listado if item["placa"] == "DMO-102")
    denegado = client.put(
        f"/vehiculos/{objetivo['id_vehiculo']}",
        headers=autenticar(client, conductor.email),
        json={"estado": "INACTIVO"},
    )
    assert denegado.status_code == 403
    despues = client.get(f"/vehiculos/{objetivo['id_vehiculo']}", headers=headers)
    assert despues.json()["estado"] == "ACTIVO"


def test_actualizacion_vacia_o_factor_invalido(client, db):
    gerente = crear_usuario(db, email="gerente.flota@distrirapido.example.com", rol="GERENTE")
    headers = autenticar(client, gerente.email)
    listado = client.get("/vehiculos", headers=headers).json()
    objetivo = next(item for item in listado if item["placa"] == "DMO-201")
    vacio = client.put(f"/vehiculos/{objetivo['id_vehiculo']}", headers=headers, json={})
    assert vacio.status_code == 422
    invalido = client.put(
        f"/vehiculos/{objetivo['id_vehiculo']}",
        headers=headers,
        json={"factor_emision_co2": 0},
    )
    assert invalido.status_code == 422
    assert "factor" in invalido.json()["detail"].lower()
