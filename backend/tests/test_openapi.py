from app.core.errores import traducir_validacion
from app.core.security import ip_valida


def test_openapi_y_swagger(client):
    especificacion = client.get("/openapi.json")
    assert especificacion.status_code == 200
    paths = especificacion.json()["paths"]
    for ruta in ("/auth/login", "/vehiculos", "/usuarios", "/conductores", "/pedidos", "/clientes"):
        assert ruta in paths
    assert "put" in paths["/vehiculos/{id_vehiculo}"]
    assert "patch" in paths["/usuarios/{id_usuario}"]
    assert "423" in paths["/auth/login"]["post"]["responses"]
    docs = client.get("/docs")
    assert docs.status_code == 200
    assert "swagger" in docs.text.lower()
    assert client.get("/health").json()["status"] == "ok"
    assert client.get("/health").headers["x-content-type-options"] == "nosniff"


def test_raiz(client):
    respuesta = client.get("/")
    assert respuesta.status_code == 200
    assert respuesta.json()["nombre"] == "EcoLogística Lima"


def test_ip_y_campo_obligatorio(client):
    assert ip_valida("testclient") is None
    assert ip_valida("10.0.0.8") == "10.0.0.8"
    assert ip_valida(None) is None
    respuesta = client.post("/auth/login", json={"password": "clave-segura"})
    assert respuesta.status_code == 422
    assert "correo" in respuesta.json()["detail"].lower() or "email" in respuesta.json()["detail"]
    assert traducir_validacion.__name__ == "traducir_validacion"
