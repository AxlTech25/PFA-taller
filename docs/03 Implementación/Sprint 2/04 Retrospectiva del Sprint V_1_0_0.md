[← Volver al README Principal](../../../README.md)

# Retrospectiva del sprint

**Nombre del Proyecto:** EcoLogística Lima – Optimizador de Rutas Sostenibles para DistriRápido S.A.C.

**Líder del Proyecto:** Carhuapoma Fano, Eilene Elizabeth

**Versión:** 1.1.0 — Sprint 2 (02/10/2026)

Se revisan también las acciones A1–A6 de la retrospectiva del Sprint 1.

---

## ¿Qué aprendimos?

- Partir US-008 en **A/B** evitó meter 29 SP en un sprint de 26. El seed de clientes (IMP-09) fue la decisión correcta: no inventamos un CRUD.
- Un test verde de bloqueo **no basta** si el reloj de la app y el de PostgreSQL no es el mismo (IMP-07). El vencimiento tiene que vivir en la base.
- Las acciones A3/A4 (CodeQL, Staging) se cayeron porque el Sprint 1 tardío comió el 2. Si no tienen historia en el sprint con SP, no ocurren.
- El menú por rol (`Shell.tsx` + `permissions.ts`) hizo la demo entendible: el docente ve qué *no* puede el Conductor sin abrir Swagger.

---

## ¿Qué estamos haciendo bien?

- Cerrar un bug de demo el mismo día (423) sin abrir alcance nuevo.
- Tests que clavan el Gherkin: 403 del Operador, DNI duplicado, pedido sin consentimiento, XSS que no persiste.
- README con recorrido de punta a punta alineado al Goal (pasos 1–7).
- No se mezcló el motor ni el mapa “porque ya estábamos en el código”.

---

## ¿Qué podemos hacer mejor?

### Personas

Axel cargó US-002 + US-003 + el fix del reloj. Katheryn y Brayan llegaron cuando la API ya existía: mejor que en el Sprint 1, pero A1 (contrato OpenAPI el día 1) otra vez fue implícito, no un entregable del Daily.

### Relaciones

A5 (Jira a Done el día del merge) **no se evidenció** en este repositorio. El software va más rápido que el tablero; el docente puede creer que el Sprint 2 “no está en Jira”.

### Procesos

Cero días de sprint “de calendario” (16–29/09) con código: todo el 2 se hizo el 01/10. Eso no es Scrum, es un *spike* de un día. Hay que o rebaselinear fechas en el Acta o arrancar el Sprint 3 el 02/10 con Daily real.

No se revisó el plan de acción S1 al planning del 2: IMP-04 sigue igual.

### Herramientas

- Sigue sin CodeQL ni Staging URL.
- `GET /clientes` existe solo para el combo del pedido; si alguien lo ve en `/docs` parece un módulo. Conviene anotar en OpenAPI “solo lectura / seed”.
- El bloqueo dependía de datetime naive; faltó una prueba de integración contra `NOW()` de Postgres desde el primer commit, no desde el hotfix.

### Acciones a realizar

| # | Acción | Eje | Dueño | Fecha | Estado S1 |
|---|---|---|---|---|---|
| A1 | OpenAPI del Sprint 3 (worker/rutas aunque sea 501) el día 1 | Personas | Jorge | Día 1 Sprint 3 | Reiterada |
| A3 | Job CodeQL en `ci.yml` | Herramientas | Axel | Antes del 27/10/2026 | **Incumplida en S2** |
| A4 | URL de Staging (Railway/Render) en el README | Herramientas | Jorge | 27/10/2026 | **Incumplida en S2** |
| A5 | Jira Done + enlace al PR el día del merge | Relaciones | Eilene | Sprint 3, cada merge | **Incumplida en S2** |
| A7 | En Planning del Sprint 3, meter US-008 B (3 SP) + US-007 (5) y **partir** ENB-001/US-010 en subtareas ≤ 8 h | Procesos | Eilene + Jorge | Día 1 Sprint 3 | Nueva |
| A8 | Añadir descripción OpenAPI a `GET /clientes`: “catálogo de demostración, sin altas” | Herramientas | Axel | Sprint 3 | Nueva |
| A9 | Test de bloqueo que avance el reloj en PostgreSQL (`clock_timestamp`) en el mismo PR que el login | Procesos | Axel | Hecho en 74dac8b; no revertir | Nueva |

Sin A3 y A4, el Hito 3 (27/10) llegará otra vez con DoD a medias.

Revisión de esta iteración: [03 Revisión del Sprint V_1_0_0.md](./03%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md). Impedimentos: [02 Registro de Impedimentos V_1_0_0.md](./02%20Registro%20de%20Impedimentos%20V_1_0_0.md).

---

## Historial de control de cambios

| Versión | Fecha | Autor | Descripción |
|---|---|---|---|
| 1.0.0 | 02/10/2026 | Equipo EcoLogística Lima | Retrospectiva del Sprint 1. |
| 1.1.0 | 02/10/2026 | Equipo EcoLogística Lima | Retrospectiva del Sprint 2; se marcan A3–A5 incumplidas y se agregan A7–A9. |

---

[← Volver al README Principal](../../../README.md)
