[← Volver al README Principal](../../../README.md)

# Registro de impedimentos

**Nombre del Proyecto:** EcoLogística Lima – Optimizador de Rutas Sostenibles para DistriRápido S.A.C.

**Líder del Proyecto:** Carhuapoma Fano, Eilene Elizabeth

**Versión:** 1.2.0 — Sprint 3 (16/10/2026 – 29/10/2026; implementación 17/10/2026)

Se heredan los impedimentos abiertos del [Sprint 2](../Sprint%202/02%20Registro%20de%20Impedimentos%20V_1_0_0.md). En este sprint no se reabren IMP-07 a IMP-10.

| Impedimento # | Fecha de Registro | Descripción del Impedimento así como el Impacto en el Proyecto | Prioridad | Reportado por | Fecha tope de Resolución | Estado | Fecha de Resolución | Resolución/Comentarios |
|---|---|---|---|---|---|---|---|---|
| IMP-04 | 30/09/2026 | *(Arrastre)* El DoD pide Staging en la nube (D4) y análisis estático CodeQL o SonarQube (D2). Sin eso el Quality Gate del repositorio no cubre el DoD completo. | Media | Cruz Salazar, Jorge Luiz | 12/11/2026 | En curso | — | **17/10/2026:** se agrega `.github/workflows/codeql.yml` (JavaScript/TypeScript y Python) en el PR del Sprint 3. **Sigue pendiente** la URL de Staging (Railway/Render): hace falta un secreto de despliegue que este repositorio no tiene, y no se publica uno de demostración. Compose sigue siendo el ambiente reproducible. Tope alineado al Hito 3 (12/11). |
| IMP-11 | 17/10/2026 | RN-005 pide polígonos distritales. El Sprint 3 siembra envolventes rectangulares en `distrito_cobertura`, no el catastro INEI. Impacto: un punto límite real podría aceptarse o rechazarse distinto al límite municipal. La demo de los cuatro distritos sí rechaza fuera del rectángulo (p. ej. Miraflores). | Baja | Leon Taza, Brayan Angel | 12/11/2026 | Aceptado | 17/10/2026 | Se documenta la limitación y se deja la validación en PostGIS (`ST_Covers`) para poder reemplazar la geometría sin cambiar la API. No bloquea US-008 B. |

**Resumen Sprint 3:** IMP-04 sigue en curso (CodeQL entregado, Staging no). IMP-11 aceptado como limitación de datos. No hubo defecto de demo abierto al cierre del código.

Informe: [01 Informe de estado del proyecto V_1_0_0.md](./01%20Informe%20de%20estado%20del%20proyecto%20V_1_0_0.md). Revisión: [03 Revisión del Sprint V_1_0_0.md](./03%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md).

---

## Historial de control de cambios

| Versión | Fecha | Autor | Descripción |
|---|---|---|---|
| 1.0.0 | 02/10/2026 | Equipo EcoLogística Lima | Impedimentos del Sprint 1. |
| 1.1.0 | 02/10/2026 | Equipo EcoLogística Lima | Sprint 2: IMP-07 a IMP-10 y arrastre de IMP-04. |
| 1.2.0 | 17/10/2026 | Equipo EcoLogística Lima | Sprint 3: CodeQL parcial de IMP-04 e IMP-11 (envolventes de cobertura). |

---

[← Volver al README Principal](../../../README.md)
