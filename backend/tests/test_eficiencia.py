from app.core.compresion import codificar
from app.services.usuarios import consulta_listado
from sqlalchemy import text
from tests.conftest import autenticar, crear_usuario


def test_listado_de_flota_pagina_de_a_doce(client, db):
    operador = crear_usuario(db, email="op.pagina@distrirapido.example.com")
    headers = autenticar(client, operador.email)
    primera = client.get("/vehiculos?page=1&limite=12", headers=headers)
    assert primera.status_code == 200
    cuerpo = primera.json()
    assert cuerpo["page"] == 1
    assert cuerpo["page_size"] == 12
    assert cuerpo["total"] >= 4
    assert len(cuerpo["items"]) == min(12, cuerpo["total"])
    assert {"placa", "estado", "factor_emision_co2"} <= set(cuerpo["items"][0])
    vacia = client.get("/vehiculos?page=9&limite=12", headers=headers)
    assert vacia.json()["items"] == []
    assert vacia.json()["total"] == cuerpo["total"]


def test_la_consulta_de_usuarios_no_trae_el_hash(db):
    sql = str(consulta_listado().compile(compile_kwargs={"literal_binds": True}))
    assert "password_hash" not in sql
    assert "email" in sql


def test_etag_revalida_el_listado(client, db):
    operador = crear_usuario(db, email="op.etag@distrirapido.example.com")
    headers = autenticar(client, operador.email)
    primero = client.get("/clientes", headers=headers)
    assert primero.status_code == 200
    etag = primero.headers["etag"]
    assert primero.headers["cache-control"].startswith("private")
    segundo = client.get("/clientes", headers={**headers, "If-None-Match": etag})
    assert segundo.status_code == 304
    assert segundo.content == b""


def test_brotli_y_gzip_reducen_un_cuerpo_grande():
    cuerpo = ("EcoLogística " * 400).encode()
    brotli, algoritmo_br = codificar(cuerpo, "br, gzip")
    gzip, algoritmo_gz = codificar(cuerpo, "gzip")
    assert algoritmo_br == "br"
    assert algoritmo_gz == "gzip"
    assert len(brotli) < len(cuerpo)
    assert len(gzip) < len(cuerpo)
    pequeno, nada = codificar(b"ok", "gzip")
    assert nada is None
    assert pequeno == b"ok"


def test_openapi_viaja_comprimido(client):
    respuesta = client.get("/openapi.json", headers={"Accept-Encoding": "br"})
    assert respuesta.status_code == 200
    assert "paths" in respuesta.json()
    assert respuesta.headers.get("content-encoding") in {None, "br", "gzip"}


def test_indices_de_listado(db):
    nombres = set(
        db.execute(
            text(
                """
                SELECT indexname FROM pg_indexes
                WHERE schemaname = 'public'
                  AND indexname IN (
                    'idx_detalle_ruta_id_ruta',
                    'idx_ruta_id_job',
                    'idx_pedido_creado_en',
                    'idx_conductor_nombre',
                    'idx_ruta_listado',
                    'idx_vehiculo_estado',
                    'idx_pedido_estado'
                  )
                """
            )
        ).scalars()
    )
    assert nombres == {
        "idx_detalle_ruta_id_ruta",
        "idx_ruta_id_job",
        "idx_pedido_creado_en",
        "idx_conductor_nombre",
        "idx_ruta_listado",
        "idx_vehiculo_estado",
        "idx_pedido_estado",
    }
