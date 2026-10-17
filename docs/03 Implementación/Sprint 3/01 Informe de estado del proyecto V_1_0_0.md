[← Volver al README Principal](../../../README.md)

# Informe de estado del proyecto

**Nombre del Proyecto:** EcoLogística Lima – Optimizador de Rutas Sostenibles para DistriRápido S.A.C.

**Líder del Proyecto:** Carhuapoma Fano, Eilene Elizabeth

**Fecha:** 17/10/2026

**Periodo del Informe:** 16/10/2026 – 29/10/2026 (Sprint 3; software el 17/10/2026, dentro de la ventana)

**Versión:** 1.2.0

Este archivo usa el nombre `V_1_0_0.md` que pide la consigna. Vive en `docs/03 Implementación/Sprint 3/`. El encabezado registra **1.2.0**. El Sprint 2 está en [`../Sprint 2/`](../Sprint%202/).

---

### **Estado del proyecto**

| Variables de control | Descripción del estado |
| --- | --- |
| **Alcance** | Compromiso cerrado del Sprint 3: **US-008 B (3 SP), US-007 (5 SP) y ENB-006 (5 SP)**. Inicio demostrable de ENB-001 / US-010: heurística del vecino más cercano, rutas en `BORRADOR` y confirmación. No se cierra el GA ni el bench de 150×15. El mapa y el dashboard siguen fuera. IMP-04: CodeQL entra en CI; la URL de Staging sigue pendiente. |
| **Cronograma** | **Dentro de ventana.** El Sprint 3 va del 16/10/2026 al 29/10/2026. El código se entrega el 17/10/2026 (día 2). Avance de sprints con software en `main` pendiente de merge: 2 cerrados y el 3 en revisión. Hito 3 el 12/11/2026; Hito 4 el 13/12/2026. |
| **Costos** | Línea base **S/ 13,000**. Cloud sigue en **S/ 0**: no hay Staging (IMP-04, parte de hosting). Contingencia S/ 1,500 intacta. No se compra infraestructura nueva en este sprint. |
| **Calidad** | CI de producto: Ruff, Pytest con cobertura ≥ 80 % y build de Vite. Se añade el workflow CodeQL (`.github/workflows/codeql.yml`) para el Quality Gate D2. Pruebas del Gherkin de cobertura, georreferencia aproximada, jornada de 8 h, descanso de 1 h, cola 202 y Redis caído (503 sin job huérfano). |

Detalle (fuente: [01 Transformando a ágil V_1_0_6.md](../../02%20Planificaci%C3%B3n/01%20Transformando%20a%20%C3%A1gil%20V_1_0_6.md) §8 y §11):

| ID | Título | SP | Estado |
|---|---|---|---|
| US-008 B | Cobertura Lima Este y punto de referencia | 3 | Completado |
| US-007 | Jornada de 8 h y descansos (Ley N.º 30224) | 5 | Completado |
| ENB-006 | Worker y cola Redis, fuera del request | 5 | Completado |
| ENB-001 | Motor metaheurístico con SLA | 13 (partido) | Inicio: heurística constructiva. Falta GA/Tabú y el bench 150×15 |
| US-010 | Generar rutas VRPTW + Green VRP | 13 (partido) | Inicio: plan factible en borrador, pico y placa y factor de congestión. Falta la metaheurística y el mapa |
| IMP-04 | CodeQL y Staging | — | CodeQL en el workflow. Staging en la nube **sigue pendiente** |

---

### **Riesgos**

| **Riesgo** | **Responsable** | **Mitigación** |
| --- | --- | --- |
| RSK-03 — La heurística no es el GA y no demuestra P95 ≤ 45 s con 150 pedidos y 15 vehículos. | Cruz Salazar, Jorge Luiz | El worker ya corta al presupuesto de `tiempo_max_optimizacion_s` (45). El Sprint 4 sustituye el vecino más cercano por la metaheurística sin cambiar el contrato 202/`job_id`. |
| RSK-05 — El Hito 3 (12/11) aún pide motor integrado y mapa. | Carhuapoma Fano, Eilene Elizabeth | El Sprint 4 arranca el 30/10 con la continuación de ENB-001 / US-010 y el inicio de US-012. No se adelantó Leaflet en este sprint. |
| RSK-08 / IMP-04 — Sin URL de Staging no se cierra el DoD D4. | Estrada Flores, Axel Sebastian | CodeQL queda en el repositorio. El deploy a Railway/Render espera credenciales; no se inventan secretos en el PR. |
| RSK-07 — La cobertura usa envolventes operativas, no el catastro INEI. | Leon Taza, Brayan Angel | Cuatro polígonos en `distrito_cobertura` (migración 004) rechazan puntos fuera de SJL, El Agustino, Santa Anita y Ate. El reemplazo por el límite oficial puede entrar sin cambiar el contrato del pedido. |

---

### **Próximos avances**

Sprint 4 (30/10/2026 – 12/11/2026), Hito 3:

1. Continuar ENB-001 / US-010: metaheurística y evidencia de factibilidad, sin reescribir la cola.
2. Inicio de US-012 (mapa Leaflet/OSM).
3. Cerrar la parte de Staging de IMP-04 si hay credenciales de Railway o Render.
4. Mover en Jira a Done, el día del merge, US-008 B, US-007 y ENB-006 (acción A5).

No se abre CRUD de clientes. El dashboard de CO₂ no entra todavía.

---

### **Notas**

- Demo: Operador registra un pedido con punto de referencia «frente a la bodega El Ahorro» (georreferencia aproximada, distrito San Juan de Lurigancho). Una coordenada de Miraflores se rechaza. En **Rutas** se encola el plan; el worker, en otro proceso, deja la ruta en Borrador. Confirmar asigna los pedidos. Una jornada de más de 8 h responde el incumplimiento de la Ley N.º 30224.
- Las geometrías de `004_sprint3_cobertura.py` son envolventes de demostración, no el límite distrital oficial.
- El calendario de pico y placa es la regla de último dígito en días hábiles que pide RN-006 (lunes 1–2, martes 3–4, miércoles 5–6, jueves 7–8, viernes 9–0). Sábado y domingo no restringen.
- `GET /clientes` queda descrito en OpenAPI como catálogo de demostración, sin altas (acción A8).
- Ambiente: `docker compose up --build` levanta Postgres (host **5433**), Redis, la API, el worker y la SPA. No hay Staging público.
- Artefactos: [Impedimentos](./02%20Registro%20de%20Impedimentos%20V_1_0_0.md) · [Revisión](./03%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md) · [Retrospectiva](./04%20Retrospectiva%20del%20Sprint%20V_1_0_0.md).

---

## Historial de control de cambios

| Versión | Fecha | Autor | Descripción |
|---|---|---|---|
| 1.0.0 | 02/10/2026 | Equipo EcoLogística Lima | Informe del Sprint 1. |
| 1.1.0 | 02/10/2026 | Equipo EcoLogística Lima | Informe del Sprint 2. |
| 1.2.0 | 17/10/2026 | Equipo EcoLogística Lima | Informe del Sprint 3: cobertura, jornada, worker y heurística. Staging sigue pendiente. |

---

[← Volver al README Principal](../../../README.md)
