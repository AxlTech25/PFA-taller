[← Volver al README Principal](../../README.md)

# UNIVERSIDAD CONTINENTAL
## Taller de Proyectos 2 — Escuela Profesional de Ingeniería de Sistemas e Informática

# 05. Cronograma de sprints

**Nombre del Proyecto:** EcoLogística Lima – Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Fecha:** 18/10/2026  
**Versión:** 1.0.3  
**Project Manager:** Carhuapoma Fano, Eilene Elizabeth

Cada sprint dura **2 semanas calendario**. El Sprint 3 arranca el **16/10/2026**; a partir de ahí el calendario se recorre 16 días. El Hito 4 queda el **13/12/2026**. Fuente de alcance: [01 Transformando a ágil V_1_0_6.md](./01%20Transformando%20a%20%C3%A1gil%20V_1_0_6.md).

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
| 3 | 16/10/2026 – 29/10/2026 | 17/10/2026 | Dentro de ventana (día 2 de 14) | [PR #15](https://github.com/AxlTech25/PFA-taller/pull/15) · [Sprint 3](../03%20Implementaci%C3%B3n/Sprint%203/) |
| 4 | 30/10/2026 – 12/11/2026 | 18/10/2026 | Adelantado: el código entra antes de abrir la ventana. El Hito 3 sigue el 12/11/2026 | [PR #16](https://github.com/AxlTech25/PFA-taller/pull/16) · [Sprint 4](../03%20Implementaci%C3%B3n/Sprint%204/) |
| 5 | 13/11/2026 – 26/11/2026 | — | — | Planificado |
| 6 | 27/11/2026 – 10/12/2026 | — | — | Planificado |
| Cierre | 11/12/2026 – 13/12/2026 | — | — | Planificado |

---

## 3. Qué entra en cada sprint (recordatorio)

| Sprint | Compromiso de referencia | Fuera de ese sprint |
|---|---|---|
| 1 | ENB-003, ENB-002, US-001, US-004, ENB-007 (26 SP) | Usuarios, pedidos, motor |
| 2 | US-002, US-003, US-005, US-006, US-008 A, ENB-004 (26 SP) | US-008 B, US-007, mapa |
| 3 | US-008 B (3), US-007 (5), ENB-006 (5), inicio de ENB-001 / US-010 | Mapa, dashboard |
| 4 | Continuación ENB-001 / US-010, inicio US-012 | Modo conductor, PDF |
| 5 | US-012, US-013, US-014, US-015, ENB-005, ENB-008, US-009 | Re-optimización |
| 6 | US-011, US-016, US-018, US-017 | Alcance Could recortable |

Detalle de historias: artefacto 01, sección 8.

---

## Historial de control de cambios

| Versión | Fecha | Autor | Descripción |
|---|---|---|---|
| 1.0.0 | 16/10/2026 | Equipo EcoLogística Lima | Calendario explícito de los 6 sprints. |
| 1.0.1 | 16/10/2026 | Equipo EcoLogística Lima | Rebaseline: Sprint 3 = 16/10/2026 – 29/10/2026. S4–S6 y cierre se recorren 16 días. Hito 3 = 12/11/2026. Hito 4 = 13/12/2026. |
| 1.0.2 | 17/10/2026 | Equipo EcoLogística Lima | Cierre en código del Sprint 3 el 17/10/2026, dentro de la ventana. US-008 B, US-007, ENB-006 e inicio de ENB-001 / US-010. |
| 1.0.3 | 18/10/2026 | Equipo EcoLogística Lima | Cierre en código del Sprint 4 el 18/10/2026, antes de la ventana 30/10–12/11. Genético, mapa iniciado y tablero iniciado. Staging sigue pendiente al 12/11. |

---

[← Volver al README Principal](../../README.md)
