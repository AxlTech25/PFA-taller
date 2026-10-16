[← Volver al README Principal](../../README.md)

# UNIVERSIDAD CONTINENTAL
## Taller de Proyectos 2 — Escuela Profesional de Ingeniería de Sistemas e Informática

# 05. Cronograma de sprints

**Nombre del Proyecto:** EcoLogística Lima – Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Fecha:** 16/10/2026  
**Versión:** 1.0.0  
**Project Manager:** Carhuapoma Fano, Eilene Elizabeth

Cada sprint dura **2 semanas calendario**. El horizonte del MVP es **02/09/2026 – 27/11/2026** (6 sprints + 3 días de cierre), alineado al Acta de Constitución. La fuente de alcance por sprint es [01 Transformando a ágil V_1_0_6.md](./01%20Transformando%20a%20%C3%A1gil%20V_1_0_6.md).

---

## 1. Calendario oficial

| Sprint | Nombre en Jira | Inicio | Fin | Hito del Acta | Enfoque |
|---|---|---|---|---|---|
| 1 | `ECO Sprint 1` | 02/09/2026 | 15/09/2026 | Hito 1 (02/09/2026) — inicio formal | Login, flota, esquema PostGIS, OpenAPI, CI |
| 2 | `ECO Sprint 2` | 16/09/2026 | 29/09/2026 | Hito 2 (29/09/2026) — identidad, flota, conductores y pedidos base | Usuarios, bloqueo, conductores, alta de pedido |
| 3 | `ECO Sprint 3` | 30/09/2026 | 13/10/2026 | — | US-008 B, jornada 8 h, worker, inicio del motor |
| 4 | `ECO Sprint 4` | 14/10/2026 | 27/10/2026 | Hito 3 (27/10/2026) — motor, mapa y dashboard integrados | Motor VRPTW, mapa Leaflet |
| 5 | `ECO Sprint 5` | 28/10/2026 | 10/11/2026 | — | Zonas, dashboard, modo conductor, WCAG |
| 6 | `ECO Sprint 6` | 11/11/2026 | 24/11/2026 | — | Re-optimización, PDF, confirmar entrega |
| Cierre | — | 25/11/2026 | 27/11/2026 | Hito 4 (27/11/2026) — entrega final | UAT, documentación y presentación |

**Release Jira:** `v1.0.3-MVP` · fecha objetivo **27/11/2026**.

```
02/09          16/09          30/09          14/10          28/10          11/11          25/11
 |---- S1 ----| |---- S2 ----| |---- S3 ----| |---- S4 ----| |---- S5 ----| |---- S6 ----| |Cierre|
 Hito 1         Hito 2                        Hito 3                                      Hito 4
```

---

## 2. Seguimiento real (lo ya ocurrido)

| Sprint | Plan | Cierre en código | Desfase | Evidencia |
|---|---|---|---|---|
| 1 | 02/09/2026 – 15/09/2026 | 30/09/2026 | +15 días | [PR #9](https://github.com/AxlTech25/PFA-taller/pull/9) · [Sprint 1](../03%20Implementaci%C3%B3n/Sprint%201/) |
| 2 | 16/09/2026 – 29/09/2026 | 01/10/2026 | +2 días | [PR #10](https://github.com/AxlTech25/PFA-taller/pull/10) · [Sprint 2](../03%20Implementaci%C3%B3n/Sprint%202/) |
| 3 | 30/09/2026 – 13/10/2026 | — | Arranque del equipo: **16/10/2026** | En curso |
| 4 | 14/10/2026 – 27/10/2026 | — | — | Planificado |
| 5 | 28/10/2026 – 10/11/2026 | — | — | Planificado |
| 6 | 11/11/2026 – 24/11/2026 | — | — | Planificado |
| Cierre | 25/11/2026 – 27/11/2026 | — | — | Planificado |

Las fechas **plan** no se mueven: el Hito 4 sigue siendo el 27/11/2026. El desfase de S1/S2 se absorbe con Daily real desde el Sprint 3 y, si hace falta, recorte MoSCoW (RSK-05) antes del Sprint 6.

**Jira `ECO Sprint 3`:** al crearlo hoy, usar **16/10/2026 – 29/10/2026** como ventana del tablero (2 semanas a partir del arranque real). El calendario de la sección 1 permanece como línea base del Acta.

---

## 3. Qué entra en cada sprint (recordatorio)

| Sprint | Compromiso de referencia | Fuera de ese sprint |
|---|---|---|
| 1 | ENB-003, ENB-002, US-001, US-004, ENB-007 (26 SP) | Usuarios, pedidos, motor |
| 2 | US-002, US-003, US-005, US-006, US-008 A, ENB-004 (26 SP) | US-008 B, US-007, mapa |
| 3 | US-008 B (3), US-007 (5), ENB-006 (5), inicio ENB-001 / US-010 | Mapa, dashboard |
| 4 | Continuación ENB-001 / US-010, inicio US-012 | Modo conductor, PDF |
| 5 | US-012, US-013, US-014, US-015, ENB-005, ENB-008, US-009 | Re-optimización |
| 6 | US-011, US-016, US-018, US-017 | Alcance Could recortable |

Detalle de historias: artefacto 01, sección 8. Planning de S1 y S2: secciones 9 y 10.

---

## Historial de control de cambios

| Versión | Fecha | Autor | Descripción |
|---|---|---|---|
| 1.0.0 | 16/10/2026 | Equipo EcoLogística Lima | Calendario explícito de los 6 sprints + cierre, con fechas plan, hitos del Acta y seguimiento real de S1/S2. |

---

[← Volver al README Principal](../../README.md)
