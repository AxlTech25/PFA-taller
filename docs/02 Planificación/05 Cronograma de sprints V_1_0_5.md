[← Volver al README Principal](../../README.md)

# UNIVERSIDAD CONTINENTAL
## Taller de Proyectos 2 — Escuela Profesional de Ingeniería de Sistemas e Informática

# 05. Cronograma de sprints

**Nombre del Proyecto:** EcoLogística Lima – Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Fecha:** 28/10/2026  
**Versión:** 1.0.5  
**Project Manager:** Carhuapoma Fano, Eilene Elizabeth

Cada sprint dura **2 semanas calendario**. El Sprint 3 arranca el **16/10/2026**; a partir de ahí el calendario se recorre 16 días. El Hito 4 queda el **13/12/2026**. Fuente de alcance: [01 Transformando a ágil V_1_0_9.md](./01%20Transformando%20a%20%C3%A1gil%20V_1_0_9.md).

---

## 1. Calendario vigente

| Sprint | Nombre en Jira | Inicio | Fin | Hito del Acta | Enfoque |
|---|---|---|---|---|---|
| 1 | `ECO Sprint 1` | 02/09/2026 | 15/09/2026 | Hito 1 (02/09/2026) — inicio formal | Login, flota, esquema PostGIS, OpenAPI, CI |
| 2 | `ECO Sprint 2` | 16/09/2026 | 29/09/2026 | Hito 2 (29/09/2026) — identidad, flota, conductores y pedidos base | Usuarios, bloqueo, conductores, alta de pedido |
| 3 | `ECO Sprint 3` | **16/10/2026** | **29/10/2026** | — | US-008 B, jornada 8 h, worker, heurística del vecino más cercano |
| 4 | `ECO Sprint 4` | 30/10/2026 | 12/11/2026 | Hito 3 (12/11/2026) — motor, mapa y dashboard integrados | AG DEAP, mapa Leaflet iniciado, dashboard iniciado |
| 5 | `ECO Sprint 5` | 13/11/2026 | 26/11/2026 | — | Cierre de mapa/zonas, árboles RN-018, modo conductor, WCAG |
| 6 | `ECO Sprint 6` | 27/11/2026 | 10/12/2026 | — | Re-optimización, PDF, confirmar entrega, US-009 |
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

## 3. Actividades por sprint

Una fila por actividad. El detalle de SP y responsables está en la sección 4. S3 y S4 reflejan lo **entregado** en los PR #15 y #16.

| Sprint | Fechas | Actividad | ID | SP |
|---|---|---|---|---|
| **1** | 02/09/2026 – 15/09/2026 | Desplegar el esquema PostgreSQL + PostGIS | ENB-003 | 8 |
| | | Configurar el pipeline CI/CD y el Quality Gate | ENB-002 | 5 |
| | | Implementar autenticación JWT (login) | US-001 | 5 |
| | | Registrar vehículos de la flota | US-004 | 5 |
| | | Publicar OpenAPI / Swagger vivo | ENB-007 | 3 |
| **2** | 16/09/2026 – 29/09/2026 | Gestionar usuarios y roles (RBAC) | US-002 | 5 |
| | | Bloquear la cuenta a 3 intentos y exigir consentimiento | US-003 | 3 |
| | | Consultar / actualizar flota y armar el menú de navegación | US-005 | 3 |
| | | Registrar conductores | US-006 | 5 |
| | | Dar de alta pedidos con cliente de demostración | US-008 A | 5 |
| | | Hardening OWASP y bitácora `log_auditoria` | ENB-004 | 5 |
| **3** | 16/10/2026 – 29/10/2026 | Validar cobertura Lima Este (migración 004, `distrito_cobertura`) | US-008 B | 3 |
| | | Validar jornada de 8 h y descansos (Ley N.º 30224) | US-007 | 5 |
| | | Worker asíncrono con Redis (`POST /optimizaciones` → 202) | ENB-006 | 5 |
| | | Heurística del vecino más cercano (inicio del motor) | ENB-001 A | 8 |
| | | Generar rutas asíncronas en BORRADOR | US-010 A | 5 |
| | | CodeQL en CI (parte D2 de IMP-04; sin SP) | IMP-04 | — |
| **4** | 30/10/2026 – 12/11/2026 | Algoritmo genético DEAP para VRPTW + Green VRP | ENB-001 B | 5 |
| | | Escenario 150 pedidos / 15 vehículos factible bajo 45 s | US-010 B | 8 |
| | | Inicio del mapa Leaflet/OSM (trazado, paradas, ETA, semáforo) | US-012 A | 8 |
| | | Inicio del dashboard (km, CO₂, combustible, soles, % ventanas) | US-014 A | 5 |
| **5** | 13/11/2026 – 26/11/2026 | Cerrar mapa: zonas de riesgo y ruta alternativa | US-013 | 5 |
| | | Factor de árboles `factor_captura_arbol_kg` (RN-018) | US-014 B | 3 |
| | | Implementar modo conductor (secuencia, ETA, alertas) | US-015 | 8 |
| | | Cumplir WCAG 2.2 AA (contraste, labels, teclado) | ENB-005 | 5 |
| | | Ajustar payload de sesión ≤ 150 KB en 2G/3G | ENB-008 | 5 |
| | | Staging Railway/Render (arrastre IMP-04; sin SP) | IMP-04 | — |
| | | Catastro INEI si hay archivo (arrastre IMP-11; sin SP) | IMP-11 | — |
| **6** | 27/11/2026 – 10/12/2026 | Re-optimizar solo las rutas afectadas por un incidente | US-011 | 8 |
| | | Generar reporte PDF de sostenibilidad | US-016 | 5 |
| | | Confirmar entrega ENTREGADO / FALLIDO | US-018 | 3 |
| | | Calcular compensación de carbono (Could) | US-017 | 5 |
| | | Registrar preferencias de horario del cliente (Could, recortable) | US-009 | 5 |
| **Cierre** | 11/12/2026 – 13/12/2026 | UAT, documentación, presentación y release `v1.0.3-MVP` | — | — |

Cada sprint suma **26 SP** (el cierre no suma historias). Recorte MoSCoW en el Sprint 6: US-009 → US-017 → US-016.

**US-009 en el Sprint 6:** el plan original de `main` la dejaba en el Sprint 5. Con el cierre real de S3/S4, el Sprint 5 ya suma 26 SP (US-013 5 + US-014 B 3 + US-015 8 + ENB-005 5 + ENB-008 5). Meter US-009 (5, Could) ahí pasaría a 31 SP. El Sprint 6 tenía 21 SP (US-011, US-016, US-018, US-017); con US-009 cierra en 26 y queda primera en recortarse si RSK-05 se materializa.

---

## 4. Compromiso por sprint (26 SP)

Velocidad: **26 SP / sprint**. Total **156 SP**. Los ítems de 13 SP se parten 8+5; los de 8 que cruzan sprint se parten 5+3. Detalle BDD: [01 Transformando a ágil V_1_0_9.md](./01%20Transformando%20a%20%C3%A1gil%20V_1_0_9.md) §§9–14.

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

### Sprint 3 — cerrado (PR #15, código 17/10/2026)

| ID | Resultado | SP | Responsable |
|---|---|---|---|
| US-008 B | Cobertura Lima Este; migración `004_sprint3_cobertura.py` | 3 | Huaman Baldeon, Katheryn Elena |
| US-007 | Jornada de 8 h y descansos (Ley N.º 30224) | 5 | Cruz Salazar, Jorge Luiz |
| ENB-006 | Worker Redis; `POST /optimizaciones` responde 202 | 5 | Cruz Salazar, Jorge Luiz |
| ENB-001 A | Heurística del vecino más cercano; timeout sin colgar la API | 8 | Cruz Salazar, Jorge Luiz |
| US-010 A | Plan factible en BORRADOR vía job asíncrono | 5 | Cruz Salazar, Jorge Luiz |
| | **Total** | **26** | |

Entregado en paralelo, **sin SP:** CodeQL (`.github/workflows/codeql.yml`). **No entra:** GA/DEAP, mapa, dashboard, Staging (IMP-04), catastro INEI (IMP-11).

### Sprint 4 — cerrado en código (PR #16, 18/10/2026; ventana 30/10–12/11, Hito 3 el 12/11)

| ID | Resultado | SP | Responsable |
|---|---|---|---|
| ENB-001 B | AG DEAP (VRPTW + Green VRP); corte a 45 s | 5 | Cruz Salazar, Jorge Luiz |
| US-010 B | Bench 150 pedidos / 15 vehículos factible | 8 | Cruz Salazar, Jorge Luiz |
| US-012 A | Inicio mapa Leaflet: trazado, paradas, ETA, semáforo | 8 | Huaman Baldeon, Katheryn Elena |
| US-014 A | Inicio dashboard: km, CO₂, combustible, soles, % ventanas | 5 | Huaman Baldeon, Katheryn Elena |
| | **Total** | **26** | |

**Pendiente al Sprint 5:** cierre de US-012 vía US-013 (zonas y ruta alternativa), US-014 B (factor árboles RN-018), Staging de IMP-04 (Railway/Render) e IMP-11 (sin catastro INEI). El Hito 3 no se mueve: 12/11/2026.

### Sprint 5 — 13/11/2026 – 26/11/2026

| ID | Resultado | SP | Responsable |
|---|---|---|---|
| US-013 | Overlay `zona_restriccion` y ruta alternativa (cierre del mapa) | 5 | Leon Taza, Brayan Angel |
| US-014 B | Factor de árboles `factor_captura_arbol_kg` (RN-018) | 3 | Huaman Baldeon, Katheryn Elena |
| US-015 | Modo conductor (secuencia, ETA, alertas) | 8 | Huaman Baldeon, Katheryn Elena |
| ENB-005 | WCAG 2.2 AA | 5 | Huaman Baldeon, Katheryn Elena |
| ENB-008 | Payload ≤ 150 KB en 2G/3G | 5 | Estrada Flores, Axel Sebastian |
| | **Total** | **26** | |

Fuera: re-optimización, PDF, confirmar entrega, US-009. IMP-04 Staging e IMP-11 siguen en paralelo, **sin SP**.

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
| 1.0.2 | 17/10/2026 | Equipo EcoLogística Lima | Cierre en código del Sprint 3 el 17/10/2026, dentro de la ventana. US-008 B, US-007, ENB-006 e inicio de ENB-001 / US-010. |
| 1.0.3 | 18/10/2026 | Equipo EcoLogística Lima | Cierre en código del Sprint 4 el 18/10/2026, antes de la ventana 30/10–12/11. Genético, mapa iniciado y tablero iniciado. Staging sigue pendiente al 12/11. |
| 1.0.4 | 21/10/2026 | Equipo EcoLogística Lima | Tabla de actividades y compromiso de 26 SP alineados a lo entregado en S3 (PR #15) y S4 (PR #16). US-009 al Sprint 6 para no romper el tope de 26 SP del Sprint 5. |
| 1.0.5 | 28/10/2026 | Equipo EcoLogística Lima | ENB-005 pasa a WCAG 2.2 AA. El archivo se renombra de V_1_0_0 a V_1_0_5 para que el nombre coincida con el encabezado. |

---

[← Volver al README Principal](../../README.md)
