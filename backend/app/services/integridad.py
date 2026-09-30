from sqlalchemy.exc import IntegrityError

MENSAJES_UNICIDAD = {
    "vehiculo_placa_key": "La placa ya se encuentra registrada",
    "conductor_dni_key": "El DNI ya se encuentra registrado",
    "usuario_email_key": "El correo ya se encuentra registrado",
    "conductor_id_usuario_key": "El usuario ya está vinculado a un conductor",
}


def mensaje_integridad(exc: IntegrityError) -> str | None:
    diag = getattr(exc.orig, "diag", None)
    nombre = getattr(diag, "constraint_name", None) or ""
    if nombre in MENSAJES_UNICIDAD:
        return MENSAJES_UNICIDAD[nombre]
    texto = str(exc.orig).lower()
    if "vehiculo_placa" in texto or "placa" in texto:
        return MENSAJES_UNICIDAD["vehiculo_placa_key"]
    if "conductor_dni" in texto or "dni" in texto:
        return MENSAJES_UNICIDAD["conductor_dni_key"]
    if "usuario_email" in texto:
        return MENSAJES_UNICIDAD["usuario_email_key"]
    return None
