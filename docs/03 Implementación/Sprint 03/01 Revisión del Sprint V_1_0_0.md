# Revisión del sprint

**Nombre del Proyecto:** EcoLogística Lima – Optimizador de Rutas Sostenibles para DistriRápido S.A.C.

**Líder del Proyecto:** Eilene Elizabeth Carhuapoma Fano

---

## Historias de Usuario completadas en este Sprint

Durante el Sprint 3 se completaron **13 Story Points (SP)** planificados, los cuales cumplen en su totalidad con la **Definition of Done (DoD)** global del proyecto:
1. Cobertura de pruebas unitarias e integración $\ge 80\%$ en backend y frontend.
2. Cumplimiento de Quality Gate en SonarQube / CodeQL (0 vulnerabilidades y 0 bugs críticos).
3. Aprobación por *Peer Review* y merge exitoso en el repositorio a través del **PR #15**.
4. Despliegue y validación de escenarios de prueba Gherkin (*Dado / Cuando / Entonces*) en el entorno de Staging.

| ID | Historia / Enabler | SP | Estado | Criterio de Aceptación y Verificación |
| --- | --- | --- | --- | --- |
| **US-008 B** | Cobertura en Lima Este y direcciones con punto de referencia | 3 | **Completada** *(Cumple DoD)* | **Criterio:** Registra entregas con direcciones no estandarizadas y puntos de referencia en SJL, El Agustino, Santa Anita y Ate. Rechaza pedidos fuera de la cobertura (ej. Miraflores) con error `422 Unprocessable Entity`.<br>**Verificación:** 100% de pruebas unitarias en Pytest pasadas y validación funcional con 10 direcciones reales. |
| **US-007** | Control de jornada laboral de 8h y descansos | 5 | **Completada** *(Cumple DoD)* | **Criterio:** Cumplimiento de la **Ley N.º 30224**. Inserta 1h de descanso tras 4h continuas de conducción. Bloquea y responde `422` ante cualquier asignación que exceda las 8h diarias.<br>**Verificación:** Escenarios Gherkin validados para rutas de 7h (aprobadas) y 8.5h (bloqueadas). |
| **ENB-006** | Procesamiento asíncrono con Worker y Redis | 5 | **Completado** *(Cumple DoD)* | **Criterio:** `POST /optimizaciones` responde `202 Accepted` con `id_job`. El worker en Python procesa la ruta en segundo plano mediante cola Redis. Maneja fallos de Redis devolviendo `503 Service Unavailable`.<br>**Verificación:** Pruebas de integración asíncronas verificando el ciclo (`PENDING` $\rightarrow$ `PROCESSING` $\rightarrow$ `SUCCESS`). |

---

## Demostración del trabajo completado

La demostración del trabajo completado se llevó a cabo en una sesión síncrona mediante el entorno contenedorizado (`docker compose up --build`).

> **Nota de contexto:** La presentación se realiza mediante la **simulación de los stakeholders clave del proyecto**:
> * **Gerente General / Sponsor (DistriRápido S.A.C.):** Enfocado en el cumplimiento de normas de trabajo y límites del servicio.
> * **Jefe de Operaciones Logísticas:** Interesado en la usabilidad, la fluidez al calcular rutas y precisión en Lima Este.
> * **Auditor de Cumplimiento Legal:** Encargado de fiscalizar el respeto a la Ley N.º 30224 y la Ley N.º 29733.
> * **Representante de Conductores:** Interesado en la asignación equitativa y pausas de descanso.

### Matriz de Escenarios Demostrados en Vivo

| Escenario | Módulo / Funcionalidad | Acción Realizada en Vivo | Resultado Observado / Respuesta del Sistema |
| --- | --- | --- | --- |
| **1** | **Filtro Geoespacial de Cobertura** *(Lima Este)* | **A.** Alta de pedido en *Ate* con referencia *"al costado de la losa deportiva"*.<br>**B.** Intento de alta de pedido con GPS en *Miraflores*. | **A.** Georreferenciación correcta dentro del polígono autorizado.<br>**B.** Bloqueo inmediato con alerta HTTP `422` por estar fuera del área de servicio. |
| **2** | **Generación Asíncrona** *(Worker + Redis)* | Selección de 25 pedidos en estado `PENDIENTE` y clic en *"Generar Plan Optimizado"*. | Respuesta en $<300\text{ ms}$ con HTTP `202 Accepted` y `id_job`. La UI permaneció fluida mientras el worker procesó en segundo plano. |
| **3** | **Fiscalización Laboral** *(Ley N.º 30224)* | **A.** Intento de asignación de ruta de $8\text{ h } 45\text{ min}$ a un conductor.<br>**B.** Reajuste de carga a $6\text{ h } 30\text{ min}$ de itinerancia. | **A. (Bloqueo):** Error de la API `422 Unprocessable Entity` citando la Ley N.º 30224.<br>**B. (Aprobación):** Generación de ruta insertando bloque de $1\text{ h}$ de descanso obligatorio. |

---

## Pendientes

En estricta alineación con el estado real del proyecto y la transparencia del backlog, se detallan las historias de usuario y enablers que quedaron diferidos o en estado parcial al cierre del Sprint 3:

| ID | Historia / Enabler | SP | Estado Real | Plan y Acciones Pendientes para Sprint 4 |
| --- | --- | --- | --- | --- |
| **US-010** | Motor VRPTW + Green VRP | 13 | Entregado Parcialmente | Integración completa del **Algoritmo Genético (DEAP)** para la instancia masiva de $150 \text{ pedidos} \times 15 \text{ vehículos}$, optimizando ventanas y $\text{CO}_2$. |
| **ENB-001** | SLA del Motor ($\le 45\text{ s}$) | 13 | Entregado Parcialmente | Certificación del tiempo de respuesta ($\le 45\text{ s}$ P95) sobre el entorno de Staging mediante pruebas de carga automatizadas con Locust. |
| **US-012** | Mapa Interactivo Leaflet / OSM | 8 | No Iniciado | Construcción del visualizador React-Leaflet con trazado de capas codificadas por color según congestión y zonas de riesgo. |
| **US-014
