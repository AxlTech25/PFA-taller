[← Volver al README Principal](../../../README.md)

# Retrospectiva del sprint

**Nombre del Proyecto:** EcoLogística Lima – Optimizador de Rutas Sostenibles para DistriRápido S.A.C.

**Líder del Proyecto:** Carhuapoma Fano, Eilene Elizabeth

## ¿Qué aprendimos?

- El Sprint 3 cabe en su ventana. El calendario y Jira lo fijan del 16/10/2026 al 29/10/2026 (`ECO Sprint 3`). El código funcional se fusionó en el [PR #15](https://github.com/AxlTech25/PFA-taller/pull/15), con cierre documentado el 17/10/2026 (día 2 de 14). La [revisión de la consigna](./01%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md) da por cerradas US-008 B (3 SP, cobertura de Lima Este), US-007 (5 SP, jornada de 8 h) y ENB-006 (5 SP, worker Redis y `202 Accepted`): **13 SP**. El [cronograma](../../02%20Planificaci%C3%B3n/05%20Cronograma%20de%20sprints%20V_1_0_5.md) suma **26 SP** en ese mismo PR al contar el incremento A de ENB-001 (vecino más cercano, 8 SP) y de US-010 (plan en borrador por job asíncrono, 5 SP). Las dos cifras conviven: la revisión deja US-010 y ENB-001 en entrega parcial porque faltan DEAP y la prueba de carga.
- Un Quality Gate en PASSED no basta si no tiene condiciones. Sobre `main` `efcfcfb` (2026-10-26) SonarQube marcó PASSED sin condiciones, con cobertura **53.1 %**, 111 issues, 1 vulnerabilidad bloqueante (`secrets:S6698`), 110 code smells, 2 hotspots `python:S2245` en revisión y 616 minutos de deuda. El frontend estaba en **6.3 %** de líneas en Vitest. Después de las correcciones del [PR #17](https://github.com/AxlTech25/PFA-taller/pull/17), el análisis en Community Build 26.10.0.133078 sobre `aaa13b6` quedó en Quality Gate **PASSED**, cobertura global **97.6 %**, duplicación **0.0 %**, 0 bugs, 0 code smells, 0 hotspots y 0 vulnerabilidades abiertas. Las dos `python:S2245` se aceptaron como Safe: `random` siembra el algoritmo genético y no protege credenciales. En la instancia del equipo, New Code quedó en 90.0 % de cobertura (umbral ≥ 80 %) y 0 issues nuevos. La verificación en la VM midió el código nuevo en 87.5 %, también PASSED.
- Sacar la contraseña del valor por defecto no cerró la regla. El re-escaneo de `0ce075d` seguía marcando `python:S2115` en el f-string de la URL. La conexión quedó en `sqlalchemy.engine.URL.create` y, si falta `POSTGRES_PASSWORD`, el proceso no arranca.
- A06 no sale de SonarQube. El escaneo final tiene 0 issues y SonarQube no reportó CVE. `npm audit` del frontend, fuera de ese escaneo, marca **9 avisos** (3 críticos y 1 alto en vitest, vite y tinypool, de servidor de desarrollo, y avisos medios en esbuild y react-router). El [reporte OWASP](./04%20OWASP%20V_1_0_0.md) deja A06 en **Bajo Revisión**: no se subieron esas versiones para conservar el comportamiento ya probado. Las otras nueve categorías de OWASP Top 10 2025 quedan en Limpio.
- Una sola pantalla en verde no cierra WCAG 2.2 AA. La línea base de Flota ya daba Lighthouse Accessibility 100, WAVE sin errores y axe DevTools en 0 issues, y el resto del sistema fallaba el foco sobre la barra, botones con el mismo nombre, el mapa sin alternativa textual y el reflow a 320 px. De 43 criterios aplicables se cumplían 27 (62.8 %). Tras el [PR #18](https://github.com/AxlTech25/PFA-taller/pull/18) se cumplen 43 (100 %). axe-core 4.10.3 corre en Vitest (9 pruebas, 0 violaciones) y entra en `npm test`.
- El rendimiento medido con `npm run dev` no es un criterio WCAG. En Lighthouse salió **86 en escritorio y 59 en móvil**. En Rutas, sobre ese servidor de desarrollo: FCP 6.8 s, LCP 11.7 s, TBT 60 ms, CLS 0.
- El arranque local sigue atado a dos impedimentos resueltos el 30/09/2026 y que la demo de este sprint volvió a usar. IMP-01: el puerto 5432 del host ya tenía PostgreSQL, y Compose publica **5433**. IMP-02: un `backend/entrypoint.sh` en CRLF tumba el contenedor (`$'\r': command not found`); `.gitattributes` lo fija en LF. El escáner de SonarQube no se asumió instalado en el host: se corrió con la imagen `sonarsource/sonar-scanner-cli` contra SonarQube Community en Docker. Si `coverage.xml` lleva la ruta absoluta del disco, o el lcov sale como `SF:src\App.tsx`, la cobertura de New Code queda en «Not computed».
- `Sprint 3/` y `Sprint 03/` son el mismo calendario. La primera guarda la gestión; la segunda, los ítems de la consigna. El [PR #19](https://github.com/AxlTech25/PFA-taller/pull/19) alineó nombres, OWASP y enlaces, y dejó esta retrospectiva para el equipo.

## ¿Qué estamos haciendo bien?

- El incremento del PR #15 se puede demostrar en `docker compose up --build`, sin URL de Staging. Un pedido en Lima Este con punto de referencia entra; Miraflores responde 422. `POST /optimizaciones` responde 202 y el worker calcula fuera del request. Si Redis cae, la API responde 503 y no deja un job huérfano. Una jornada por encima de 8 h se bloquea, con descanso de 1 h cada 4 h (Ley N.º 30224). La sesión se mostró a los perfiles de la revisión: gerencia, operaciones, cumplimiento legal y conductores.
- La deuda de la línea base bajó en el mismo sprint: de 616 minutos y 111 issues a 0 issues abiertos, 0 hotspots y `sqale_index` 0 en el escaneo final. Pytest quedó en 78 pruebas y 97.71 % de líneas sobre `app`. Vitest pasó de 7 pruebas a 52 en el cierre de calidad (99.54 % de líneas) y a **64** con las 9 de axe-core (99.58 % de líneas).
- Las correcciones de accesibilidad cubren las nueve superficies: login, Flota, Conductores, Pedidos, Rutas, Tablero, Usuarios, Modo conductor y acceso denegado. WAVE, después del cambio, da 0 errores, 0 contrastes y 0 alertas (AIM 10/10) en las pantallas auditadas. Lighthouse Accessibility es 100. El anillo de foco, el salto al contenido, el nombre de cada botón y la alternativa textual del mapa quedaron en el código.
- CodeQL está en `.github/workflows/codeql.yml` desde el PR #15. La CI sigue exigiendo Ruff, pytest con cobertura mínima 80 %, `npm test` y el build del frontend. Las pruebas de axe-core entran por `npm test`, sin un workflow aparte.
- No se inventó una dirección de Staging. IMP-04 sigue en curso, con tope en el Hito 3 (12/11/2026), porque el repositorio no tiene secreto de Railway ni de Render. IMP-11 quedó aceptado: la cobertura usa envolventes rectangulares, no el catastro INEI, y `ST_Covers` permite cambiar la geometría sin tocar la API.
- El PR #19 dejó el reporte OWASP alineado con el escaneo final (A02 en Limpio tras marcar Safe) y el archivo de accesibilidad con el nombre de la consigna (`05 WCAG V_1_0_0.md`).

## ¿Qué podemos hacer mejor?

### Personas

- El [cronograma](../../02%20Planificaci%C3%B3n/05%20Cronograma%20de%20sprints%20V_1_0_5.md) asigna US-007, ENB-006, ENB-001 A y US-010 A a Cruz Salazar, Jorge Luiz, y US-008 B a Huaman Baldeon, Katheryn Elena. Worker, heurística y jornada quedan en una sola persona. La pantalla de pedidos y de rutas va por otro lado, y el contrato OpenAPI volvió a llegar junto con el código.
- Calidad, OWASP y WCAG (PR #17, #18 y #19) entraron después del cierre funcional del 17/10. Quien redacta el informe necesita el escaneo y las capturas; el merge del PR #15 no las trae.
- Esta retrospectiva quedó fuera del PR #19 a propósito. El equipo la cierra el 29/10/2026, último día de la ventana.

### Relaciones

- En el [artefacto de Jira](../../02%20Planificaci%C3%B3n/02%20Artefactos%20Jira%20V_1_0_10.md), `ECO Sprint 3` tiene el Sprint Goal del operador (Lima Este, jornada de 8 h, worker con vecino más cercano) y las tarjetas ECO-19, ECO-21, ECO-22, ECO-23 y ECO-24 (26 SP). La acción A5 de la retrospectiva de gestión sigue sin evidencia en el repositorio: no hay captura de esas tarjetas en Done con enlace al PR #15. El mismo hueco ya venía del Sprint 2.
- La demostración a los stakeholders se hizo en la máquina del equipo. Quien no estuvo en esa sesión no tiene una URL para repetirla.
- ENB-005 (WCAG 2.2 AA, 5 SP) sigue en el Sprint 5 del cronograma, y la evaluación con correcciones ya está en el PR #18. Hay que decirlo en Jira para no planificar el mismo trabajo otra vez y para no dar el ítem por cerrado dos veces.

### Procesos

- El Sprint 4 se fusionó el 18/10/2026 ([PR #16](https://github.com/AxlTech25/PFA-taller/pull/16)), todavía dentro del calendario del Sprint 3 y antes de su ventana (30/10/2026 – 12/11/2026). El Hito 3 no se movió. El mapa y el tablero entraron comprimidos. La retrospectiva de gestión ya pedía no dejar ese sprint para el último día.
- Partir ENB-001 y US-010 permitió mostrar el vecino más cercano con el algoritmo genético todavía pendiente. La revisión y el cronograma no cuentan igual ese corte (13 SP frente a 26 SP). El lector no debería tener que reconstruir la diferencia.
- El DoD que cita la revisión pide SonarQube y CodeQL. CodeQL está en el workflow. El Quality Gate de SonarQube se obtuvo en una instancia local y en una verificación en la VM. La CI no falla si ese gate se rompe.
- Dos carpetas para un mismo sprint (`Sprint 3/` y `Sprint 03/`) confundieron la entrega hasta que el PR #19 lo escribió en el README. Conviene repetir esa distinción cada vez que se enlace un ítem.

### Herramientas

- SonarQube Community se levantó en Docker y el análisis se lanzó con `sonarsource/sonar-scanner-cli` (8.1.0.6389 en la verificación de la VM, Community Build 26.10.0.133078). El comando documentado es PowerShell, con el repositorio montado en `/usr/src` y `SONAR_HOST_URL` en `http://host.docker.internal:9000`. Pytest y Vitest ya dejan rutas relativas (`backend/app/...` y `frontend/src/...`). Reescribir `<source>` a mano antes de escanear vuelve a romper la cobertura.
- PostgreSQL del host en 5432 sigue chocando con Compose. El arreglo vigente es publicar **5433:5432**. Volver a 5432 rompe el arranque en las máquinas que ya tienen Postgres local.
- `backend/entrypoint.sh` tiene que quedar en LF. Un guardado en CRLF desde Windows repite IMP-02.
- `npm audit` no está en la CI. Los 9 avisos de A06 no impiden fusionar.
- Lighthouse sobre el servidor de Vite mezcla el costo del modo desarrollo con el de la aplicación. Performance 59 en móvil y 86 en escritorio no son cifras de `npm run build`. El informe WCAG ya indica repetir Performance con `npm run preview`.

### Acciones a realizar

- Actualizar las dependencias npm que originan los 9 avisos de `npm audit` (vitest, vite, tinypool, esbuild y react-router) y volver a ejecutar `npm audit`, `npm test` y `npm run build`. Dueño: equipo. Meta: en el Sprint 4, antes del 12/11/2026, dejar A06 fuera de Bajo Revisión, con los 9 avisos en cero o con una justificación por aviso en el reporte OWASP.
- Medir Lighthouse Performance sobre `npm run build` y `npm run preview`, y tratar el resultado móvil como trabajo de producto. La cifra conocida hoy es la del servidor de desarrollo: 86 en escritorio y 59 en móvil; en Rutas, FCP 6.8 s y LCP 11.7 s. Dueño: equipo. Meta: en el Sprint 4, documentar la pasada de producción y, si el Performance móvil sigue en 59 o el LCP sigue en ese orden, ajustar la carga del mapa y del bundle.
- Incorporar el Quality Gate de SonarQube al pipeline de CI. En este sprint el gate se obtuvo en local, con el escáner en Docker; la CI ya exige Ruff, pytest con umbral 80 % y `npm test` (incluye axe-core). Dueño: equipo. Meta: en el Sprint 4, un job que falle el pull request si el Quality Gate no queda PASSED.
- Pasar en Jira las tarjetas ECO-19, ECO-21, ECO-22, ECO-23 y ECO-24 a Done con el enlace al PR #15, y anotar que el PR #18 adelanta la evaluación WCAG 2.2 AA que el cronograma ubica en ENB-005 (Sprint 5). Dueño: equipo. Meta: evidencia en `docs/02 Planificación/evidencias/` o en el artefacto de Jira el 30/10/2026, al abrir el Sprint 4.
- Dejar por escrito una sola cifra de SP cerrados del Sprint 3. La revisión dice 13 y el cronograma 26 porque una no cuenta el incremento A de ENB-001 y US-010. Dueño: equipo. Meta: nota de conciliación en la revisión o en el cronograma durante el Sprint 4, antes del 12/11/2026.
- Conservar el puerto host 5433 y los saltos LF de `backend/entrypoint.sh` en la próxima demo con Compose, y correr el escáner de SonarQube con las rutas relativas que ya dejan pytest y Vitest. Dueño: equipo. Meta: primera corrida del Sprint 4, sin choque en 5432, sin `$'\r': command not found` y sin cobertura de New Code en «Not computed».
- Resolver IMP-04 solo con una URL real de despliegue. Dueño: equipo. Meta: el 12/11/2026, o el README publica esa URL, o el impedimento sigue abierto. No se escribe una dirección de demostración.

Revisión: [01 Revisión del Sprint V_1_0_0.md](./01%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md). Calidad: [03 Calidad de código V_1_0_0.md](./03%20Calidad%20de%20c%C3%B3digo%20V_1_0_0.md). OWASP: [04 OWASP V_1_0_0.md](./04%20OWASP%20V_1_0_0.md). WCAG: [05 WCAG V_1_0_0.md](./05%20WCAG%20V_1_0_0.md).

[← Volver al README Principal](../../../README.md)
