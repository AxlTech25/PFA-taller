[← Volver al README Principal](../../README.md)

# Informe de estado del proyecto

**Nombre del Proyecto:** EcoLogística Lima – Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Líder del Proyecto:** Carhuapoma Fano, Eilene Elizabeth  
**Sprint:** 2  
**Fechas planificadas:** 16/09/2026 – 29/09/2026  
**Fecha del informe:** 02/10/2026  
**Versión:** 1.1.0

El archivo `V_1_0_0` de esta misma carpeta es el informe del **Sprint 1**. Esta versión `V_1_1_0` cubre el Sprint 2 (semver: mismo artefacto, siguiente iteración), para no pisar el entregable anterior. La consigna reitera el nombre `V_1_0_0`; el control de versiones semántico de la rúbrica obliga a incrementar.

---

## 1. Estado general de la iteración

El Sprint 2 cerró el **compromiso de 26 SP** (US-002, US-003, US-005, US-006, US-008 A, ENB-004). Código en `main` desde el [PR #10](https://github.com/AxlTech25/PFA-taller/pull/10) (01/10/2026), con corrección del bloqueo 423 el mismo día ([74dac8b](https://github.com/AxlTech25/PFA-taller/commit/74dac8b)).

| Indicador | Plan | Real al cierre |
|---|---|---|
| Story Points comprometidos | 26 | 26 en software demostrable |
| Sprint Goal | Admin gestiona usuarios; Operador registra conductores y pedidos sobre la flota del Sprint 1 | Cumplido en Compose (`localhost:5173`) |
| Quality Gate | Pytest cobertura ≥ 80 %, Ruff, build del frontend | Job `CI` verde en el [PR #10](https://github.com/AxlTech25/PFA-taller/pull/10) |
| Staging en la nube | DoD D4 (Railway/Render) | **No desplegado.** Demo en Compose (`localhost:5173` / `localhost:8000`) — IMP-04 |
| US-008 | Incremento A (5 SP) en este sprint; B (3 SP) en el 3 | A hecho. B **no** se hizo (cobertura Lima Este y punto de referencia) |
| Hito 2 del Acta | 29/09/2026 | Software fusionado el 01/10/2026 (2 días de retraso; el Sprint 1 ya venía 15 días tarde) |
| Deuda del Sprint 1 | Staging cloud y CodeQL (IMP-04) | **Sigue abierta** |

El Sprint 1 (login, flota, PostGIS, CI, OpenAPI) permanece vigente. No se tocó el motor VRPTW ni el mapa.

---

## Historias de Usuario completadas en este Sprint

Compromiso de [01 Transformando a ágil V_1_0_5.md](../02%20Planificaci%C3%B3n/01%20Transformando%20a%20%C3%A1gil%20V_1_0_5.md) §10.

| ID | Título | SP | Estado | Evidencia |
|---|---|---|---|---|
| US-002 | Usuarios y roles RBAC | 5 | Completado | `POST /usuarios` solo Admin; Operador 403; Gerente lista. UI `UsuariosPage.tsx`. |
| US-003 | Consentimiento y bloqueo | 3 | Completado | Tercer fallo → `BLOQUEADO` 15 min, HTTP 423. Pedido a Bodega Los Pinos se rechaza. Reloj de bloqueo con `clock_timestamp()` de PostgreSQL (fix 74dac8b). |
| US-005 | Consultar / actualizar flota + menú | 3 | Completado | `GET/PUT /vehiculos`. Menú Flota · Conductores · Pedidos · Usuarios en `Shell.tsx`. |
| US-006 | Registrar conductor | 5 | Completado | DNI único, licencia, horario, lat/lon de partida. DNI duplicado 409. |
| US-008 A | Alta de pedido (cliente demo) | 5 | Completado | Pedido PENDIENTE a Bodega El Ahorro. Sin CRUD de clientes: seed en migración `003_clientes_demo.py`. |
| ENB-004 | Hardening OWASP y logs | 5 | Completado (alcance S2) | 403 por rol, rechazo de `<script>` en formularios, `log_auditoria` en login, usuario, vehículo, conductor y pedido. TLS 1.3 en Staging cloud **no** aplica (sigue Compose local). |

**Total compromiso: 26 SP.** US-008 sigue estimada 8 en el backlog; este sprint consume 5.

---

## Demostración del trabajo completado

Demostración a los stakeholders de las funcionalidades implementadas.

**Stakeholders:** docente del curso (I-04, Registro de interesados) y el equipo EcoLogística Lima. Entorno: Docker Compose, no un Staging público.

**Guion del Sprint 2** (sobre el login y la flota del Sprint 1):

1. Admin crea un usuario Conductor en **Usuarios**.
2. Operador edita `DMO-101` (estado o factor de CO₂) en **Flota**.
3. Operador da de alta un **conductor** (DNI, licencia, horario, partida).
4. Operador registra un **pedido** a Bodega El Ahorro → Pendiente. Bodega Los Pinos → rechazo por consentimiento.
5. Tres claves incorrectas → cuenta bloqueada (423, 15 minutos).
6. El Conductor no entra a Usuarios ni edita flota (403 / mensaje de permiso).

Detalle del recorrido: README, sección “Recorrido de punta a punta”.

---

## Pendientes

| Ítem | Tipo | Destino |
|---|---|---|
| US-008 B: cobertura SJL/El Agustino/Santa Anita/Ate y punto de referencia | Alcance partido | Sprint 3 (3 SP) |
| US-007 Jornada 8 h y descansos | Planificado | Sprint 3 |
| ENB-006 Worker Redis + ENB-001 / US-010 motor | Planificado | Sprints 3–4 |
| Staging cloud y CodeQL (IMP-04, acción A3/A4 de la retro S1) | DoD | Aún no cerrado |
| CRUD de clientes | Fuera de backlog | No se abrirá; se mantiene seed |

---

## Organización del código

La consigna ilustra `src/frontend` y `src/backend`. El equipo mantiene carpetas hermanas en la raíz, equivalentes y alineadas a Docker Compose:

| Carpeta | Contenido del Sprint 2 |
|---|---|
| `frontend/src/pages/` | `UsuariosPage`, `ConductoresPage`, `PedidosPage`, `FlotaPage`, `Shell` (menú por rol) |
| `frontend/src/permissions.ts` | Qué ve cada rol |
| `backend/app/api/routes/` | `usuarios`, `conductores`, `pedidos`, `clientes` (solo lectura del seed) |
| `backend/alembic/versions/003_clientes_demo.py` | Bodega El Ahorro / Bodega Los Pinos |
| `.github/workflows/ci.yml` | Ruff + Pytest ≥ 80 % + build Vite |

`.gitignore` en la raíz excluye `.env`, `node_modules/`, `.venv/`, `vendor/`, coberturas y cachés. Secretos de demo: `.env.example`.

Documentos de esta iteración: [Informe](./01%20Informe%20de%20estado%20del%20proyecto%20V_1_1_0.md) · [Impedimentos](./02%20Registro%20de%20Impedimentos%20V_1_1_0.md) · [Revisión](./03%20Revisi%C3%B3n%20del%20Sprint%20V_1_1_0.md) · [Retrospectiva](./04%20Retrospectiva%20del%20Sprint%20V_1_1_0.md).

---

## Historial de control de cambios

| Versión | Fecha | Autor | Descripción |
|---|---|---|---|
| 1.0.0 | 02/10/2026 | Equipo EcoLogística Lima | Informe del Sprint 1. |
| 1.1.0 | 02/10/2026 | Equipo EcoLogística Lima | Informe del Sprint 2: 26 SP, PR #10, incremento A de US-008, deuda IMP-04 vigente. |

---

[← Volver al README Principal](../../README.md)
