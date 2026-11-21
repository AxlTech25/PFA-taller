"""Zonas de restricción para el mapa y el motor (US-013, RN-012, RN-013).

La reserva ecológica es una restricción dura: un segmento que la intersecta
no es factible. La zona de riesgo se penaliza y la ruta alternativa la rodea.
La geometría de trabajo es el anillo exterior en (latitud, longitud).
"""

import heapq
import json
import math
from dataclasses import dataclass

from sqlalchemy import text

RESERVA = "RESERVA_ECOLOGICA"
RIESGO = "RIESGO_SEGURIDAD"
# Kilómetros ficticios que el vecino más cercano suma por cada zona de riesgo
# cruzada, para preferir un tramo más largo que no la atraviese (RN-012).
PENALIZACION_KM = 12.0
# Mismo criterio dentro del costo verde del genético, en la escala del objetivo.
PENALIZACION_RIESGO = 250.0
# Margen para no ir pegado al borde del polígono. No es una distancia oficial.
MARGEN_METROS = 150.0
_METROS_POR_GRADO = 111_320.0

Punto = tuple[float, float]


@dataclass(frozen=True)
class Poligono:
    id_zona: str
    nombre: str
    tipo: str
    severidad: str
    anillo: tuple[Punto, ...]


@dataclass
class Resultado:
    puntos: list[Punto] | None
    motivo: str
    avisos: list[str]


def _cerrar(anillo: tuple[Punto, ...]) -> tuple[Punto, ...]:
    if not anillo:
        return anillo
    if anillo[0] == anillo[-1]:
        return anillo
    return anillo + (anillo[0],)


def _igual(a: Punto, b: Punto) -> bool:
    return abs(a[0] - b[0]) < 1e-9 and abs(a[1] - b[1]) < 1e-9


def _orientacion(a: Punto, b: Punto, c: Punto) -> float:
    return (b[1] - a[1]) * (c[0] - a[0]) - (b[0] - a[0]) * (c[1] - a[1])


def _sobre(a: Punto, punto: Punto, b: Punto) -> bool:
    if abs(_orientacion(a, b, punto)) > 1e-12:
        return False
    return (
        min(a[0], b[0]) - 1e-12 <= punto[0] <= max(a[0], b[0]) + 1e-12
        and min(a[1], b[1]) - 1e-12 <= punto[1] <= max(a[1], b[1]) + 1e-12
    )


def punto_en_anillo(punto: Punto, anillo: tuple[Punto, ...]) -> bool:
    cerrado = _cerrar(anillo)
    if any(_sobre(cerrado[i], punto, cerrado[i + 1]) for i in range(len(cerrado) - 1)):
        return True
    lat, lon = punto
    dentro = False
    for i in range(len(cerrado) - 1):
        lat1, lon1 = cerrado[i]
        lat2, lon2 = cerrado[i + 1]
        if (lon1 > lon) == (lon2 > lon):
            continue
        lat_corte = lat1 + (lon - lon1) * (lat2 - lat1) / (lon2 - lon1)
        if lat < lat_corte:
            dentro = not dentro
    return dentro


def segmentos_se_cruzan(a: Punto, b: Punto, c: Punto, d: Punto) -> bool:
    if _igual(a, b) or _igual(c, d):
        return False
    o1 = _orientacion(a, b, c)
    o2 = _orientacion(a, b, d)
    o3 = _orientacion(c, d, a)
    o4 = _orientacion(c, d, b)
    cruza = (o1 > 0) != (o2 > 0) and (o3 > 0) != (o4 > 0)
    if cruza and o1 != 0 and o2 != 0 and o3 != 0 and o4 != 0:
        return True
    return _sobre(a, c, b) or _sobre(a, d, b) or _sobre(c, a, d) or _sobre(c, b, d)


def segmento_intersecta(a: Punto, b: Punto, anillo: tuple[Punto, ...]) -> bool:
    if punto_en_anillo(a, anillo) or punto_en_anillo(b, anillo):
        return True
    if _igual(a, b):
        return False
    cerrado = _cerrar(anillo)
    return any(
        segmentos_se_cruzan(a, b, cerrado[i], cerrado[i + 1]) for i in range(len(cerrado) - 1)
    )


def reserva_bloquea(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
    zonas: list[Poligono],
) -> bool:
    if not zonas:
        return False
    a, b = (lat1, lon1), (lat2, lon2)
    return any(
        zona.tipo == RESERVA and segmento_intersecta(a, b, zona.anillo) for zona in zonas
    )


def cruces_riesgo(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
    zonas: list[Poligono],
) -> int:
    if not zonas:
        return 0
    a, b = (lat1, lon1), (lat2, lon2)
    return sum(
        zona.tipo == RIESGO and segmento_intersecta(a, b, zona.anillo) for zona in zonas
    )


def _km(a: Punto, b: Punto) -> float:
    radio = 6371.0
    phi1, phi2 = math.radians(a[0]), math.radians(b[0])
    d_phi = math.radians(b[0] - a[0])
    d_lon = math.radians(b[1] - a[1])
    valor = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lon / 2) ** 2
    return 2 * radio * math.asin(math.sqrt(valor))


def _caja_expandida(anillo: tuple[Punto, ...]) -> tuple[float, float, float, float]:
    lats = [punto[0] for punto in anillo]
    lons = [punto[1] for punto in anillo]
    sur, norte = min(lats), max(lats)
    oeste, este = min(lons), max(lons)
    medio = (sur + norte) / 2
    buf_lat = MARGEN_METROS / _METROS_POR_GRADO
    buf_lon = buf_lat / max(math.cos(math.radians(medio)), 0.2)
    return sur - buf_lat, oeste - buf_lon, norte + buf_lat, este + buf_lon


def _nodos_de_margen(anillo: tuple[Punto, ...]) -> list[Punto]:
    sur, oeste, norte, este = _caja_expandida(anillo)
    medio_lat = (sur + norte) / 2
    medio_lon = (oeste + este) / 2
    return [
        (sur, oeste),
        (sur, medio_lon),
        (sur, este),
        (norte, oeste),
        (norte, medio_lon),
        (norte, este),
        (medio_lat, oeste),
        (medio_lat, este),
    ]


def _clave(punto: Punto) -> tuple[float, float]:
    return (round(punto[0], 7), round(punto[1], 7))


def _libre(a: Punto, b: Punto, prohibidos: list[Poligono]) -> bool:
    if _igual(a, b):
        return False
    return not any(segmento_intersecta(a, b, zona.anillo) for zona in prohibidos)


def _compactar(puntos: list[Punto]) -> list[Punto]:
    limpios: list[Punto] = []
    for punto in puntos:
        if limpios and _igual(limpios[-1], punto):
            continue
        limpios.append(punto)
    return limpios


def _rodear(origen: Punto, destino: Punto, prohibidos: list[Poligono]) -> list[Punto] | None:
    nodos: list[Punto] = [origen, destino]
    vistos = {_clave(origen), _clave(destino)}
    for zona in prohibidos:
        for nodo in _nodos_de_margen(zona.anillo):
            clave = _clave(nodo)
            if clave in vistos:
                continue
            if any(punto_en_anillo(nodo, otro.anillo) for otro in prohibidos):
                continue
            vistos.add(clave)
            nodos.append(nodo)
    cantidad = len(nodos)
    distancias = [float("inf")] * cantidad
    distancias[0] = 0.0
    previo = [-1] * cantidad
    cola: list[tuple[float, int]] = [(0.0, 0)]
    while cola:
        acumulado, indice = heapq.heappop(cola)
        if acumulado != distancias[indice]:
            continue
        if indice == 1:
            break
        for vecino in range(cantidad):
            if vecino == indice or not _libre(nodos[indice], nodos[vecino], prohibidos):
                continue
            nuevo = acumulado + _km(nodos[indice], nodos[vecino])
            if nuevo + 1e-9 < distancias[vecino]:
                distancias[vecino] = nuevo
                previo[vecino] = indice
                heapq.heappush(cola, (nuevo, vecino))
    if math.isinf(distancias[1]):
        return None
    orden: list[Punto] = []
    cursor = 1
    while cursor != -1:
        orden.append(nodos[cursor])
        cursor = previo[cursor]
    orden.reverse()
    return _compactar(orden)


def _prohibidos(origen: Punto, destino: Punto, zonas: list[Poligono]) -> list[Poligono]:
    activos: list[Poligono] = []
    for zona in zonas:
        if zona.tipo == RESERVA:
            activos.append(zona)
            continue
        if zona.tipo != RIESGO:
            continue
        if punto_en_anillo(origen, zona.anillo) or punto_en_anillo(destino, zona.anillo):
            continue
        activos.append(zona)
    return activos


def _trazado_libre(trazado: list[Punto], paradas: list[Punto], zonas: list[Poligono]) -> bool:
    inevitables = {
        zona.id_zona
        for parada in paradas
        for zona in zonas
        if zona.tipo == RIESGO and punto_en_anillo(parada, zona.anillo)
    }
    for inicio, fin in zip(trazado, trazado[1:], strict=False):
        if _igual(inicio, fin):
            continue
        for zona in zonas:
            if zona.tipo == RIESGO and zona.id_zona in inevitables:
                continue
            if zona.tipo not in (RESERVA, RIESGO):
                continue
            if segmento_intersecta(inicio, fin, zona.anillo):
                return False
    return True


def calcular_alternativa(puntos: list[Punto], zonas: list[Poligono]) -> Resultado:
    if len(puntos) < 2:
        return Resultado(None, "sin_coordenadas", [])
    reservas = [
        zona.nombre
        for punto in puntos
        for zona in zonas
        if zona.tipo == RESERVA and punto_en_anillo(punto, zona.anillo)
    ]
    if reservas:
        return Resultado(None, "parada_en_reserva", reservas)
    riesgos = [
        zona.nombre
        for punto in puntos
        for zona in zonas
        if zona.tipo == RIESGO and punto_en_anillo(punto, zona.anillo)
    ]
    actual = [puntos[0]]
    for destino in puntos[1:]:
        origen = actual[-1]
        prohibidos = _prohibidos(origen, destino, zonas)
        if _libre(origen, destino, prohibidos):
            actual.append(destino)
            continue
        tramo = _rodear(origen, destino, prohibidos)
        if tramo is None:
            return Resultado(None, "sin_salida", riesgos)
        actual.extend(tramo[1:])
    actual = _compactar(actual)
    if not _trazado_libre(actual, puntos, zonas):
        return Resultado(None, "sin_salida", riesgos)
    return Resultado(actual, "ok", riesgos)


def anillo_de_geojson(crudo: str | dict) -> tuple[Punto, ...]:
    datos = json.loads(crudo) if isinstance(crudo, str) else crudo
    if not isinstance(datos, dict) or datos.get("type") != "Polygon":
        return ()
    anillos = datos.get("coordinates") or []
    if not anillos:
        return ()
    puntos: list[Punto] = []
    for par in anillos[0]:
        if not isinstance(par, list | tuple) or len(par) < 2:
            continue
        puntos.append((float(par[1]), float(par[0])))
    if len(puntos) >= 2 and _igual(puntos[0], puntos[-1]):
        puntos.pop()
    return tuple(puntos)


def linea_de_puntos(puntos: list[Punto]) -> dict | None:
    coordenadas: list[list[float]] = []
    for lat, lon in puntos:
        par = [lon, lat]
        if coordenadas and _igual((coordenadas[-1][1], coordenadas[-1][0]), (lat, lon)):
            continue
        coordenadas.append(par)
    if len(coordenadas) < 2:
        return None
    return {"type": "LineString", "coordinates": coordenadas}


def puntos_de_linea(geo: dict | None) -> list[list[float]]:
    if not geo:
        return []
    coordenadas = geo.get("coordinates") or []
    puntos: list[list[float]] = []
    for par in coordenadas:
        if isinstance(par, list | tuple) and len(par) >= 2:
            puntos.append([float(par[1]), float(par[0])])
    return puntos


def cargar_poligonos(db) -> list[Poligono]:
    filas = db.execute(
        text(
            """
            SELECT id_zona::text, nombre, tipo, severidad, ST_AsGeoJSON(geometria)
            FROM zona_restriccion
            WHERE activo
            ORDER BY nombre
            """
        )
    ).all()
    poligonos: list[Poligono] = []
    for id_zona, nombre, tipo, severidad, geojson in filas:
        anillo = anillo_de_geojson(geojson)
        if len(anillo) >= 3:
            poligonos.append(Poligono(str(id_zona), nombre, tipo, severidad, anillo))
    return poligonos
