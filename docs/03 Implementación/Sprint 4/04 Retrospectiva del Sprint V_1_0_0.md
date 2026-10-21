[← Volver al README Principal](../../../README.md)

# Retrospectiva del sprint

**Nombre del Proyecto:** EcoLogística Lima – Optimizador de Rutas Sostenibles para DistriRápido S.A.C.

**Líder del Proyecto:** Carhuapoma Fano, Eilene Elizabeth

**Versión:** 1.3.0 — Sprint 4 (18/10/2026)

Se revisan las acciones A1, A4, A5 y A10 de la retrospectiva del Sprint 3.

---

## ¿Qué aprendimos?

- El contrato de ENB-006 se pudo conservar: el genético vive en `python -m app.worker`. Si el cálculo volviera al request, el 202 dejaría de significar algo.
- Comparar contra el vecino más cercano evita vender una mejora que no existe. En la grilla de 150×15 el genético iguala la línea base; en el cruce de cuatro paradas sí la baja, y ahí se mide el 15 % frente al óptimo enumerado.
- El Hito 3 nombra el dashboard. Iniciarlo con los números que la ruta ya guarda no obliga a dar US-014 por cerrada.
- A4 (Staging) otra vez no ocurre sin secreto. Inventar una URL sería peor que dejar IMP-04 abierto hasta el 12/11.

---

## ¿Qué estamos haciendo bien?

- No se reescribió la cola ni el borrador hasta confirmar.
- No se editó una migración vieja. No hizo falta una nueva: la comparación cabe en el JSON del job.
- El factor de árboles no se rellenó con un número que el documento 11 deja al docente.
- Las envolventes de Lima Este no se disfrazaron de catastro (A10).

---

## ¿Qué podemos hacer mejor?

### Personas

Jorge sigue concentrando el motor. Katheryn recibe el mapa y el tablero en el mismo incremento, otra vez con el OpenAPI junto al código (A1).

### Relaciones

A5 (Jira a Done el día del merge) sigue sin evidencia en el repo. US-008 B, US-007 y ENB-006 debían moverse al merge del Sprint 3; este PR no lo sustituye.

### Procesos

El código del Sprint 4 entra el 18/10, antes del 30/10. Conviene no tratar esa fecha como si el Hito 3 ya hubiera pasado: el tope del hito sigue siendo el 12/11, y Staging cabe ahí si hay credenciales.

### Herramientas

- CodeQL sigue en el workflow. Hay que mirar el run de este PR.
- Sigue sin URL de Staging.
- Leaflet pide red para las teselas. La tabla es el respaldo cuando OpenStreetMap no responde; hay que decirlo en la sustentación.

### Acciones a realizar

| # | Acción | Eje | Dueño | Fecha | Estado |
|---|---|---|---|---|---|
| A1 | Publicar el OpenAPI del sprint el día 1, antes de la UI | Personas | Jorge | Sprint 4 | Parcial: `/docs` publica `/indicadores` y la comparación en el mismo PR. No hubo un día 1 separado |
| A4 | URL de Staging (Railway/Render) en el README | Herramientas | Jorge | 12/11/2026 | Pendiente. No hay secreto de deploy |
| A5 | Jira Done + enlace al PR el día del merge | Relaciones | Eilene | Al merge | Pendiente desde el Sprint 2 |
| A10 | No presentar las envolventes como catastro INEI | Procesos | Brayan | Review con el docente | Se mantiene |
| A11 | No presentar el tablero iniciado como el cierre de US-014 | Procesos | Katheryn | Sprint 5 | Nueva |
| A12 | Medir el P95 del bench en Staging cuando exista URL | Herramientas | Jorge | 12/11/2026, si hay Staging | Nueva. Hoy la evidencia es la prueba de CI y ocho corridas locales |

Revisión: [03 Revisión del Sprint V_1_0_0.md](./03%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md). Impedimentos: [02 Registro de Impedimentos V_1_0_0.md](./02%20Registro%20de%20Impedimentos%20V_1_0_0.md).

---

## Historial de control de cambios

| Versión | Fecha | Autor | Descripción |
|---|---|---|---|
| 1.0.0 | 02/10/2026 | Equipo EcoLogística Lima | Retrospectiva del Sprint 1. |
| 1.1.0 | 02/10/2026 | Equipo EcoLogística Lima | Retrospectiva del Sprint 2. |
| 1.2.0 | 17/10/2026 | Equipo EcoLogística Lima | Retrospectiva del Sprint 3. |
| 1.3.0 | 18/10/2026 | Equipo EcoLogística Lima | Retrospectiva del Sprint 4. A4 y A5 siguen abiertas. A11 y A12 nuevas. |

---

[← Volver al README Principal](../../../README.md)
