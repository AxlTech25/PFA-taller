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

A continuación, se detalla el estado de cada Historia de Usuario y Enabler completado:

* **US-008 B: Cobertura en Lima Este y direcciones con punto de referencia (3 SP)**
  * **Estado:** Completada (Cumple DoD).
  * **Criterio de Aceptación:** Implementación del filtro geográfico de pedidos a nivel de API REST (`POST /pedidos`) y componentes de entrada en React. El sistema permite registrar entregas con direcciones no estandarizadas respaldadas por puntos de referencia locales (ej. *«frente a la bodega El Ahorro»* o *«a dos cuadras del mercado Huandoy»*) dentro de los distritos de San Juan de Lurigancho, El Agustino, Santa Anita y Ate. Si se intenta ingresar un pedido con coordenadas GPS o dirección ubicada fuera de la cobertura de Lima Este (ej. Miraflores o San Isidro), el backend rechaza la solicitud de forma inmediata devolviendo un código de error `422 Unprocessable Entity`.
  * **Verificación:** Pruebas unitarias en Pytest pasadas al 100% y prueba funcional con 10 direcciones reales de Lima Este.

* **US-007: Control de jornada laboral de 8 horas y descansos de conductores (5 SP)**
  * **Estado:** Completada (Cumple DoD).
  * **Criterio de Aceptación:** Garantizar el cumplimiento estricto del marco legal laboral peruano (**Ley N.º 30224**). El motor backend evalúa el tiempo total de itinerancia de la ruta e inserta automáticamente una pausa obligatoria de 1 hora de descanso tras 4 horas continuas de conducción. Si el tiempo total acumulado de un conductor supera las 8 horas diarias de trabajo, la API bloquea la confirmación de la ruta y responde con una excepción `422 Unprocessable Entity` citando el incumplimiento de la norma legal.
  * **Verificación:** Escenarios Gherkin validados tanto para rutas de 7 h (aprobadas con pausa) como para rutas simuladas de 8.5 h (bloqueadas automáticamente).

* **ENB-006: Procesamiento asíncrono de rutas con Worker y cola Redis (5 SP)**
  * **Estado:** Completado (Cumple DoD).
  * **Criterio de Aceptación:** Al solicitar la optimización del plan diario mediante `POST /optimizaciones`, la API responde inmediatamente con un estado `202 Accepted` y entrega un token de seguimiento `id_job`, evitando el bloqueo o congelamiento de la interfaz de usuario. El procesamiento de la ruta es asumido en segundo plano por un worker en Python que consume la cola en Redis. En caso de que el servicio Redis quede inalcanzable, la API maneja la contingencia de forma segura devolviendo un error `503 Service Unavailable`.
  * **Verificación:** Pruebas de integración asíncronas con Celery/Redis verificando el ciclo de vida del *job* (`PENDING` $\rightarrow$ `PROCESSING` $\rightarrow$ `SUCCESS`).

---

## Demostración del trabajo completado

La demostración del trabajo completado se llevó a cabo en una sesión síncrona mediante el entorno contenedorizado (`docker compose up --build`). **Nota de contexto:** La presentación se realiza mediante la **simulación de los stakeholders clave del proyecto**, representando los intereses y validaciones de los siguientes roles:
* **Gerente General / Sponsor (DistriRápido S.A.C.):** Enfocado en el cumplimiento de normas de trabajo y límites del servicio.
* **Jefe de Operaciones Logísticas:** Interesado en la usabilidad, la no congelación del sistema al calcular rutas y la precisión de direcciones en Lima Este.
* **Auditor de Cumplimiento Legal:** Encargado de fiscalizar el respeto a la Ley N.º 30224 y la Ley N.º 29733.
* **Representante de Conductores:** Interesado en la asignación equitativa y pausas de descanso.

### Escenarios Demostrados en Vivo:

1. **Filtro Geoespacial de Cobertura (Lima Este):**
   * **Acción:** Se ingresó al sistema con el rol *Operador* y se abrió el formulario de alta de pedidos.
   * **Resultado A:** Se registró exitosamente un pedido para una bodega en *Ate* agregando el punto de referencia *"al costado de la losa deportiva"*. El sistema georreferenció el punto correctamente dentro del polígono de Lima Este.
   * **Resultado B:** Se intentó ingresar un pedido simulado asignando coordenadas GPS del distrito de *Miraflores*. El sistema detuvo el registro y mostró en pantalla una alerta clara de error HTTP `422` notificando que la ubicación se encuentra fuera del área de servicio autorizada.

2. **Generación Asíncrona de Rutas con Worker y Redis:**
   * **Acción:** Se seleccionaron 25 pedidos en estado `PENDIENTE` y se hizo clic en "Generar Plan Optimizado".
   * **Resultado:** La interfaz web respondió en menos de 300 ms entregando el mensaje *"Optimización iniciada (Job #ORD-8921)"* con estado HTTP `202 Accepted`. Se mostró cómo la interfaz continuó navegable mientras el worker en segundo plano (consultado mediante Redis) procesó el cálculo y guardó el resultado en estado `BORRADOR`.

3. **Fiscalización Laboral y Control de Jornada (Ley N.º 30224):**
   * **Acción:** Se forzó la asignación de una secuencia de entregas con un tiempo estimado de trayecto y servicio de 8 horas y 45 minutos a un mismo conductor.
   * **Resultado A (Bloqueo):** Al presionar "Confirmar y Asignar Ruta", la plataforma rechazó la transacción devolviendo una alerta de la API (`422 Unprocessable Entity`): *"Error de Validación Legal: La ruta excede el límite de 8 horas laborales diarias estipulado en la Ley N.º 30224"*.
   * **Resultado B (Aprobación con descanso):** Se reajustó la carga a 6 horas y 30 minutos de itinerancia. El sistema aprobó la ruta insertando automáticamente un bloque de 60 minutos etiquetado como *"Pausa Obligatoria de Descanso"* tras las primeras 4 horas de recorrido, pasando los pedidos de estado `PENDIENTE` a `ASIGNADO`.

---

## Pendientes

En estricta alineación con el estado real del proyecto y la transparencia del backlog, se detallan las historias de usuario y enablers que quedaron diferidos o en estado parcial al cierre del Sprint 3:

* **US-010: Algoritmo de Optimización Avanzado VRPTW + Green VRP (13 SP - Entregado Parcialmente)**
  * **Estado Real:** Se entregó e integró la versión base del motor (*Vecino Más Cercano*) para permitir la generación y persistencia de rutas en estado `BORRADOR`.
  * **Pendiente para Sprint 4:** Integración completa de la metaheurística basada en **Algoritmo Genético (librería DEAP)** para resolver la instancia masiva de $150 \text{ pedidos} \times 15 \text{ vehículos}$, asegurando la optimización cruzada de ventanas de tiempo y emisiones de $\text{CO}_2$.

* **ENB-001: SLA y Rendimiento del Motor de Ruteo ($\le 45\text{ s}$) (13 SP - Entregado Parcialmente)**
  * **Estado Real:** Implementación del mecanismo de corte de tiempo por tiempo máximo (*timeout*) ejecutado a nivel local.
  * **Pendiente para Sprint 4:** Certificación del SLA de tiempo de respuesta ($\le 45\text{ segundos}$ P95) sobre el entorno formal de Staging mediante pruebas de rendimiento automatizadas con Locust/JMeter.

* **US-012: Visualización Geoespacial en Mapa Interactivo Leaflet / OSM (8 SP - No Iniciado)**
  * **Pendiente para Sprint 4:** Construcción del visualizador en frontend con React-Leaflet, trazado de capas de ruta codificadas por colores según nivel de congestión (verde/amarillo/rojo) y marcaje de zonas de riesgo en Lima Este.

* **US-014: Dashboard de Métricas Sostenibles y Operativas (8 SP - No Iniciado)**
  * **Pendiente para Sprint 4:** Implementación del tablero principal de indicadores con gráficos interactivos que consoliden: consumo de combustible (litros), emisiones de $\text{CO}_2$ (kg), soles economizados vs. línea base tradicional y equivalencia en árboles requeridos.
