from fastapi.exceptions import RequestValidationError


def traducir_validacion(exc: RequestValidationError) -> str:
    textos: list[str] = []
    for err in exc.errors():
        loc = [str(parte) for parte in err.get("loc", []) if parte != "body"]
        campo = loc[-1] if loc else "dato"
        msg = str(err.get("msg", "Dato inválido"))
        if msg.startswith("Value error, "):
            textos.append(msg.removeprefix("Value error, "))
        elif msg == "Field required":
            textos.append(f"El campo {campo} es obligatorio")
        elif "valid email" in msg.lower():
            textos.append("El correo no es válido")
        else:
            textos.append(msg)
    if not textos:
        return "Datos inválidos"
    return textos[0] if len(textos) == 1 else " ".join(textos)
