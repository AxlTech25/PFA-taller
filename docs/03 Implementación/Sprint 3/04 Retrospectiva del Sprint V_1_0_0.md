[← Volver al README Principal](../../../README.md)

# Retrospectiva del sprint

**Nombre del Proyecto:** EcoLogística Lima – Optimizador de Rutas Sostenibles para DistriRápido S.A.C.

**Líder del Proyecto:** Carhuapoma Fano, Eilene Elizabeth

**Versión:** 1.2.0 — Sprint 3 (17/10/2026)

Se revisan las acciones A3, A4, A5, A7, A8 y A9 de la retrospectiva del Sprint 2.

---

## ¿Qué aprendimos?

- Partir ENB-001 y US-010 dejó algo demostrable (worker + vecino más cercano) sin fingir que el GA de 13 SP ya está hecho.
- El contrato de ENB-006 es el 202 y el proceso aparte. Si el cálculo vive en el request, el C4 no se cumple aunque la heurística sea correcta.
- A3 (CodeQL) sí cabe en el sprint cuando se escribe el workflow en el mismo PR. A4 (Staging) no: sin secreto de Railway/Render no hay URL honesta.
- Las envolventes de distrito alcanzan para el Gherkin de cobertura y hay que decirlo, para no venderlas como el límite municipal.

---

## ¿Qué estamos haciendo bien?

- No se abrió un CRUD de clientes. `GET /clientes` ahora lo dice en OpenAPI (A8).
- Los tests clavan el rechazo de 8 h, el descanso de 1 h, el 503 sin fila de job y el pedido que no se crea fuera de Lima Este.
- El menú ganó **Rutas** con la misma matriz de roles: el Conductor no la ve; el Gerente no confirma.
- A9 se mantuvo: el bloqueo sigue decidido con `clock_timestamp()` en PostgreSQL.

---

## ¿Qué podemos hacer mejor?

### Personas

Jorge concentra worker, heurística y jornada. Katheryn tiene la pantalla de pedidos y de rutas, pero el contrato OpenAPI otra vez llegó junto con el código y no como un entregable del día 1 (A1, reiterada).

### Relaciones

A5 (Jira a Done el día del merge) sigue sin evidencia en el repo. El tablero puede ir detrás de este PR igual que pasó con el Sprint 2.

### Procesos

El Sprint 3 sí cae dentro de su ventana (16/10–29/10), a diferencia del 2. Conviene no comprimir el 4 el último día: el mapa y la metaheurística no caben en un spike.

### Herramientas

- CodeQL está en `.github/workflows/codeql.yml`. Falta ver el primer análisis en verde en GitHub (el runner no se ejecuta en la máquina de desarrollo).
- Sigue sin URL de Staging.
- Redis es obligatorio para optimizar. Compose lo levanta; sin el worker la pantalla se queda en «En cola», que es el comportamiento correcto y hay que decirlo en la demo.

### Acciones a realizar

| # | Acción | Eje | Dueño | Fecha | Estado |
|---|---|---|---|---|---|
| A1 | Publicar el OpenAPI del sprint el día 1, antes de la UI | Personas | Jorge | Sprint 4, día 1 | Reiterada |
| A3 | Job CodeQL en CI | Herramientas | Axel | 17/10/2026 | **Hecha en este sprint** (workflow). Verificar el run del PR |
| A4 | URL de Staging (Railway/Render) en el README | Herramientas | Jorge | 12/11/2026 | Pendiente. No hay secreto de deploy |
| A5 | Jira Done + enlace al PR el día del merge | Relaciones | Eilene | Al merge | Pendiente desde el Sprint 2 |
| A7 | Partir ENB-001 / US-010 en un tramo demostrable | Procesos | Eilene + Jorge | 17/10/2026 | **Hecha:** heurística y worker. El GA queda en el Sprint 4 |
| A8 | OpenAPI de `GET /clientes`: catálogo de demostración, sin altas | Herramientas | Axel | 17/10/2026 | **Hecha** |
| A10 | No presentar las envolventes como catastro INEI en la sustentación | Procesos | Brayan | Review con el docente | Nueva |

Revisión: [03 Revisión del Sprint V_1_0_0.md](./03%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md). Impedimentos: [02 Registro de Impedimentos V_1_0_0.md](./02%20Registro%20de%20Impedimentos%20V_1_0_0.md).

---

## Historial de control de cambios

| Versión | Fecha | Autor | Descripción |
|---|---|---|---|
| 1.0.0 | 02/10/2026 | Equipo EcoLogística Lima | Retrospectiva del Sprint 1. |
| 1.1.0 | 02/10/2026 | Equipo EcoLogística Lima | Retrospectiva del Sprint 2. |
| 1.2.0 | 17/10/2026 | Equipo EcoLogística Lima | Retrospectiva del Sprint 3. A3, A7 y A8 hechas. A4 y A5 siguen abiertas. |

---

[← Volver al README Principal](../../../README.md)
