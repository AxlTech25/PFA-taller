[← Volver al README principal](../../../README.md)

# Retrospectiva del sprint

**Nombre del Proyecto:** EcoLogística Lima – Optimizador de Rutas Sostenibles para DistriRápido S.A.C.

**Líder del Proyecto:** Carhuapoma Fano, Eilene Elizabeth

**Sprint:** 4 (`ECO Sprint 4`, 30/10/2026 – 12/11/2026). Hito 3 el 12/11/2026. Retrospectiva: 20/11/2026. Versión: 1.0.0.

El detalle de lo entregado está en la [revisión del sprint](./01%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md). Las cifras de Lighthouse y de CO₂ del software están en el [informe de reducción del impacto ambiental](../reduccion%20del%20impacto%20ambiental/01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md).

## ¿Qué aprendimos?

- El corte de 45 segundos (RN-014, `tiempo_max_optimizacion_s`) no se cumple agrandando la población. En `metaheuristica.py` la población de DEAP es 16 y baja a 8 cuando hay más de 40 pedidos; el tope es 40 generaciones y se corta también por 8 generaciones sin mejora. Así el bench de 150 pedidos y 15 vehículos cabe en 45 s. Si el genético no baja el costo verde, se conserva el plan del vecino más cercano: el worker no devuelve un plan peor ni deja colgada la API.
- Una línea recta entre la partida y las paradas no es una ruta de reparto. OSRM, sobre OpenStreetMap, devuelve la geometría por calles (`router.project-osrm.org`, o `VITE_OSRM_URL`). El servidor público rechaza pedidos con demasiadas coordenadas, así que el trazado se parte en tramos de 25 puntos. Si OSRM falla o tarda más de 8 segundos, el mapa vuelve a la línea recta. OSRM acerca cada parada a la calle: hizo falta un enlace punteado hasta la coordenada real para que el marcador y la línea coincidieran.
- Lighthouse 12.1.0, el de `@lhci/cli@0.14.0`, marcaba «Error!» en seis auditorías (`frame_sequence`) con Chrome 157. No era un fallo de la compilación. Lighthouse 13.6.0 (`@lhci/cli@0.16.1`) lee esa traza. Con esa versión, el 13/11/2026, las ocho pantallas quedaron en performance 100, TBT 0 ms y CLS 0. El CLS de `/rutas` había pasado de 0,105814 a 0,038150 al reservar el alto del mapa, y llegó a 0 al reservar también la lista textual y el panel, desactivar el fundido y el zoom animado de Leaflet, y dar `min-height: 100vh` al aviso de carga. El peso de `/rutas` quedó en 746 304 bytes, bajo el tope de 1,1 MB. El FCP de escritorio bajó a unos 161 ms en siete pantallas; en `/flota` la medición fue 283,3689 ms.
- Subir de versión mayor en el frontend sí cerró los avisos que el Sprint 3 había dejado a propósito. El 07/11/2026 `npm audit` contaba 12 vulnerabilidades (3 críticas, 1 alta y 8 moderadas) en Vitest, `@vitest/coverage-v8`, Vite y React Router. Vite 8, Vitest 5, `@vitejs/plugin-react` 6 y React Router 7 dejaron el audit en 0, con las pruebas de Vitest en verde. `coverage.all` ya no existe en Vitest 5 y hubo que quitarlo.
- Preparar Railway no es tener Staging. El PR #23 acepta la URL `postgres://` de Railway, arranca el worker con la misma imagen (`PROCESO=worker`) y deja un Caddy que sirve la SPA y hace de proxy de la API. Sin el proyecto creado y sin el dominio de `web`, la revisión sigue siendo `localhost:5173` y `localhost:8000`. Inventar una URL habría falseado el Hito 3.
- El código del compromiso entró el 18/10/2026, antes de la ventana 30/10–12/11. Adelantar el merge dio tiempo al trazado OSRM (07/11) y a Green IT (12/11 y 13/11). El calendario del Hito 3 no se movió: sigue el 12/11/2026.

## ¿Qué estamos haciendo bien?

- Los 26 SP quedaron partidos en incrementos demostrables. ENB-001 B y US-010 B se prueban con un bench reproducible, no con una corrida manual que no se puede repetir. US-012 A y US-014 A tienen criterios Gherkin y pruebas de interfaz, y dejan explícito lo que no cierran (zonas y árboles).
- Cuando una medición no cumplía, se volvió a medir con la herramienta que sí leía la traza, y se publicaron el antes y el después. El CLS de `/rutas` no se dio por bueno en 0,038: la aserción del flujo sigue en 0,02 y el valor final es 0.
- El audit de npm se llevó a cero dentro del sprint, que era una acción abierta de la retrospectiva del Sprint 3. Las pruebas de Vitest siguieron pasando después de los saltos de versión mayor.
- La demo de la revisión usó Docker Compose, el mismo arranque que cualquier compañero puede repetir. No se mostró una dirección de nube que el repositorio no tiene.
- CodeQL, el Quality Gate de Pytest (mínimo 80 %) y la auditoría Lighthouse de las ocho pantallas ya corren solos en GitHub Actions.

## ¿Qué podemos hacer mejor?

### Personas

- Afinar DEAP (población, estancamiento y el corte de 45 s) quedó concentrado en quien escribe el worker. El resto del equipo ve el plan en Borrador y no el criterio por el que se bajó la población de 16 a 8. Conviene explicar ese número el día en que se cambia, con el bench al lado.
- Lighthouse 13.6, OSRM y el salto a Vite 8 llegaron en la misma ventana. Quien no corrió la auditoría solo vio el puntaje 100 en el informe. La próxima medición se comenta en la retrospectiva con la pantalla abierta, no solo con la tabla.

### Relaciones

- El Gerente pidió árboles y el Jefe de operaciones pidió zonas de riesgo en la misma revisión en la que se aceptaban el tablero y el mapa. Esas dos peticiones ya estaban en el Sprint 5 (US-014 B y US-013). Hay que decirlo en la sala, con el SP al lado, para que un comentario no se lea como alcance de más del sprint que se está cerrando.
- El patrocinador preguntó por la dirección de Staging. La respuesta correcta fue que no existe. Decirlo al empezar la demo evita que alguien anote una URL de ejemplo.

### Procesos

- El Hito 3 (12/11/2026) y el merge del motor (18/10/2026) no son la misma fecha. El seguimiento tiene que nombrar las dos, como ya hace el cronograma, para no cerrar la ventana el día del primer pull request ni mover el hito porque el código llegó antes.
- El Definition of Done pide Staging (D4). Este sprint cierra las cuatro historias por sus criterios de aceptación y deja D4 abierto a propósito. Eso tiene que constar en la revisión cada vez que se mueva una tarjeta a Done sin URL pública.
- La cobertura del backend bloquea el merge por debajo del 80 %. La del frontend no: CI ejecuta `vitest run` y no `vitest run --coverage`. El proveedor v8 está instalado y el porcentaje de la interfaz no forma parte del Quality Gate.
- No hay una prueba de extremo a extremo que recorra login, generación, mapa y tablero en el navegador. Las pruebas de componente y el bench cubren las piezas; un fallo de proxy o de cookie entre pantallas no lo vería ese conjunto.

### Herramientas

- El servidor público de OSRM es un dependencia de la demo. A los 8 segundos el mapa degrada a línea recta, y eso está probado, pero la revisión en vivo depende de que ese servidor conteste. Hace falta dejar anotado el `VITE_OSRM_URL` de respaldo antes del Sprint 5, no durante la demo.
- Railway quedó descrito y no ejecutado. Falta crear los cinco servicios. Hasta entonces, Compose es el único ambiente y el puerto 5433 del host sigue siendo el que evita chocar con otro PostgreSQL en 5432.
- El preset móvil de `/login` (Lighthouse 12.6.1, 12/11/2026) dio FCP 1 351,7659 ms. El umbral de la rúbrica es 1,0 s. La consola se usa en escritorio y esa es la cifra de aceptación, pero el número móvil no se puede citar como cumplido.
- Playwright no está en el repositorio. Tampoco hay un resultado SUS. Las dos herramientas se nombran desde la planificación de la experiencia de uso y todavía no tienen una corrida.

### Acciones a realizar

Cada acción tiene un responsable, una fecha y una forma de saber si se cumplió. Las fechas caen dentro del Sprint 5 (cierra el 26/11/2026). Al 20/11/2026 ninguna de estas cuatro herramientas nuevas está hecha: no hay proyecto Railway creado, no hay Playwright, no hay SUS archivado y no hay un acta que junte el estado de los tres workflows.

| ID | Acción | Responsable | Fecha | Cómo se sabe que está hecha |
| --- | --- | --- | --- | --- |
| A1 | Crear en Railway los cinco servicios del PR #23 (`db` con `postgis/postgis:16-3.4`, Redis, `api`, `worker` con `PROCESO=worker`, y `web` con `Dockerfile.prod`) y anotar el dominio generado de `web`. | Cruz Salazar, Jorge Luiz | 26/11/2026 | El dominio responde y `GET /health` de la API, visto a través de ese mismo origen, devuelve 200. La URL queda escrita en el informe del Sprint 5. Hoy no se publica ninguna porque no existe. |
| A2 | Agregar un workflow de GitHub Actions con Playwright que recorra, contra Compose o los servicios de CI, el inicio de sesión, `POST /optimizaciones` en 202, el mapa o la tabla de respaldo, y el tablero (métricas o el mensaje de período vacío). | Estrada Flores, Axel Sebastian | 26/11/2026 | El archivo está en `.github/workflows/` y una corrida en `main` termina en verde, con cero escenarios fallidos de ese guion. |
| A3 | Pasar el cuestionario SUS de la consola (mapa y tablero) a personas con el perfil de Operador o de Gerente, usando la demo de Docker Compose en `localhost:5173`. | Huaman Baldeon, Katheryn Elena, con la convocatoria de Carhuapoma Fano, Eilene Elizabeth | 26/11/2026 | Hay al menos 5 cuestionarios completos. El puntaje SUS, de 0 a 100, está calculado con la fórmula estándar y archivado junto a la revisión del Sprint 5. |
| A4 | Dejar por escrito el estado de `ci.yml`, `codeql.yml` y `green-audit.yml`, y la ausencia del job de despliegue, para que el planning del Sprint 5 no vuelva a tratar el pipeline como si ya publicara Staging. | Carhuapoma Fano, Eilene Elizabeth | 24/11/2026 | Una nota de una página lista la última corrida de cada workflow y dice, en una línea, que ninguno despliega a Railway. |
| A5 | Mantener IMP-11 sin geometría inventada. Si el archivo del catastro INEI llega al repositorio, reemplazar las envolventes de `distrito_cobertura` y conservar `ST_Covers`. Si no llega, el impedimento sigue Aceptado. | Leon Taza, Brayan Angel | 26/11/2026 | O hay una migración nueva que sustituye las envolventes de `004_sprint3_cobertura.py` por el archivo recibido, o el registro del Sprint 5 repite que no había archivo y que no se cargó un polígono de relleno. |

US-013 (zonas y ruta alternativa, 5 SP) y US-014 B (factor de árboles, 3 SP) siguen siendo el compromiso de producto del Sprint 5. No se reabren como acciones de esta retrospectiva: ya tienen responsable y SP en el cronograma. A1 a A5 cubren lo que este sprint dejó configurado y sin ejecutar.

[← Volver al README principal](../../../README.md)
