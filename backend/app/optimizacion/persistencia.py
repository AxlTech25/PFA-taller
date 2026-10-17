"""Persiste el plan de la heurística. No se invoca desde la petición HTTP."""

from decimal import Decimal

from app.models.entities import AsignacionRuta, DescansoRuta, DetalleRuta, JobOptimizacion, Ruta
from app.optimizacion.heuristica import Plan


def _cantidad(valor: float, escala: str) -> Decimal:
    return Decimal(str(round(valor, 4))).quantize(Decimal(escala))


def persistir_plan(db, job: JobOptimizacion, plan: Plan) -> list[str]:
    identificadores: list[str] = []
    for item in plan.rutas:
        ruta = Ruta(
            fecha=job.fecha,
            estado="BORRADOR",
            distancia_total_km=_cantidad(item.distancia_km, "0.01"),
            tiempo_total_min=_cantidad(item.minutos_reloj, "0.01"),
            combustible_estimado_l=_cantidad(item.combustible_l, "0.01"),
            co2_estimado_kg=_cantidad(item.co2_kg, "0.001"),
            minutos_conduccion=_cantidad(item.minutos_conduccion, "0.01"),
            id_job=job.id_job,
        )
        db.add(ruta)
        db.flush()
        db.add(
            AsignacionRuta(
                id_ruta=ruta.id_ruta,
                id_vehiculo=item.id_vehiculo,
                id_conductor=item.id_conductor,
            )
        )
        for indice, parada in enumerate(item.paradas, start=1):
            db.add(
                DetalleRuta(
                    id_ruta=ruta.id_ruta,
                    id_pedido=parada.id_pedido,
                    secuencia=indice,
                    eta=parada.eta,
                    estado_entrega="PENDIENTE",
                )
            )
        for descanso in item.descansos:
            db.add(
                DescansoRuta(
                    id_ruta=ruta.id_ruta,
                    despues_de_secuencia=descanso.despues_de_secuencia,
                    duracion_min=descanso.duracion_min,
                    motivo="LEY_30224",
                )
            )
        identificadores.append(str(ruta.id_ruta))
    return identificadores
