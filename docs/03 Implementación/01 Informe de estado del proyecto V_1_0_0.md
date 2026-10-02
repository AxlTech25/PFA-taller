[← Volver al README Principal](../../README.md)

# Informe de estado del proyecto

**Nombre del Proyecto:** EcoLogística Lima – Optimizador de Rutas Sostenibles para DistriRápido S.A.C.

**Líder del Proyecto:** Carhuapoma Fano, Eilene Elizabeth

**Fecha:** 02/10/2026

**Periodo del Informe:** 16/09/2026 – 29/09/2026 (Sprint 2; software fusionado el 01/10/2026)

**Versión:** 1.1.0

Este archivo usa el **nombre exacto** que pide la consigna (`V_1_0_0`). El encabezado registra **1.1.0** porque es el informe del Sprint 2. El Sprint 1 quedó en [`Sprint 1/`](./Sprint%201/).

---

### **Estado del proyecto**

| Variables de control | Descripción del estado |
| --- | --- |
| **Alcance** | Compromiso del Sprint 2: **26 / 26 SP** demostrables (US-002, US-003, US-005, US-006, US-008 A, ENB-004). Código en `main` desde el [PR #10](https://github.com/AxlTech25/PFA-taller/pull/10). US-008 B (cobertura Lima Este, 3 SP) **no** entra: queda para el Sprint 3. Del MVP Must (RF-001 a RF-007 del Acta) siguen fuera jornada 8 h, motor VRPTW, mapa y dashboard. El Sprint 1 (login, flota, PostGIS, CI, OpenAPI) permanece vigente. |
| **Cronograma** | **Atrasados.** El Hito 2 del Acta cerraba el 29/09/2026; el merge ocurrió el 01/10/2026 (**2 días**). El Sprint 1 ya venía 15 días tarde (IMP-03), así que el 2 no tuvo Daily de calendario: todo el incremento se implementó el 01/10 (IMP-08). Avance de sprints: **2 de 6** (33 %). Sprints restantes hasta el Hito 4 (27/11/2026): 4. |
| **Costos** | Línea base **S/ 13,000**. Plan de caja Mes 1 (Sprints 1–2): S/ 4,500 (RR. HH. S/ 3,334 + hardware/software S/ 1,000 + cloud S/ 166). Ejecutado al 02/10: RR. HH. prorrateado S/ 3,334; hardware de laboratorio en uso ≈ S/ 730 (el dominio de S/ 70 no se compró); **cloud S/ 0** porque no hay Staging (IMP-04). Contingencia S/ 1,500 **intacta**. No se sobrepasa el techo; el gasto cloud queda diferido al Sprint 3. |
| **Calidad** | 1 defecto crítico de demo (IMP-07: el bloqueo 423 no se aplicaba por desfase de reloj Python/PostgreSQL) **cerrado el mismo 01/10** (`74dac8b`). CI verde: Ruff, Pytest cobertura ≥ 80 %, build Vite. Actividades: pruebas Gherkin de 403 por rol, DNI duplicado, pedido sin consentimiento y rechazo de `<script>`. Deuda: DoD D2/D4 (CodeQL/Sonar y Staging cloud) sigue abierta. |

Detalle del compromiso (fuente: [01 Transformando a ágil V_1_0_5.md](../02%20Planificaci%C3%B3n/01%20Transformando%20a%20%C3%A1gil%20V_1_0_5.md) §10):

| ID | Título | SP | Estado |
|---|---|---|---|
| US-002 | Usuarios y roles RBAC | 5 | Completado |
| US-003 | Consentimiento y bloqueo a 3 intentos | 3 | Completado (tras IMP-07) |
| US-005 | Consultar / actualizar flota + menú | 3 | Completado |
| US-006 | Registrar conductor | 5 | Completado |
| US-008 A | Alta de pedido con cliente demo | 5 | Completado |
| ENB-004 | Hardening OWASP y `log_auditoria` (alcance S2) | 5 | Completado |
| | **Total** | **26** | |

---

### **Riesgos**

| **Riesgo** | **Responsable** | **Mitigación** |
| --- | --- | --- |
| RSK-05 — El desfase de calendario se materializó (Hito 2 +2 días; Sprint 2 comprimido a un día de código). Si el Sprint 3 se implementa igual, el Hito 3 (27/10) no llega con motor + mapa. | Carhuapoma Fano, Eilene Elizabeth | Daily real desde el 02/10. Partir ENB-001/US-010 en subtareas ≤ 8 h. Recorte MoSCoW (RF-006, RF-009, RF-010) si al cierre del Sprint 4 no hay heurística demostrable. |
| RSK-08 — TLS 1.3 y CodeQL no están (IMP-04). El bloqueo y el consentimiento sí se demostraron, pero el DoD de seguridad queda incompleto. | Estrada Flores, Axel Sebastian | Job CodeQL en `ci.yml` y URL de Staging (Railway/Render) antes del 27/10. No promover a Staging con secretos de `.env.example`. |
| RSK-11 — Jira no se actualizó a Done el día del merge (A5). El tablero puede contradecir el software en `main`. | Carhuapoma Fano, Eilene Elizabeth | Mover US-002, US-003, US-005, US-006, US-008 A y ENB-004 a Done con enlace al PR #10 en esta misma semana. |
| RSK-07 — US-008 B exige cobertura SJL/El Agustino/Santa Anita/Ate y punto de referencia; el alta actual usa el seed sin validar distrito. | Huaman Baldeon, Katheryn Elena / Leon Taza, Brayan Angel | Incremento B (3 SP) en el Sprint 3: distrito de cobertura + georreferencia aproximada, sin abrir CRUD de clientes. |
| RSK-03 — El motor VRPTW entra en Sprints 3–4 (13+13 SP). Sigue siendo el riesgo High no ejecutado. | Cruz Salazar, Jorge Luiz | Heurística constructiva demostrable al cierre del Sprint 3; no esperar el GA completo para tener algo que enseñar. |

---

### **Próximos avances**

Sprint 3 (plan 30/09/2026 – 13/10/2026; arranque real 02/10/2026):

1. US-008 B (3 SP): distritos de Lima Este y punto de referencia.
2. US-007 (5 SP): jornada de 8 h y descansos (Ley N.º 30224).
3. Inicio de ENB-006 / ENB-001 / US-010 (worker + motor), partidos en subtareas ≤ 8 h.
4. Cerrar IMP-04: CodeQL en CI y URL de Staging en el README (acciones A3/A4).
5. Anotar en OpenAPI que `GET /clientes` es catálogo de demostración, sin altas (A8).

No se abrirá un módulo de CRUD de clientes. El mapa Leaflet y el dashboard de CO₂ no entran todavía.

---

### **Notas**

- Demo del periodo: Administrador crea un Conductor; Operador edita flota (`DMO-101`), da de alta conductor y pedido a Bodega El Ahorro (Pendiente); Bodega Los Pinos se rechaza; tres claves incorrectas bloquean 15 min (423); el Conductor no entra a Usuarios. Recorrido en el README.
- Ambiente de demostración: `docker compose up --build` (`localhost:5173` / `localhost:8000`). No hay Staging público.
- Clientes de demo: migración `003_clientes_demo.py` (Bodega El Ahorro con consentimiento, Bodega Los Pinos sin). No hay historia de clientes en el backlog.
- Código: `frontend/` y `backend/` en la raíz (equivalente a `src/frontend` / `src/backend`). `.gitignore` excluye `.env`, `node_modules/`, `.venv/` y `vendor/`.
- Artefactos de esta iteración: [Impedimentos](./02%20Registro%20de%20Impedimentos%20V_1_0_0.md) · [Revisión](./03%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md) · [Retrospectiva](./04%20Retrospectiva%20del%20Sprint%20V_1_0_0.md).

---

## Historial de control de cambios

| Versión | Fecha | Autor | Descripción |
|---|---|---|---|
| 1.0.0 | 02/10/2026 | Equipo EcoLogística Lima | Informe del Sprint 1. |
| 1.1.0 | 02/10/2026 | Equipo EcoLogística Lima | Informe del Sprint 2 según plantilla oficial (alcance, cronograma, costos, calidad, riesgos, próximos avances y notas). |

---

[← Volver al README Principal](../../README.md)
