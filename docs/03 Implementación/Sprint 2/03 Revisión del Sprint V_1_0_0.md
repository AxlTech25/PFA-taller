[← Volver al README Principal](../../../README.md)

# Revisión del sprint

**Nombre del Proyecto:** EcoLogística Lima – Optimizador de Rutas Sostenibles para DistriRápido S.A.C.

**Líder del Proyecto:** Carhuapoma Fano, Eilene Elizabeth

**Versión:** 1.1.0 — Sprint 2 (revisión 01/10/2026, merge [PR #10](https://github.com/AxlTech25/PFA-taller/pull/10); informe 02/10/2026)

---

## Historias de Usuario completadas en este Sprint

Sprint Goal: *un Administrador gestiona usuarios y roles, y un Operador ya autenticado registra conductores y pedidos sobre la flota del Sprint 1, con bloqueo de cuenta y menú de navegación.*

| ID | Historia / Enabler | SP | ¿Done? | Comentario de la Review |
|---|---|---|---|---|
| US-002 | Usuarios y roles RBAC | 5 | Sí | Admin crea Conductor; Operador no crea Admin (403). Contraseña no viaja en el JSON de respuesta. |
| US-003 | Bloqueo 3 intentos + consentimiento | 3 | Sí | 423 + Retry-After. Pedido sin consentimiento 422 y evento `pedido_sin_consentimiento`. Corregido el reloj (IMP-07) el mismo día del merge. |
| US-005 | Lista / editar flota + menú | 3 | Sí | PUT estado/factor. Shell con módulos según rol. Conductor no ve Usuarios. |
| US-006 | Alta de conductor | 5 | Sí | Punto de partida lat/lon; DNI único. No se listó/edición completa (no estaba en el compromiso). |
| US-008 A | Alta de pedido con cliente demo | 5 | Sí | Estado PENDIENTE. Incremento B (cobertura y “frente a la bodega”) **fuera** de esta Review. |
| ENB-004 | 403, sanitización, auditoría | 5 | Sí (S2) | Headers `X-Content-Type-Options` en health. TLS de Staging cloud no aplica. |

**Resultado:** 26 SP aceptados. No se aceptó US-008 B ni US-007.

---

## Demostración del trabajo completado

Demostración a los stakeholders de las funcionalidades implementadas.

**Audiencia:** docente (I-04) y el equipo. **Ambiente:** `docker compose up --build`.

| Paso | Qué se vio | Historia |
|---|---|---|
| 1 | Login Admin → **Usuarios** → alta de un Conductor | US-002 |
| 2 | Login Operador → menú Flota, Conductores, Pedidos (sin Usuarios) | US-005 |
| 3 | Flota: `DMO-101` a Mantenimiento o cambio de CO₂ | US-005 |
| 4 | Conductores: alta con DNI y punto de partida | US-006 |
| 5 | Pedidos: Bodega El Ahorro → Pendiente; Los Pinos → rechazo Ley 29733 | US-008 A + US-003 |
| 6 | Tres passwords malos → bloqueo 15 min | US-003 |
| 7 | Login Conductor: no entra a Usuarios; no edita flota | US-002 / ENB-004 |
| 8 | `/docs` lista `/usuarios`, `/conductores`, `/pedidos`, `/clientes` | ENB-007 vigente |

**Feedback:** el Goal se entiende en pantallas. Se pidió no vender el seed de clientes como “módulo de clientes”. Se dejó explícito que el mapa y el ruteo no existen aún.

---

## Pendientes

| Pendiente | Dueño | Sprint destino |
|---|---|---|
| US-008 B (3 SP): distritos de cobertura y georreferencia aproximada | Katheryn / Brayan | 3 |
| US-007 jornada 8 h | Jorge | 3 |
| ENB-006, ENB-001, US-010 (motor; partir 13+13 SP) | Jorge | 3–4 |
| IMP-04 Staging + CodeQL | Axel / Jorge | 3 (Hito 3: 27/10) |
| Actualizar Jira a Done el día del merge (acción A5, retro S1) | Eilene | Inmediato |

Guion detallado y métricas: [01 Informe de estado del proyecto V_1_0_0.md](./01%20Informe%20de%20estado%20del%20proyecto%20V_1_0_0.md). Impedimentos: [02 Registro de Impedimentos V_1_0_0.md](./02%20Registro%20de%20Impedimentos%20V_1_0_0.md).

---

## Historial de control de cambios

| Versión | Fecha | Autor | Descripción |
|---|---|---|---|
| 1.0.0 | 02/10/2026 | Equipo EcoLogística Lima | Review del Sprint 1. |
| 1.1.0 | 02/10/2026 | Equipo EcoLogística Lima | Review del Sprint 2 alineada al PR #10 y al Goal de 26 SP. |

---

[← Volver al README Principal](../../../README.md)
