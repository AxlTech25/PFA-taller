from app.models.entities import LogAuditoria, Usuario
from app.services.auditoria import registrar
from sqlalchemy import select
from tests.conftest import autenticar, crear_usuario


def test_login_exitoso_entrega_jwt_y_audita(client, db):
    crear_usuario(db, email="operador@distrirapido.example.com", rol="OPERADOR")
    respuesta = client.post(
        "/auth/login",
        json={"email": "operador@distrirapido.example.com", "password": "clave-segura"},
    )
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["token_type"] == "bearer"
    assert cuerpo["rol"] == "OPERADOR"
    assert cuerpo["access_token"]
    db.expire_all()
    evento = db.scalar(select(LogAuditoria).where(LogAuditoria.accion == "login"))
    assert evento is not None
    assert evento.datos_nuevos["rol"] == "OPERADOR"


def test_auditoria_persiste_ip(db):
    usuario = crear_usuario(db, email="ip@distrirapido.example.com")
    registrar(
        db,
        id_usuario=usuario.id_usuario,
        accion="login",
        tabla="usuario",
        registro_id=usuario.id_usuario,
        ip="10.1.2.3",
        nuevos={"rol": usuario.rol},
    )
    db.commit()
    db.expire_all()
    evento = db.scalar(select(LogAuditoria).where(LogAuditoria.accion == "login"))
    assert str(evento.ip_origen) == "10.1.2.3"


def test_credencial_invalida_incrementa_intentos_sin_revelar_existencia(client, db):
    crear_usuario(db, email="operador@distrirapido.example.com")
    desconocido = client.post(
        "/auth/login",
        json={"email": "nadie@distrirapido.example.com", "password": "clave-segura"},
    )
    incorrecta = client.post(
        "/auth/login",
        json={"email": "operador@distrirapido.example.com", "password": "otra-clave"},
    )
    assert desconocido.status_code == 401
    assert incorrecta.status_code == 401
    assert desconocido.json() == incorrecta.json()
    assert desconocido.json()["detail"] == "Credenciales inválidas"
    db.expire_all()
    usuario = db.scalar(select(Usuario).where(Usuario.email == "operador@distrirapido.example.com"))
    assert usuario.intentos_fallidos == 1


def test_fallos_incrementan_intentos_sin_bloquear_la_cuenta(client, db):
    crear_usuario(db, email="bloqueo@distrirapido.example.com")
    for _ in range(3):
        respuesta = client.post(
            "/auth/login",
            json={"email": "bloqueo@distrirapido.example.com", "password": "incorrecta"},
        )
        assert respuesta.status_code == 401
    db.expire_all()
    usuario = db.scalar(select(Usuario).where(Usuario.email == "bloqueo@distrirapido.example.com"))
    assert usuario.intentos_fallidos == 3
    assert usuario.estado == "ACTIVO"
    assert usuario.bloqueado_hasta is None


def test_cuenta_bloqueada_no_inicia_sesion(client, db):
    crear_usuario(db, email="ya.bloqueado@distrirapido.example.com", estado="BLOQUEADO")
    respuesta = client.post(
        "/auth/login",
        json={"email": "ya.bloqueado@distrirapido.example.com", "password": "clave-segura"},
    )
    assert respuesta.status_code == 403


def test_cuenta_inactiva_responde_403(client, db):
    crear_usuario(db, email="inactivo@distrirapido.example.com", estado="INACTIVO")
    respuesta = client.post(
        "/auth/login",
        json={"email": "inactivo@distrirapido.example.com", "password": "clave-segura"},
    )
    assert respuesta.status_code == 403


def test_me_exige_token(client, db):
    usuario = crear_usuario(db, email="yo@distrirapido.example.com", rol="GERENTE")
    sin_token = client.get("/auth/me")
    assert sin_token.status_code == 401
    headers = autenticar(client, usuario.email)
    perfil = client.get("/auth/me", headers=headers)
    assert perfil.status_code == 200
    assert perfil.json()["rol"] == "GERENTE"
    invalido = client.get("/auth/me", headers={"Authorization": "Bearer no-es-un-jwt"})
    assert invalido.status_code == 401
