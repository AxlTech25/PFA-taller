[← Volver al README Principal](../../README.md)

# UNIVERSIDAD CONTINENTAL
## Taller de Proyectos 2 — Escuela Profesional de Ingeniería de Sistemas e Informática

# 04. Presupuesto del Proyecto

**Nombre del Proyecto:** EcoLogística Lima – Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Fecha:** 11/09/2026  
**Versión:** 1.0.1  
**Project Manager:** Carhuapoma Fano, Eilene Elizabeth  
**Moneda de costeo:** USD  
**Tipo de cambio de referencia:** S/ 3.70 por USD (setiembre 2026)  
**Horizonte:** 12.4 semanas (6 sprints + 3 días de cierre), 02/09/2026 – 27/11/2026, equivalente a 3 meses calendario de facturación.

---

## 1. Propósito y premisas

Este documento modela el costo integral del PFA según la consigna de planificación: recursos humanos (CAPEX de ejecución), licenciamiento y herramientas, infraestructura cloud (OPEX) y reserva de contingencia derivada del [registro de riesgos](./03%20Registro%20de%20riesgos%20V_1_0_0.md).

### 1.1 Premisas de costeo

| Premisa | Valor | Fuente |
|---|---|---|
| Duración del MVP | 12.4 semanas / 6 sprints + cierre | Acta de Constitución (corregida) |
| Costeo de RR. HH. | Equivalencia profesional de 40 h/semana × 12.4 semanas por integrante (≈2,485 h) | Simulación comercial del PFA |
| Jira | Cloud Standard, 5 usuarios, 3 meses | Consigna ALM |

El costeo profesional (40 h/semana) representa el **valor de mercado de entregar el MVP**, no las horas académicas disponibles. La capacidad real de sprint se gestiona en Jira con las dedicaciones del documento 01.

---

## 2. Costo de Recursos Humanos (CAPEX)

**Fórmula:** `Costo = Horas asignadas × Tarifa hora (USD)`

Mapeo de roles de la consigna hacia el equipo:

| Rol de consigna | Integrante | Lógica de asignación |
|---|---|---|
| Project Manager | Carhuapoma Fano, Eilene Elizabeth | Liderazgo, Jira, interesados, control de cambios |
| Software Architect | Cruz Salazar, Jorge Luiz | Arquitectura C4 + motor VRPTW/Green VRP |
| Senior Developer | Estrada Flores, Axel Sebastian (70 %) | Backend FastAPI, integración, CI |
| QA Engineer | Estrada Flores, Axel Sebastian (30 %) | Estrategia de pruebas, BDD, aceptación |
| UI/UX Designer | Huaman Baldeon, Katheryn Elena (36 %) | Modo conductor, WCAG 2.1 AA, mockups Figma |
| Junior Developer | Huaman Baldeon, Katheryn Elena (64 %) + Leon Taza, Brayan Angel | Frontend React y modelo de datos / PostGIS |

| Rol | Responsable | Horas | Tarifa (USD/h) | Costo (USD) | Costo (PEN) |
|---|---|---|---|---|---|
| Project Manager | Carhuapoma Fano, Eilene Elizabeth | 497 | 37.00 | 18,389.00 | 68,039.30 |
| Software Architect | Cruz Salazar, Jorge Luiz | 497 | 42.00 | 20,874.00 | 77,233.80 |
| Senior Developer | Estrada Flores, Axel Sebastian | 355 | 33.00 | 11,715.00 | 43,345.50 |
| QA Engineer | Estrada Flores, Axel Sebastian | 142 | 28.00 | 3,976.00 | 14,711.20 |
| UI/UX Designer | Huaman Baldeon, Katheryn Elena | 177 | 30.00 | 5,310.00 | 19,647.00 |
| Junior Developer (Frontend) | Huaman Baldeon, Katheryn Elena | 320 | 23.00 | 7,360.00 | 27,232.00 |
| Junior Developer (Datos) | Leon Taza, Brayan Angel | 497 | 21.00 | 10,437.00 | 38,616.90 |
| **Total RR. HH.** | | **2,485** | | **78,061.00** | **288,825.70** |

Tarifa media ponderada: USD 87,960 / 2,800 h = **USD 31.41/h** (≈ S/ 116/h), alineada a tarifas locales de un equipo mixto junior–senior en Lima para un proyecto de  12.4 semanas.

Control: el Acta reservó S/ 325,000 para RR. HH. Este desglose cierra en S/ 288,825.70 (**-11.1 %**), dentro de la holgura por la reducción de 14 a 12.4 semanas.

---

## 3. Costo de Licenciamiento y Herramientas

| Ítem | Base de cálculo (3 meses) | USD | PEN |
|---|---|---|---|
| Jira Software Cloud Standard | 5 usuarios × USD 9.05 × 3 | 135.75 | 502.28 |
| Figma Professional | 2 editores × USD 20.00 × 3 | 120.00 | 444.00 |
| JetBrains All Products (IDE) | 5 puestos × USD 25.00 × 3 | 375.00 | 1,387.50 |
| GitHub Team | 5 usuarios × USD 4.00 × 3 | 60.00 | 222.00 |
| SonarCloud (análisis estático) | USD 10.00 × 3 | 30.00 | 111.00 |
| Docker Hub Pro | USD 11.00 × 3 | 33.00 | 122.10 |
| Dominio y DNS | 1 año prorrateado al PFA | 15.00 | 55.50 |
| **Subtotal software** | | **768.75** | **2,844.38** |
| Estaciones de trabajo del laboratorio | 5 laptops × USD 800.00 | 4,000.00 | 14,800.00 |
| **Total licenciamiento y herramientas** | | **4,768.75** | **17,644.38** |

No se presupuestan licencias de Google Maps ni de solvers propietarios: el stack del documento 10 usa Leaflet/OpenStreetMap, FastAPI, PostgreSQL y DEAP/OR-Tools. VS Code y GitHub Actions permanecen en el plan gratuito como respaldo si se desactiva GitHub Team.

---

## 4. Infraestructura Cloud y Servicios (OPEX)

Dimensionada para cumplir RNF-001 (worker de optimización), RNF-006 (disponibilidad ≥ 99.5 % en horario 05:00–22:00) y el almacenamiento de reportes PDF.

| Servicio | Especificación | USD/mes | 3 meses (USD) | 3 meses (PEN) |
|---|---|---|---|---|
| Compute API + SPA | Lightsail 4 GB / 2 vCPU | 40.00 | 120.00 | 444.00 |
| Worker de optimización | Lightsail 8 GB / 4 vCPU | 80.00 | 240.00 | 888.00 |
| Staging | Lightsail 2 GB | 20.00 | 60.00 | 222.00 |
| PostgreSQL + PostGIS gestionado | 2 GB RAM, backups diarios | 60.00 | 180.00 | 666.00 |
| Redis (sesiones y cola) | 1 GB | 15.00 | 45.00 | 166.50 |
| Object storage + CDN | Reportes PDF y estáticos | 25.00 | 75.00 | 277.50 |
| Snapshots y backups | Retención 14 días | 20.00 | 60.00 | 222.00 |
| Observabilidad | Logs y métricas | 18.00 | 54.00 | 199.80 |
| Tráfico, DNS y TLS | Let's Encrypt + egress | 12.00 | 36.00 | 133.20 |
| Cómputo extra (picos GA/ACO) | Burst del worker | 35.00 | 105.00 | 388.50 |
| **Total Cloud / OPEX** | | **325.00** | **975.00** | **3,607.50** |

Certificados SSL: USD 0 (Let's Encrypt). CI/CD: GitHub Actions incluido en la línea de GitHub Team. No se incluye GPU: el motor corre en CPU, coherente con C-03 y con RSK-01.

---

## 5. Reserva de Contingencia (Imprevistos)

La exposición media del registro de riesgos es **10.6 (Medium)**, con dos riesgos High (RSK-03 algoritmo y RSK-05 cronograma). Se aplica el **12 %** sugerido por la consigna sobre el subtotal.

`Reserva = 0.12 × (RR. HH. + Licencias + Cloud) = 0.12 × 83,804.75 = 10,056.57 USD``

Uso de la reserva: solo con autorización del PM y registro en el historial de control de cambios. Prioridad de consumo: RSK-03 (cómputo extra del motor) y RSK-01 (migración de nube).

---

## 6. Tabla Resumen Financiera

| Categoría | Costo Subtotal (USD) | Costo (PEN) | Porcentaje del Subtotal |
|---|---|---|---|
| 1. Recursos Humanos (CAPEX) | $ 78,061.00 | S/ 288,825.70 | 93.2 % |
| 2. Licenciamiento de Software | $ 4,768.75 | S/ 17,644.38 | 5.7 % |
| 3. Infraestructura Cloud (OPEX) | $ 975.00 | S/ 3,607.50 | 1.2 % |
| **SUBTOTAL DE PROYECTO** | **$ 83,804.75** | **S/ 310,077.58** | **100.0 %** |
| 4. Reserva de Contingencia (12 %) | $ 10,056.57 | S/ 37,209.31 | N/A |
| **PRESUPUESTO TOTAL ESTIMADO** | **$ 93,861.32** | **S/ 347,286.89** | **100.0 %** |

### 6.1 Reconciliación con el Acta de Constitución

| Concepto | PEN | USD |
|---|---|---|
| Techo autorizado (C-01 / Acta) | S/ 500,000.00 | $ 135,135.14 |
| Línea base de ejecución (este documento) | S/ 347,286.89 | $ 93,861.32 |
| Holgura de gestión | S/ 152,713.11 | $ 41,273.82 |
| Uso del techo | 69.5 % | 69.5 % |

---

## 7. Justificación frente al alcance del PFA

El presupuesto se sostiene en el alcance congelado del MVP (RF-001 a RF-010, RNF-001 a RNF-010) y en estas decisiones de costo:

1. **RR. HH. es el 93.3 % del subtotal.** Es coherente con un producto de software: el valor está en diseño de algoritmo, API, datos geoespaciales y UX inclusiva, no en licencias.
2. **Open source obligatorio (C-03)** mantiene Cloud + software por debajo del 7 % del subtotal. Leaflet/OSM evita la partida de Google Maps API, que en 150 pedidos/día × 15 vehículos podría superar el OPEX aquí presupuestado.
3. **Laboratorio de 5 estaciones (USD 4,000)** se carga al PFA porque el Acta contemplaba Hardware/Software (S/ 50,000). Aquí se compra solo lo necesario; el resto del techo queda como holgura.
4. **Contingencia 12 %** está trazada a la exposición cuantitativa de riesgos, no es un porcentaje decorativo.
5. **No se duplica el costo académico y el profesional.** Las 1 204 h de dedicación real gobiernan el *sprint capacity*; las 2 800 h tarifadas gobiernan el valor económico del entregable.

### 7.1 Distribución visual

​```mermaid
pie showData
    title Composición del subtotal (USD 83,805)
    "RR. HH. CAPEX" : 78061
    "Licencias y herramientas" : 4769
    "Cloud OPEX" : 975
​```

---

## 8. Flujo trimestral de caja (referencia)

| Mes | RR. HH. | Licencias (prorrateo) | Cloud | Total mes |
|---|---|---|---|---|
| Mes 1 – Septiembre (Sprints 1–2) | 26,020.00 | 4,256.25 | 325.00 | 30,601.25 |
| Mes 2 – Octubre (Sprints 3–4) | 26,020.00 | 256.25 | 325.00 | 26,601.25 |
| Mes 3 – Noviembre + cierre (Sprints 5–6) | 26,021.00 | 256.25 | 325.00 | 26,602.25 |
| **Suma 3 meses** | **78,061.00** | **4,768.75** | **975.00** | **83,804.75** |

La reserva de USD 10,056.57 no se calendariza: permanece retenida hasta que un riesgo High o Medium se materialice.

---

## 9. Historial de Control de Cambios

| Versión | Fecha | Autor | Descripción |
|---|---|---|---|
| 1.0.0 | 11/09/2026 | Equipo EcoLogística Lima | Línea base de ejecución USD 105,593.60 (S/ 390,696.32), contingencia 12 %, reconciliación con techo del Acta S/ 500,000. |

| Versión | Fecha | Autor | Descripción |
|---|---|---|---|
| 1.0.0 | 11/09/2026 | Equipo EcoLogística Lima | Línea base de ejecución USD 105,593.60 (S/ 390,696.32), contingencia 12 %, reconciliación con techo del Acta S/ 500,000. |
| 1.0.1 (corrección) | 11/09/2026 | Equipo EcoLogística Lima | Cronograma corregido a 6 sprints + 3 días de cierre (02/09/2026 – 27/11/2026, 12.4 semanas en vez de 14). Recalculado el presupuesto completo: RR. HH. USD 78,061.00, Licencias USD 4,768.75, Cloud USD 975.00, Contingencia (12%) USD 10,056.57. Nueva línea base de ejecución: **USD 93,861.32 (S/ 347,286.89)**, uso del techo del Acta 69.5 % (antes 78.1 %). |
---

[← Volver al README Principal](../../README.md)
