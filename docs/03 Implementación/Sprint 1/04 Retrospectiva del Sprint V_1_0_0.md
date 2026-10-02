[← Volver al README Principal](../../../README.md)

# Retrospectiva del sprint

**Nombre del Proyecto:** EcoLogística Lima – Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Líder del Proyecto:** Carhuapoma Fano, Eilene Elizabeth  
**Sprint:** 1  
**Fecha:** 02/10/2026  
**Versión:** 1.0.0

Formato *qué aprendimos / qué funciona / qué mejorar*, con los cuatro ejes exigidos por la consigna y un plan de acción con dueño y fecha.

---

## ¿Qué aprendimos?

- El Sprint Goal en lenguaje de **pantallas** (login + alta de vehículo) permite demostrar 26 SP sin explicar PostgreSQL ni JWT al docente.
- Docker Compose y un `.env.example` sin contraseñas rellenas no bastan: si nadie completa `SEED_*`, la demo de US-001 parece rota.
- Un Quality Gate con **cobertura mínima 80 %** en CI obliga a escribir pruebas del Gherkin (login 401, placa duplicada) antes del merge; eso sí es DoD, no un porcentaje decorativo.
- El calendario académico (RSK-05) no se “recupera” en Jira: el Acta decía 15/09 y el merge fue 30/09. Hay que timeboxear el arranque, no solo el alcance.
- Windows + scripts de contenedor exigen **LF explícito** (`.gitattributes`); si no, el impedimento se descubre el día de la demo.

---

## ¿Qué estamos haciendo bien?

- Vertical slice de punta a punta: migración → API → pantalla → prueba → CI, en un solo PR (#9).
- Contratos en español (mensajes 409/422) alineados a los escenarios Gherkin del artefacto 01.
- Separación `frontend/` y `backend/` con un solo Compose, reproducible en tres comandos.
- No se subieron secretos: `.env` está en `.gitignore` y las claves de demo viven en `.env.example` vacías.

---

## ¿Qué podemos hacer mejor?

### Personas

La implementación del Sprint 1 se concentró tarde (cierre 30/09). Brayan (BD) y Axel (API/CI) cargaron el camino crítico; Katheryn pudo entrar a la UI de flota solo cuando existió `POST /vehiculos`. Falta un acuerdo de **pareja el día 1** (contrato API + pantalla en paralelo con OpenAPI mock o contrato FastAPI ya publicado).

### Relaciones

El PM tuvo Jira y evidencias listas antes que el código. Eso desalineó al docente respecto de “tablero vs software”. La Review debe citar el **commit/PR**, no solo la captura de Jira del mes anterior.

### Procesos

No hubo Daily con inspección del burndown real (el trabajo ocurrió en un bloque al final). El DoR se cumplió en el markdown (Gherkin, SP) pero no se partió ENB-003 en subtareas visibles en Jira durante el sprint. El desfase de 15 días se aceptó sin change request formal al Acta.

### Herramientas

- CI sin CodeQL/Sonar (DoD D2 incompleto).
- No hay Staging URL; Compose es local (DoD D4 incompleto).
- Jira no reflejó el Done real del PR #9 el mismo día del merge.
- Choque de puerto 5432 no estaba en el README hasta que Brayan lo descubrió.

### Acciones a realizar

| # | Acción | Eje | Dueño | Fecha |
|---|---|---|---|---|
| A1 | En el día 1 de cada sprint, publicar el contrato OpenAPI (aunque el endpoint sea 501) para desbloquear frontend | Personas / procesos | Jorge Cruz | Sprint 3, día 1 |
| A2 | Timebox de 2 h de “máquina en verde” (Compose + `.env` + login) el primer día del sprint | Procesos | Axel Estrada | Cada sprint, día 1 |
| A3 | Añadir job CodeQL (o SonarCloud) al workflow `ci.yml` | Herramientas | Axel Estrada | Antes del cierre Sprint 3 |
| A4 | Decidir URL de Staging (Railway o Render) y documentarla en el README | Herramientas | Jorge Cruz | 27/10/2026 (Hito 3) |
| A5 | Actualizar Jira a Done el mismo día del merge a `main`, con enlace al PR | Relaciones | Eilene Carhuapoma | Inmediato, Sprint 2 en adelante |
| A6 | Mantener en el README el puerto **5433** y el aviso CRLF/LF | Herramientas | Brayan Leon | Hecho en README actual; revisar si alguien vuelve a 5432 |

Las acciones A3 y A4 cierran IMP-04. A2 y A5 mitigan IMP-03 / RSK-05.

---

## Historial de control de cambios

| Versión | Fecha | Autor | Descripción |
|---|---|---|---|
| 1.0.0 | 02/10/2026 | Equipo EcoLogística Lima | Retrospectiva del Sprint 1 con plan de acción A1–A6. |

---

[← Volver al README Principal](../../../README.md)
