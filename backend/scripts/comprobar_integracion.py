"""Comprueba la API ya arrancada: salud, login, listado y un 422.

No entra en pytest. Lo llama el job de integración con uvicorn en marcha.
"""

import json
import os
import sys
import urllib.error
import urllib.request

BASE = os.environ.get("API_BASE", "http://127.0.0.1:8000")
EMAIL = os.environ.get("SEED_ADMIN_EMAIL", "admin@distrirapido.example.com")
PASSWORD = os.environ.get("SEED_ADMIN_PASSWORD", "AdminDemo1")


def pedir(method: str, path: str, body: dict | None = None, token: str | None = None) -> tuple[int, dict]:
    datos = None if body is None else json.dumps(body).encode()
    solicitud = urllib.request.Request(BASE + path, data=datos, method=method)
    solicitud.add_header("Accept", "application/json")
    if datos is not None:
        solicitud.add_header("Content-Type", "application/json")
    if token:
        solicitud.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(solicitud, timeout=10) as respuesta:
            crudo = respuesta.read().decode()
            return respuesta.status, json.loads(crudo) if crudo else {}
    except urllib.error.HTTPError as exc:
        crudo = exc.read().decode()
        try:
            payload = json.loads(crudo) if crudo else {}
        except json.JSONDecodeError:
            payload = {"detail": crudo}
        return exc.code, payload


def main() -> None:
    salud_estado, salud = pedir("GET", "/health")
    assert salud_estado == 200 and salud.get("status") == "ok", salud

    anon_estado, _anon = pedir("GET", "/vehiculos?page=1&limite=12")
    assert anon_estado == 401, anon_estado

    malo_estado, _malo = pedir(
        "POST",
        "/auth/login",
        {"email": "nadie@distrirapido.example.com", "password": "clave-incorrecta"},
    )
    assert malo_estado == 401, malo_estado

    sesion_estado, sesion = pedir("POST", "/auth/login", {"email": EMAIL, "password": PASSWORD})
    assert sesion_estado == 200 and sesion.get("access_token"), sesion
    token = str(sesion["access_token"])

    flota_estado, flota = pedir("GET", "/vehiculos?page=1&limite=12", token=token)
    assert flota_estado == 200 and flota.get("total", 0) >= 1, flota

    horario_estado, horario = pedir(
        "POST",
        "/conductores",
        {
            "nombre": "Integracion horario",
            "dni": "87654321",
            "licencia_categoria": "A-IIIb",
            "anios_experiencia": 1,
            "disponibilidad_inicio": "18:00",
            "disponibilidad_fin": "08:00",
            "lat_punto_partida": -12.01,
            "lon_punto_partida": -76.98,
        },
        token=token,
    )
    assert horario_estado == 422, horario
    print(
        json.dumps(
            {
                "health": salud_estado,
                "anonimo": anon_estado,
                "login_invalido": malo_estado,
                "login": sesion_estado,
                "vehiculos": flota_estado,
                "horario": horario_estado,
            }
        )
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        print(f"integracion fallo: {exc}", file=sys.stderr)
        sys.exit(1)
