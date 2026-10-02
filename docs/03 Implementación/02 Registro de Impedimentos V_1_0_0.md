[← Volver al README Principal](../../README.md)

# Registro de impedimentos

**Nombre del Proyecto:** EcoLogística Lima – Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Líder del Proyecto:** Carhuapoma Fano, Eilene Elizabeth  
**Sprint cubierto:** 1 (02/09/2026 – 15/09/2026; implementación fusionada el 30/09/2026)  
**Fecha:** 02/10/2026  
**Versión:** 1.0.0

Los impedimentos se numeran `IMP-0n`. La prioridad usa la misma escala del registro de riesgos (Alto / Medio / Bajo). El estado es Abierto, En curso, Resuelto o Aceptado.

| Impedimento # | Fecha de Registro | Descripción del Impedimento así como el Impacto en el Proyecto | Prioridad | Reportado por | Fecha tope de Resolución | Estado | Fecha de Resolución | Resolución/Comentarios |
|---|---|---|---|---|---|---|---|---|
| IMP-01 | 30/09/2026 | El puerto **5432** del host ya tenía una instancia de PostgreSQL. Docker Compose no podía publicar la base PostGIS y el equipo no levantaba el esquema (ENB-003) ni los tests. Impacto: bloqueo total del Sprint 1 en máquinas con Postgres local. | Alta | Leon Taza, Brayan Angel | 30/09/2026 | Resuelto | 30/09/2026 | Se publicó el contenedor en el host como **5433:5432** (`docker-compose.yml`). `DATABASE_URL` de desarrollo apunta a `localhost:5433`. Documentado en el README. |
| IMP-02 | 30/09/2026 | En Windows, `backend/entrypoint.sh` se guardaba con saltos **CRLF** y el contenedor de la API fallaba al arrancar (`$'\r': command not found`). Impacto: la demo con Compose no arrancaba en laptops del equipo. | Alta | Estrada Flores, Axel Sebastian | 30/09/2026 | Resuelto | 30/09/2026 | Se versionó `.gitattributes` con `eol=lf` para el entrypoint. El README advierte no convertir a CRLF. |
| IMP-03 | 15/09/2026 | El Sprint 1 del Acta cerraba el **15/09/2026**; el código se fusionó el **30/09/2026** (PR #9). Causa: carga académica simultánea (RSK-05) y arranque tardío de la vertical slice. Impacto: el Hito 1 de software quedó 15 días detrás del cronograma, comprimiendo el Sprint 2. | Alta | Carhuapoma Fano, Eilene Elizabeth | 30/09/2026 | Aceptado | 30/09/2026 | Se aceptó el desfase y se priorizó completar los 26 SP antes de abrir alcance nuevo. Acción de retrospectiva: timebox de arranque en el día 1 del sprint siguiente. El Sprint 2 se fusionó el 01/10/2026 (PR #10) para recuperar ritmo. |
| IMP-04 | 30/09/2026 | El DoD global exige **Staging en la nube** (D4) y **CodeQL/SonarQube** (D2). El CI actual solo corre Ruff, Pytest ≥ 80 % y el build de Vite. Impacto: el Quality Gate es real, pero no cubre el 100 % del DoD; un docente puede objetar “no está en Staging”. | Media | Cruz Salazar, Jorge Luiz | 27/10/2026 | En curso | — | Mitigación: Compose como Staging local reproducible. Contingencia: añadir CodeQL y un deploy a Railway/Render en un enabler de CI posterior, sin bloquear la aceptación de US-001 y US-004. |
| IMP-05 | 11/09/2026 | El backlog de Jira no tenía las 26 historias; solo un subconjunto visible en las evidencias. Impacto: trazabilidad CMMI/ALM débil (RSK-11) y confusión sobre qué demostrar en el Sprint 1. | Media | Carhuapoma Fano, Eilene Elizabeth | 29/09/2026 | Resuelto | 29/09/2026 | Se planificó el Sprint 2 en el artefacto 01 V_1_0_3 / Jira V_1_0_5 y se listó explícitamente qué tarjetas van a cada sprint. El Sprint 1 en código se ancló a los cinco ítems del Goal, no al backlog incompleto de las capturas. |
| IMP-06 | 30/09/2026 | `.env.example` deja `SEED_*_PASSWORD` vacío: si no se edita `.env`, no hay usuario Operador y el login de la demo “falla”. Impacto: falsa percepción de que US-001 no funciona. | Baja | Huaman Baldeon, Katheryn Elena | 30/09/2026 | Resuelto | 30/09/2026 | El README exige copiar `.env.example` y definir contraseñas de ≥ 8 caracteres. La flota demo (migración 002) no depende de esas claves. |

**Resumen Sprint 1:** 6 impedimentos · 4 resueltos · 1 aceptado (calendario) · 1 en curso (Staging/CodeQL). Ninguno deja las historias US-001 / US-004 sin software demostrable.

---

## Historial de control de cambios

| Versión | Fecha | Autor | Descripción |
|---|---|---|---|
| 1.0.0 | 02/10/2026 | Equipo EcoLogística Lima | Registro inicial de impedimentos del Sprint 1. |

---

[← Volver al README Principal](../../README.md)
