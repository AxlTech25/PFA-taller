[← Volver al README Principal](../../../README.md)

# Revisión del sprint

**Nombre del Proyecto:** EcoLogística Lima – Optimizador de Rutas Sostenibles para DistriRápido S.A.C.

**Líder del Proyecto:** Carhuapoma Fano, Eilene Elizabeth

**Versión:** 1.2.0 — Sprint 3 (revisión 17/10/2026, [PR #15](https://github.com/AxlTech25/PFA-taller/pull/15))

---

## Historias de Usuario completadas en este Sprint

Sprint Goal: *un Operador registra pedidos con cobertura de Lima Este y punto de referencia; el sistema respeta la jornada de 8 h; queda un worker listo y una heurística de rutas demostrable (aunque no sea el GA final).*

| ID | Historia / Enabler | SP | ¿Done? | Comentario de la Review |
|---|---|---|---|---|
| US-008 B | Cobertura Lima Este y punto de referencia | 3 | Sí | «frente a la bodega El Ahorro» marca `georreferencia_aproximada`. Fuera de SJL / El Agustino / Santa Anita / Ate no se crea el pedido. La ventana inválida sigue en 422. |
| US-007 | Jornada de 8 h y descansos | 5 | Sí | Confirmar una conducción de más de 8 h responde el incumplimiento de la Ley N.º 30224 y no cambia el borrador. Un tramo de 4 h inserta 1 h de descanso. La suma del día del mismo conductor también se rechaza. |
| ENB-006 | Worker y cola Redis | 5 | Sí | `POST /optimizaciones` responde 202 con `id_job` y no calcula en el request. El proceso `python -m app.worker` consume Redis. Si Redis no responde, 503 y no queda job en la base. |
| ENB-001 | Motor con SLA | 13, partido | No (inicio) | Hay presupuesto de 45 s y corte controlado. No hay GA/Tabú/ACO ni bench 150×15 en Staging. |
| US-010 | Rutas VRPTW + Green VRP | 13, partido | No (inicio) | Vecino más cercano: capacidad, ventana, punto de partida, pico y placa por último dígito y factor de congestión. Rutas en `BORRADOR` hasta confirmar. Falta la metaheurística y el escenario de 150/15. |

**Resultado:** 13 SP cerrados (3 + 5 + 5) y el inicio demostrable del motor. No se acepta el cierre de los 13 SP de ENB-001 ni de US-010.

---

## Demostración del trabajo completado

**Audiencia:** docente (I-04) y el equipo. **Ambiente:** `docker compose up --build` (API, worker, Redis, Postgres en el puerto 5433 del host, SPA en 5173).

| Paso | Qué se ve | Historia |
|---|---|---|
| 1 | Login Operador → Pedidos → punto de referencia «frente a la bodega El Ahorro» → Pendiente, distrito y georreferencia aproximada | US-008 B |
| 2 | La misma alta con coordenadas de Miraflores → rechazo de cobertura, sin fila nueva | US-008 B |
| 3 | Rutas → Generar rutas → el mensaje dice que el trabajo quedó en cola; al terminar, la ruta está en Borrador | ENB-006 + inicio US-010 |
| 4 | Confirmar ruta → pasa a Confirmada y los pedidos a Asignado, dentro de 8 h | US-007 |
| 5 | Una ruta armada con más de 8 h de conducción → 422 y texto de la Ley N.º 30224; sigue en Borrador | US-007 |
| 6 | `/docs` describe `GET /clientes` como catálogo de demostración, sin altas, y publica `/optimizaciones` y `/rutas` | A8 + ENB-007 |

**Feedback previsto:** no presentar la heurística como el algoritmo genético final ni las envolventes como el catastro de Lima.

---

## Pendientes

| Pendiente | Dueño | Sprint destino |
|---|---|---|
| Resto de ENB-001 y US-010 (metaheurística, 150×15, SLA en Staging) | Jorge | 4 |
| US-012 mapa Leaflet/OSM | Katheryn | 4–5 |
| IMP-04 Staging (Railway/Render) | Axel / Jorge | Hito 3, 12/11/2026 |
| Sustituir envolventes por polígonos oficiales (IMP-11) | Brayan | 4, si hay el archivo |
| Jira a Done el día del merge (A5) | Eilene | Al merge de este PR |

Guion y métricas: [01 Informe de estado del proyecto V_1_0_0.md](./01%20Informe%20de%20estado%20del%20proyecto%20V_1_0_0.md). Impedimentos: [02 Registro de Impedimentos V_1_0_0.md](./02%20Registro%20de%20Impedimentos%20V_1_0_0.md).

---

## Historial de control de cambios

| Versión | Fecha | Autor | Descripción |
|---|---|---|---|
| 1.0.0 | 02/10/2026 | Equipo EcoLogística Lima | Review del Sprint 1. |
| 1.1.0 | 02/10/2026 | Equipo EcoLogística Lima | Review del Sprint 2. |
| 1.2.0 | 17/10/2026 | Equipo EcoLogística Lima | Review del Sprint 3. 13 SP cerrados y motor solo en su primer tramo. |

---

[← Volver al README Principal](../../../README.md)
