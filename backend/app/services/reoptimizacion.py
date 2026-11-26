"""Re-optimización de una ruta activa ante un evento (US-011, RF-007, RN-014, RN-015).

Solo se recalcula la ruta pedida (RN-015). Las paradas ENTREGADO o FALLIDO se
conservan. Si no hay solución dentro del tope, se conserva la ruta anterior, el
evento queda registrado como SIN_SOLUCION para revisión manual y se responde 422.
"""

import time
import uuid
from datetime import UTC, datetime
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.entities import (
    AsignacionRuta,
    Cliente,
    Conductor,
    DescansoRuta,
    DetalleRuta,
    Incidencia,
    Pedido,
    Ruta,
    Usuario,
    Vehiculo,
)
from app.optimizacion.evaluacion import LITROS_POR_GALON, Instancia, PedidoNodo, Recurso
from app.optimizacion.heuristica import _origen, _parametro, pedidos_del_dia
from app.optimizacion.reoptimizacion import presupuesto, reoptimizar
from app.optimizacion.zonas import RESERVA, cargar_poligonos, linea_de_puntos
from app.services.auditoria import registrar
from app.services.rutas import salida_ruta
from app.services.sanitizacion import exigir_textos_seguros
from app.services.zonas import consultar_cruces

ESTADOS_ACTIVOS = ("CONFIRMADA", "EN_EJECUCION")
ESTADOS_FIJOS = ("ENTREGADO", "FALLIDO")
ACCION = "reoptimizar_ruta"
ACCION_FALLO = "reoptimizacion_sin_solucion"
# El CHECK de incidencia.tipo no tiene PARADA_FALLIDA: ese motivo queda solo en auditoría.
TIPOS_INCIDENCIA = {"NUEVO_PEDIDO", "CANCELACION", "ACCIDENTE_TRANSITO", "CONGESTION"}

MENSAJE_RUTA_NO_ACTIVA = "Solo se re-optimiza una ruta CONFIRMADA o EN_EJECUCION"
MENSAJE_SIN_PENDIENTES = "No quedan paradas pendientes que re-optimizar en esta ruta."
MENSAJE_SIN_SOLUCION = (
    "No hay solución factible para las paradas pendientes dentro del tiempo límite. "
    "Se conserva la ruta anterior y el evento quedó registrado para revisión manual."
)
MENSAJE_TIEMPO = (
    "Se alcanzó el tiempo límite de re-optimización sin una secuencia completa. "
    "Se conserva la ruta anterior y el evento quedó registrado para revisión manual."
)


def _cantidad(valor: float, escala: str) -> Decimal:
    return Decimal(str(round(valor, 4))).quantize(Decimal(escala))


def _nodo(pedido: Pedido) -> PedidoNodo:
    return PedidoNodo(
        id=pedido.id_pedido,
        lat=float(pedido.latitud),
        lon=float(pedido.longitud),
        peso=float(pedido.peso_kg),
        volumen=float(pedido.volumen_m3),
        ventana_inicio=pedido.ventana_inicio,
        ventana_fin=pedido.ventana_fin,
        express=pedido.prioridad == "EXPRESS",
    )


def _ruta_activa(db: Session, id_ruta: uuid.UUID) -> tuple[Ruta, AsignacionRuta]:
    ruta = db.scalar(select(Ruta).where(Ruta.id_ruta == id_ruta).with_for_update())
    if ruta is None:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    if ruta.estado not in ESTADOS_ACTIVOS:
        raise HTTPException(status_code=409, detail=MENSAJE_RUTA_NO_ACTIVA)
    asignacion = db.scalar(select(AsignacionRuta).where(AsignacionRuta.id_ruta == id_ruta))
    if asignacion is None:
        raise HTTPException(status_code=409, detail="La ruta no tiene conductor asignado")
    return ruta, asignacion


def _recurso(db: Session, ruta: Ruta, asignacion: AsignacionRuta) -> Recurso:
    vehiculo = db.get(Vehiculo, asignacion.id_vehiculo)
    conductor = db.get(Conductor, asignacion.id_conductor)
    lat, lon = _origen(conductor)
    return Recurso(
        id_vehiculo=vehiculo.id_vehiculo,
        id_conductor=conductor.id_conductor,
        placa=vehiculo.placa,
        capacidad_kg=float(vehiculo.capacidad_kg),
        capacidad_m3=float(vehiculo.capacidad_m3),
        consumo_km_l=float(vehiculo.consumo_km_l),
        factor_co2=float(vehiculo.factor_emision_co2),
        origen_lat=lat,
        origen_lon=lon,
        inicio=datetime.combine(ruta.fecha, conductor.disponibilidad_inicio, tzinfo=UTC),
        fin=datetime.combine(ruta.fecha, conductor.disponibilidad_fin, tzinfo=UTC),
    )


def _detalles(db: Session, id_ruta: uuid.UUID) -> list[DetalleRuta]:
    return list(
        db.scalars(
            select(DetalleRuta)
            .where(DetalleRuta.id_ruta == id_ruta)
            .order_by(DetalleRuta.secuencia)
            .with_for_update()
        ).all()
    )


def _validar_cancelar(detalles: list[DetalleRuta], cancelar: list[uuid.UUID]) -> None:
    por_pedido = {detalle.id_pedido: detalle for detalle in detalles}
    for id_pedido in cancelar:
        detalle = por_pedido.get(id_pedido)
        if detalle is None:
            raise HTTPException(
                status_code=422, detail="Un pedido a cancelar no pertenece a esta ruta."
            )
        if detalle.estado_entrega in ESTADOS_FIJOS:
            raise HTTPException(
                status_code=409,
                detail=f"El pedido ya fue registrado como {detalle.estado_entrega}; no se cancela.",
            )


def _validar_agregar(db: Session, ruta: Ruta, agregar: list[uuid.UUID]) -> list[Pedido]:
    if not agregar:
        return []
    disponibles = {pedido.id_pedido: pedido for pedido in pedidos_del_dia(db, ruta.fecha)}
    pedidos = []
    for id_pedido in agregar:
        pedido = disponibles.get(id_pedido)
        if pedido is None:
            raise HTTPException(
                status_code=422,
                detail=(
                    "Un pedido nuevo no está PENDIENTE, no es de la fecha de la ruta "
                    "o ya está en otra ruta."
                ),
            )
        pedidos.append(pedido)
    return pedidos


def _instancia(db: Session, ruta: Ruta, nodos: list[PedidoNodo], limite: float) -> Instancia:
    return Instancia(
        fecha=ruta.fecha,
        pedidos=nodos,
        recursos=[],
        velocidad=max(_parametro(db, "velocidad_urbana_km_h", 25), 1),
        congestion=max(_parametro(db, "factor_congestion", 1), 0.1),
        limite=limite,
        precio_litro=_parametro(db, "precio_diesel_galon", 17.50) / LITROS_POR_GALON,
        costo_km=_parametro(db, "costo_mantenimiento_km", 1.20),
        excluidos=0,
        semilla=0,
        zonas=cargar_poligonos(db),
    )


def _incidencia(
    db: Session,
    ruta: Ruta,
    datos,
    estado: str,
) -> uuid.UUID | None:
    if datos.motivo not in TIPOS_INCIDENCIA:
        return None
    pedido = (datos.agregar or datos.cancelar or [None])[0]
    fila = Incidencia(
        tipo=datos.motivo,
        origen="MANUAL",
        id_ruta=ruta.id_ruta,
        id_pedido=pedido,
        descripcion=datos.descripcion,
        estado=estado,
        resuelta_en=datetime.now(UTC),
    )
    db.add(fila)
    db.flush()
    return fila.id_incidencia


def _cruza_reserva(db: Session, puntos: list[tuple[float, float]]) -> bool:
    geo = linea_de_puntos(puntos)
    if geo is None:
        return False
    return any(zona["tipo"] == RESERVA for zona in consultar_cruces(db, geo))


def _rechazar(
    db: Session,
    ruta: Ruta,
    datos,
    actor: Usuario,
    ip: str | None,
    mensaje: str,
    resultado: dict,
) -> None:
    id_incidencia = _incidencia(db, ruta, datos, "SIN_SOLUCION")
    registrar(
        db,
        id_usuario=actor.id_usuario,
        accion=ACCION_FALLO,
        tabla="ruta",
        registro_id=ruta.id_ruta,
        ip=ip,
        nuevos={
            "motivo": datos.motivo,
            "id_incidencia": str(id_incidencia) if id_incidencia else None,
            **resultado,
        },
    )
    db.commit()
    raise HTTPException(status_code=422, detail=mensaje)


def _renumerar(
    db: Session,
    ruta: Ruta,
    detalles: list[DetalleRuta],
    fijas: int,
    orden: list[uuid.UUID],
    plan,
) -> None:
    # UNIQUE (id_ruta, secuencia) no es diferible: primero se apartan las secuencias.
    for detalle in detalles:
        detalle.secuencia += 10_000
    db.flush()
    por_pedido = {detalle.id_pedido: detalle for detalle in detalles}
    fijos = [d for d in detalles if d.estado_entrega in ESTADOS_FIJOS]
    for indice, detalle in enumerate(fijos, start=1):
        detalle.secuencia = indice
    for posicion, id_pedido in enumerate(orden, start=fijas + 1):
        parada = plan.paradas[posicion - 1]
        detalle = por_pedido.get(id_pedido)
        if detalle is None:
            detalle = DetalleRuta(
                id_ruta=ruta.id_ruta,
                id_pedido=id_pedido,
                secuencia=posicion,
                eta=parada.eta,
                estado_entrega="PENDIENTE",
            )
            db.add(detalle)
            continue
        detalle.secuencia = posicion
        detalle.eta = parada.eta
    db.flush()


def _totales(db: Session, ruta: Ruta, plan) -> None:
    ruta.distancia_total_km = _cantidad(plan.distancia_km, "0.01")
    ruta.tiempo_total_min = _cantidad(plan.minutos_reloj, "0.01")
    ruta.combustible_estimado_l = _cantidad(plan.combustible_l, "0.01")
    ruta.co2_estimado_kg = _cantidad(plan.co2_kg, "0.001")
    ruta.minutos_conduccion = _cantidad(plan.minutos_conduccion, "0.01")
    # El trazado guardado era del orden anterior; el nuevo se dibuja parada a parada.
    ruta.trazado_geojson = None
    ruta.evita_riesgo = False
    db.execute(delete(DescansoRuta).where(DescansoRuta.id_ruta == ruta.id_ruta))
    for descanso in plan.descansos:
        db.add(
            DescansoRuta(
                id_ruta=ruta.id_ruta,
                despues_de_secuencia=descanso.despues_de_secuencia,
                duracion_min=descanso.duracion_min,
                motivo="LEY_30224",
            )
        )


def reoptimizar_ruta(
    db: Session,
    id_ruta: uuid.UUID,
    datos,
    actor: Usuario,
    ip: str | None,
) -> dict:
    inicio = time.perf_counter()
    tope = presupuesto(_parametro(db, "tiempo_max_reoptimizacion_s", 30))
    limite = inicio + tope
    exigir_textos_seguros(
        db,
        id_usuario=actor.id_usuario,
        ip=ip,
        tabla="ruta",
        campos=[(datos.descripcion, "descripcion")],
    )
    ruta, asignacion = _ruta_activa(db, id_ruta)
    detalles = _detalles(db, id_ruta)
    _validar_cancelar(detalles, datos.cancelar)
    nuevos = _validar_agregar(db, ruta, datos.agregar)

    cancelados = set(datos.cancelar)
    pedidos = {d.id_pedido: db.get(Pedido, d.id_pedido) for d in detalles}
    fijas = [_nodo(pedidos[d.id_pedido]) for d in detalles if d.estado_entrega in ESTADOS_FIJOS]
    pendientes = [
        _nodo(pedidos[d.id_pedido])
        for d in detalles
        if d.estado_entrega not in ESTADOS_FIJOS and d.id_pedido not in cancelados
    ]
    agregados = [_nodo(pedido) for pedido in nuevos]
    if not pendientes and not agregados:
        raise HTTPException(status_code=409, detail=MENSAJE_SIN_PENDIENTES)

    recurso = _recurso(db, ruta, asignacion)
    inst = _instancia(db, ruta, fijas + pendientes + agregados, limite)
    resultado = reoptimizar(recurso, fijas, pendientes, agregados, inst, inicio=inicio)
    traza = {
        "segundos": round(resultado.segundos, 4),
        "presupuesto_s": tope,
        "cortado": resultado.cortado,
    }
    if not resultado.factible or resultado.ruta is None:
        mensaje = MENSAJE_TIEMPO if resultado.cortado else MENSAJE_SIN_SOLUCION
        _rechazar(db, ruta, datos, actor, ip, mensaje, traza)

    puntos_pendientes = [(p.lat, p.lon) for p in resultado.ruta.paradas[len(fijas) - 1 :]]
    if not fijas:
        puntos_pendientes = [(recurso.origen_lat, recurso.origen_lon)] + [
            (p.lat, p.lon) for p in resultado.ruta.paradas
        ]
    if _cruza_reserva(db, puntos_pendientes):
        _rechazar(db, ruta, datos, actor, ip, MENSAJE_SIN_SOLUCION, traza)

    distancia_antes = float(ruta.distancia_total_km) if ruta.distancia_total_km else None
    for detalle in detalles:
        if detalle.id_pedido in cancelados:
            pedidos[detalle.id_pedido].estado = "CANCELADO"
            db.delete(detalle)
    detalles = [d for d in detalles if d.id_pedido not in cancelados]
    db.flush()
    for pedido in nuevos:
        pedido.estado = "ASIGNADO"
    _renumerar(db, ruta, detalles, len(fijas), resultado.orden, resultado.ruta)
    _totales(db, ruta, resultado.ruta)
    id_incidencia = _incidencia(db, ruta, datos, "REOPTIMIZADA")
    segundos = time.perf_counter() - inicio
    registrar(
        db,
        id_usuario=actor.id_usuario,
        accion=ACCION,
        tabla="ruta",
        registro_id=ruta.id_ruta,
        ip=ip,
        nuevos={
            "motivo": datos.motivo,
            "id_incidencia": str(id_incidencia) if id_incidencia else None,
            "agregados": [str(item) for item in datos.agregar],
            "cancelados": [str(item) for item in datos.cancelar],
            "estrategia": resultado.estrategia,
            "segundos": round(segundos, 4),
            "presupuesto_s": tope,
            "cortado": resultado.cortado,
        },
    )
    db.commit()
    db.refresh(ruta)
    mensaje = (
        f"Ruta re-optimizada en {segundos:.2f} s (tope {tope:.0f} s). "
        f"Se conservaron {len(fijas)} parada(s) ya resueltas y se ordenaron "
        f"{len(resultado.orden)} pendiente(s)."
    )
    if resultado.cortado:
        mensaje += " Se llegó al tope y se usó la mejor secuencia hallada."
    cuerpo_ruta = salida_ruta(db, ruta, actor.rol)
    return {
        "mensaje": mensaje,
        "segundos": round(segundos, 4),
        "presupuesto_s": tope,
        "cortado": resultado.cortado,
        "estrategia": resultado.estrategia,
        "paradas_fijas": len(fijas),
        "paradas_reordenadas": len(resultado.orden),
        "agregadas": len(nuevos),
        "canceladas": len(cancelados),
        "distancia_antes_km": distancia_antes,
        "distancia_despues_km": float(ruta.distancia_total_km)
        if ruta.distancia_total_km is not None
        else None,
        "ruta": cuerpo_ruta,
    }


def pedidos_disponibles(db: Session, id_ruta: uuid.UUID) -> list[dict]:
    ruta = db.get(Ruta, id_ruta)
    if ruta is None:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    salida = []
    for pedido in pedidos_del_dia(db, ruta.fecha)[:50]:
        cliente = db.get(Cliente, pedido.id_cliente)
        salida.append(
            {
                "id_pedido": pedido.id_pedido,
                "nombre_cliente": cliente.nombre if cliente else None,
                "punto_referencia": pedido.punto_referencia,
                "peso_kg": float(pedido.peso_kg),
                "prioridad": pedido.prioridad,
            }
        )
    return salida
