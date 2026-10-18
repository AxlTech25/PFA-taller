[← Volver al README Principal](../../../README.md)

# Informe de estado del proyecto

**Nombre del Proyecto:** EcoLogística Lima – Optimizador de Rutas Sostenibles para DistriRápido S.A.C.

**Líder del Proyecto:** Carhuapoma Fano, Eilene Elizabeth

**Fecha:** 18/10/2026

**Periodo del Informe:** 30/10/2026 – 12/11/2026 (Sprint 4; software el 18/10/2026, antes de abrir la ventana)

**Versión:** 1.3.0

Este archivo usa el nombre `V_1_0_0.md` que pide la consigna. Vive en `docs/03 Implementación/Sprint 4/`. El encabezado registra **1.3.0**. El Sprint 3 está en [`../Sprint 3/`](../Sprint%203/).

---

### **Estado del proyecto**

| Variables de control | Descripción del estado |
| --- | --- |
| **Alcance** | Se cierra en código la continuación de **ENB-001 / US-010**: algoritmo genético VRPTW + Green VRP con DEAP, en el worker, comparado con el vecino más cercano del Sprint 3. El escenario de 150 pedidos y 15 vehículos queda factible y bajo el presupuesto de 45 s en la prueba de CI. **US-012** queda iniciada: mapa Leaflet/OSM con trazado, paradas, ETA por tramo y semáforo. El tablero de sostenibilidad queda **iniciado** (km, CO₂, combustible, soles, % de ventanas); US-014 no se cierra. IMP-04: Staging en Railway/Render **sigue pendiente**. |
| **Cronograma** | **Adelantado respecto de la ventana.** El Sprint 4 va del 30/10/2026 al 12/11/2026 (Hito 3 el 12/11/2026). El código se entrega el 18/10/2026 en el [PR #16](https://github.com/AxlTech25/PFA-taller/pull/16), todavía dentro del calendario del Sprint 3. El Hito 3 no se mueve. Hito 4 el 13/12/2026. |
| **Costos** | Línea base **S/ 13,000**. Cloud sigue en **S/ 0**: no hay Staging (IMP-04). Contingencia S/ 1,500 intacta. No se compra infraestructura nueva. DEAP y Leaflet son de código abierto. |
| **Calidad** | CI de producto: Ruff, Pytest con cobertura ≥ 80 % y build de Vite. CodeQL sigue en `.github/workflows/codeql.yml`. Pruebas nuevas del genético frente al vecino, del bench 150×15, del semáforo, del tablero vacío y del tablero con plan. |

Detalle (fuente: [01 Transformando a ágil V_1_0_6.md](../../02%20Planificaci%C3%B3n/01%20Transformando%20a%20%C3%A1gil%20V_1_0_6.md) §8 y §12):

| ID | Título | SP | Estado |
|---|---|---|---|
| ENB-001 | Motor metaheurístico con SLA | 13 (cierre del tramo) | Hecho en código: GA con DEAP, corte a 45 s, bench 150×15 factible. La corrida «en Staging» del Gherkin sigue abierta por IMP-04 |
| US-010 | Generar rutas VRPTW + Green VRP | 13 (cierre del tramo) | Hecho en código: plan en borrador, pico y placa, congestión, comparación con el vecino más cercano. El P95 estadístico en Staging no se mide |
| US-012 | Mapa Leaflet/OSM | 8 (inicio) | Inicio: trazado, paradas, ETA por tramo y semáforo verde/amarillo/rojo. El cierre (zonas, alternativa) es del Sprint 5 |
| US-014 | Dashboard de sostenibilidad | 8 | Solo iniciado, por el Hito 3. No está Done. Falta el período amplio y el factor de árboles |
| IMP-04 | Staging | — | **Sigue pendiente.** Tope 12/11/2026. No hay secreto de Railway/Render |
| IMP-11 | Polígonos oficiales | — | Sigue aceptado. No hay archivo del catastro INEI en el repositorio |

---

### **Riesgos**

| **Riesgo** | **Responsable** | **Mitigación** |
| --- | --- | --- |
| RSK-03 — El motor no cumple ≤ 45 s ni factibilidad en 150×15. | Cruz Salazar, Jorge Luiz | La prueba `test_bench_150_pedidos_15_vehiculos_en_45_segundos` arma 150 pedidos y 15 vehículos, exige factibilidad (capacidad, ventana, jornada, pico y placa) y un costo verde que no empeora al vecino más cercano. En esta máquina ocho corridas tardaron menos de 0,1 s. No sustituye el P95 en Staging. |
| RSK-05 — El Hito 3 pide motor, mapa y dashboard integrados. | Carhuapoma Fano, Eilene Elizabeth | Motor y mapa quedan integrados en Rutas. El tablero muestra los indicadores del último plan del día y el vacío del período. US-014 sigue abierta para el Sprint 5. |
| RSK-08 / IMP-04 — Sin URL de Staging no se cierra el DoD D4 ni la frase «en Staging» de ENB-001. | Estrada Flores, Axel Sebastian | No se inventan secretos ni una URL de demostración. Compose sigue siendo el ambiente reproducible. Tope 12/11/2026. |
| RSK-07 — Cobertura por envolventes, no catastro INEI (IMP-11). | Leon Taza, Brayan Angel | No había archivo oficial que sustituir. La validación sigue en PostGIS. |

---

### **Próximos avances**

Sprint 5 (13/11/2026 – 26/11/2026):

1. Cerrar US-012 y abrir US-013 (zonas de riesgo y reserva ecológica).
2. Cerrar US-014: período, y el factor `factor_captura_arbol_kg` cuando el docente lo ratifique (RN-018).
3. US-015 modo conductor, ENB-005 y ENB-008.
4. IMP-04 solo si aparecen credenciales de Railway o Render antes del 12/11/2026.

No se abre CRUD de clientes.

---

### **Notas**

- Función objetivo del Green VRP: soles de combustible (precio del galón de `configuracion_sistema` / 3,785411784 L, RN-017) + soles de mantenimiento (S/ 1,20/km) + kg de CO₂ (RN-016, peso 1 para desempatar hacia el vehículo más limpio). RN-011 suma S/ 50 por cada puesto después del primero en un pedido Exprés. No es un precio de carbono de mercado.
- El genético (DEAP, permutación, cruce ordenado, mutación y elitismo) parte del vecino más cercano y de un 2-opt por ruta de hasta 16 paradas. Si no mejora el costo, se conserva la línea base. El contrato sigue siendo `POST /optimizaciones` → 202 e `id_job`.
- En un cruce de cuatro paradas el genético baja el costo frente al vecino y queda a lo sumo 15 % por encima del óptimo enumerado (RNF-008 en ese escenario controlado). En la grilla regular de 150×15 el vecino ya es competitivo y el genético lo iguala.
- Mapa: Leaflet 1.9 y teselas de OpenStreetMap. El semáforo usa `factor_congestion` y la hora punta 07:00–09:00 y 17:00–20:00 sobre el reloj que ya guarda el ETA. Si las teselas fallan, la pantalla avisa y deja la tabla.
- Árboles: el documento 11 deja `factor_captura_arbol_kg` pendiente de ratificación. El tablero no inventa el número; muestra la nota de RN-018.
- Ambiente: `docker compose up --build` levanta Postgres (host **5433**), Redis, la API, el worker y la SPA. No hay Staging público.
- Artefactos: [Impedimentos](./02%20Registro%20de%20Impedimentos%20V_1_0_0.md) · [Revisión](./03%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md) · [Retrospectiva](./04%20Retrospectiva%20del%20Sprint%20V_1_0_0.md).

---

## Historial de control de cambios

| Versión | Fecha | Autor | Descripción |
|---|---|---|---|
| 1.0.0 | 02/10/2026 | Equipo EcoLogística Lima | Informe del Sprint 1. |
| 1.1.0 | 02/10/2026 | Equipo EcoLogística Lima | Informe del Sprint 2. |
| 1.2.0 | 17/10/2026 | Equipo EcoLogística Lima | Informe del Sprint 3. |
| 1.3.0 | 18/10/2026 | Equipo EcoLogística Lima | Informe del Sprint 4: genético, mapa iniciado y tablero iniciado. Staging sigue pendiente. |

---

[← Volver al README Principal](../../../README.md)
