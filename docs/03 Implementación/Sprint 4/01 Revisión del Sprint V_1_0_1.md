[← Volver al README principal](../../../README.md)

# Revisión del sprint

**Nombre del Proyecto:** EcoLogística Lima – Optimizador de Rutas Sostenibles para DistriRápido S.A.C.

**Líder del Proyecto:** Carhuapoma Fano, Eilene Elizabeth

**Sprint:** 4 (`ECO Sprint 4`, 30/10/2026 – 12/11/2026). Hito 3 el 12/11/2026. Revisión de cierre: 20/11/2026. Versión: 1.0.1.

---

## Historias de Usuario completadas en este Sprint

El compromiso del Sprint 4 fue **26 Story Points**: el algoritmo genético, el escenario de 150 pedidos y 15 vehículos, el inicio del mapa y el inicio del tablero. Las cuatro tarjetas están en **Done** en Jira y el código está en `main`. El motor, el mapa y el tablero entraron el 18/10/2026, antes de abrir la ventana; el Hito 3 se mantiene el 12/11/2026. Los pull requests posteriores cerraron el trazado por calles y la medición de Green IT.

Fuente del alcance: [01 Transformando a ágil](../../02%20Planificaci%C3%B3n/01%20Transformando%20a%20%C3%A1gil%20V_1_0_10.md) (§5 y §12), [02 Artefactos Jira](../../02%20Planificaci%C3%B3n/02%20Artefactos%20Jira%20V_1_0_10.md) (§5.3) y [05 Cronograma de sprints](../../02%20Planificaci%C3%B3n/05%20Cronograma%20de%20sprints%20V_1_0_5.md) (§4).

La sesión del 20/11/2026 se demostró en Docker Compose, en `http://localhost:5173` y `http://localhost:8000`. El entorno público de esta versión es producción: la interfaz en [https://ecologistica-lima-beige.vercel.app](https://ecologistica-lima-beige.vercel.app) y la API en [https://api-production-b8dfa3c0.up.railway.app](https://api-production-b8dfa3c0.up.railway.app). El detalle está en [Demostración del trabajo completado](#demostración-del-trabajo-completado).

| Tarjeta | Incremento | SP | Responsable | Estado |
| --- | --- | ---: | --- | --- |
| ECO-23 | **ENB-001 B** — AG DEAP, corte a 45 s | 5 | Cruz Salazar, Jorge Luiz | Done |
| ECO-24 | **US-010 B** — 150 pedidos / 15 vehículos factible | 8 | Cruz Salazar, Jorge Luiz | Done |
| ECO-25 | **US-012 A** — mapa Leaflet/OSM (trazado, paradas, ETA, semáforo) | 8 | Huaman Baldeon, Katheryn Elena | Done |
| ECO-27 | **US-014 A** — tablero (km, CO₂, combustible, soles, % de ventanas) | 5 | Huaman Baldeon, Katheryn Elena | Done |
| | **Total** | **26** | | |

### ENB-001 B — Motor metaheurístico con algoritmo genético DEAP (5 SP)

Como equipo de arquitectura, el worker ejecuta un algoritmo genético (DEAP) sobre VRPTW + Green VRP, con corte a 45 segundos, y devuelve una solución factible. Si no mejora el costo verde, conserva el plan del vecino más cercano y la API no se cuelga.

Criterios de aceptación del artefacto 01:

- **Bench 150×15.** Con un conjunto sintético de 150 pedidos y 15 vehículos, el P95 queda en ≤ 45 s y la solución no viola capacidad, ventanas ni pico y placa.
- **Timeout controlado.** Si el algoritmo no converge al llegar el presupuesto de tiempo, se devuelve la mejor solución factible o un error de dominio, sin colgar la API.

Verificación. El motor vive en `backend/app/optimizacion/metaheuristica.py`. DEAP minimiza el costo verde (`weights=(-1.0,)`). La población es 16 y baja a 8 cuando hay más de 40 pedidos; el tope es 40 generaciones y el estancamiento es 8. El presupuesto sale de `tiempo_max_optimizacion_s` (45 s, RN-014). La búsqueda parte del vecino más cercano, aplica 2-opt y no devuelve un plan peor. `test_bench_150_pedidos_15_vehiculos_en_45_segundos` arma 150 pedidos y 15 vehículos el lunes 02/11/2026, exige que esa corrida termine en ≤ 45 s, con cero pedidos sin asignar y con capacidad, jornada y ventanas respetadas, y con placas no restringidas ese día. Esa corrida es la evidencia automatizada del tope de 45 s que quedó en el repositorio. `test_el_genetico_mejora_el_cruce_y_queda_a_quince_por_ciento` comprueba que el genético baja el costo del cruce y queda a lo sumo un 15 % del óptimo enumerado, también dentro de los 45 s. El worker sigue fuera del request (`POST /optimizaciones` responde 202). El Quality Gate de CI es Ruff más `pytest --cov=app --cov-fail-under=80` en [`.github/workflows/ci.yml`](../../../.github/workflows/ci.yml). El último SonarQube publicado, commit [`aaa13b6`](https://github.com/AxlTech25/PFA-taller/commit/aaa13b6c4ad9457a0fc79566af48e722a5d23f2e) (27/10/2026, ya con este motor), midió 97,6 % de cobertura y Quality Gate PASSED. Los PR #21 a #28 no tienen otro informe de SonarQube en el repositorio.

Cierre: [PR #16](https://github.com/AxlTech25/PFA-taller/pull/16), merge [`14ea729e8ff4da593495ee2b2a604df54096ce3d`](https://github.com/AxlTech25/PFA-taller/commit/14ea729e8ff4da593495ee2b2a604df54096ce3d) (18/10/2026). Commit del motor: [`617139724d4301c9c0902318ecb3ed31cf7c7376`](https://github.com/AxlTech25/PFA-taller/commit/617139724d4301c9c0902318ecb3ed31cf7c7376).

### US-010 B — Generación de rutas VRPTW en 150 pedidos / 15 vehículos (8 SP)

Como Operador de Logística, generar rutas que reduzcan distancia, combustible, CO₂ y penalizaciones de ventana, y dejar un plan factible en menos de 45 segundos.

Criterios de aceptación del incremento B:

- **Solución factible a tiempo.** Con pedidos `PENDIENTE` y vehículos y conductores `ACTIVO`, la metaheurística devuelve rutas válidas en ≤ 45 s (P95, hasta 150 pedidos y 15 vehículos) y las deja en `BORRADOR`.
- **Pico y placa y tráfico.** Si aplica el D.S. N.º 033-2012-MTC o hay overlay de congestión, se excluyen los vehículos restringidos ese día y se ajustan los tiempos de viaje.
- **Sin factible.** Si no hay flota o se agota el tiempo, se notifica el fallo, se conserva el estado anterior y se sugiere agregar vehículos o relajar ventanas.

Verificación. El mismo bench de 150×15 deja el plan factible y el tiempo dentro de los 45 s. El semáforo de congestión (`VERDE`, `AMARILLO`, `ROJO`) está cubierto por `test_semaforo_de_congestion`. La restricción por último dígito está en `backend/app/optimizacion/pico_placa.py` (lunes 1–2, martes 3–4, miércoles 5–6, jueves 7–8, viernes 9–0; sábado y domingo no restringen). El plan persiste para el mapa. La comparación con el vecino más cercano viaja en el resultado del job y alimenta el tablero.

Cierre: el mismo [PR #16](https://github.com/AxlTech25/PFA-taller/pull/16) ([`14ea729e8ff4da593495ee2b2a604df54096ce3d`](https://github.com/AxlTech25/PFA-taller/commit/14ea729e8ff4da593495ee2b2a604df54096ce3d)).

### US-012 A — Mapa interactivo Leaflet / OSM (8 SP)

Como Operador o Gerente, ver la ruta sobre el mapa con ETA por parada y semáforo de congestión. El incremento A es el trazado, las paradas, el ETA y el semáforo, con vista tabular si fallan las teselas. Las zonas de riesgo y la ruta alternativa son US-013 (Sprint 5) y no entran en estos 8 SP.

Criterios de aceptación:

- **Render de ruta.** Si hay rutas generadas y el usuario elige una, el sistema dibuja el trazado, los puntos de entrega, el ETA por tramo y el nivel verde, amarillo o rojo.
- **Mapa no disponible.** Si las teselas de OpenStreetMap fallan, se muestra el error y la secuencia de entregas en tabla.

Verificación. Leaflet 1.9 dibuja el plan en `frontend/src/pages/MapaRutas.tsx`. El PR #16 unía las paradas en línea recta. El [PR #21](https://github.com/AxlTech25/PFA-taller/pull/21) pide la geometría a OSRM (`https://router.project-osrm.org`, o `VITE_OSRM_URL`), parte los recorridos largos en tramos de hasta 25 puntos y, si el servicio falla o tarda más de 8 segundos, vuelve a la línea recta. Un enlace punteado une el punto ajustado a la calle con la coordenada real de la parada. Si las teselas no cargan, el aviso es: «No se pudo cargar el mapa de OpenStreetMap. La secuencia de entregas sigue disponible en la tabla.» Lo cubren `frontend/src/mapa.test.ts` y `frontend/src/pages/MapaRutas.test.tsx` (geometría OSRM, línea recta de respaldo y caída a la tabla). `accesibilidad.test.tsx` revisa con axe-core la pantalla de rutas, el mapa y su alternativa textual. Las teselas se piden en PNG y sin la variante retina.

Cierre: [PR #16](https://github.com/AxlTech25/PFA-taller/pull/16) ([`14ea729e8ff4da593495ee2b2a604df54096ce3d`](https://github.com/AxlTech25/PFA-taller/commit/14ea729e8ff4da593495ee2b2a604df54096ce3d)) y [PR #21](https://github.com/AxlTech25/PFA-taller/pull/21) ([`79b454390cdc0e9f443967d4d04e0c7049f48b58`](https://github.com/AxlTech25/PFA-taller/commit/79b454390cdc0e9f443967d4d04e0c7049f48b58), 07/11/2026). El peso y el CLS de `/rutas` quedaron medidos en los PR #27 y #28 (tabla de Lighthouse más abajo).

### US-014 A — Dashboard de sostenibilidad (5 SP)

Como Gerente de Operaciones, consultar los números del último plan. El incremento A muestra kilómetros, kg de CO₂, combustible, soles y el porcentaje de ventanas. Si no hay operación, los valores van en cero con un mensaje. El equivalente en árboles es el incremento B (`factor_captura_arbol_kg`, RN-018) y no se inventa: `arboles` queda nulo.

Criterios de aceptación del incremento A, leídos sobre el alcance partido en el artefacto 01:

- **Dashboard con datos.** Con un Gerente u Operador autenticado y rutas del día, el tablero muestra km, kg de CO₂, litros, el porcentaje de ventanas y los soles. Los soles usan RN-017: S/ 17,50 por galón y S/ 1,20 por km.
- **Sin operación.** Si no hay rutas en el período, los valores se muestran en cero con el mensaje «Sin datos de operación para el período seleccionado».

Verificación. `GET /indicadores` agrega el último job `COMPLETADO` del día (`backend/app/services/indicadores.py`). `test_periodo_sin_rutas` exige ceros, el mensaje literal y `arboles` nulo con nota de RN-018. `test_indicadores_del_plan_y_conductor_sin_acceso` exige km, CO₂, litros y soles mayores que cero, cumplimiento de ventanas al 100 % en el plan de prueba, y 403 para el rol Conductor. En la interfaz, `DashboardPage.test.tsx` cubre las métricas del día y el período vacío. El [PR #25](https://github.com/AxlTech25/PFA-taller/pull/25) solo corrige la revisión del Sprint 3 para no dejar US-014 como pendiente de aquel sprint: el incremento A es de este Sprint 4.

Cierre de código del tablero: [PR #16](https://github.com/AxlTech25/PFA-taller/pull/16) ([`14ea729e8ff4da593495ee2b2a604df54096ce3d`](https://github.com/AxlTech25/PFA-taller/commit/14ea729e8ff4da593495ee2b2a604df54096ce3d)). Medición y aligeramiento de la pantalla `/dashboard`: PR #24, #26, #27 y #28, enlazados en la sección siguiente. Corrección documental: [PR #25](https://github.com/AxlTech25/PFA-taller/pull/25) ([`6dfb8a630b6638e3b2de408e22aef3ef14df2f7b`](https://github.com/AxlTech25/PFA-taller/commit/6dfb8a630b6638e3b2de408e22aef3ef14df2f7b)).

### Trabajo técnico en paralelo, sin Story Points

Estas entregas salieron de la retrospectiva del Sprint 3 y del arrastre de IMP-04. No suman al compromiso de 26 SP.

| Entrega | Qué quedó en `main` | PR y commit |
| --- | --- | --- |
| Auditoría de dependencias del frontend | `npm audit` reportaba 12 vulnerabilidades (3 críticas, 1 alta y 8 moderadas) en Vitest, `@vitest/coverage-v8`, Vite y React Router. Quedaron en 0 al subir a Vite 8, Vitest 5, `@vitejs/plugin-react` 6 y React Router 7. En `frontend/package.json` las versiones declaradas son `vite` ^8.3.6, `vitest` ^5.1.0, `@vitejs/plugin-react` ^6.2.1 y `react-router-dom` ^7.18.5. | [PR #22](https://github.com/AxlTech25/PFA-taller/pull/22) · [`0fd5fa230caa130ab84b4ebb444185e939353976`](https://github.com/AxlTech25/PFA-taller/commit/0fd5fa230caa130ab84b4ebb444185e939353976) (07/11/2026) |
| Preparación de Staging en Railway | `DATABASE_URL` acepta `postgres://` y `postgresql://`. `entrypoint.sh` toma `PORT` y `HOST`; con `PROCESO=worker` la misma imagen arranca el worker. `frontend/Dockerfile.prod` y el Caddyfile sirven la SPA y hacen de proxy de la API en el mismo origen. El README describe los cinco servicios (`db` PostGIS, Redis, `api`, `worker`, `web`). No se creó el proyecto en Railway y no hay dominio. | [PR #23](https://github.com/AxlTech25/PFA-taller/pull/23) · [`f9a079b7881fc5c6f24606963e07f701a2c0bd41`](https://github.com/AxlTech25/PFA-taller/commit/f9a079b7881fc5c6f24606963e07f701a2c0bd41) (07/11/2026) |
| Green IT y Lighthouse en las ocho pantallas | Consultas magras, página de 12, code splitting, caché, SVG en línea y mediciones SWDM v4. Lighthouse 13.6.0 deja performance 100 y CLS 0 en las ocho URL, `/rutas` incluida. | [PR #24](https://github.com/AxlTech25/PFA-taller/pull/24) · [PR #26](https://github.com/AxlTech25/PFA-taller/pull/26) · [PR #27](https://github.com/AxlTech25/PFA-taller/pull/27) · [PR #28](https://github.com/AxlTech25/PFA-taller/pull/28) |

Lighthouse 13.6.0 (`@lhci/cli@0.16.1`), preset de escritorio, caché fría, 13/11/2026, estado posterior al PR #28. Fuente: [informe de reducción del impacto ambiental](../reduccion%20del%20impacto%20ambiental/01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md), sección 1.8. El TBT es 0 ms en las ocho pantallas. El CLS de `/rutas` venía de 0,105814 (Lighthouse 12.1.0, antes) y de 0,038150 (después de reservar el alto del mapa); con Lighthouse 13.6.0 quedó en 0.

| Pantalla | Score | FCP (ms) | LCP (ms) | CLS | Peso (bytes) |
| --- | ---: | ---: | ---: | ---: | ---: |
| `/login` | 100 | 160,6824 | 370,0473 | 0 | 64 681 |
| `/dashboard` | 100 | 160,8621 | 416,5862 | 0 | 67 573 |
| `/flota` | 100 | 283,3689 | 454,7378 | 0 | 69 323 |
| `/conductores` | 100 | 160,8015 | 414,2062 | 0 | 68 343 |
| `/pedidos` | 100 | 160,6632 | 457,6526 | 0 | 70 590 |
| `/usuarios` | 100 | 160,7802 | 454,1210 | 0 | 68 688 |
| `/modo` | 100 | 160,6525 | 368,9575 | 0 | 65 705 |
| `/rutas` | 100 | 160,9660 | 537,8642 | 0 | 746 304 |

`lighthouserc.cjs` exige, en las ocho URL, performance ≥ 0,9, FCP ≤ 1,0 s, LCP ≤ 1,4 s, TBT ≤ 85 ms, CLS ≤ 0,02 y peso ≤ 1,1 MB. El flujo es [`.github/workflows/green-audit.yml`](../../../.github/workflows/green-audit.yml). Esas ocho cifras de escritorio cumplen el umbral. El preset móvil, medido solo en el estado posterior de `/login` el 12/11/2026 con Lighthouse 12.6.1, dio performance 100 y FCP 1 351,7659 ms: ese FCP no cumple 1,0 s. El informe toma el escritorio como medición de la consola de planificación.

Commits de Green IT en `main`:

- [PR #24](https://github.com/AxlTech25/PFA-taller/pull/24), merge [`60e0b79ee57d0f5e48d93686229ee06daeb97f08`](https://github.com/AxlTech25/PFA-taller/commit/60e0b79ee57d0f5e48d93686229ee06daeb97f08) (13/11/2026). Funcionalidad: [`e51600f5a1d61d0ddef1c45a18faefeee4c68749`](https://github.com/AxlTech25/PFA-taller/commit/e51600f5a1d61d0ddef1c45a18faefeee4c68749) (12/11/2026).
- [PR #26](https://github.com/AxlTech25/PFA-taller/pull/26), merge [`23291800657389e82396741e2424ba7a998cfcce`](https://github.com/AxlTech25/PFA-taller/commit/23291800657389e82396741e2424ba7a998cfcce) (13/11/2026).
- [PR #27](https://github.com/AxlTech25/PFA-taller/pull/27), merge [`693cb4b195ff466e0cb7e48fae11c35dd52d40fb`](https://github.com/AxlTech25/PFA-taller/commit/693cb4b195ff466e0cb7e48fae11c35dd52d40fb) (13/11/2026).
- [PR #28](https://github.com/AxlTech25/PFA-taller/pull/28), merge [`b5edc5c38a1e1bba132bc35c5b8cc4d9951a23dc`](https://github.com/AxlTech25/PFA-taller/commit/b5edc5c38a1e1bba132bc35c5b8cc4d9951a23dc) (13/11/2026). Corrección de CLS: [`74adfa9fb81dfcf234a37055f701945ff98c15b8`](https://github.com/AxlTech25/PFA-taller/commit/74adfa9fb81dfcf234a37055f701945ff98c15b8).

Lo que ya ejecuta GitHub Actions, y lo que todavía falta para que el despliegue salga solo, queda en Pendientes. El workflow es [`.github/workflows/deploy-production.yml`](../../../.github/workflows/deploy-production.yml).

---

## Demostración del trabajo completado

El entorno es **producción**.

| Pieza | Dónde está | URL |
| --- | --- | --- |
| Interfaz | Vercel, equipo `eco-pfa`, proyecto `ecologistica-lima`, raíz `frontend` | [https://ecologistica-lima-beige.vercel.app](https://ecologistica-lima-beige.vercel.app) |
| API y contrato | Railway, servicio `api` | [https://api-production-b8dfa3c0.up.railway.app](https://api-production-b8dfa3c0.up.railway.app) (`/health`, `/docs`) |

`ecologistica-lima.vercel.app` es otro sitio. No es esta aplicación.

La SPA se construye con Vite y Node 22 (`npm ci`, `npm run build`, salida `dist`). `frontend/vercel.json` reenvía `/auth`, `/usuarios`, `/vehiculos`, `/conductores`, `/pedidos`, `/clientes`, `/optimizaciones`, `/rutas`, `/indicadores`, `/health`, `/docs` y `/openapi.json` a la API. Si el navegador pide HTML en `/usuarios`, `/conductores`, `/pedidos` o `/rutas`, responde `index.html`. En Railway, proyecto `81c6f2b1-cac0-4061-bc96-6d8bd46754be`, entorno `production`, `api` (`19dd40e0-d91a-4674-8ca8-557a21c46806`) y `worker` (`e68f06e4-9cc5-40cd-a3bd-ba6945d1f28f`) salen de `backend/Dockerfile` con `railway up`. El entrypoint aplica Alembic, siembra y arranca uvicorn; el worker usa `PROCESO=worker`. `db` (`postgis/postgis:16-3.4`) y `Redis` no tienen dominio público.

La sesión con los interesados del 20/11/2026 se hizo en la máquina del equipo, con `docker compose up --build` (`http://localhost:5173` y `http://localhost:8000`). Esa sesión no usó la URL pública. Los escenarios de la tabla son los de esa sesión. El despliegue público se hizo a mano; [`.github/workflows/deploy-production.yml`](../../../.github/workflows/deploy-production.yml) lo repite cuando el repositorio tenga `RAILWAY_TOKEN`, `VERCEL_TOKEN`, `VERCEL_ORG_ID` y `VERCEL_PROJECT_ID`. En un pull request ese workflow se omite y no falla.

Perfiles presentes en la revisión:

- **Gerente de operaciones de DistriRápido S.A.C.:** kilómetros, CO₂, combustible, soles y cumplimiento de ventanas.
- **Jefe de operaciones logísticas:** generación del plan, trazado por calles, paradas y semáforo de congestión.
- **Patrocinador:** ver el Hito 3 en la sesión local. Pidió una URL pública; esta versión la registra arriba.
- **Representante de los conductores:** jornada y descansos ya cerrados en el Sprint 3, y que el plan nuevo no los ignore al confirmar.

### Escenarios demostrados

| Escenario | Qué se hizo | Qué se vio |
| --- | --- | --- |
| **1. Plan con el algoritmo genético** | El Operador abrió Rutas, eligió la fecha de un pedido de demostración y pulsó Generar rutas. En paralelo se mostró el bench automatizado de 150 pedidos y 15 vehículos. | La API respondió `202 Accepted`. El worker corrió DEAP dentro del presupuesto de 45 s y dejó el plan en Borrador, comparado con el vecino más cercano. El bench `test_bench_150_pedidos_15_vehiculos_en_45_segundos` terminó en ≤ 45 s, con los 150 pedidos asignados, sin violar capacidad, ventanas, jornada ni pico y placa. La base de demostración no contiene 150 pedidos: esa cifra es la prueba sintética, no un alta manual de 150 fichas. |
| **2. Mapa por calles** | Se eligió la ruta en borrador. | Leaflet dibujó el recorrido con la geometría de OSRM, los marcadores de parada, el ETA por tramo y el semáforo verde, amarillo o rojo. Se explicó el respaldo: si OSRM no responde en 8 s, la línea recta; si OpenStreetMap no carga, la tabla con el aviso de teselas. |
| **3. Tablero del mismo día** | El Gerente abrió Tablero en la fecha del plan y, después, en un día sin rutas. | Con plan: km, kg de CO₂, litros, soles (S/ 17,50 por galón y S/ 1,20 por km) y el porcentaje de ventanas. Sin plan: ceros y el texto «Sin datos de operación para el período seleccionado». El equivalente en árboles quedó en blanco, con la nota de que RN-018 no está ratificado. |
| **4. Comentarios de la revisión** | Se recorrió el mismo flujo con los cuatro perfiles y se anotó qué pedían para el Sprint 5. | El Gerente aceptó los cinco indicadores del incremento A y pidió el factor de árboles solo cuando esté ratificado. El Jefe de operaciones validó el trazado por calles y pidió las zonas de riesgo y la ruta alternativa (US-013). El patrocinador aceptó la demo local y pidió una URL pública. Esta versión deja esa URL arriba: la interfaz en Vercel y la API en Railway. |

---

## Pendientes

Nada de lo siguiente formaba parte de los 26 SP cerrados. Sigue fuera de Done.

| ID | Qué queda | SP | Dónde está al 20/11/2026 | Hacia dónde va |
| --- | --- | ---: | --- | --- |
| **IMP-04** | El sitio público ya está en producción, desplegado a mano: Vercel para la SPA y Railway para `api`, `worker`, `db` y `Redis`. CodeQL ya corre. Falta que GitHub Actions pueda repetir el despliegue: los secretos `RAILWAY_TOKEN`, `VERCEL_TOKEN`, `VERCEL_ORG_ID` y `VERCEL_PROJECT_ID` todavía no están en el repositorio. La topología real no publica el servicio `web` de `Dockerfile.prod`. | — | Producción en línea. El workflow existe y se omite hasta que haya secretos. | Cargar los cuatro secretos en el entorno `production` de GitHub. Seguimiento: Cruz Salazar, Jorge Luiz. |
| **IMP-11** | Catastro INEI. RN-005 pide polígonos distritales. La migración `004_sprint3_cobertura.py` carga envolventes rectangulares de San Juan de Lurigancho, El Agustino, Santa Anita y Ate, y el propio archivo dice que no son el catastro del INEI. No hay un archivo oficial en el repositorio. La validación sigue en PostGIS (`ST_Covers`). | — | Aceptado el 17/10/2026. Sigue sin archivo. | No se sustituye la geometría con un polígono inventado. Si aparece el archivo, lo toma Leon Taza, Brayan Angel, sin cambiar el contrato de la API. |
| **US-013** | Zonas de riesgo (`zona_restriccion`) y acción de ruta alternativa. Cierra el mapa que US-012 A dejó iniciado. Reserva ecológica como restricción dura (RN-013). | 5 | No iniciado en este sprint. | Sprint 5 (13/11/2026 – 26/11/2026). Leon Taza, Brayan Angel. Tarjeta ECO-26. |
| **US-014 B** | Factor de árboles `factor_captura_arbol_kg` (RN-018). El tablero no muestra un equivalente inventado. | 3 | `arboles` es nulo y la nota cita RN-018. | Sprint 5. Huaman Baldeon, Katheryn Elena. Misma tarjeta ECO-27, incremento B. |

El resto del compromiso del Sprint 5 (26 SP en total) ya estaba planificado y no es trabajo a medias del Sprint 4: US-015 modo conductor (8 SP), ENB-005 WCAG 2.2 AA (5 SP) y ENB-008 payload ≤ 150 KB (5 SP). US-013 (5) y US-014 B (3) completan esos 26.

Verificación automática que ya está en el repositorio, y la que todavía no:

- **Ya corre.** `ci.yml` en cada push y cada pull request: Ruff, Pytest con cobertura mínima del 80 % sobre `app`, `npm test` (Vitest) y `npm run build`. `tests.yml` corre pytest, Vitest, la integración HTTP y Playwright (Chromium, Firefox y WebKit). `codeql.yml` analiza JavaScript/TypeScript y Python en `main`, en pull requests y cada lunes a las 06:00 UTC. `green-audit.yml` corre Lighthouse CI 0.16.1 sobre las ocho pantallas. `deploy-production.yml` está en el repositorio: despliega `api` y `worker` en Railway y la SPA en Vercel después de `Tests` en verde en un push a `main`, o al publicar una etiqueta `v*`. En un pull request se omite.
- **Todavía no está.** Los cuatro secretos del entorno `production`, así que el workflow todavía no despliega desde GitHub. No hay un cuestionario SUS archivado. El comando de frontend en CI es `vitest run`, sin `--coverage`: `@vitest/coverage-v8` está instalado y configurado, y el workflow no exige un porcentaje de cobertura de la interfaz. El FCP móvil de 1 351,7659 ms en `/login` queda fuera del umbral de 1,0 s; la medición de aceptación de este sprint es la de escritorio.

El cuestionario SUS sigue como acción de la [retrospectiva](./02%20Retrospectiva%20del%20Sprint%20V_1_0_0.md). Playwright y el workflow de despliegue ya están en el repositorio.

---

## Historial de Control de Cambios

| Versión | Fecha | Autor | Descripción |
|---|---|---|---|
| 1.0.0 | 20/11/2026 | Equipo EcoLogística Lima | Revisión de cierre del Sprint 4. Las cuatro tarjetas del compromiso (26 SP) quedan en Done. La sesión con interesados de ese día fue en Docker Compose. |
| 1.0.1 | 20/11/2026 | Equipo EcoLogística Lima | El entorno público es producción: Vercel (`ecologistica-lima-beige.vercel.app`) y Railway (`api-production-b8dfa3c0.up.railway.app`). Se registra el workflow de despliegue y que Playwright ya está en el repositorio. El archivo pasa a V_1_0_1. |

---

[← Volver al README principal](../../../README.md)
