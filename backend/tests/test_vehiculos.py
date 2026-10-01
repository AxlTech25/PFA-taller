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
