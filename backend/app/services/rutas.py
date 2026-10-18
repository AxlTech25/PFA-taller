"""Solicitud asíncrona de rutas y confirmación de jornada (ENB-006, US-007, US-010)."""

import uuid
from datetime import date

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.entities import (
    AsignacionRuta,
    Cliente,
    Conductor,
    DescansoRuta,
    DetalleRuta,
    JobOptimizacion,
    Pedido,
    Ruta,
    Usuario,
    Vehiculo,
)
from app.optimizacion import cola
from app.optimizacion.congestion import nivel_congestion
from app.optimizacion.evaluacion import DEPOSITO_SJL, distancia_km
from app.optimizacion.heuristica import _parametro
from app.optimizacion.jornada import MENSAJE_JORNADA, descansos_requeridos
from app.services.auditoria import registrar

MENSAJE_ENCOLADO = (
    "La optimización quedó en cola. Consulte el resultado con el identificador del trabajo."
)
MENSAJE_CONFIRMADA = (
    "Ruta confirmada. La jornada respeta las 8 horas y los descansos de la Ley N.º 30224."
)


def solicitar(db: Session, actor: Usuario, fecha: date, ip: str | None) -> JobOptimizacion:
    if not cola.disponible():
        raise HTTPException(status_code=503, detail=cola.MENSAJE_COLA)
    job = JobOptimizacion(
        estado="ENCOLADO",
        id_usuario=actor.id_usuario,
        fecha=fecha,
        mensaje=MENSAJE_ENCOLADO,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    try:
        cola.encolar(str(job.id_job))
    except cola.ColaNoDisponible:
        db.delete(job)
        db.commit()
        raise HTTPException(status_code=503, detail=cola.MENSAJE_COLA) from None
    registrar(
        db,
        id_usuario=actor.id_usuario,
        accion="solicitar_optimizacion",
        tabla="job_optimizacion",
        registro_id=job.id_job,
        ip=ip,
        nuevos={"fecha": fecha.isoformat(), "estado": job.estado},
    )
    db.commit()
    return job


def obtener_job(db: Session, id_job: uuid.UUID) -> JobOptimizacion:
    job = db.get(JobOptimizacion, id_job)
    if job is None:
        raise HTTPException(status_code=404, detail="Trabajo de optimización no encontrado")
    return job


def _float(valor) -> float | None:
    if valor is None:
        return None
    return float(valor)


def _mapa(db: Session) -> tuple[float, float]:
    velocidad = max(_parametro(db, "velocidad_urbana_km_h", 25), 1)
    congestion = max(_parametro(db, "factor_congestion", 1), 0.1)
    return velocidad, congestion


def salida_ruta(
    db: Session,
    ruta: Ruta,
    rol: str,
    mapa: tuple[float, float] | None = None,
) -> dict:
    asignacion = db.scalar(select(AsignacionRuta).where(AsignacionRuta.id_ruta == ruta.id_ruta))
    vehiculo = db.get(Vehiculo, asignacion.id_vehiculo) if asignacion else None
    conductor = db.get(Conductor, asignacion.id_conductor) if asignacion else None
    anonimo = rol == "AUDITOR"
    detalles = list(
        db.scalars(
            select(DetalleRuta)
            .where(DetalleRuta.id_ruta == ruta.id_ruta)
            .order_by(DetalleRuta.secuencia)
        ).all()
    )
    descansos = list(
        db.scalars(
            select(DescansoRuta)
            .where(DescansoRuta.id_ruta == ruta.id_ruta)
            .order_by(DescansoRuta.despues_de_secuencia)
        ).all()
    )
    velocidad, congestion = mapa or _mapa(db)
    origen_lat = None
    origen_lon = None
    if conductor is not None and not anonimo:
        if conductor.lat_punto_partida is not None and conductor.lon_punto_partida is not None:
            origen_lat = _float(conductor.lat_punto_partida)
            origen_lon = _float(conductor.lon_punto_partida)
        else:
            origen_lat, origen_lon = DEPOSITO_SJL
    previo = (origen_lat, origen_lon)
    paradas = []
    for detalle in detalles:
        pedido = db.get(Pedido, detalle.id_pedido)
        cliente = db.get(Cliente, pedido.id_cliente) if pedido else None
        latitud = None if anonimo or pedido is None else _float(pedido.latitud)
        longitud = None if anonimo or pedido is None else _float(pedido.longitud)
        minutos = None
        hay_tramo = None not in (previo[0], previo[1], latitud, longitud)
        if hay_tramo:
            km = distancia_km(previo[0], previo[1], latitud, longitud)
            minutos = round((km / velocidad) * 60.0 * congestion, 2)
            previo = (latitud, longitud)
        paradas.append(
            {
                "secuencia": detalle.secuencia,
                "id_pedido": detalle.id_pedido,
                "nombre_cliente": cliente.nombre if cliente else None,
                "eta": detalle.eta,
                "latitud": latitud,
                "longitud": longitud,
                "punto_referencia": None if anonimo or pedido is None else pedido.punto_referencia,
                "minutos_tramo": minutos,
                "nivel_congestion": nivel_congestion(congestion, detalle.eta),
            }
        )
    comparacion = None
    if ruta.id_job is not None:
        job = db.get(JobOptimizacion, ruta.id_job)
        if job is not None and job.resultado:
            comparacion = job.resultado.get("comparacion")
    return {
        "id_ruta": ruta.id_ruta,
        "fecha": ruta.fecha,
        "estado": ruta.estado,
        "distancia_total_km": _float(ruta.distancia_total_km),
        "tiempo_total_min": _float(ruta.tiempo_total_min),
        "minutos_conduccion": _float(ruta.minutos_conduccion),
        "combustible_estimado_l": _float(ruta.combustible_estimado_l),
        "co2_estimado_kg": _float(ruta.co2_estimado_kg),
        "placa": vehiculo.placa if vehiculo else None,
        "conductor": conductor.nombre if conductor else None,
        "id_conductor": conductor.id_conductor if conductor else None,
        "origen_lat": origen_lat,
        "origen_lon": origen_lon,
        "comparacion": comparacion,
        "descansos": [
            {
                "despues_de_secuencia": descanso.despues_de_secuencia,
                "duracion_min": descanso.duracion_min,
                "motivo": descanso.motivo,
            }
            for descanso in descansos
        ],
        "paradas": paradas,
    }


def salida_job(db: Session, job: JobOptimizacion, rol: str) -> dict:
    rutas = list(
        db.scalars(select(Ruta).where(Ruta.id_job == job.id_job).order_by(Ruta.generada_en)).all()
    )
    mapa = _mapa(db)
    comparacion = None
    algoritmo = None
    if job.resultado:
        comparacion = job.resultado.get("comparacion")
        algoritmo = job.resultado.get("algoritmo")
    return {
        "id_job": job.id_job,
        "estado": job.estado,
        "fecha": job.fecha,
        "mensaje": job.mensaje,
        "algoritmo": algoritmo,
        "comparacion": comparacion,
        "rutas": [salida_ruta(db, ruta, rol, mapa) for ruta in rutas],
    }


def listar_rutas(db: Session, actor: Usuario, fecha: date | None) -> list[dict]:
    consulta = select(Ruta).order_by(Ruta.fecha.desc(), Ruta.generada_en.desc())
    if fecha is not None:
        consulta = consulta.where(Ruta.fecha == fecha)
    filas = list(db.scalars(consulta.limit(100)).all())
    mapa = _mapa(db)
    return [salida_ruta(db, fila, actor.rol, mapa) for fila in filas]


def confirmar(db: Session, id_ruta: uuid.UUID, actor: Usuario, ip: str | None) -> dict:
    ruta = db.get(Ruta, id_ruta)
    if ruta is None:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    if ruta.estado != "BORRADOR":
        raise HTTPException(status_code=409, detail="Solo se puede confirmar una ruta en borrador")
    asignacion = db.scalar(select(AsignacionRuta).where(AsignacionRuta.id_ruta == ruta.id_ruta))
    if asignacion is None:
        raise HTTPException(status_code=409, detail="La ruta no tiene conductor asignado")

    minutos = float(ruta.minutos_conduccion or 0)
    otros = db.scalar(
        select(func.coalesce(func.sum(Ruta.minutos_conduccion), 0))
        .join(AsignacionRuta, AsignacionRuta.id_ruta == Ruta.id_ruta)
        .where(
            AsignacionRuta.id_conductor == asignacion.id_conductor,
            Ruta.fecha == ruta.fecha,
            Ruta.estado.in_(("CONFIRMADA", "EN_EJECUCION")),
            Ruta.id_ruta != ruta.id_ruta,
        )
    )
    total = minutos + float(otros or 0)
    if total > 8 * 60:
        registrar(
            db,
            id_usuario=actor.id_usuario,
            accion="rechazo_jornada",
            tabla="ruta",
            registro_id=ruta.id_ruta,
            ip=ip,
            nuevos={"minutos_conduccion": total},
        )
        db.commit()
        raise HTTPException(status_code=422, detail=MENSAJE_JORNADA)

    existentes = list(
        db.scalars(select(DescansoRuta).where(DescansoRuta.id_ruta == ruta.id_ruta)).all()
    )
    faltan = descansos_requeridos(minutos) - len(existentes)
    for _ in range(max(faltan, 0)):
        db.add(
            DescansoRuta(
                id_ruta=ruta.id_ruta,
                despues_de_secuencia=0,
                duracion_min=60,
                motivo="LEY_30224",
            )
        )
    ruta.estado = "CONFIRMADA"
    detalles = list(
        db.scalars(select(DetalleRuta).where(DetalleRuta.id_ruta == ruta.id_ruta)).all()
    )
    for detalle in detalles:
        pedido = db.get(Pedido, detalle.id_pedido)
        if pedido is not None and pedido.estado == "PENDIENTE":
            pedido.estado = "ASIGNADO"
    mensaje = MENSAJE_CONFIRMADA
    if faltan > 0:
        mensaje += " Se insertó el descanso obligatorio de 1 hora."
    registrar(
        db,
        id_usuario=actor.id_usuario,
        accion="confirmar_ruta",
        tabla="ruta",
        registro_id=ruta.id_ruta,
        ip=ip,
        nuevos={"estado": "CONFIRMADA", "descansos_insertados": max(faltan, 0)},
    )
    db.commit()
    db.refresh(ruta)
    cuerpo = salida_ruta(db, ruta, actor.rol)
    cuerpo["mensaje"] = mensaje
    return cuerpo
