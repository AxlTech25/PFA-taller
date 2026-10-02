[← Volver al README Principal](../../README.md)

# Registro de impedimentos

**Nombre del Proyecto:** EcoLogística Lima – Optimizador de Rutas Sostenibles para DistriRápido S.A.C.

**Líder del Proyecto:** Carhuapoma Fano, Eilene Elizabeth

**Versión:** 1.1.0 — Sprint 2 (16/09/2026 – 29/09/2026; implementación 01/10/2026)

Se heredan los impedimentos abiertos del Sprint 1 (`V_1_0_0`). Los nuevos del Sprint 2 empiezan en IMP-07.

| Impedimento # | Fecha de Registro | Descripción del Impedimento así como el Impacto en el Proyecto | Prioridad | Reportado por | Fecha tope de Resolución | Estado | Fecha de Resolución | Resolución/Comentarios |
|---|---|---|---|---|---|---|---|---|
| IMP-04 | 30/09/2026 | *(Arrastre Sprint 1)* No hay Staging en la nube ni CodeQL/Sonar en CI. Impacto: el DoD D2/D4 sigue incompleto al mostrar el Sprint 2. | Media | Cruz Salazar, Jorge Luiz | 27/10/2026 | En curso | — | Compose sigue siendo el ambiente de demo. A3/A4 de la retrospectiva S1 no se ejecutaron en este sprint (el equipo priorizó US de negocio). |
| IMP-07 | 01/10/2026 | El bloqueo a 3 intentos **no se aplicaba** en algunos entornos: `bloqueado_hasta` se comparaba con un `datetime` de Python mal alineado con la zona de PostgreSQL. Impacto: US-003 fallaba en la demo (el tercer login no devolvía 423). | Alta | Estrada Flores, Axel Sebastian | 01/10/2026 | Resuelto | 01/10/2026 | Commit `74dac8b`: el vencimiento lo decide `clock_timestamp()` en PostgreSQL (`backend/app/services/auth.py`). Test `test_tercer_fallo_bloquea_la_cuenta_quince_minutos`. |
| IMP-08 | 29/09/2026 | El Sprint 1 se fusionó el 30/09; el 2 quedó comprimido (plan 16–29/09, código 01/10). Impacto: no hubo Daily ni burndown del Sprint 2; el Hito 2 del Acta (29/09) se incumplió por 2 días. | Alta | Carhuapoma Fano, Eilene Elizabeth | 01/10/2026 | Aceptado | 01/10/2026 | Se aceptó entregar el software al día siguiente y no recortar US-002/US-006. El increment B de US-008 sí se dejó para el Sprint 3 para no inflar el 2. |
| IMP-09 | 29/09/2026 | US-008 exige un cliente con consentimiento y **no hay historia de CRUD de clientes**. Impacto: el pedido no se podía demostrar sin inventar un módulo fuera de alcance. | Media | Leon Taza, Brayan Angel | 01/10/2026 | Resuelto | 01/10/2026 | Migración `003_clientes_demo.py`: Bodega El Ahorro (con consentimiento) y Bodega Los Pinos (sin). `GET /clientes` solo lista el seed; no hay altas de cliente en UI. |
| IMP-10 | 01/10/2026 | Payload con `<script>` o SQL en nombre/dirección debe rechazarse (ENB-004) sin romper el alta válida. Impacto: riesgo de falso positivo que bloqueara la demo de pedidos. | Baja | Huaman Baldeon, Katheryn Elena | 01/10/2026 | Resuelto | 01/10/2026 | Sanitización en servicios de pedidos y conductores; tests `test_inyeccion_en_pedido_no_persiste` y DNI/nombre inválido en conductores. |

**Resumen Sprint 2:** 1 arrastre en curso (IMP-04) · 3 resueltos · 1 aceptado (calendario). US-003 quedó demostrable solo después de IMP-07.

Informe del sprint: [01 Informe de estado del proyecto V_1_1_0.md](./01%20Informe%20de%20estado%20del%20proyecto%20V_1_1_0.md). Revisión: [03 Revisión del Sprint V_1_1_0.md](./03%20Revisi%C3%B3n%20del%20Sprint%20V_1_1_0.md).

---

## Historial de control de cambios

| Versión | Fecha | Autor | Descripción |
|---|---|---|---|
| 1.0.0 | 02/10/2026 | Equipo EcoLogística Lima | Impedimentos del Sprint 1 (IMP-01 a IMP-06). |
| 1.1.0 | 02/10/2026 | Equipo EcoLogística Lima | Sprint 2: IMP-07 a IMP-10 y arrastre de IMP-04. |

---

[← Volver al README Principal](../../README.md)
