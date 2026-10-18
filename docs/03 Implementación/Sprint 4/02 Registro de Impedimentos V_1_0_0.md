[← Volver al README Principal](../../../README.md)

# Registro de impedimentos

**Nombre del Proyecto:** EcoLogística Lima – Optimizador de Rutas Sostenibles para DistriRápido S.A.C.

**Líder del Proyecto:** Carhuapoma Fano, Eilene Elizabeth

**Versión:** 1.3.0 — Sprint 4 (ventana 30/10/2026 – 12/11/2026; implementación 18/10/2026)

Se heredan los impedimentos abiertos del [Sprint 3](../Sprint%203/02%20Registro%20de%20Impedimentos%20V_1_0_0.md). En este sprint no se reabren IMP-07 a IMP-10.

| Impedimento # | Fecha de Registro | Descripción del Impedimento así como el Impacto en el Proyecto | Prioridad | Reportado por | Fecha tope de Resolución | Estado | Fecha de Resolución | Resolución/Comentarios |
|---|---|---|---|---|---|---|---|---|
| IMP-04 | 30/09/2026 | *(Arrastre)* El DoD pide Staging en la nube (D4). Sin URL pública no se cierra el Quality Gate completo ni la frase «corre el worker en Staging» de ENB-001. | Media | Cruz Salazar, Jorge Luiz | 12/11/2026 | En curso | — | **18/10/2026:** CodeQL sigue en el workflow del Sprint 3. **Sigue pendiente** la URL de Staging (Railway/Render). Este repositorio no tiene un secreto de despliegue y no se publica uno de demostración. Compose sigue siendo el ambiente reproducible. El tope no se mueve: 12/11/2026, Hito 3. |
| IMP-11 | 17/10/2026 | RN-005 pide polígonos distritales. Siguen las envolventes de `004_sprint3_cobertura.py`, no el catastro INEI. | Baja | Leon Taza, Brayan Angel | 12/11/2026 | Aceptado | 17/10/2026 | **18/10/2026:** no hay archivo oficial en el repositorio. No se sustituye la geometría con un polígono inventado. La validación sigue en PostGIS. |

**Resumen Sprint 4:** IMP-04 sigue en curso (solo Staging; CodeQL ya estaba). IMP-11 sigue aceptado. No se abre un defecto de demo.

Informe: [01 Informe de estado del proyecto V_1_0_0.md](./01%20Informe%20de%20estado%20del%20proyecto%20V_1_0_0.md). Revisión: [03 Revisión del Sprint V_1_0_0.md](./03%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md).

---

## Historial de control de cambios

| Versión | Fecha | Autor | Descripción |
|---|---|---|---|
| 1.0.0 | 02/10/2026 | Equipo EcoLogística Lima | Impedimentos del Sprint 1. |
| 1.1.0 | 02/10/2026 | Equipo EcoLogística Lima | Sprint 2: IMP-07 a IMP-10 y arrastre de IMP-04. |
| 1.2.0 | 17/10/2026 | Equipo EcoLogística Lima | Sprint 3: CodeQL parcial de IMP-04 e IMP-11. |
| 1.3.0 | 18/10/2026 | Equipo EcoLogística Lima | Sprint 4: Staging de IMP-04 sigue pendiente al 12/11. IMP-11 sin archivo INEI. |

---

[← Volver al README Principal](../../../README.md)
