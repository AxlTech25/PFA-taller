# Revisión del Sprint

**Nombre del proyecto:** EcoLogística Lima – Optimizador de Rutas Sostenibles para DistriRápido S.A.C.

**Líder del proyecto:** Eilene Elizabeth Carhuapoma Fano

---

## Historias de usuario completadas en este Sprint

Durante el Sprint 3 se completaron las actividades correspondientes a **13 Story Points (SP)** planificados. Las historias de usuario y el enabler finalizados cumplieron con los criterios establecidos en la *Definition of Done* (DoD) del proyecto, que considera los siguientes aspectos:

1. Cobertura de pruebas unitarias y de integración igual o superior al 80 % en el backend y frontend.
2. Aprobación de los controles de calidad en SonarQube y CodeQL, sin vulnerabilidades ni errores críticos.
3. Revisión del código por otro integrante del equipo (*Peer Review*) y fusión de los cambios en el repositorio mediante el PR #15.
4. Despliegue en el entorno de *Staging* y validación de los escenarios de prueba utilizando Gherkin (*Dado / Cuando / Entonces*).

| ID | Historia / Enabler | SP | Estado | Criterio de aceptación y verificación |
| --- | --- | --- | --- | --- |
| **US-008 B** | Cobertura en Lima Este y direcciones con punto de referencia | 3 | **Completada** | **Criterio:** Permite registrar entregas con direcciones no estandarizadas y puntos de referencia en San Juan de Lurigancho, El Agustino, Santa Anita y Ate. Los pedidos ubicados fuera de la zona de cobertura, como Miraflores, son rechazados con el código `422 Unprocessable Entity`.<br><br>**Verificación:** Se ejecutaron las pruebas unitarias en Pytest y se validó el funcionamiento con 10 direcciones reales. |
| **US-007** | Control de jornada laboral de 8 horas y descansos | 5 | **Completada** | **Criterio:** Controla la duración de las jornadas de conducción e incorpora una hora de descanso después de cuatro horas continuas. También bloquea las asignaciones que superan las ocho horas diarias, devolviendo el código `422`.<br><br>**Verificación:** Se validaron los escenarios Gherkin correspondientes a una ruta de siete horas, que fue aprobada, y otra de ocho horas y treinta minutos, que fue bloqueada. |
| **ENB-006** | Procesamiento asíncrono con Worker y Redis | 5 | **Completado** | **Criterio:** El endpoint `POST /optimizaciones` devuelve una respuesta `202 Accepted` junto con un `id_job`. El procesamiento de las rutas se realiza en segundo plano mediante un worker en Python y una cola Redis. Si Redis presenta fallos, el sistema responde con `503 Service Unavailable`.<br><br>**Verificación:** Se realizaron pruebas de integración para comprobar el cambio de estado del trabajo desde `PENDING` hasta `PROCESSING` y, finalmente, `SUCCESS`. |

---

## Demostración del trabajo completado

La demostración del Sprint 3 se realizó en una sesión en vivo, utilizando el entorno del proyecto mediante el comando `docker compose up --build`. Durante la presentación se probaron las principales funcionalidades implementadas, con el propósito de comprobar su funcionamiento y mostrar cómo responden ante diferentes situaciones.

Para la demostración se consideraron los siguientes perfiles relacionados con el proyecto:

- **Gerente general o patrocinador de DistriRápido S.A.C.:** interesado en el cumplimiento de las condiciones del servicio y las normas laborales.
- **Jefe de operaciones logísticas:** enfocado en la facilidad de uso, el cálculo de rutas y la cobertura de las entregas en Lima Este.
- **Auditor de cumplimiento legal:** encargado de revisar el cumplimiento de los requisitos legales y la protección de los datos personales.
- **Representante de los conductores:** interesado en la distribución de las rutas y el respeto de los tiempos de descanso.

### Escenarios demostrados en vivo

| Escenario | Módulo / funcionalidad | Acción realizada | Resultado observado |
| --- | --- | --- | --- |
| **1. Validación de la zona de cobertura** | Filtro geoespacial de Lima Este | Se registró un pedido en Ate con la referencia «al costado de la losa deportiva». Luego, se intentó registrar otro pedido ubicado en Miraflores. | El pedido de Ate se ubicó dentro de la zona autorizada. En el caso de Miraflores, el sistema rechazó el registro y devolvió el código HTTP `422`, debido a que la dirección estaba fuera del área de servicio. |
| **2. Generación de rutas en segundo plano** | Worker y Redis | Se seleccionaron 25 pedidos en estado `PENDIENTE` y se ejecutó la opción «Generar Plan Optimizado». | El sistema respondió con `202 Accepted` y un `id_job` en menos de 300 ms. El procesamiento continuó en segundo plano, permitiendo que la interfaz siguiera funcionando mientras se generaba el plan. |
| **3. Control de la jornada laboral** | Validación de horarios y descansos | Se intentó asignar a un conductor una ruta de ocho horas y cuarenta y cinco minutos. Después, se ajustó la carga para una ruta de seis horas y treinta minutos. | La primera asignación fue bloqueada con una respuesta `422 Unprocessable Entity`. En el segundo caso, se aprobó la ruta y se incorporó un bloque de una hora de descanso. |

Los escenarios permitieron comprobar la validación de las zonas de cobertura, el procesamiento asíncrono de los pedidos y las restricciones relacionadas con la jornada de los conductores.

---

## Pendientes para el siguiente Sprint

Al cierre del Sprint 3, quedaron algunas funcionalidades que requieren trabajo adicional para completar su implementación y validación. Estas actividades se incorporarán al Sprint 4, de acuerdo con el estado en el que se encuentran.

| ID | Historia / Enabler | SP | Estado al cierre del Sprint 3 | Actividades pendientes para el Sprint 4 |
| --- | --- | --- | --- | --- |
| **US-010** | Motor VRPTW + Green VRP | 13 | Entrega parcial | Completar la integración del algoritmo genético mediante DEAP para procesar una instancia de 150 pedidos y 15 vehículos. Se debe mejorar la optimización de las ventanas horarias y reducir las emisiones de CO₂. |
| **ENB-001** | SLA del motor (≤ 45 s) | 13 | Entrega parcial | Ejecutar pruebas de carga automatizadas con Locust en el entorno de *Staging* para evaluar el tiempo de respuesta y verificar que el percentil 95 (P95) no supere los 45 segundos. |
| **US-012** | Mapa interactivo con Leaflet / OSM | 8 | No iniciado | Desarrollar el mapa interactivo con React-Leaflet y OpenStreetMap para visualizar las rutas, utilizando colores para diferenciar los niveles de congestión y las zonas de riesgo. |
| **US-014** | Dashboard de métricas | 8 | No iniciado | Implementar un tablero de indicadores que permita visualizar el consumo de combustible en litros, las emisiones de CO₂ en kilogramos, el ahorro económico en soles y su equivalencia en árboles. |

Las actividades pendientes se retomarán en el siguiente Sprint para avanzar con la optimización de rutas, evaluar el rendimiento del motor y completar las funcionalidades de visualización y seguimiento de indicadores. Las historias con entrega parcial requieren finalizar su implementación y verificar los criterios de aceptación antes de considerarse completadas.
