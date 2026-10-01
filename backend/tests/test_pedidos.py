from app.models.entities import Cliente, LogAuditoria, Pedido
from sqlalchemy import func, select
from tests.conftest import autenticar, crear_usuario

CORREO_OK = "demo.consentido@distrirapido.example.com"
CORREO_NO = "demo.sin.consentimiento@distrirapido.example.com"


def _cliente(db, correo: str) -> Cliente:
    cliente = db.scalar(select(Cliente).where(Cliente.email == correo))
    assert cliente is not None
    return cliente


def _alta(id_cliente: str, **cambios: object) -> dict:
    datos: dict = {
        "id_cliente": id_cliente,
        "direccion": "Av. Próceres de la Independencia 1200",
        "latitud": -12.0025,
        "longitud": -76.9901,
        "peso_kg": 25,
        "volumen_m3": 0.4,
        "ventana_inicio": "2026-09-16T08:00:00Z",
        "ventana_fin": "2026-09-16T12:00:00Z",
        "prioridad": "ESTANDAR",
        "tipo_producto": "NO_PERECEDERO",
    }
    datos.update(cambios)
    return datos


def test_operador_registra_pedido_pendiente_con_consentimiento(client, db):
    operador = crear_usuario(db, email="op.pedido@distrirapido.example.com")
    headers = autenticar(client, operador.email)
    cliente = _cliente(db, CORREO_OK)
    clientes = client.get("/clientes", headers=headers)
    assert clientes.status_code == 200
    assert any(
        item["email"] == CORREO_OK and item["consentimiento_datos"] for item in clientes.json()
    )
    alta = client.post("/pedidos", headers=headers, json=_alta(str(cliente.id_cliente)))
    assert alta.status_code == 201
    cuerpo = alta.json()
    assert cuerpo["mensaje"] == "Pedido registrado correctamente"
    assert cuerpo["estado"] == "PENDIENTE"
    assert cuerpo["nombre_cliente"] == "Bodega El Ahorro"
    listado = client.get("/pedidos", headers=headers)
    assert any(item["id_pedido"] == cuerpo["id_pedido"] for item in listado.json())
    db.expire_all()
    evento = db.scalar(select(LogAuditoria).where(LogAuditoria.accion == "crear_pedido"))
    assert evento is not None
    assert evento.datos_nuevos["estado"] == "PENDIENTE"


def test_pedido_sin_consentimiento_se_rechaza(client, db):
    operador = crear_usuario(db, email="op.ley@distrirapido.example.com")
    cliente = _cliente(db, CORREO_NO)
    antes = db.scalar(select(func.count()).select_from(Pedido))
    respuesta = client.post(
        "/pedidos",
        headers=autenticar(client, operador.email),
        json=_alta(str(cliente.id_cliente)),
    )
    assert respuesta.status_code == 422
    assert "consentimiento" in respuesta.json()["detail"].lower()
    db.expire_all()
    assert db.scalar(select(func.count()).select_from(Pedido)) == antes
    evento = db.scalar(
        select(LogAuditoria).where(LogAuditoria.accion == "pedido_sin_consentimiento")
    )
    assert evento is not None


def test_inyeccion_en_pedido_no_persiste(client, db):
    operador = crear_usuario(db, email="op.xss@distrirapido.example.com")
    cliente = _cliente(db, CORREO_OK)
    antes = db.scalar(select(func.count()).select_from(Pedido))
    respuesta = client.post(
        "/pedidos",
        headers=autenticar(client, operador.email),
        json=_alta(str(cliente.id_cliente), direccion="' OR '1'='1"),
    )
    assert respuesta.status_code == 422
    assert respuesta.json()["detail"] == "La entrada contiene un patrón no permitido"
    db.expire_all()
    assert db.scalar(select(func.count()).select_from(Pedido)) == antes
    evento = db.scalar(select(LogAuditoria).where(LogAuditoria.accion == "entrada_rechazada"))
    assert evento.tabla_afectada == "pedido"


def test_ventana_invalida_peso_y_roles(client, db):
    operador = crear_usuario(db, email="op.valida@distrirapido.example.com")
    conductor = crear_usuario(
        db, email="conductor.pedido@distrirapido.example.com", rol="CONDUCTOR"
    )
    auditor = crear_usuario(db, email="auditor.pedido@distrirapido.example.com", rol="AUDITOR")
    cliente = _cliente(db, CORREO_OK)
    headers = autenticar(client, operador.email)
    ventana = client.post(
        "/pedidos",
        headers=headers,
        json=_alta(
            str(cliente.id_cliente),
            ventana_inicio="2026-09-16T18:00:00Z",
            ventana_fin="2026-09-16T08:00:00Z",
        ),
    )
    assert ventana.status_code == 422
    peso = client.post(
        "/pedidos",
        headers=headers,
        json=_alta(str(cliente.id_cliente), peso_kg=0),
    )
    assert peso.status_code == 422
    assert client.post(
        "/pedidos",
        headers=autenticar(client, conductor.email),
        json=_alta(str(cliente.id_cliente)),
    ).status_code == 403
    creado = client.post(
        "/pedidos",
        headers=headers,
        json=_alta(str(cliente.id_cliente), direccion="Mz K lote 4"),
    )
    assert creado.status_code == 201
    anonimo = client.get("/pedidos", headers=autenticar(client, auditor.email))
    assert anonimo.status_code == 200
    fila = next(item for item in anonimo.json() if item["id_pedido"] == creado.json()["id_pedido"])
    assert fila["direccion"] is None
    assert fila["latitud"] is None
    assert client.get("/pedidos", headers=autenticar(client, conductor.email)).json() == []
    clientes = client.get("/clientes", headers=autenticar(client, auditor.email))
    assert all(item["email"] is None and item["telefono"] is None for item in clientes.json())
    assert client.get("/clientes", headers=autenticar(client, conductor.email)).status_code == 403
    assert client.post(
        "/pedidos",
        headers=headers,
        json=_alta("00000000-0000-0000-0000-000000000000"),
    ).status_code == 404
