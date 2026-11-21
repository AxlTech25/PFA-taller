"""Zonas de restricción, ruta alternativa y reserva ecológica (US-013, RN-013)."""

import json
from datetime import date, time
from decimal import Decimal
from uuid import UUID, uuid4

from app.models.entities import AsignacionRuta, Conductor, DetalleRuta, Ruta, Vehiculo
from app.optimizacion.evaluacion import (
    Instancia,
    PedidoNodo,
    Recurso,
    RutaPlan,
    costo_verde,
    vecino_mas_cercano,
)
from app.optimizacion.metaheuristica import generar_plan
from app.optimizacion.zonas import (
    PENALIZACION_RIESGO,
    RESERVA,
    RIESGO,
    Poligono,
    calcular_alternativa,
    punto_en_anillo,
    segmento_intersecta,
)
from sqlalchemy import select, text
from tests.conftest import autenticar, crear_usuario

FECHA = "2026-10-21"
DIA = date(2026, 10, 21)


def _rect(
    tipo: str,
    sur: float,
    oeste: float,
    norte: float,
    este: float,
    nombre: str = "z",
) -> Poligono:
    return Poligono(
        "z1",
        nombre,
        tipo,
        "ALTA",
        ((sur, oeste), (sur, este), (norte, este), (norte, oeste)),
    )


def _pedido_nodo(indice: int, lat: float, lon: float) -> PedidoNodo:
    from datetime import UTC, datetime, timedelta

    inicio = datetime(2026, 10, 21, 7, tzinfo=UTC)
    return PedidoNodo(
        id=UUID(int=indice),
        lat=lat,
        lon=lon,
        peso=10,
        volumen=0.2,
        ventana_inicio=inicio,
        ventana_fin=inicio + timedelta(hours=12),
        express=False,
    )


def _recurso(lat: float, lon: float) -> Recurso:
    from datetime import UTC, datetime

    return Recurso(
        id_vehiculo=UUID(int=1),
        id_conductor=UUID(int=2),
        placa="DMO-101",
        capacidad_kg=1000,
        capacidad_m3=8,
        consumo_km_l=10,
        factor_co2=0.2,
        origen_lat=lat,
        origen_lon=lon,
        inicio=datetime(2026, 10, 21, 6, tzinfo=UTC),
        fin=datetime(2026, 10, 21, 20, tzinfo=UTC),
    )


def _instancia(pedidos, recursos, zonas) -> Instancia:
    import time

    return Instancia(
        fecha=DIA,
        pedidos=pedidos,
        recursos=recursos,
        velocidad=25,
        congestion=1,
        limite=time.perf_counter() + 5,
        precio_litro=4,
        costo_km=1,
        excluidos=0,
        semilla=1,
        zonas=zonas,
    )


def _operador(client, db, email: str):
    usuario = crear_usuario(db, email=email)
    return autenticar(client, usuario.email), usuario


def _conductor(db, dni: str) -> Conductor:
    fila = Conductor(
        dni=dni,
        nombre="Rosa Quispe",
        licencia_categoria="A-IIIb",
        disponibilidad_inicio=time(6, 0),
        disponibilidad_fin=time(20, 0),
        lat_punto_partida=Decimal("-12.0100"),
        lon_punto_partida=Decimal("-76.9800"),
        estado="ACTIVO",
    )
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
        "direccion": "Av. de la demostración 100",
        "latitud": -12.03,
        "longitud": -76.955,
        "peso_kg": 10,
        "volumen_m3": 0.2,
        "ventana_inicio": f"{FECHA}T08:00:00Z",
        "ventana_fin": f"{FECHA}T18:00:00Z",
        "prioridad": "ESTANDAR",
        "tipo_producto": "NO_PERECEDERO",
    }
    cuerpo.update(cambios)
    respuesta = client.post("/pedidos", headers=headers, json=cuerpo)
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def _borrador(db, conductor: Conductor, id_pedido: str) -> Ruta:
    vehiculo = db.scalar(select(Vehiculo).where(Vehiculo.placa == "DMO-101"))
    ruta = Ruta(
        fecha=DIA,
        estado="BORRADOR",
        minutos_conduccion=Decimal("40"),
        distancia_total_km=Decimal("8"),
        combustible_estimado_l=Decimal("1.20"),
        co2_estimado_kg=Decimal("1.500"),
        tiempo_total_min=Decimal("50"),
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
    db.add(
        DetalleRuta(
            id_ruta=ruta.id_ruta,
            id_pedido=UUID(id_pedido),
            secuencia=1,
            estado_entrega="PENDIENTE",
        )
    )
    db.commit()
    db.refresh(ruta)
    return ruta


def _caja(db, nombre: str, tipo: str, oeste: float, sur: float, este: float, norte: float) -> None:
    db.execute(
        text(
            """
            INSERT INTO zona_restriccion (nombre, tipo, geometria, severidad, activo)
            VALUES (
                :nombre, :tipo,
                ST_MakeEnvelope(:oeste, :sur, :este, :norte, 4326),
                'ALTA', TRUE
            )
            """
        ),
        {"nombre": nombre, "tipo": tipo, "oeste": oeste, "sur": sur, "este": este, "norte": norte},
    )
    db.commit()


def _cruza(db, trazado: list, tipo: str | None = None) -> int:
    geo = {"type": "LineString", "coordinates": [[lon, lat] for lat, lon in trazado]}
    filtro = "AND tipo = :tipo" if tipo else ""
    return db.execute(
        text(
            f"""
            SELECT COUNT(*) FROM zona_restriccion
            WHERE activo
              {filtro}
              AND ST_Intersects(
                    geometria,
                    ST_SetSRID(ST_GeomFromGeoJSON(:geo), 4326)
                  )
            """
        ),
        {"geo": json.dumps(geo), "tipo": tipo},
    ).scalar_one()


def test_geometria_y_desvio_alrededor_de_un_poligono():
    caja = _rect(RIESGO, -12.012, -76.992, -12.008, -76.988)
    afuera = (-12.02, -76.99)
    adentro = (-12.01, -76.99)
    assert punto_en_anillo(adentro, caja.anillo) is True
    assert punto_en_anillo(afuera, caja.anillo) is False
    assert segmento_intersecta(afuera, (-12.0, -76.99), caja.anillo) is True
    assert segmento_intersecta((-12.02, -76.97), (-12.0, -76.97), caja.anillo) is False

    resultado = calcular_alternativa([afuera, (-12.0, -76.99)], [caja])
    assert resultado.motivo == "ok"
    assert resultado.puntos is not None
    assert resultado.puntos[0] == afuera
    assert resultado.puntos[-1] == (-12.0, -76.99)
    assert len(resultado.puntos) > 2
    for inicio, fin in zip(resultado.puntos, resultado.puntos[1:], strict=False):
        assert segmento_intersecta(inicio, fin, caja.anillo) is False

    reserva = _rect(RESERVA, -12.012, -76.992, -12.008, -76.988)
    dentro = calcular_alternativa([adentro, (-12.0, -76.99)], [reserva])
    assert dentro.motivo == "parada_en_reserva"
    libre = calcular_alternativa([(-12.02, -76.97), (-12.0, -76.97)], [caja])
    assert libre.motivo == "ok"
    assert libre.puntos == [(-12.02, -76.97), (-12.0, -76.97)]


def test_sin_salida_cuando_todo_segmento_esta_bloqueado(monkeypatch):
    monkeypatch.setattr("app.optimizacion.zonas.punto_en_anillo", lambda *_args: False)
    monkeypatch.setattr("app.optimizacion.zonas.segmento_intersecta", lambda *_args: True)
    bloqueada = _rect(RIESGO, -12.012, -76.992, -12.008, -76.988)
    resultado = calcular_alternativa([(-12.02, -76.99), (-12.0, -76.99)], [bloqueada])
    assert resultado.motivo == "sin_salida"
    assert calcular_alternativa([(-12.0, -76.99)], []).motivo == "sin_coordenadas"


def test_el_vecino_evita_el_riesgo_y_rechaza_la_reserva():
    riesgo = _rect(RIESGO, -12.006, -77.002, -12.004, -76.998, "riesgo")
    cerca = _pedido_nodo(3, -12.01, -77.0)
    lejos = _pedido_nodo(4, -12.0, -76.985)
    inst = _instancia([cerca, lejos], [_recurso(-12.0, -77.0)], [riesgo])
    rutas, _libres, _ = vecino_mas_cercano(inst)
    assert rutas[0].paradas[0].id_pedido == lejos.id
    assert rutas[0].cruces_riesgo >= 0

    reserva = _rect(RESERVA, -12.006, -77.002, -12.004, -76.998, "reserva")
    bloqueada = _instancia([cerca], [_recurso(-12.0, -77.0)], [reserva])
    vacias, sin_asignar, _ = vecino_mas_cercano(bloqueada)
    assert vacias == []
    assert sin_asignar == [cerca.id]

    base = RutaPlan(
        id_vehiculo=UUID(int=1),
        id_conductor=UUID(int=2),
        paradas=[],
        descansos=[],
        distancia_km=1,
        minutos_conduccion=1,
        minutos_reloj=1,
        combustible_l=1,
        co2_kg=1,
    )
    con_cruce = RutaPlan(
        id_vehiculo=base.id_vehiculo,
        id_conductor=base.id_conductor,
        paradas=[],
        descansos=[],
        distancia_km=1,
        minutos_conduccion=1,
        minutos_reloj=1,
        combustible_l=1,
        co2_kg=1,
        cruces_riesgo=2,
    )
    assert costo_verde([con_cruce], [], inst)["total"] == (
        costo_verde([base], [], inst)["total"] + 2 * PENALIZACION_RIESGO
    )


def test_zonas_demo_no_son_catastro_ni_cortan_los_repartos_de_prueba(db):
    filas = db.execute(
        text("SELECT nombre, tipo FROM zona_restriccion WHERE activo ORDER BY nombre")
    ).all()
    assert {nombre for nombre, _tipo in filas} >= {
        "DEMO · riesgo ilustrativo en Santa Anita sur",
        "DEMO · reserva ecológica ilustrativa en Ate sur",
    }
    assert all(nombre.startswith("DEMO") for nombre, _tipo in filas)
    cubiertas = db.execute(
        text(
            """
            SELECT COUNT(*) FROM zona_restriccion z
            WHERE NOT EXISTS (
                SELECT 1 FROM distrito_cobertura d
                WHERE ST_CoveredBy(z.geometria, d.geometria)
            )
            """
        )
    ).scalar_one()
    assert cubiertas == 0
    for linea in (
        [(-12.0100, -76.9800), (-12.0025, -76.9901)],
        [(-12.0100, -76.9800), (-12.02, -76.97)],
        [(-11.9100, -77.0200), (-12.045, -76.925)],
    ):
        assert _cruza(db, linea) == 0
    assert _cruza(db, [(-12.0100, -76.9800), (-12.082, -76.965)], RIESGO) == 1
    distrito = db.execute(
        text(
            """
            SELECT nombre FROM distrito_cobertura
            WHERE ST_Covers(geometria, ST_SetSRID(ST_MakePoint(-76.965, -12.082), 4326))
            """
        )
    ).scalar_one()
    assert distrito == "Santa Anita"


def test_listado_marca_la_demostracion_y_oculta_la_inactiva(client, db):
    headers, _ = _operador(client, db, "op.zonas@distrirapido.example.com")
    _caja(db, "Caja inactiva de prueba", RESERVA, -76.95, -12.04, -76.94, -12.03)
    db.execute(
        text("UPDATE zona_restriccion SET activo = FALSE WHERE nombre = 'Caja inactiva de prueba'")
    )
    db.commit()
    respuesta = client.get("/rutas/zonas-restriccion", headers=headers)
    assert respuesta.status_code == 200, respuesta.text
    cuerpo = respuesta.json()
    assert "INEI" in cuerpo["advertencia"]
    nombres = {zona["nombre"] for zona in cuerpo["zonas"]}
    assert "DEMO · reserva ecológica ilustrativa en Ate sur" in nombres
    assert "Caja inactiva de prueba" not in nombres
    assert all(zona["es_demostracion"] for zona in cuerpo["zonas"])
    assert cuerpo["zonas"][0]["geometria"]["type"] == "Polygon"
    conductor = crear_usuario(db, email="con.zonas@distrirapido.example.com", rol="CONDUCTOR")
    negado = client.get(
        "/rutas/zonas-restriccion",
        headers=autenticar(client, conductor.email),
    )
    assert negado.status_code == 403
    auditor = crear_usuario(db, email="aud.zonas@distrirapido.example.com", rol="AUDITOR")
    permitido = client.get(
        "/rutas/zonas-restriccion",
        headers=autenticar(client, auditor.email),
    )
    assert permitido.status_code == 200
    especificacion = client.get("/openapi.json").json()["paths"]
    assert "/rutas/zonas-restriccion" in especificacion
    assert "/rutas/{id_ruta}/alternativa-segura" in especificacion


def test_la_reserva_ecologica_rechaza_la_confirmacion_y_el_algoritmo(client, db):
    headers, _ = _operador(client, db, "op.reserva@distrirapido.example.com")
    conductor = _conductor(db, "70801901")
    pedido = _pedido(client, headers, db, latitud=-12.03, longitud=-76.955)
    _caja(db, "Reserva de prueba entre paradas", RESERVA, -76.972, -12.023, -76.962, -12.017)
    plan = generar_plan(db, DIA)
    assert plan.factible is False
    assert UUID(pedido["id_pedido"]) in plan.sin_asignar

    ruta = _borrador(db, conductor, pedido["id_pedido"])
    rechazo = client.post(f"/rutas/{ruta.id_ruta}/confirmar", headers=headers)
    assert rechazo.status_code == 422, rechazo.text
    assert "RN-013" in rechazo.json()["detail"]
    assert "Reserva de prueba" in rechazo.json()["detail"]
    db.expire_all()
    assert db.get(Ruta, ruta.id_ruta).estado == "BORRADOR"

    alternativa = client.post(f"/rutas/{ruta.id_ruta}/alternativa-segura", headers=headers)
    assert alternativa.status_code == 200, alternativa.text
    cuerpo = alternativa.json()
    assert cuerpo["evita_riesgo"] is True
    assert cuerpo["trazado"]
    assert "desvío geométrico" in cuerpo["mensaje"]
    assert _cruza(db, cuerpo["trazado"], RESERVA) == 0
    confirmada = client.post(f"/rutas/{ruta.id_ruta}/confirmar", headers=headers)
    assert confirmada.status_code == 200, confirmada.text
    assert confirmada.json()["estado"] == "CONFIRMADA"


def test_parada_dentro_de_la_reserva_no_tiene_alternativa(client, db):
    headers, _ = _operador(client, db, "op.dentro@distrirapido.example.com")
    conductor = _conductor(db, "70801902")
    pedido = _pedido(client, headers, db, latitud=-12.02, longitud=-76.967)
    _caja(db, "Reserva que contiene la parada", RESERVA, -76.972, -12.023, -76.962, -12.017)
    ruta = _borrador(db, conductor, pedido["id_pedido"])
    respuesta = client.post(f"/rutas/{ruta.id_ruta}/alternativa-segura", headers=headers)
    assert respuesta.status_code == 422
    assert "RN-013" in respuesta.json()["detail"]
    confirmada = client.post(f"/rutas/{ruta.id_ruta}/confirmar", headers=headers)
    assert confirmada.status_code == 422
    assert "RN-013" in confirmada.json()["detail"]


def test_alternativa_rodea_el_riesgo_demo_y_respeta_roles(client, db):
    headers, _ = _operador(client, db, "op.segura@distrirapido.example.com")
    conductor = _conductor(db, "70801903")
    pedido = _pedido(client, headers, db, latitud=-12.082, longitud=-76.965)
    ruta = _borrador(db, conductor, pedido["id_pedido"])
    antes = client.get(f"/rutas?fecha={FECHA}", headers=headers).json()["items"]
    assert any(item["id_ruta"] == str(ruta.id_ruta) and item["zonas_cruzadas"] for item in antes)
    respuesta = client.post(f"/rutas/{ruta.id_ruta}/alternativa-segura", headers=headers)
    assert respuesta.status_code == 200, respuesta.text
    cuerpo = respuesta.json()
    assert _cruza(db, cuerpo["trazado"], RIESGO) == 0
    assert _cruza(db, cuerpo["trazado"], RESERVA) == 0
    assert cuerpo["distancia_total_km"] > 0
    otra = client.post(f"/rutas/{ruta.id_ruta}/alternativa-segura", headers=headers)
    assert otra.status_code == 200, otra.text

    gerente = crear_usuario(db, email="ger.zonas@distrirapido.example.com", rol="GERENTE")
    assert (
        client.post(
            f"/rutas/{ruta.id_ruta}/alternativa-segura",
            headers=autenticar(client, gerente.email),
        ).status_code
        == 403
    )
    assert client.post(f"/rutas/{uuid4()}/alternativa-segura", headers=headers).status_code == 404
    confirmada = client.post(f"/rutas/{ruta.id_ruta}/confirmar", headers=headers)
    assert confirmada.status_code == 200, confirmada.text
    repetida = client.post(f"/rutas/{ruta.id_ruta}/alternativa-segura", headers=headers)
    assert repetida.status_code == 409

    vacia = _borrador(db, _conductor(db, "70801904"), pedido["id_pedido"])
    db.execute(text("DELETE FROM detalle_ruta WHERE id_ruta = :id"), {"id": vacia.id_ruta})
    db.commit()
    sin_puntos = client.post(f"/rutas/{vacia.id_ruta}/alternativa-segura", headers=headers)
    assert sin_puntos.status_code == 422


def test_una_zona_inactiva_no_bloquea_la_confirmacion(client, db):
    headers, _ = _operador(client, db, "op.inactiva@distrirapido.example.com")
    conductor = _conductor(db, "70801905")
    pedido = _pedido(client, headers, db, latitud=-12.03, longitud=-76.955)
    _caja(db, "Reserva apagada", RESERVA, -76.972, -12.023, -76.962, -12.017)
    db.execute(text("UPDATE zona_restriccion SET activo = FALSE WHERE nombre = 'Reserva apagada'"))
    db.commit()
    ruta = _borrador(db, conductor, pedido["id_pedido"])
    respuesta = client.post(f"/rutas/{ruta.id_ruta}/confirmar", headers=headers)
    assert respuesta.status_code == 200, respuesta.text
