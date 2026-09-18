[← Volver al README Principal](../../README.md)

# UNIVERSIDAD CONTINENTAL
## Taller de Proyectos 2 — Escuela Profesional de Ingeniería de Sistemas e Informática

# 03. Registro de Riesgos del Proyecto

**Nombre del Proyecto:** EcoLogística Lima – Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Fecha:** 18/09/2026  
**Versión:** 1.0.3  
**Project Manager:** Carhuapoma Fano, Eilene Elizabeth  
**Estándar:** PMBOK 8ª Edición / CMMI-DEV (Gestión de Riesgos)

---

## 1. Propósito

Este registro consolida la línea base de gestión de riesgos del PFA. Cada amenaza se evalúa de forma cuantitativa, se clasifica por severidad y cuenta con un plan preventivo (mitigación) y un plan reactivo (contingencia), de modo que el equipo pueda actuar antes y después de la materialización del evento.

El análisis parte de los riesgos macro del [Acta de Constitución](../01%20Inicio/02.%20Acta%20de%20constituci%C3%B3n%20V_1_0_1.md), de las restricciones del [documento 13](../01%20Inicio/13.%20Restricciones%20V_1_0_1.md) y de los supuestos del [documento 04](../01%20Inicio/04.%20Registro%20de%20supuestos%20y%20restricciones%20V_1_0_1.md).

---

## 2. Criterios de Evaluación

**Fórmula de exposición:**

`Severidad (Exposición) = Probabilidad (1 a 5) × Impacto (1 a 5)`

| Dimensión | Escala |
|---|---|
| **Probabilidad** | 1 = Muy baja · 2 = Baja · 3 = Media · 4 = Alta · 5 = Muy alta |
| **Impacto** | 1 = Insignificante · 2 = Menor · 3 = Moderado · 4 = Mayor · 5 = Catastrófico |
| **Severidad** | **Low (1–6)** · **Medium (8–12)** · **High (15–25)** |

> No existen productos 7, 11, 13 ni 14 en la escala 1–5. Los umbrales 1–6 / 8–12 / 15–25 coinciden con la consigna.

### 2.1 Matriz de calor Probabilidad × Impacto

| P \ I | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| **5** | 5 L | 10 M | 15 H | 20 H | 25 H |
| **4** | 4 L | 8 M | 12 M | 16 H | 20 H |
| **3** | 3 L | 6 L | 9 M | 12 M | 15 H |
| **2** | 2 L | 4 L | 6 L | 8 M | 10 M |
| **1** | 1 L | 2 L | 3 L | 4 L | 5 L |

### 2.2 Umbral de escalamiento

| Severidad | Tratamiento |
|---|---|
| High (15–25) | Revisión semanal en Daily/Sprint Review. El PM escala al docente si el plan de mitigación no reduce la exposición en un sprint. |
| Medium (8–12) | Seguimiento quincenal en Sprint Planning. Dueño del riesgo reporta estado en la retrospectiva. |
| Low (1–6) | Monitoreo pasivo. Se reevalúa solo si cambia el contexto. |

---

## 3. Matriz de Evaluación de Riesgos

| ID | Descripción del Riesgo | Categoría | Prob. | Imp. | Severidad | Plan de Mitigación (Preventivo) | Plan de Contingencia (Reactivo) |
|---|---|---|---|---|---|---|---|
| RSK-01 | Indisponibilidad de servicios Cloud en el proveedor por límites de cuota (CPU del worker de optimización, conexiones a PostgreSQL o almacenamiento de reportes PDF). | Técnica / Infraestructura | 2 | 4 | **8 (Medium)** | Monitorear consumo de cuotas e implementar alertas de umbral al 70%. Dimensionar instancias con margen y definir topes en Railway/Render/AWS. | Migrar temporalmente los contenedores a una cuenta secundaria de respaldo o degradar a modo de cálculo local en el entorno de Staging. |
| RSK-02 | Curva de aprendizaje elevada en el framework del frontend (React + TypeScript + Vite) y en la integración con Leaflet, que retrasa las historias de mapa y modo conductor. | Recursos Humanos / Capacidades | 3 | 3 | **9 (Medium)** | Realizar 2 jornadas de *Pair Programming* y pases de conocimiento al inicio del Sprint 1. Acotar el alcance de UI a componentes reutilizables. | Reasignar las tareas de mayor complejidad a Axel (Full-Stack) y dejar a Katheryn las vistas de menor acoplamiento (formularios CRUD). |
| RSK-03 | El motor VRPTW + Green VRP no alcanza el SLA de ≤ 45 s para 150 pedidos y 15 vehículos (RNF-001 / RN-014), bloqueando la aceptación de RF-003. | Técnica / Algoritmos | 3 | 5 | **15 (High)** | Diseño incremental: heurística constructiva (Sweep/NN) en Sprint 3, metaheurística (GA/Tabú) en Sprints 4–5, profiling con datasets de 50/100/150 pedidos. | Entregar una solución factible subóptima (desviación ≤ 15% según RNF-008) y documentar el *trade-off*; relajar el tamaño del escenario de demo a 80 pedidos si el docente lo autoriza. |
| RSK-04 | APIs de tráfico (Waze CCP / Google Maps) inestables o sin cobertura suficiente en vías periféricas de San Juan de Lurigancho (supuesto S-01). | Técnica / Integración externa | 4 | 3 | **12 (Medium)** | Implementar desde Sprint 3 un conector con *fallback* a carga manual de congestión y a tiles OSM. No acoplar el algoritmo a un único proveedor. | Operar con matriz de tiempos estática + overlay manual de incidentes; registrar el degradado en el dashboard para no ocultar la pérdida de precisión. |
| RSK-05 | Incumplimiento del cronograma de 12.4 semanas (6 sprints + cierre) por carga académica simultánea del equipo (restricción C-02 / RES-T4). | Cronograma / Organizacional | 4 | 4 | **16 (High)** | Rituales Scrum de 2 semanas, WIP limitado a 3 ítems *In Progress*, sin holgura de un sprint completo (velocidad exacta 26 SP/sprint): cualquier desviación activa recorte MoSCoW desde el Sprint 4. Dedicaciones semanales declaradas en Jira. | Recortar el alcance del MVP al 70% de RF de prioridad Alta (objetivo SMART del Acta): diferir RF-006, RF-009 y RF-010 al *Won't have* del MoSCoW antes de entrar al Sprint 6. |
| RSK-06 | Fallas de integración entre flota, pedidos, ruteo y mapa (contratos API inconsistentes, estados de pedido desalineados). | Técnica / Integración | 3 | 3 | **9 (Medium)** | Contrato OpenAPI desde Sprint 1; integración continua (GitHub Actions) y pruebas de contrato en cada PR. | Congelar el contrato de la API, abrir un *spike* de 8 h y rehacer el *adapter* del mapa sobre la vista tabular de respaldo (RF-004 ruta infeliz). |
| RSK-07 | Direcciones no estandarizadas y geocodificación débil en SJL, El Agustino, Santa Anita y Ate (supuesto S-03 / RES-CS2). | Datos / Operativa | 4 | 3 | **12 (Medium)** | Campo obligatorio de punto de referencia + coordenadas; bandera de “georreferencia aproximada”; dataset sintético validado por el analista de datos. | Permitir pin manual en el mapa y excluir del cálculo los pedidos sin coordenada válida, notificándolos al Operador. |
| RSK-08 | Incumplimiento de la Ley N.º 29733 (datos personales de conductores y clientes) o aparición de vulnerabilidades OWASP Top 10. | Normativa / Seguridad | 2 | 5 | **10 (Medium)** | Consentimiento explícito (RN-020), JWT + bloqueo de 3 intentos (RN-019), TLS 1.3, checklist OWASP en el DoD, CodeQL/SonarQube en CI. | Aislar el ambiente, rotar secretos, desactivar el módulo afectado y notificar al docente/auditor. No promover a Staging hasta cerrar el hallazgo crítico. |
| RSK-09 | La re-optimización dinámica supera los 30 s o invalida rutas en ejecución cuando ocurren pedidos nuevos, cancelaciones o averías (RF-007 / RNF-001). | Técnica / Rendimiento | 3 | 4 | **12 (Medium)** | Re-optimizar solo las rutas afectadas (RN-015); ejecutar el motor en worker separado (Redis/cola) para no bloquear la API. | Conservar la ruta previa, marcar el evento como “revisión manual” y notificar al Operador y al conductor, cumpliendo la ruta infeliz de RF-007. |
| RSK-10 | El modo conductor no cumple el presupuesto de datos (≤ 150 KB) ni el tiempo de carga en 2G/3G (RNF-009 / RNF-005). | Técnica / UX | 3 | 3 | **9 (Medium)** | Diseño *mobile-first* con iconos, tiles de mapa diferidos y payload mínimo; prueba en throttling 3G desde Sprint 5. | Desactivar el mapa en modo degradado y mostrar solo la secuencia tabular de entregas (mismo respaldo que RF-004). |
| RSK-11 | Baja adopción de Jira (épicas sin descomponer, Story Points no actualizados, tablero desactualizado) que degrada la trazabilidad CMMI/PMBOK. | Proceso / ALM | 2 | 2 | **4 (Low)** | El PM es administrador del tablero; Definition of Ready exige enlace US ↔ RF/RNF; revisión del tablero en cada Daily. | El PM reconstruye el Sprint Board al cierre del día y registra una no conformidad menor en la retrospectiva. |
| RSK-12 | *Scope creep* por funcionalidades fuera del MVP (notificaciones SMS masivas, app nativa, GPU en la nube, Google Maps de pago). | Alcance | 3 | 4 | **12 (Medium)** | MoSCoW congelado en este documento y en Jira; cambios solo vía control de versión semántica de los artefactos de Inicio. | Rechazar el cambio o sustituir una historia de prioridad Media ya planificada, actualizando Roadmap y Release `v1.0.0-MVP`. |
| RSK-13 | Complejidad de PostGIS (zonas de riesgo y reservas ecológicas) retrasa RF-004 / RN-012 / RN-013. | Técnica / Datos | 3 | 3 | **9 (Medium)** | Brayan prototipa `zona_restriccion` con GIST en Sprint 2; el algoritmo consume un flag booleano, no geometría cruda, en la primera versión. | Usar polígonos *bounding box* simplificados o una lista de distritos vetados hasta completar PostGIS en Sprint 6. |
| RSK-14 | Dependencia de un único integrante en el motor de optimización (Jorge) o en el modelo de datos (Brayan). | Recursos Humanos / Conocimiento | 3 | 4 | **12 (Medium)** | *Pair programming* semanal, README técnico del motor y sesiones de 60 min de transferencia. Código y tests en el repositorio desde el primer commit útil. | Reasignar el *spike* al Full-Stack (Axel) con la heurística constructiva ya documentada; el Architect queda como revisor, no como único ejecutor. |

---

## 4. Resumen de Exposición

| Severidad | IDs | Cantidad | % |
|---|---|---|---|
| High (15–25) | RSK-03, RSK-05 | 2 | 14 % |
| Medium (8–12) | RSK-01, RSK-02, RSK-04, RSK-06, RSK-07, RSK-08, RSK-09, RSK-10, RSK-12, RSK-13, RSK-14 | 11 | 79 % |
| Low (1–6) | RSK-11 | 1 | 7 % |
| **Total** | | **14** | **100 %** |

**Exposición agregada (suma de P×I):** 2×4 + 3×3 + 3×5 + 4×3 + 4×4 + 3×3 + 4×3 + 2×5 + 3×4 + 3×3 + 2×2 + 3×4 + 3×3 + 3×4 = **149**  
**Exposición media por riesgo:** 149 / 14 ≈ **10.6 (Medium)**

Los dos riesgos High (algoritmo y cronograma académico) condicionan la estrategia híbrida ya elegida en el documento 01: *spike* temprano del motor y sprints cortos con recorte MoSCoW predefinido y **sin sprint de colchón**, por lo que la vigilancia semanal de RSK-05 es crítica desde el Sprint 3.

---

## 5. Mapa de Calor de Riesgos

Mapa **5 × 5** alineado a la sección 3. Cada celda se colorea por la banda de `P × I` (🟢 Low 1–6, 🟡 Medium 8–12, 🔴 High 15–25). Los identificadores se colocan en la celda de su probabilidad (filas) y su impacto (columnas).

No hay riesgos con probabilidad 1 ni 5; esas filas quedan vacías de IDs, pero conservan el color de su banda.

| P \ I | 1 Insignificante | 2 Menor | 3 Moderado | 4 Mayor | 5 Catastrófico |
|---|---|---|---|---|---|
| **5 Muy alta** | 🟢 5 | 🟡 10 | 🔴 15 | 🔴 20 | 🔴 25 |
| **4 Alta** | 🟢 4 | 🟡 8 | 🟡 12<br>RSK-04<br>RSK-07 | 🔴 **16 RSK-05** | 🔴 20 |
| **3 Media** | 🟢 3 | 🟢 6 | 🟡 9<br>RSK-02<br>RSK-06<br>RSK-10<br>RSK-13 | 🟡 12<br>RSK-09<br>RSK-12<br>RSK-14 | 🔴 **15 RSK-03** |
| **2 Baja** | 🟢 2 | 🟢 **4 RSK-11** | 🟢 6 | 🟡 **8 RSK-01** | 🟡 **10 RSK-08** |
| **1 Muy baja** | 🟢 1 | 🟢 2 | 🟢 3 | 🟢 4 | 🟢 5 |

**Lectura:** RSK-05 (cronograma) y RSK-03 (algoritmo) son los únicos High. RSK-08 tiene impacto catastrófico, pero probabilidad baja, por eso permanece Medium. RSK-11 es el único Low.

---

## 6. Trazabilidad con la Línea Base de Inicio

| Riesgo | Origen en Fase 01 | RF / RNF / RN relacionados |
|---|---|---|
| RSK-01 | Nueva (infraestructura del stack) | RNF-006 |
| RSK-02 | Nueva (capacidades del equipo) | RF-004, RF-005, RNF-003 |
| RSK-03 | R-01 del Acta | RF-003, RNF-001, RN-014 |
| RSK-04 | R-02 del Acta / S-01 | RF-003, RF-007 |
| RSK-05 | R-03 del Acta / C-02 | Objetivo SMART de cronograma |
| RSK-06 | R-04 del Acta | RF-001 a RF-007 |
| RSK-07 | R-05 del Acta / S-03 | RF-002, RN-005 |
| RSK-08 | R-06 del Acta / C-05 | RNF-002, RNF-010, RN-019, RN-020 |
| RSK-09 | RNF-001 / RN-015 | RF-007 |
| RSK-10 | C-07 / RNF-009 | RF-005 (modo conductor) |
| RSK-11 | Nueva (ALM de esta fase) | DoD global |
| RSK-12 | Estabilidad de alcance (documento 01) | RF-001 a RF-010 |
| RSK-13 | Documento 11 (PostGIS) | RN-012, RN-013, RF-004 |
| RSK-14 | Dedicaciones del documento 01 | ENB-001, documento 11 |

---

## 7. Reserva para Imprevistos

La exposición media Medium justifica una **reserva de contingencia del 12 %** sobre el subtotal de proyecto, coherente con la consigna de presupuesto y con los dos riesgos High. El uso de esta reserva requiere autorización del PM y registro en el historial de control de cambios.

Detalle monetario: [04 Presupuesto del proyecto V_1_0_1.md](./04%20Presupuesto%20del%20proyecto%20V_1_0_1.md).

---

## 8. Historial de Control de Cambios

| Versión | Fecha | Autor | Descripción |
|---|---|---|---|
| 1.0.0 | 11/09/2026 | Equipo EcoLogística Lima | Creación del registro cuantitativo de 14 riesgos, matriz P×I y planes de mitigación/contingencia. |
| 1.0.1 | 11/09/2026 | Equipo EcoLogística Lima | Roadmap y Release recalculados a 6 sprints (02/09–24/11/2026), release 27/11/2026 en vez de 14/12/2026. |
| 1.0.2 | 18/09/2026 | Equipo EcoLogística Lima | Corrección del mapa de calor para renderizado en GitHub y matriz P×I con los 14 riesgos. |
| 1.0.3 | 18/09/2026 | Equipo EcoLogística Lima | Mapa de calor 5×5 con bandas de color, se elimina el quadrantChart 2×2 y se corrigen enlaces a la Fase 01 / presupuesto vigentes. |

---

[← Volver al README Principal](../../README.md)
