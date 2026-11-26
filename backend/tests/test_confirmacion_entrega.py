"""US-018: el conductor confirma una parada como ENTREGADO o FALLIDO."""

import uuid
from datetime import UTC, date, datetime, timedelta

from app.models.entities import DetalleRuta, LogAuditoria, Pedido, Ruta
from app.services.jornada_demo import asegurar_jornada_demo
from app.services.modo import fecha_operativa
from sqlalchemy import select
from tests.conftest import autenticar, crear_usuario
from tests.test_modo import _cliente, _conductor, _marcar, _pedido, _ruta, _vehiculo


def _escenario(db, sufijo: str, dni: str, *, estado: str = "CONFIRMADA", paradas: int = 2):
    dia = fecha_operativa()
    usuario = crear_usuario(db, email=f"entrega.{sufijo}@distrirapido.example.com", rol="CONDUCTOR")
    ficha = _conductor(db, usuario, dni)
    pedidos = [
        (_pedido(db, _cliente(db), dia, f"{sufijo}-{n}", (8, 0), (12, 0)), _marcar(dia, 9, n))
        for n in range(paradas)
    ]
    ruta = _ruta(db, ficha, _vehiculo(db), dia, pedidos, estado=estado)
    db.commit()
    detalles = list(
        db.scalars(
            select(DetalleRuta)
            .where(DetalleRuta.id_ruta == ruta.id_ruta)
            .order_by(DetalleRuta.secuencia)
        ).all()
    )
    return usuario, ruta, detalles


def _url(id_detalle) -> str:
    return f"/modo/paradas/{id_detalle}/confirmacion"


def test_confirma_entregado_y_fallido_con_quien_y_cuando(client, db):
    usuario, ruta, detalles = _escenario(db, "feliz", "70018001")
    headers = autenticar(client, usuario.email)
    antes = datetime.now(UTC) - timedelta(seconds=5)

    entregado = client.post(
        _url(detalles[0].id_detalle),
        json={"resultado": "ENTREGADO", "motivo": "se ignora"},
        headers=headers,
    )
    assert entregado.status_code == 200, entregado.text
    cuerpo = entregado.json()
    assert cuerpo["estado_entrega"] == "ENTREGADO"
    assert cuerpo["motivo_fallo"] is None
    assert cuerpo["secuencia"] == 1
    assert cuerpo["mensaje"] == "Parada 1 registrada como entregada."

    fallido = client.post(
        _url(detalles[1].id_detalle),
        json={"resultado": "FALLIDO", "motivo": "  Cliente   ausente  "},
        headers=headers,
    )
    assert fallido.status_code == 200, fallido.text
    assert fallido.json()["motivo_fallo"] == "Cliente ausente"
    assert fallido.json()["mensaje"] == "Parada 2 registrada como fallida."

    db.expire_all()
    primero = db.get(DetalleRuta, detalles[0].id_detalle)
    segundo = db.get(DetalleRuta, detalles[1].id_detalle)
    assert primero.estado_entrega == "ENTREGADO"
    assert primero.confirmada_por == usuario.id_usuario
    assert primero.confirmada_en is not None and primero.confirmada_en >= antes
    assert db.get(Pedido, primero.id_pedido).estado == "ENTREGADO"
    assert segundo.estado_entrega == "FALLIDO"
    assert segundo.motivo_fallo == "Cliente ausente"
    assert db.get(Pedido, segundo.id_pedido).estado == "ASIGNADO"
    assert db.get(Ruta, ruta.id_ruta).estado == "EN_EJECUCION"

    auditoria = db.scalars(
        select(LogAuditoria).where(
            LogAuditoria.accion == "confirmar_entrega",
            LogAuditoria.id_usuario == usuario.id_usuario,
        )
    ).all()
    assert len(auditoria) == 2
    assert {fila.datos_anteriores["estado_entrega"] for fila in auditoria} == {"PENDIENTE"}

    jornada = client.get("/modo/jornada", headers=headers).json()
    assert jornada["hay_ruta"] is True
    assert [p["estado_entrega"] for p in jornada["paradas"]] == ["ENTREGADO", "FALLIDO"]
    assert jornada["paradas"][1]["motivo_fallo"] == "Cliente ausente"


def test_parada_de_otro_conductor_responde_403(client, db):
    _, _, detalles = _escenario(db, "duena", "70018002")
    intruso, _, _ = _escenario(db, "intrusa", "70018003", paradas=1)
    respuesta = client.post(
        _url(detalles[0].id_detalle),
        json={"resultado": "ENTREGADO"},
        headers=autenticar(client, intruso.email),
    )
    assert respuesta.status_code == 403
    assert respuesta.json()["detail"] == "La parada pertenece a la ruta de otro conductor"
    db.expire_all()
    assert db.get(DetalleRuta, detalles[0].id_detalle).estado_entrega == "PENDIENTE"
    denegada = db.scalar(
        select(LogAuditoria).where(
            LogAuditoria.accion == "confirmacion_entrega_denegada",
            LogAuditoria.id_usuario == intruso.id_usuario,
        )
    )
    assert denegada is not None


def test_solo_el_rol_conductor(client, db):
    _, _, detalles = _escenario(db, "rol", "70018004", paradas=1)
    operador = crear_usuario(db, email="op.entrega@distrirapido.example.com", rol="OPERADOR")
    respuesta = client.post(
        _url(detalles[0].id_detalle),
        json={"resultado": "ENTREGADO"},
        headers=autenticar(client, operador.email),
    )
    assert respuesta.status_code == 403
    anonimo = client.post(_url(detalles[0].id_detalle), json={"resultado": "ENTREGADO"})
    assert anonimo.status_code == 401


def test_parada_inexistente_responde_404(client, db):
    usuario, _, _ = _escenario(db, "nada", "70018005", paradas=1)
    respuesta = client.post(
        _url(uuid.uuid4()),
        json={"resultado": "ENTREGADO"},
        headers=autenticar(client, usuario.email),
    )
    assert respuesta.status_code == 404
    assert respuesta.json()["detail"] == "Parada no encontrada"


def test_confirmar_dos_veces_responde_409(client, db):
    usuario, _, detalles = _escenario(db, "doble", "70018006", paradas=1)
    headers = autenticar(client, usuario.email)
    url = _url(detalles[0].id_detalle)
    assert client.post(url, json={"resultado": "ENTREGADO"}, headers=headers).status_code == 200
    segunda = client.post(url, json={"resultado": "FALLIDO", "motivo": "x"}, headers=headers)
    assert segunda.status_code == 409
    assert segunda.json()["detail"] == "La parada ya fue registrada como ENTREGADO"
    db.expire_all()
    assert db.get(DetalleRuta, detalles[0].id_detalle).estado_entrega == "ENTREGADO"


def test_ruta_en_borrador_responde_409(client, db):
    usuario, _, detalles = _escenario(db, "borrador", "70018007", estado="BORRADOR", paradas=1)
    respuesta = client.post(
        _url(detalles[0].id_detalle),
        json={"resultado": "ENTREGADO"},
        headers=autenticar(client, usuario.email),
    )
    assert respuesta.status_code == 409


def test_fallido_sin_motivo_y_resultado_invalido_responden_422(client, db):
    usuario, _, detalles = _escenario(db, "motivo", "70018008", paradas=1)
    headers = autenticar(client, usuario.email)
    url = _url(detalles[0].id_detalle)
    for cuerpo in (
        {"resultado": "FALLIDO"},
        {"resultado": "FALLIDO", "motivo": "   "},
    ):
        respuesta = client.post(url, json=cuerpo, headers=headers)
        assert respuesta.status_code == 422
        assert respuesta.json()["detail"] == "Indique el motivo cuando la entrega es fallida."
    assert client.post(url, json={"resultado": "REPROGRAMADO"}, headers=headers).status_code == 422
    largo = client.post(url, json={"resultado": "FALLIDO", "motivo": "a" * 251}, headers=headers)
    assert largo.status_code == 422
    peligroso = client.post(
        url, json={"resultado": "FALLIDO", "motivo": "<script>alert(1)</script>"}, headers=headers
    )
    assert peligroso.status_code == 422
    db.expire_all()
    assert db.get(DetalleRuta, detalles[0].id_detalle).estado_entrega == "PENDIENTE"


def test_jornada_demo_reinicia_las_paradas_al_cambiar_de_dia(db):
    usuario = crear_usuario(db, email="reinicio.demo@distrirapido.example.com", rol="CONDUCTOR")
    assert asegurar_jornada_demo(db, usuario) is True
    detalle = db.scalar(
        select(DetalleRuta)
        .join(Pedido, Pedido.id_pedido == DetalleRuta.id_pedido)
        .where(Pedido.punto_referencia == "frente a la bodega El Ahorro")
    )
    detalle.estado_entrega = "FALLIDO"
    detalle.motivo_fallo = "prueba"
    detalle.confirmada_por = usuario.id_usuario
    detalle.confirmada_en = datetime.now(UTC)
    db.flush()
    assert asegurar_jornada_demo(db, usuario) is True
    assert detalle.estado_entrega == "FALLIDO"
    ruta = db.get(Ruta, detalle.id_ruta)
    ruta.fecha = date(2026, 1, 1)
    db.flush()
    assert asegurar_jornada_demo(db, usuario) is True
    assert detalle.estado_entrega == "PENDIENTE"
    assert detalle.motivo_fallo is None
    assert detalle.confirmada_por is None
    assert detalle.confirmada_en is None
