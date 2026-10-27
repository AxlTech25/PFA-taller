[← Volver al README Principal](../../../README.md)

# Evaluación de Calidad de Código — SonarQube

**Nombre del Proyecto:** EcoLogística Lima – Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Fecha de Análisis:** 2026-10-26  
**Versión del Análisis:** V_1_0_0  

Línea base local sobre la rama `main`, commit `efcfcfb`. Servidor SonarQube Community. Clave de proyecto `pfa-taller`. La remediación de este documento se aplicó el 2026-10-27. Las métricas posteriores al cambio quedan **pendiente de re-escaneo**: hay que volver a correr el escáner en la máquina local y completar la tabla Antes / Después.

## 1. Resumen Ejecutivo de Quality Gate

- **Estado del Quality Gate:** PASSED
- **Porcentaje de Cobertura de Pruebas (Coverage):** 53.1 %
- **Duplicación de Código:** 0.0 %

El Quality Gate local respondió OK. La instancia no tenía condiciones configuradas, así que el estado PASSED convive con los hallazgos de abajo: 111 issues, 1 vulnerabilidad, 2 security hotspots y 616 minutos de deuda técnica. LOC (ncloc): 5399. Confiabilidad A (0 bugs). Mantenibilidad A (110 code smells). Seguridad E por la vulnerabilidad bloqueante. Cobertura del frontend medida con vitest en esa línea base: 6.3 % de líneas (3 archivos de prueba). El backend tenía 64 pruebas pytest en verde.

## 2. Métricas Principales

| Categoría | Cantidad Detectada | Severidad (Bloqueante / Alta / Media / Baja) |
|---|---|---|
| **Bugs** | 0 | Sin hallazgos. Rating de confiabilidad A. |
| **Vulnerabilidades** | 1 | Bloqueante (1). Rating de seguridad E. |
| **Code Smells** | 110 | Bloqueante 46, Alta 9, Media 47, Baja 8. Rating de mantenibilidad A. |
| **Security Hotspots** | 2 | Media (2), ambos `TO_REVIEW`, regla `python:S2245`. |

Severidad de los 111 issues (vulnerabilidad + code smells): Bloqueante 47, Alta 9, Media 47, Baja 8.

| Regla | Tipo | Severidad | Cantidad | Dónde |
|---|---|---|---|---|
| secrets:S6698 | Vulnerabilidad | Bloqueante | 1 | `backend/app/core/config.py:12` |
| python:S8410 | Code smell | Bloqueante | 44 | Dependencias `Depends` y `Query` en `backend/app/api/routes/` |
| python:S8409 | Code smell | Bloqueante | 1 | `backend/app/api/routes/auth.py:15` |
| python:S8414 | Code smell | Bloqueante | 1 | `backend/app/main.py:31` |
| python:S3776 | Code smell | Alta | 5 | `evaluacion.py`, `metaheuristica.py`, `services/indicadores.py`, `services/rutas.py` |
| python:S1192 | Code smell | Alta | 3 | `backend/app/models/entities.py` |
| typescript:S2004 | Code smell | Alta | 1 | `frontend/src/pages/MapaRutas.tsx:62` |
| python:S8415 | Code smell | Media | 1 | `backend/app/api/routes/health.py:15` |
| python:S5864 | Code smell | Media | 2 | `backend/app/optimizacion/cola.py` |
| typescript:S6772 | Code smell | Media | 34 | Etiquetas de formulario en `frontend/src/pages/` |
| typescript:S6819 | Code smell | Media | 10 | `role="status"` y `role="region"` en páginas React |
| python:S5713 | Code smell | Baja | 3 | `backend/app/optimizacion/cola.py` |
| typescript:S6759 | Code smell | Baja | 3 | Props de `MapaRutas`, `App` y `AuthProvider` |
| typescript:S7735 | Code smell | Baja | 1 | `frontend/src/pages/RutasPage.tsx:200` |
| typescript:S7764 | Code smell | Baja | 1 | `frontend/src/pages/RutasPage.tsx:19` |

## 3. Plan de Remediación y Deuda Técnica

- **Deuda Técnica Estimada:** 616 minutos (10 h 16 min), `sqale_index` de la línea base.
- **Principales hallazgos y acciones correctivas:**

1. **secrets:S6698 (Bloqueante).** La URL por defecto de PostgreSQL llevaba usuario y contraseña escritos en `backend/app/core/config.py`. Corrección: `database_url` queda vacío en el código y se completa con `DATABASE_URL`. Si esa variable no viene, la URL se arma con `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT` y `POSTGRES_DB`. La contraseña de demostración sigue en `.env.example`, en los valores por defecto de `docker-compose.yml` y en el workflow de CI, que es de donde la toma el proceso. Archivos: `backend/app/core/config.py`, `backend/tests/test_config_entorno.py`.

2. **python:S8410 (Bloqueante, 44).** FastAPI pedía `Annotated` en la inyección de dependencias y en `Query`. Corrección: cada `Depends` y cada `Query` de los endpoints pasa a `Annotated[...]`. El valor por defecto de `limite` y de la fecha opcional queda en `=`, que es la forma que acepta FastAPI 0.115. Archivos: `backend/app/api/routes/auth.py`, `health.py`, `indicadores.py`, `optimizaciones.py`, `rutas.py`, `clientes.py`, `conductores.py`, `pedidos.py`, `usuarios.py`, `vehiculos.py`.

3. **python:S8409 (Bloqueante).** `POST /auth/login` repetía `response_model=TokenResponse` junto al retorno `-> TokenResponse`. Corrección: se quitó `response_model`. Los códigos 401, 403 y 423 siguen declarados en `responses`. Archivo: `backend/app/api/routes/auth.py`.

4. **python:S8414 (Bloqueante).** `CORSMiddleware` no era el último `add_middleware`. En Starlette el último agregado es el más externo. Corrección: primero se registra `SecurityHeadersMiddleware` y al final `CORSMiddleware`, para que las cabeceras CORS cubran también esa respuesta. Archivo: `backend/app/main.py`.

5. **python:S3776 (Alta, 5).** Complejidad cognitiva por encima de 15: `evaluacion.py` `_armar_por_cercania` (17) y `mejorar_orden_local` (29), `metaheuristica.py` `_correr` (25), `services/indicadores.py` `consultar` (25) y `services/rutas.py` `salida_ruta` (32). Corrección: se extrajeron funciones con la misma secuencia de decisiones (elección del vecino, 2-opt, cruce y mutación del algoritmo genético, tablero e hidratación de la ruta). Archivos: `backend/app/optimizacion/evaluacion.py`, `backend/app/optimizacion/metaheuristica.py`, `backend/app/services/indicadores.py`, `backend/app/services/rutas.py`.

6. **python:S1192 (Alta, 3).** Literales repetidos en el modelo: `uuid_generate_v4()` (11), `usuario.id_usuario` (3) y `ruta.id_ruta` (3). Corrección: constantes de módulo `_UUID_V4`, `_FK_USUARIO` y `_FK_RUTA`. También se unificó `CURRENT_TIMESTAMP` en `_AHORA` para el mismo criterio. Archivo: `backend/app/models/entities.py`.

7. **typescript:S2004 (Alta).** En `MapaRutas` el dibujo de cada parada anidaba funciones a más de cuatro niveles. Corrección: `pintarParada`, `pintarRuta` y `dibujar` quedan en el módulo. El efecto solo importa Leaflet y llama a `dibujar`. Archivo: `frontend/src/pages/MapaRutas.tsx`.

8. **python:S8415 (Media).** `GET /health` lanzaba HTTP 503 sin declararlo. Corrección: `responses={503: ...}`. Archivo: `backend/app/api/routes/health.py`.

9. **python:S5864 y python:S5713 (Media y Baja).** En la cola Redis, `raise _traducir(exc)` elevaba una función que ya lanzaba (el analizador la veía como `None`) y `TimeoutError` era redundante porque ya lo cubre `OSError`. Corrección: `_traducir` devuelve `NoReturn` y se invoca directo; los `except` quedan en `(redis.RedisError, OSError)`. `TimeoutError` de Redis sigue cayendo en `RedisError`. Archivo: `backend/app/optimizacion/cola.py`.

10. **typescript:S6772 (Media, 34).** Entre el texto de la etiqueta y el control había un salto de línea. JSX elimina ese espacio, y la regla lo marca como ambiguo. Corrección: un comentario vacío `{/* */}` entre el texto y el `<input>` o `<select>`, que deja explícito que no hay espacio. El `label` sigue en rejilla con `gap`. Archivos: `frontend/src/pages/LoginPage.tsx`, `DashboardPage.tsx`, `PedidosPage.tsx`, `RutasPage.tsx`, `ConductoresPage.tsx`, `UsuariosPage.tsx`, `FlotaPage.tsx`.

11. **typescript:S6819 (Media, 10).** `role="status"` se reemplazó por `<output>` (rol implícito status) y `role="region"` del mapa por `<section aria-label>`. `.aviso`, `.exito` y `.alerta` usan `display: block` para conservar el bloque que antes daba `<p>`. Archivos: `DashboardPage.tsx`, `MapaRutas.tsx`, `RutasPage.tsx`, `ConductoresPage.tsx`, `PedidosPage.tsx`, `UsuariosPage.tsx`, `FlotaPage.tsx`, `frontend/src/styles.css`.

12. **typescript:S6759, S7735 y S7764 (Baja).** Las props de `MapaRutas`, `Modulo` y `AuthProvider` quedaron en `Readonly`. La condición de minutos de tramo quedó en forma positiva (`== null` primero). `window.setTimeout` pasó a `globalThis.setTimeout`. Archivos: `frontend/src/pages/MapaRutas.tsx`, `frontend/src/App.tsx`, `frontend/src/auth.tsx`, `frontend/src/pages/RutasPage.tsx`.

13. **python:S2245 (hotspots, sin cambio de generador).** Los dos usos de `random` alimentan el cruce y la mutación del algoritmo genético, con semilla del plan y estado restaurado al salir. Es un uso no criptográfico. Decisión: **Safe**. No se cambió el generador: `secrets` no es sembrable y alteraría los planes. El detalle y el comentario para marcarlo en la interfaz de SonarQube están en [04 OWASP V_1_0_0.md](./04%20OWASP%20V_1_0_0.md). Tras el extracto de complejidad, las llamadas quedan en `backend/app/optimizacion/metaheuristica.py` líneas 148 y 156.

Cobertura de apoyo, fuera del porcentaje de SonarQube: se añadieron pruebas de `api.ts`, de roles y del semáforo del mapa, y tres pruebas de que la URL de Postgres sale del entorno. Vitest local (`@vitest/coverage-v8` 2.1.9) midió **8.39 %** de líneas en `frontend/src` (la línea base citaba 6.3 %). `api.ts`, `mapa.ts` y `permissions.ts` quedan al 100 % de líneas. Las páginas siguen sin montarse en el entorno `node` de vitest. El porcentaje que publique SonarQube sigue pendiente de re-escaneo.

## 4. Antes / Después

| Métrica | Antes (línea base 2026-10-26, `efcfcfb`) | Después |
|---|---|---|
| Quality Gate | PASSED (sin condiciones configuradas) | pendiente de re-escaneo |
| Cobertura | 53.1 % | pendiente de re-escaneo |
| Duplicación | 0.0 % | pendiente de re-escaneo |
| ncloc | 5399 | pendiente de re-escaneo |
| Bugs | 0 (confiabilidad A) | pendiente de re-escaneo |
| Vulnerabilidades | 1, Bloqueante, seguridad E | pendiente de re-escaneo |
| Code smells | 110 (Bloqueante 46, Alta 9, Media 47, Baja 8) | pendiente de re-escaneo |
| Security hotspots | 2, Media, `TO_REVIEW` | pendiente de re-escaneo |
| Deuda técnica | 616 min | pendiente de re-escaneo |
| Cobertura frontend (vitest, líneas) | 6.3 % | 8.39 % en medición local v8; el valor de SonarQube queda pendiente de re-escaneo |
| Pruebas backend | 64 pytest en verde | 67 pytest en verde (las 64 originales más 3 de configuración) |
| Pruebas frontend | 7 vitest en verde | 13 vitest en verde (las 7 originales más 6) |

### Comandos para el re-escaneo

Desde la raíz del repositorio, con SonarQube local en marcha y el token del proyecto `pfa-taller`:

```bash
cd backend
pytest --cov=app --cov-report=xml --cov-fail-under=80
cd ../frontend
npx vitest run --coverage
cd ..
sonar-scanner -Dsonar.host.url=http://localhost:9000 -Dsonar.token="$SONAR_TOKEN"
```

`sonar-project.properties` ya apunta a `backend/app` y `frontend/src`, a `backend/coverage.xml` y a `frontend/coverage/lcov.info`, y excluye pruebas, migraciones de Alembic y `backend/app/seed.py`. Después del análisis, marcar los dos hotspots `python:S2245` como Safe con el comentario del reporte OWASP y copiar las métricas nuevas a la columna Después de esta tabla.

[← Volver al README Principal](../../../README.md)
