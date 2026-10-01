from app.models.entities import LogAuditoria, Usuario
from sqlalchemy import func, select
from tests.conftest import autenticar, crear_usuario


def _alta(**cambios: object) -> dict:
    datos: dict = {
        "email": "nuevo.conductor@distrirapido.example.com",
        "password": "clave-segura",
        "rol": "CONDUCTOR",
        "estado": "ACTIVO",
    }
    datos.update(cambios)
    return datos


def test_admin_crea_conductor_y_audita(client, db):
    admin = crear_usuario(db, email="admin.usuarios@distrirapido.example.com", rol="ADMIN")
    headers = autenticar(client, admin.email)
    alta = client.post("/usuarios", headers=headers, json=_alta())
    assert alta.status_code == 201
    cuerpo = alta.json()
    assert cuerpo["mensaje"] == "Usuario registrado correctamente"
    assert cuerpo["rol"] == "CONDUCTOR"
    assert cuerpo["estado"] == "ACTIVO"
    assert "password" not in cuerpo
    sesion = client.post(
        "/auth/login",
        json={"email": "nuevo.conductor@distrirapido.example.com", "password": "clave-segura"},
    )
    assert sesion.status_code == 200
    assert sesion.json()["rol"] == "CONDUCTOR"
    db.expire_all()
    evento = db.scalar(select(LogAuditoria).where(LogAuditoria.accion == "crear_usuario"))
    assert evento is not None
    assert evento.datos_nuevos["rol"] == "CONDUCTOR"


def test_operador_no_crea_administradores(client, db):
    operador = crear_usuario(db, email="op.usuarios@distrirapido.example.com")
    antes = db.scalar(select(func.count()).select_from(Usuario))
    respuesta = client.post(
        "/usuarios",
        headers=autenticar(client, operador.email),
        json=_alta(email="intruso@distrirapido.example.com", rol="ADMIN"),
    )
    assert respuesta.status_code == 403
    db.expire_all()
    assert db.scalar(select(func.count()).select_from(Usuario)) == antes


def test_admin_cambia_rol_y_desactiva(client, db):
    admin = crear_usuario(db, email="admin.rol@distrirapido.example.com", rol="ADMIN")
    headers = autenticar(client, admin.email)
    creado = client.post(
        "/usuarios",
        headers=headers,
        json=_alta(email="rotar@distrirapido.example.com", rol="OPERADOR"),
    ).json()
    cambio = client.patch(
        f"/usuarios/{creado['id_usuario']}",
        headers=headers,
        json={"rol": "CONDUCTOR", "estado": "INACTIVO"},
    )
    assert cambio.status_code == 200
    assert cambio.json()["rol"] == "CONDUCTOR"
    assert cambio.json()["estado"] == "INACTIVO"
    ingreso = client.post(
        "/auth/login",
        json={"email": "rotar@distrirapido.example.com", "password": "clave-segura"},
    )
    assert ingreso.status_code == 403
    db.expire_all()
    evento = db.scalar(select(LogAuditoria).where(LogAuditoria.accion == "actualizar_usuario"))
    assert evento.datos_anteriores["rol"] == "OPERADOR"
    assert evento.datos_nuevos["estado"] == "INACTIVO"


def test_gerente_lista_pero_no_crea_y_el_admin_no_se_desactiva(client, db):
    admin = crear_usuario(db, email="admin.lista@distrirapido.example.com", rol="ADMIN")
    gerente = crear_usuario(db, email="gerente.lista@distrirapido.example.com", rol="GERENTE")
    conductor = crear_usuario(db, email="conductor.lista@distrirapido.example.com", rol="CONDUCTOR")
    listado = client.get("/usuarios", headers=autenticar(client, gerente.email))
    assert listado.status_code == 200
    assert any(item["email"] == admin.email for item in listado.json())
    denegado = client.post(
        "/usuarios",
        headers=autenticar(client, gerente.email),
        json=_alta(email="otro@distrirapido.example.com"),
    )
    assert denegado.status_code == 403
    sin_acceso = client.get("/usuarios", headers=autenticar(client, conductor.email))
    assert sin_acceso.status_code == 403
    propio = client.patch(
        f"/usuarios/{admin.id_usuario}",
        headers=autenticar(client, admin.email),
        json={"estado": "INACTIVO"},
    )
    assert propio.status_code == 409
    vacio = client.patch(
        f"/usuarios/{gerente.id_usuario}",
        headers=autenticar(client, admin.email),
        json={},
    )
    assert vacio.status_code == 422
    fantasma = client.patch(
        "/usuarios/00000000-0000-0000-0000-000000000000",
        headers=autenticar(client, admin.email),
        json={"rol": "AUDITOR"},
    )
    assert fantasma.status_code == 404


def test_admin_reactiva_una_cuenta_bloqueada(client, db):
    admin = crear_usuario(db, email="admin.reactiva@distrirapido.example.com", rol="ADMIN")
    bloqueado = crear_usuario(
        db, email="bloqueado.reactiva@distrirapido.example.com", estado="BLOQUEADO"
    )
    bloqueado.intentos_fallidos = 3
    db.commit()
    headers = autenticar(client, admin.email)
    respuesta = client.patch(
        f"/usuarios/{bloqueado.id_usuario}",
        headers=headers,
        json={"estado": "ACTIVO"},
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "ACTIVO"
    assert respuesta.json()["intentos_fallidos"] == 0
    ingreso = client.post(
        "/auth/login",
        json={"email": bloqueado.email, "password": "clave-segura"},
    )
    assert ingreso.status_code == 200


def test_correo_duplicado_y_clave_corta(client, db):
    admin = crear_usuario(db, email="admin.dup@distrirapido.example.com", rol="ADMIN")
    headers = autenticar(client, admin.email)
    client.post("/usuarios", headers=headers, json=_alta())
    duplicado = client.post("/usuarios", headers=headers, json=_alta())
    assert duplicado.status_code == 409
    assert duplicado.json()["detail"] == "El correo ya se encuentra registrado"
    corta = client.post(
        "/usuarios",
        headers=headers,
        json=_alta(email="corta@distrirapido.example.com", password="123"),
    )
    assert corta.status_code == 422
    inyeccion = client.post(
        "/usuarios",
        headers=headers,
        json=_alta(email="<script>alert(1)</script>", password="clave-segura"),
    )
    assert inyeccion.status_code == 422
