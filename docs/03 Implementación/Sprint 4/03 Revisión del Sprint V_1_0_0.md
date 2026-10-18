[← Volver al README Principal](../../../README.md)

# Revisión del sprint

**Nombre del Proyecto:** EcoLogística Lima – Optimizador de Rutas Sostenibles para DistriRápido S.A.C.

**Líder del Proyecto:** Carhuapoma Fano, Eilene Elizabeth

**Versión:** 1.3.0 — Sprint 4 (revisión 18/10/2026)

---

## Historias de Usuario completadas en este Sprint

Sprint Goal: *el worker calcula el plan del día con un algoritmo genético VRPTW + Green VRP, lo compara con el vecino más cercano y lo deja en borrador dentro del presupuesto de 45 s; el operador ve el trazado en el mapa.*

| ID | Historia / Enabler | SP | ¿Done? | Comentario de la Review |
|---|---|---|---|---|
| ENB-001 | Motor con SLA | 13, cierre del tramo | Sí en código; Staging no | DEAP en el worker. Bench 150×15 factible, sin violar capacidad, ventanas, jornada ni pico y placa, y sin empeorar el costo verde del vecino. Ocho corridas locales bajo 0,1 s. Falta la misma corrida en Staging (IMP-04). |
| US-010 | Rutas VRPTW + Green VRP | 13, cierre del tramo | Sí en código | `POST /optimizaciones` sigue en 202. El mensaje nombra al algoritmo genético y al vecino más cercano. Pico y placa, congestión, borrador y el fallo sin solución se conservan. El P95 en Staging no se certifica. |
| US-012 | Mapa Leaflet/OSM | 8 | No (inicio) | Trazado, punto de partida, paradas, ETA por tramo y semáforo. Si las teselas fallan, aviso y tabla. Zonas y ruta alternativa quedan en el Sprint 5. |
| US-014 | Dashboard | 8 | No (inicio) | El Hito 3 lo nombra. Hay km, kg CO₂, litros, % de ventanas, soles de combustible, de mantenimiento y ahorrados frente a la línea base. Período vacío: «Sin datos de operación para el período seleccionado.» Árboles en blanco hasta ratificar RN-018. |

**Resultado:** se cierra el tramo de motor que el Sprint 3 dejó abierto. No se acepta el cierre de los 8 SP de US-012 ni de US-014. IMP-04 no se cierra.

---

## Demostración del trabajo completado

**Audiencia:** docente (I-04) y el equipo. **Ambiente:** `docker compose up --build` (API, worker, Redis, Postgres en el puerto 5433 del host, SPA en 5173).

| Paso | Qué se ve | Historia |
|---|---|---|
| 1 | Login Operador → Rutas → Generar rutas. El mensaje dice que el trabajo quedó en cola | ENB-006, se mantiene |
| 2 | Al terminar, el texto nombra al algoritmo genético y la comparación con el vecino más cercano. La ruta sigue en Borrador | ENB-001, US-010 |
| 3 | El mapa dibuja la partida y las paradas. La tabla muestra el ETA del tramo y el semáforo | US-012 |
| 4 | Tablero del mismo día: km, CO₂, litros, soles y % de ventanas. Otro día sin rutas muestra el mensaje de período vacío | US-014, inicio |
| 5 | Confirmar ruta sigue rechazando más de 8 h (Ley N.º 30224) | US-007, regresión |

**Feedback previsto:** no presentar la muestra local de ocho corridas como el P95 de Staging, ni el tablero como el cierre de US-014, ni las envolventes como el catastro de Lima.

---

## Pendientes

| Pendiente | Dueño | Sprint destino |
|---|---|---|
| IMP-04 Staging (Railway/Render), incluida la corrida del bench en ese ambiente | Axel / Jorge | Hito 3, 12/11/2026 |
| Cierre de US-012 y US-013 | Katheryn | 5 |
| Cierre de US-014 y factor de árboles ratificado | Katheryn / Brayan | 5 |
| IMP-11 polígonos oficiales, si aparece el archivo | Brayan | Cuando exista el archivo |
| Jira a Done el día del merge (A5) | Eilene | Al merge de este PR |

Guion y métricas: [01 Informe de estado del proyecto V_1_0_0.md](./01%20Informe%20de%20estado%20del%20proyecto%20V_1_0_0.md). Impedimentos: [02 Registro de Impedimentos V_1_0_0.md](./02%20Registro%20de%20Impedimentos%20V_1_0_0.md).

---

## Historial de control de cambios

| Versión | Fecha | Autor | Descripción |
|---|---|---|---|
| 1.0.0 | 02/10/2026 | Equipo EcoLogística Lima | Review del Sprint 1. |
| 1.1.0 | 02/10/2026 | Equipo EcoLogística Lima | Review del Sprint 2. |
| 1.2.0 | 17/10/2026 | Equipo EcoLogística Lima | Review del Sprint 3. |
| 1.3.0 | 18/10/2026 | Equipo EcoLogística Lima | Review del Sprint 4. Motor cerrado en código. Mapa y tablero iniciados. Staging abierto. |

---

[← Volver al README Principal](../../../README.md)
