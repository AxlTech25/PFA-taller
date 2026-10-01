from datetime import date


def validar_anio(anio: int) -> int:
    if anio < 1990 or anio > date.today().year:
        raise ValueError("El año de fabricación no es válido")
    return anio
