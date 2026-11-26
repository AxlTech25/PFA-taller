"""US-011: re-optimización de las paradas pendientes de una ruta activa."""

import time
import uuid
from decimal import Decimal

import pytest
from app.models.entities import (
    DetalleRuta,
    Incidencia,
    LogAuditoria,
    Pedido,
    Ruta,
)
from app.optimizacion.reoptimizacion import TOPE_REOPTIMIZACION_S, presupuesto, reoptimizar
from app.optimizacion.zonas import RESERVA, cargar_poligonos, reserva_bloquea
from app.services.modo import fecha_operativa
from app.services.reoptimizacion import (
    MENSAJE_SIN_PENDIENTES,
    MENSAJE_TIEMPO,
    _instancia,
    _nodo,
    _recurso,
)
from sqlalchemy import select, text
from tests.conftest import autenticar, crear_usuario
from tests.test_modo import _cliente, _conductor, _marcar, _pedido, _ruta, _vehiculo

# Caja DEMO de reserva ecológica de la migración 006: lon −76.910…−76.885, lat −12.105…−12.090.
OESTE_RESERVA = (Decimal("-12.0975000"), Decimal("-76.9300000"))
NORTE_RESERVA = (Decimal("-12.0800000"), Decimal("-76.9000000"))
ESTE_RESERVA = (Decimal("-12.0975000"), Decimal("-76.8700000"))


def _url(id_ruta) -> str:
    return f"/rutas/{id_ruta}/reoptimizar"


def _operador(client, db, nombre: str) -> dict:
    usuario = crear_usuario(db, email=f"op.{nombre}@distrirapido.example.com", rol="OPERADOR")
    return autenticar(client, usuario.email)


def _ubicar(pedido: Pedido, punto: tuple[Decimal, Decimal]) -> None:
    pedido.latitud, pedido.longitud = punto


def _escenario(db, sufijo: str, dni: str, paradas: int = 4, estado: str = "CONFIRMADA"):
    dia = fecha_operativa()
    usuario = crear_usuario(db, email=f"reopt.{sufijo}@distrirapido.example.com", rol="CONDUCTOR")
    ficha = _conductor(db, usuario, dni)
    pedidos = []
    for n in range(paradas):
        pedido = _pedido(db, _cliente(db), dia, f"reopt-{sufijo}-{n}", (8, 0), (16, 0))
        pedido.latitud = Decimal("-12.0100000") + Decimal(n % 3) * Decimal("0.0060000")
        pedido.longitud = Decimal("-76.9800000") + Decimal(n % 4) * Decimal("0.0050000")
        pedidos.append((pedido, _marcar(dia, 9, n)))
    ruta = _ruta(db, ficha, _vehiculo(db), dia, pedidos, estado=estado)
    db.commit()
    return usuario, ficha, ruta, _detalles(db, ruta)


def _detalles(db, ruta) -> list[DetalleRuta]:
    db.expire_all()
    return list(
        db.scalars(
            select(DetalleRuta)
            .where(DetalleRuta.id_ruta == ruta.id_ruta)
            .order_by(DetalleRuta.secuencia)
        ).all()
    )


def _pedido_libre(db, referencia: str) -> Pedido:
    dia = fecha_operativa()
    pedido = _pedido(db, _cliente(db), dia, referencia, (8, 0), (16, 0))
    pedido.estado = "PENDIENTE"
    db.commit()
    return pedido


def test_presupuesto_nunca_pasa_de_30_segundos():
    assert TOPE_REOPTIMIZACION_S == 30
    assert presupuesto(None) == 30
    assert presupuesto(999) == 30
    assert presupuesto(12) == 12
    assert presupuesto(-5) == 0


def test_reoptimiza_conserva_resueltas_agrega_y_cancela(client, db):
    usuario, _, ruta, detalles = _escenario(db, "feliz", "70011001", paradas=5)
    detalles[0].estado_entrega = "ENTREGADO"
    detalles[2].estado_entrega = "FALLIDO"
    eta_fijas = {detalles[0].id_pedido: detalles[0].eta, detalles[2].id_pedido: detalles[2].eta}
    cancelado = detalles[4].id_pedido
    db.commit()
    nuevo = _pedido_libre(db, "reopt-feliz-nuevo")
    headers = _operador(client, db, "feliz")

    respuesta = client.post(
        _url(ruta.id_ruta),
        json={
            "motivo": "NUEVO_PEDIDO",
            "descripcion": "  Pedido   urgente de la bodega ",
            "agregar": [str(nuevo.id_pedido)],
            "cancelar": [str(cancelado)],
        },
        headers=headers,
    )
    assert respuesta.status_code == 200, respuesta.text
    cuerpo = respuesta.json()
    assert cuerpo["segundos"] <= 30
    assert cuerpo["presupuesto_s"] == 30
    assert cuerpo["paradas_fijas"] == 2
    assert cuerpo["paradas_reordenadas"] == 3
    assert cuerpo["agregadas"] == 1
    assert cuerpo["canceladas"] == 1
    assert cuerpo["mensaje"].startswith("Ruta re-optimizada en ")
    paradas = cuerpo["ruta"]["paradas"]
    assert [p["secuencia"] for p in paradas] == [1, 2, 3, 4, 5]
    assert [p["estado_entrega"] for p in paradas[:2]] == ["ENTREGADO", "FALLIDO"]
    assert str(nuevo.id_pedido) in {p["id_pedido"] for p in paradas}
    assert str(cancelado) not in {p["id_pedido"] for p in paradas}

    nuevos_detalles = _detalles(db, ruta)
    assert [d.id_pedido for d in nuevos_detalles[:2]] == list(eta_fijas)
    for detalle in nuevos_detalles[:2]:
        assert detalle.eta == eta_fijas[detalle.id_pedido]
    assert db.get(Pedido, cancelado).estado == "CANCELADO"
    assert db.get(Pedido, nuevo.id_pedido).estado == "ASIGNADO"
    actualizada = db.get(Ruta, ruta.id_ruta)
    assert actualizada.estado == "CONFIRMADA"
    assert actualizada.distancia_total_km is not None

    incidencia = db.scalar(select(Incidencia).where(Incidencia.id_ruta == ruta.id_ruta))
    assert incidencia.tipo == "NUEVO_PEDIDO"
    assert incidencia.estado == "REOPTIMIZADA"
    assert incidencia.descripcion == "Pedido urgente de la bodega"
    log = db.scalar(
        select(LogAuditoria).where(
            LogAuditoria.accion == "reoptimizar_ruta", LogAuditoria.registro_id == ruta.id_ruta
        )
    )
    assert log is not None and log.datos_nuevos["segundos"] <= 30

    jornada = client.get("/modo/jornada", headers=autenticar(client, usuario.email)).json()
    assert jornada["alertas"][0]["codigo"] == "REOPTIMIZACION"
    assert "re-optimizó" in jornada["alertas"][0]["texto"]


def test_nunca_cruza_la_reserva_ecologica(client, db):
    _, ficha, ruta, detalles = _escenario(db, "reserva", "70011002", paradas=2)
    ficha.lat_punto_partida, ficha.lon_punto_partida = OESTE_RESERVA
    # Orden actual: primero el punto al este, que obliga a atravesar la reserva.
    _ubicar(db.get(Pedido, detalles[0].id_pedido), ESTE_RESERVA)
    _ubicar(db.get(Pedido, detalles[1].id_pedido), NORTE_RESERVA)
    db.commit()
    zonas = cargar_poligonos(db)
    assert any(zona.tipo == RESERVA for zona in zonas)
    assert reserva_bloquea(*map(float, OESTE_RESERVA + ESTE_RESERVA), zonas)

    respuesta = client.post(
        _url(ruta.id_ruta),
        json={"motivo": "ACCIDENTE_TRANSITO", "descripcion": "Vía bloqueada"},
        headers=_operador(client, db, "reserva"),
    )
    assert respuesta.status_code == 200, respuesta.text
    referencias = [p["punto_referencia"] for p in respuesta.json()["ruta"]["paradas"]]
    assert referencias == ["reopt-reserva-1", "reopt-reserva-0"]
    puntos = [OESTE_RESERVA, NORTE_RESERVA, ESTE_RESERVA]
    for inicio, fin in zip(puntos, puntos[1:], strict=False):
        assert not reserva_bloquea(
            float(inicio[0]), float(inicio[1]), float(fin[0]), float(fin[1]), zonas
        )
    cruces = respuesta.json()["ruta"]["zonas_cruzadas"]
    assert all(zona["tipo"] != "RESERVA_ECOLOGICA" for zona in cruces)


def test_sin_salida_por_reserva_conserva_la_ruta(client, db):
    _, ficha, ruta, detalles = _escenario(db, "encerrada", "70011003", paradas=1)
    ficha.lat_punto_partida, ficha.lon_punto_partida = OESTE_RESERVA
    _ubicar(db.get(Pedido, detalles[0].id_pedido), ESTE_RESERVA)
    db.commit()
    respuesta = client.post(
        _url(ruta.id_ruta),
        json={"motivo": "CONGESTION"},
        headers=_operador(client, db, "encerrada"),
    )
    assert respuesta.status_code == 422
    assert "Se conserva la ruta anterior" in respuesta.json()["detail"]
    assert [d.id_detalle for d in _detalles(db, ruta)] == [d.id_detalle for d in detalles]
    incidencia = db.scalar(select(Incidencia).where(Incidencia.id_ruta == ruta.id_ruta))
    assert incidencia.estado == "SIN_SOLUCION"


def test_tope_de_tiempo_en_cero_conserva_la_ruta(client, db):
    _, _, ruta, detalles = _escenario(db, "tope", "70011004", paradas=3)
    db.execute(
        text(
            "UPDATE configuracion_sistema SET valor = '0' "
            "WHERE clave = 'tiempo_max_reoptimizacion_s'"
        )
    )
    db.commit()
    respuesta = client.post(
        _url(ruta.id_ruta),
        json={"motivo": "PARADA_FALLIDA"},
        headers=_operador(client, db, "tope"),
    )
    assert respuesta.status_code == 422
    assert respuesta.json()["detail"] == MENSAJE_TIEMPO
    assert [d.secuencia for d in _detalles(db, ruta)] == [1, 2, 3]
    fallo = db.scalar(
        select(LogAuditoria).where(
            LogAuditoria.accion == "reoptimizacion_sin_solucion",
            LogAuditoria.registro_id == ruta.id_ruta,
        )
    )
    assert fallo.datos_nuevos["cortado"] is True
    assert fallo.datos_nuevos["presupuesto_s"] == 0
    # PARADA_FALLIDA no es un tipo de incidencia: queda solo en auditoría.
    assert db.scalar(select(Incidencia).where(Incidencia.id_ruta == ruta.id_ruta)) is None


def test_al_llegar_al_tope_devuelve_la_mejor_secuencia_hallada(db):
    _, _, ruta, detalles = _escenario(db, "reloj", "70011005", paradas=8)
    from app.models.entities import AsignacionRuta

    asignacion = db.scalar(select(AsignacionRuta).where(AsignacionRuta.id_ruta == ruta.id_ruta))
    pendientes = [_nodo(db.get(Pedido, d.id_pedido)) for d in detalles]
    llamadas = {"n": 0}

    def reloj() -> float:
        llamadas["n"] += 1
        return float(llamadas["n"])

    # Cada consulta al reloj «gasta» 1 s simulado; el tope llega a mitad del 2-opt.
    inst = _instancia(db, ruta, pendientes, limite=40.0)
    resultado = reoptimizar(_recurso(db, ruta, asignacion), [], pendientes, [], inst, reloj, 0.0)
    assert resultado.cortado is True
    assert resultado.factible is True
    assert sorted(map(str, resultado.orden)) == sorted(str(p.id) for p in pendientes)
    assert resultado.costo_final is not None
    assert resultado.costo_final <= resultado.costo_inicial + 1e-6


@pytest.mark.parametrize("paradas", [12, 30])
def test_mide_el_tiempo_real_de_reoptimizacion(client, db, paradas):
    _, _, ruta, detalles = _escenario(db, f"medida{paradas}", f"700111{paradas:02d}", paradas)
    detalles[0].estado_entrega = "ENTREGADO"
    db.commit()
    headers = _operador(client, db, f"medida{paradas}")
    antes = time.perf_counter()
    respuesta = client.post(_url(ruta.id_ruta), json={"motivo": "CONGESTION"}, headers=headers)
    total = time.perf_counter() - antes
    assert respuesta.status_code == 200, respuesta.text
    cuerpo = respuesta.json()
    print(
        f"REOPT_MEDIDA paradas={paradas} calculo_s={cuerpo['segundos']:.4f} "
        f"peticion_s={total:.4f} estrategia={cuerpo['estrategia']} cortado={cuerpo['cortado']}"
    )
    assert cuerpo["segundos"] <= TOPE_REOPTIMIZACION_S
    assert total <= TOPE_REOPTIMIZACION_S


@pytest.mark.parametrize("rol", ["CONDUCTOR", "GERENTE", "AUDITOR"])
def test_solo_admin_y_operador(client, db, rol):
    _, _, ruta, _ = _escenario(db, f"rol{rol.lower()}", f"7001120{len(rol)}", paradas=2)
    usuario = crear_usuario(db, email=f"{rol.lower()}.reopt@distrirapido.example.com", rol=rol)
    respuesta = client.post(
        _url(ruta.id_ruta),
        json={"motivo": "CONGESTION"},
        headers=autenticar(client, usuario.email),
    )
    assert respuesta.status_code == 403
    disponibles = client.get(
        f"/rutas/{ruta.id_ruta}/pedidos-disponibles", headers=autenticar(client, usuario.email)
    )
    assert disponibles.status_code == 403
    assert client.post(_url(ruta.id_ruta), json={"motivo": "CONGESTION"}).status_code == 401


def test_admin_puede_reoptimizar(client, db):
    _, _, ruta, _ = _escenario(db, "admin", "70011301", paradas=2)
    admin = crear_usuario(db, email="admin.reopt@distrirapido.example.com", rol="ADMIN")
    respuesta = client.post(
        _url(ruta.id_ruta), json={"motivo": "CONGESTION"}, headers=autenticar(client, admin.email)
    )
    assert respuesta.status_code == 200, respuesta.text


def test_errores_de_estado_y_de_datos(client, db):
    headers = _operador(client, db, "errores")
    assert (
        client.post(_url(uuid.uuid4()), json={"motivo": "CONGESTION"}, headers=headers).status_code
        == 404
    )
    _, _, borrador, _ = _escenario(db, "borrador", "70011401", paradas=2, estado="BORRADOR")
    assert (
        client.post(_url(borrador.id_ruta), json={"motivo": "CONGESTION"}, headers=headers)
        .status_code
        == 409
    )
    _, _, ruta, detalles = _escenario(db, "resuelta", "70011402", paradas=2)
    for detalle in detalles:
        detalle.estado_entrega = "ENTREGADO"
    db.commit()
    resuelta = client.post(_url(ruta.id_ruta), json={"motivo": "CONGESTION"}, headers=headers)
    assert resuelta.status_code == 409
    assert resuelta.json()["detail"] == MENSAJE_SIN_PENDIENTES
    cancelar_entregado = client.post(
        _url(ruta.id_ruta),
        json={"motivo": "CANCELACION", "cancelar": [str(detalles[0].id_pedido)]},
        headers=headers,
    )
    assert cancelar_entregado.status_code == 409

    _, _, activa, propios = _escenario(db, "datos", "70011403", paradas=2)
    for cuerpo, texto in (
        ({"motivo": "NUEVO_PEDIDO"}, "Indique al menos un pedido nuevo para agregar."),
        ({"motivo": "CANCELACION"}, "Indique al menos un pedido para cancelar."),
        (
            {
                "motivo": "CONGESTION",
                "agregar": [str(propios[0].id_pedido)],
                "cancelar": [str(propios[0].id_pedido)],
            },
            "Un pedido no puede agregarse y cancelarse a la vez.",
        ),
    ):
        respuesta = client.post(_url(activa.id_ruta), json=cuerpo, headers=headers)
        assert respuesta.status_code == 422
        assert respuesta.json()["detail"] == texto
    ajeno = client.post(
        _url(activa.id_ruta),
        json={"motivo": "NUEVO_PEDIDO", "agregar": [str(detalles[0].id_pedido)]},
        headers=headers,
    )
    assert ajeno.status_code == 422
    fuera = client.post(
        _url(activa.id_ruta),
        json={"motivo": "CANCELACION", "cancelar": [str(uuid.uuid4())]},
        headers=headers,
    )
    assert fuera.status_code == 422
    peligroso = client.post(
        _url(activa.id_ruta),
        json={"motivo": "CONGESTION", "descripcion": "<script>x</script>"},
        headers=headers,
    )
    assert peligroso.status_code == 422


def test_pedidos_disponibles_de_la_fecha(client, db):
    _, _, ruta, _ = _escenario(db, "disp", "70011501", paradas=1)
    libre = _pedido_libre(db, "reopt-disp-libre")
    headers = _operador(client, db, "disp")
    respuesta = client.get(f"/rutas/{ruta.id_ruta}/pedidos-disponibles", headers=headers)
    assert respuesta.status_code == 200
    assert str(libre.id_pedido) in {fila["id_pedido"] for fila in respuesta.json()}
    faltante = client.get(f"/rutas/{uuid.uuid4()}/pedidos-disponibles", headers=headers)
    assert faltante.status_code == 404


