"""Consulta de zonas y trazado que evita riesgo sin cruzar reservas (US-013)."""

import json
import uuid
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.models.entities import (
    AsignacionRuta,
    Conductor,
    DetalleRuta,
    Pedido,
    Ruta,
    Usuario,
    Vehiculo,
)
from app.optimizacion.evaluacion import DEPOSITO_SJL, distancia_km
from app.optimizacion.heuristica import _parametro
from app.optimizacion.zonas import (
    RESERVA,
    RIESGO,
    Resultado,
    calcular_alternativa,
    cargar_poligonos,
    linea_de_puntos,
    punto_en_anillo,
    puntos_de_linea,
)
from app.services.auditoria import registrar

ADVERTENCIA = (
    "Las zonas cuyo nombre empieza por DEMO son polígonos ilustrativos de la demostración. "
    "No son el catastro del INEI ni el límite oficial "
    "de una reserva ecológica o de una zona de riesgo."
)
MENSAJE_PARADA_RESERVA = (
    "Una parada queda dentro de una reserva ecológica. "
    "Ninguna ruta puede atravesarla (RN-013)."
)
MENSAJE_SIN_SALIDA = (
    "No hay un trazado que evite las zonas de riesgo y las reservas ecológicas (RN-012 y RN-013)."
)
MENSAJE_DESVIO = (
    "Ruta alternativa más segura calculada. El trazado rodea las zonas de riesgo "
    "y no atraviesa reservas ecológicas (RN-012 y RN-013). "
    "Es un desvío geométrico de demostración, no un recorrido callejero ni un límite oficial."
)
MENSAJE_YA_SEGURA = (
    "El trazado entre las paradas ya evita las zonas de riesgo "
    "y no atraviesa reservas ecológicas (RN-012 y RN-013)."
)
MENSAJE_PARADA_RIESGO = (
    "Alguna parada queda dentro de una zona de riesgo; el acceso a ese punto no se puede evitar."
)
MENSAJE_SIN_COORDENADAS = (
    "La ruta no tiene coordenadas suficientes para calcular una alternativa."
)


def _cantidad(valor: float, escala: str) -> Decimal:
    return Decimal(str(round(valor, 4))).quantize(Decimal(escala))


def _geo(valor) -> dict | None:
    if isinstance(valor, str):
        cargado = json.loads(valor)
        return cargado if isinstance(cargado, dict) else None
    if isinstance(valor, dict):
        return valor
    return None


def listar(db: Session) -> dict:
    filas = db.execute(
        text(
            """
            SELECT id_zona, nombre, tipo, severidad, ST_AsGeoJSON(geometria) AS geo
            FROM zona_restriccion
            WHERE activo
            ORDER BY tipo, nombre
            """
        )
    ).all()
    zonas = []
    for fila in filas:
        zonas.append(
            {
                "id_zona": fila.id_zona,
                "nombre": fila.nombre,
                "tipo": fila.tipo,
                "severidad": fila.severidad,
                "es_demostracion": fila.nombre.startswith("DEMO"),
                "geometria": _geo(fila.geo) or {},
            }
        )
    return {"advertencia": ADVERTENCIA, "zonas": zonas}


def consultar_cruces(db: Session, geo: dict | None) -> list[dict]:
    if not geo:
        return []
    filas = db.execute(
        text(
            """
            SELECT id_zona, nombre, tipo, severidad
            FROM zona_restriccion
            WHERE activo
              AND ST_Intersects(
                    geometria,
                    ST_SetSRID(ST_GeomFromGeoJSON(CAST(:geo AS text)), 4326)
                  )
            ORDER BY tipo, nombre
            """
        ),
        {"geo": json.dumps(geo)},
    ).all()
    return [
        {
            "id_zona": fila.id_zona,
            "nombre": fila.nombre,
            "tipo": fila.tipo,
            "severidad": fila.severidad,
        }
        for fila in filas
    ]


def puntos_de_ruta(db: Session, ruta: Ruta) -> list[tuple[float, float]]:
    asignacion = db.scalar(select(AsignacionRuta).where(AsignacionRuta.id_ruta == ruta.id_ruta))
    conductor = db.get(Conductor, asignacion.id_conductor) if asignacion else None
    puntos: list[tuple[float, float]] = []
    if conductor is not None:
        if conductor.lat_punto_partida is None or conductor.lon_punto_partida is None:
            puntos.append(DEPOSITO_SJL)
        else:
            puntos.append((float(conductor.lat_punto_partida), float(conductor.lon_punto_partida)))
    detalles = db.scalars(
        select(DetalleRuta)
        .where(DetalleRuta.id_ruta == ruta.id_ruta)
        .order_by(DetalleRuta.secuencia)
    ).all()
    for detalle in detalles:
        pedido = db.get(Pedido, detalle.id_pedido)
        if pedido is None:
            continue
        puntos.append((float(pedido.latitud), float(pedido.longitud)))
    return puntos


def resumen(db: Session, ruta: Ruta, puntos: list[tuple[float, float]], ocultar: bool) -> dict:
    guardado = _geo(ruta.trazado_geojson)
    geo = guardado or linea_de_puntos(puntos)
    return {
        "trazado": None if ocultar or guardado is None else puntos_de_linea(guardado),
        "zonas_cruzadas": consultar_cruces(db, geo),
    }


def _es_desvio(original: list[tuple[float, float]], calculado: list[tuple[float, float]]) -> bool:
    if len(calculado) != len(original):
        return True
    return any(
        abs(a[0] - b[0]) > 1e-7 or abs(a[1] - b[1]) > 1e-7
        for a, b in zip(original, calculado, strict=False)
    )


def _recalcular(db: Session, ruta: Ruta, puntos: list[tuple[float, float]]) -> None:
    kilometros = 0.0
    for inicio, fin in zip(puntos, puntos[1:], strict=False):
        kilometros += distancia_km(inicio[0], inicio[1], fin[0], fin[1])
    anterior = float(ruta.distancia_total_km or 0)
    velocidad = max(_parametro(db, "velocidad_urbana_km_h", 25), 1)
    congestion = max(_parametro(db, "factor_congestion", 1), 0.1)
    minutos = (kilometros / velocidad) * 60.0 * congestion
    if ruta.minutos_conduccion is not None and ruta.tiempo_total_min is not None:
        delta = minutos - float(ruta.minutos_conduccion)
        ruta.tiempo_total_min = _cantidad(max(float(ruta.tiempo_total_min) + delta, 0), "0.01")
    ruta.distancia_total_km = _cantidad(kilometros, "0.01")
    ruta.minutos_conduccion = _cantidad(minutos, "0.01")
    if anterior <= 0:
        _recalcular_desde_vehiculo(db, ruta, kilometros)
        return
    factor = kilometros / anterior
    if ruta.combustible_estimado_l is not None:
        ruta.combustible_estimado_l = _cantidad(float(ruta.combustible_estimado_l) * factor, "0.01")
    if ruta.co2_estimado_kg is not None:
        ruta.co2_estimado_kg = _cantidad(float(ruta.co2_estimado_kg) * factor, "0.001")


def _recalcular_desde_vehiculo(db: Session, ruta: Ruta, kilometros: float) -> None:
    asignacion = db.scalar(select(AsignacionRuta).where(AsignacionRuta.id_ruta == ruta.id_ruta))
    vehiculo = db.get(Vehiculo, asignacion.id_vehiculo) if asignacion else None
    if vehiculo is None:
        return
    consumo = float(vehiculo.consumo_km_l)
    if consumo:
        ruta.combustible_estimado_l = _cantidad(kilometros / consumo, "0.01")
    ruta.co2_estimado_kg = _cantidad(kilometros * float(vehiculo.factor_emision_co2), "0.001")


def _mensaje(resultado: Resultado, desvio: bool) -> str:
    if resultado.motivo == "parada_en_reserva":
        texto = MENSAJE_PARADA_RESERVA
        if resultado.avisos:
            citados = ", ".join(f"«{nombre}»" for nombre in resultado.avisos)
            texto = f"{texto} {citados}."
        raise HTTPException(status_code=422, detail=texto)
    if resultado.motivo != "ok" or not resultado.puntos:
        raise HTTPException(status_code=422, detail=MENSAJE_SIN_SALIDA)
    texto = MENSAJE_DESVIO if desvio else MENSAJE_YA_SEGURA
    if resultado.avisos:
        texto = f"{texto} {MENSAJE_PARADA_RIESGO}"
    return texto


def _rechazar_si_postgis_cruza(
    db: Session,
    geo: dict,
    puntos: list[tuple[float, float]],
) -> None:
    cruces = consultar_cruces(db, geo)
    if any(zona["tipo"] == RESERVA for zona in cruces):
        raise HTTPException(status_code=422, detail=MENSAJE_SIN_SALIDA)
    zonas = cargar_poligonos(db)
    inevitables = {
        zona.id_zona
        for punto in puntos
        for zona in zonas
        if zona.tipo == RIESGO and punto_en_anillo(punto, zona.anillo)
    }
    for zona in cruces:
        if zona["tipo"] == RIESGO and str(zona["id_zona"]) not in inevitables:
            raise HTTPException(status_code=422, detail=MENSAJE_SIN_SALIDA)


def solicitar_alternativa(db: Session, id_ruta: uuid.UUID, actor: Usuario, ip: str | None) -> str:
    ruta = db.get(Ruta, id_ruta)
    if ruta is None:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    if ruta.estado != "BORRADOR":
        raise HTTPException(
            status_code=409,
            detail="Solo se puede pedir una alternativa de una ruta en borrador",
        )
    puntos = puntos_de_ruta(db, ruta)
    if len(puntos) < 2:
        raise HTTPException(status_code=422, detail=MENSAJE_SIN_COORDENADAS)
    resultado = calcular_alternativa(puntos, cargar_poligonos(db))
    if resultado.motivo != "ok" or not resultado.puntos:
        _mensaje(resultado, False)
    desvio = _es_desvio(puntos, resultado.puntos or [])
    if desvio:
        geo = linea_de_puntos(resultado.puntos or [])
        if geo is None:
            raise HTTPException(status_code=422, detail=MENSAJE_SIN_SALIDA)
        _rechazar_si_postgis_cruza(db, geo, puntos)
        ruta.trazado_geojson = geo
        _recalcular(db, ruta, resultado.puntos or [])
    else:
        ruta.trazado_geojson = None
    ruta.evita_riesgo = True
    mensaje = _mensaje(resultado, desvio)
    registrar(
        db,
        id_usuario=actor.id_usuario,
        accion="alternativa_segura",
        tabla="ruta",
        registro_id=ruta.id_ruta,
        ip=ip,
        nuevos={"evita_riesgo": True, "desvio": desvio},
    )
    db.commit()
    db.refresh(ruta)
    return mensaje


def asegurar_sin_reserva(db: Session, ruta: Ruta, actor: Usuario, ip: str | None) -> None:
    geo = _geo(ruta.trazado_geojson) or linea_de_puntos(puntos_de_ruta(db, ruta))
    if geo is None:
        return
    reservas = [zona for zona in consultar_cruces(db, geo) if zona["tipo"] == RESERVA]
    if not reservas:
        return
    citados = ", ".join(f"«{zona['nombre']}»" for zona in reservas)
    registrar(
        db,
        id_usuario=actor.id_usuario,
        accion="rechazo_reserva_ecologica",
        tabla="ruta",
        registro_id=ruta.id_ruta,
        ip=ip,
        nuevos={"zonas": [zona["nombre"] for zona in reservas]},
    )
    db.commit()
    raise HTTPException(
        status_code=422,
        detail=(
            f"La ruta atraviesa la reserva ecológica {citados} "
            "y no puede confirmarse (RN-013)."
        ),
    )
