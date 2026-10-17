[← Volver al README Principal](../../README.md)

# UNIVERSIDAD CONTINENTAL
## Taller de Proyectos 2 — Escuela Profesional de Ingeniería de Sistemas e Informática

# 05. Cronograma de sprints

**Nombre del Proyecto:** EcoLogística Lima – Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Fecha:** 16/10/2026  
**Versión:** 1.0.2  
**Project Manager:** Carhuapoma Fano, Eilene Elizabeth

Cada sprint dura **2 semanas calendario**. El Sprint 3 arranca el **16/10/2026**; a partir de ahí el calendario se recorre 16 días. El Hito 4 queda el **13/12/2026**. Fuente de alcance: [01 Transformando a ágil V_1_0_7.md](./01%20Transformando%20a%20%C3%A1gil%20V_1_0_7.md).

---

## 1. Calendario vigente

| Sprint | Nombre en Jira | Inicio | Fin | Hito del Acta | Enfoque |
|---|---|---|---|---|---|
| 1 | `ECO Sprint 1` | 02/09/2026 | 15/09/2026 | Hito 1 (02/09/2026) — inicio formal | Login, flota, esquema PostGIS, OpenAPI, CI |
| 2 | `ECO Sprint 2` | 16/09/2026 | 29/09/2026 | Hito 2 (29/09/2026) — identidad, flota, conductores y pedidos base | Usuarios, bloqueo, conductores, alta de pedido |
| 3 | `ECO Sprint 3` | **16/10/2026** | **29/10/2026** | — | US-008 B, jornada 8 h, worker, inicio del motor |
| 4 | `ECO Sprint 4` | 30/10/2026 | 12/11/2026 | Hito 3 (12/11/2026) — motor, mapa y dashboard integrados | Motor VRPTW, mapa Leaflet |
| 5 | `ECO Sprint 5` | 13/11/2026 | 26/11/2026 | — | Zonas, dashboard, modo conductor, WCAG |
| 6 | `ECO Sprint 6` | 27/11/2026 | 10/12/2026 | — | Re-optimización, PDF, confirmar entrega |
| Cierre | — | 11/12/2026 | 13/12/2026 | Hito 4 (13/12/2026) — entrega final | UAT, documentación y presentación |

**Release Jira:** `v1.0.3-MVP` · fecha objetivo **13/12/2026**.

```
02/09          16/09          16/10          30/10          13/11          27/11          11/12
 |---- S1 ----| |---- S2 ----| … |---- S3 ----| |---- S4 ----| |---- S5 ----| |---- S6 ----| |Cierre|
 Hito 1         Hito 2                            Hito 3                                    Hito 4
```

Entre el fin planificado del Sprint 2 (29/09) y el arranque del 3 (16/10) hay un hueco de calendario: el software del 2 se fusionó el 01/10 y el equipo reabre Daily el 16/10.

---

## 2. Seguimiento real

| Sprint | Plan vigente | Cierre en código | Desfase | Evidencia |
|---|---|---|---|---|
| 1 | 02/09/2026 – 15/09/2026 | 30/09/2026 | +15 días | [PR #9](https://github.com/AxlTech25/PFA-taller/pull/9) · [Sprint 1](../03%20Implementaci%C3%B3n/Sprint%201/) |
| 2 | 16/09/2026 – 29/09/2026 | 01/10/2026 | +2 días | [PR #10](https://github.com/AxlTech25/PFA-taller/pull/10) · [Sprint 2](../03%20Implementaci%C3%B3n/Sprint%202/) |
| 3 | 16/10/2026 – 29/10/2026 | — | Calendario rebaselinado el 16/10 | En curso |
| 4 | 30/10/2026 – 12/11/2026 | — | — | Planificado |
| 5 | 13/11/2026 – 26/11/2026 | — | — | Planificado |
| 6 | 27/11/2026 – 10/12/2026 | — | — | Planificado |
| Cierre | 11/12/2026 – 13/12/2026 | — | — | Planificado |

---

## 3. Compromiso por sprint (26 SP)

Velocidad: **26 SP / sprint**. Total **156 SP**. Los ítems de 13 SP se parten 8+5; los de 8 que cruzan sprint se parten 5+3. Detalle BDD: [01 Transformando a ágil V_1_0_7.md](./01%20Transformando%20a%20%C3%A1gil%20V_1_0_7.md) §§9–14.

### Sprint 1 — cerrado (PR #9)

| ID | Resultado | SP | Responsable |
|---|---|---|---|
| ENB-003 | Esquema PostgreSQL + PostGIS | 8 | Leon Taza, Brayan Angel |
| ENB-002 | Pipeline CI/CD y Quality Gate | 5 | Estrada Flores, Axel Sebastian |
| US-001 | Autenticación JWT | 5 | Estrada Flores, Axel Sebastian |
| US-004 | Registrar vehículo | 5 | Huaman Baldeon, Katheryn Elena |
| ENB-007 | OpenAPI vivo | 3 | Cruz Salazar, Jorge Luiz |
| | **Total** | **26** | |

Fuera: usuarios, pedidos, motor.

### Sprint 2 — cerrado (PR #10)

| ID | Resultado | SP | Responsable |
|---|---|---|---|
| US-002 | Usuarios y roles RBAC | 5 | Estrada Flores, Axel Sebastian |
| US-003 | Consentimiento y bloqueo | 3 | Estrada Flores, Axel Sebastian |
| US-005 | Consultar / actualizar flota + menú | 3 | Huaman Baldeon, Katheryn Elena |
| US-006 | Registrar conductor | 5 | Leon Taza, Brayan Angel |
| US-008 A | Alta de pedido con cliente demo | 5 | Huaman Baldeon, Katheryn Elena |
| ENB-004 | Hardening OWASP y `log_auditoria` | 5 | Cruz Salazar, Jorge Luiz |
| | **Total** | **26** | |

Fuera: US-008 B, US-007, mapa.

### Sprint 3 — 16/10/2026 – 29/10/2026 (en curso)

| ID | Resultado | SP | Responsable |
|---|---|---|---|
| US-008 B | Cobertura Lima Este y punto de referencia | 3 | Huaman Baldeon, Katheryn Elena |
| US-007 | Jornada de 8 h y descansos (Ley N.º 30224) | 5 | Cruz Salazar, Jorge Luiz |
| ENB-006 | Worker y cola Redis (API 202 + `job_id`) | 5 | Cruz Salazar, Jorge Luiz |
| ENB-001 A | Heurística constructiva Sweep/NN demostrable | 8 | Cruz Salazar, Jorge Luiz |
| US-010 A | Generar rutas: job asíncrono y plan factible (escenario ≤ 50 pedidos) | 5 | Cruz Salazar, Jorge Luiz |
| | **Total** | **26** | |

Fuera: GA/SLA 150×15, mapa, dashboard. IMP-04 (CodeQL + Staging) corre en paralelo, **sin SP** del compromiso.

### Sprint 4 — 30/10/2026 – 12/11/2026 · Hito 3

| ID | Resultado | SP | Responsable |
|---|---|---|---|
| ENB-001 B | Metaheurística GA/Tabú; P95 ≤ 45 s en 150×15 | 5 | Cruz Salazar, Jorge Luiz |
| US-010 B | Cierre: persistir rutas BORRADOR, pico y placa, 150 pedidos / 15 vehículos | 8 | Cruz Salazar, Jorge Luiz |
| US-012 | Mapa Leaflet/OSM (trazado, paradas, congestión; tabular si fallan tiles) | 8 | Huaman Baldeon, Katheryn Elena |
| US-014 A | Dashboard: km, kg CO₂ y litros de la última ruta | 5 | Huaman Baldeon, Katheryn Elena |
| | **Total** | **26** | |

Fuera: modo conductor, PDF, re-optimización. El Hito 3 pide motor + mapa + dashboard: el dashboard entra iniciado (incremento A); equivalentes en soles/árboles quedan para el Sprint 5.

### Sprint 5 — 13/11/2026 – 26/11/2026

| ID | Resultado | SP | Responsable |
|---|---|---|---|
| US-014 B | Dashboard: % ventanas, soles, árboles y período vacío | 3 | Huaman Baldeon, Katheryn Elena |
| US-013 | Zonas de riesgo PostGIS y ruta alternativa | 5 | Leon Taza, Brayan Angel |
| US-015 | Modo conductor (secuencia, ETA, alertas) | 8 | Huaman Baldeon, Katheryn Elena |
| ENB-005 | WCAG 2.1 AA | 5 | Huaman Baldeon, Katheryn Elena |
| ENB-008 | Payload ≤ 150 KB en 2G/3G | 5 | Estrada Flores, Axel Sebastian |
| | **Total** | **26** | |

Fuera: re-optimización, PDF, confirmar entrega. US-009 (Could) pasa al Sprint 6, primera en recortarse si RSK-05 se materializa.

### Sprint 6 — 27/11/2026 – 10/12/2026

| ID | Resultado | SP | Responsable |
|---|---|---|---|
| US-011 | Re-optimización dinámica (≤ 30 s en rutas afectadas) | 8 | Cruz Salazar, Jorge Luiz |
| US-016 | Reporte PDF de sostenibilidad | 5 | Estrada Flores, Axel Sebastian |
| US-018 | Confirmar entrega ENTREGADO / FALLIDO | 3 | Huaman Baldeon, Katheryn Elena |
| US-017 | Compensación de carbono (Could) | 5 | Cruz Salazar, Jorge Luiz |
| US-009 | Preferencias de horario del cliente (Could, recortable) | 5 | Huaman Baldeon, Katheryn Elena |
| | **Total** | **26** | |

Si hay que recortar: primero US-009, después US-017, después US-016 (Could del Acta).

### Cierre — 11/12/2026 – 13/12/2026 · Hito 4

Sin historias nuevas. UAT, documentación, presentación y release `v1.0.3-MVP`.

---

## Historial de control de cambios

| Versión | Fecha | Autor | Descripción |
|---|---|---|---|
| 1.0.0 | 16/10/2026 | Equipo EcoLogística Lima | Calendario explícito de los 6 sprints. |
| 1.0.1 | 16/10/2026 | Equipo EcoLogística Lima | Rebaseline: Sprint 3 = 16/10/2026 – 29/10/2026. S4–S6 y cierre se recorren 16 días. Hito 3 = 12/11/2026. Hito 4 = 13/12/2026. |
| 1.0.2 | 17/10/2026 | Equipo EcoLogística Lima | Compromiso de 26 SP por sprint (S3–S6 partidos: ENB-001 8+5, US-010 5+8, US-014 5+3; US-009 al Sprint 6). |

---

[← Volver al README Principal](../../README.md)
