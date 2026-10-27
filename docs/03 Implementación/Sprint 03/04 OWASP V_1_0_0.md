[← Volver al README Principal](../../../README.md)

# Reporte de Seguridad OWASP Top 10 (2025)

**Nombre del Proyecto:** EcoLogística Lima – Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Herramienta de Escaneo:** SonarQube / SonarCloud  

Línea base: escaneo local SonarQube Community del 2026-10-26 sobre `main` (`efcfcfb`), proyecto `pfa-taller`. Este reporte cruza ese resultado con la revisión del código (JWT, bcrypt, RBAC, bloqueo de cuenta, CORS, secretos y dependencias) y con la remediación aplicada el 2026-10-27. La confirmación numérica del escáner queda pendiente de re-escaneo; los comandos están en [03 Calidad de código V_1_0_0.md](./03%20Calidad%20de%20c%C3%B3digo%20V_1_0_0.md).

## 1. Matriz de Cumplimiento OWASP Top 10 2025

| Categoría OWASP 2025 | Estado en Proyecto (Limpio / Vulnerable / Bajo Revisión) | Hallazgos de SonarQube |
|---|---|---|
| A01:2025-Broken Access Control | Limpio | Sin hallazgos. El acceso lo decide `require_roles` en `backend/app/core/deps.py`: cada ruta declara el rol, un rol distinto recibe HTTP 403 y la interfaz oculta el módulo. Hay pruebas de operador, gerente, auditor y conductor. |
| A02:2025-Cryptographic Failures | Bajo Revisión | Dos hotspots `python:S2245` (Media, `TO_REVIEW`) en el algoritmo genético. Las contraseñas de usuario se guardan con bcrypt y el acceso usa JWT HS256. La decisión de este cambio es marcar el generador como Safe; SonarQube lo seguirá mostrando en revisión hasta confirmarlo en la interfaz. |
| A03:2025-Injection | Limpio | Sin hallazgos. Las consultas van por SQLAlchemy. El `text()` del factor de árboles usa parámetro enlazado. `sanitizacion.py` rechaza patrones obvios de script o SQL y deja auditoría `entrada_rechazada`. |
| A04:2025-Insecure Design | Limpio | Sin hallazgos. El diseño ya separa la API del worker, exige consentimiento para el pedido, corta la jornada a 8 h y bloquea la cuenta al tercer fallo. |
| A05:2025-Security Misconfiguration | Limpio | La línea base traía 1 vulnerabilidad Bloqueante `secrets:S6698` (contraseña de PostgreSQL en `backend/app/core/config.py:12`). Quedó fuera del código de la aplicación: llega por `DATABASE_URL` o `POSTGRES_PASSWORD`. CORS se registra como middleware externo. Cabeceras `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy` y `Permissions-Policy` siguen en `SecurityHeadersMiddleware`. |
| A06:2025-Vulnerable and Outdated Components | Bajo Revisión | SonarQube no reportó CVEs. `npm audit` del frontend, fuera de esa línea base, marca 9 avisos (3 críticos y 1 alto en vitest/vite/tinypool, de servidor de desarrollo, y avisos medios en esbuild y react-router). No se subieron esas versiones en este cambio para conservar el comportamiento ya probado. |
| A07:2025-Identification and Authentication Failures | Limpio | Sin hallazgos de SonarQube sobre el login. `POST /auth/login` verifica bcrypt, firma JWT con `JWT_SECRET`, responde 403 si la cuenta está inactiva y 423 con `Retry-After` si está bloqueada. Al tercer intento fallido el estado pasa a `BLOQUEADO` 15 minutos. |
| A08:2025-Software and Data Integrity Failures | Limpio | Sin hallazgos. No hay deserialización de código ni de objetos no confiables. El plan de rutas se persiste en tablas propias. CI corre Ruff, pytest con umbral 80 % y el build del frontend. |
| A09:2025-Security Logging and Monitoring Failures | Limpio | Sin hallazgos. `log_auditoria` registra login, login fallido, bloqueo, rechazo de entrada y las altas de vehículo, conductor, pedido y optimización, con IP cuando es válida. |
| A10:2025-Server-Side Request Forgery (SSRF) | Limpio | Sin hallazgos. El backend no abre URLs elegidas por el usuario. El mapa pide teselas a `https://tile.openstreetmap.org` con una plantilla fija en el navegador. |

## 2. Detalles de Security Hotspots y Vulnerabilidades Críticas

- **Hotspot #1:** `python:S2245`, debilidad criptográfica, severidad Media, estado de la línea base `TO_REVIEW`. Ubicación original: `backend/app/optimizacion/metaheuristica.py:167` (`random.random()` en el cruce). Ubicación tras extraer la complejidad cognitiva: línea 148, función `_cruzar`. El generador decide si dos individuos del algoritmo genético se recombinan (probabilidad 0.7). Mitigación: se clasifica como **Safe**. El módulo siembra `random` con `inst.semilla`, guarda el estado global y lo restaura al terminar. No interviene en contraseñas, JWT ni tokens. Sustituirlo por `secrets` rompería la reproducibilidad del plan y usaría un generador pensado para secretos en un sorteo de rutas. En SonarQube: Security Hotspots, abrir este punto y marcarlo Safe con el comentario «PRNG del algoritmo genético VRPTW, sembrado y restaurado; no protege credenciales».

- **Hotspot #2:** `python:S2245`, el mismo mensaje, Media, `TO_REVIEW`. Ubicación original: `backend/app/optimizacion/metaheuristica.py:172`. Ubicación actual: línea 156, función `_mutar`. `random.random()` decide si un hijo se muta (`mutShuffleIndexes`, probabilidad 0.3). Misma mitigación que el hotspot #1: uso no criptográfico, decisión **Safe**, misma marca en la interfaz de SonarQube. El comentario del módulo deja escrita esa decisión junto al código.

- **Vulnerabilidad:** `secrets:S6698`, Bloqueante. Ubicación de la línea base: `backend/app/core/config.py:12`. El valor por defecto de `database_url` incluía la contraseña de PostgreSQL de la demostración dentro del código fuente. SonarQube pedía cambiarla y quitarla del código. Mitigación aplicada: el código ya no contiene esa contraseña. `Settings` toma `DATABASE_URL` del entorno. Si no está definida, arma la URL con `POSTGRES_PASSWORD` (y el resto de `POSTGRES_*`), codificando usuario y clave para la URL. Docker Compose sigue inyectando `DATABASE_URL` a partir de `POSTGRES_PASSWORD` (el archivo `.env` o el valor de demostración del compose). `.env.example` sigue documentando la copia local. CI sigue pasando `TEST_DATABASE_URL` al job. La prueba `tests/test_config_entorno.py` cubre la URL explícita, la clave leída del entorno y el caso sin contraseña. El valor de demostración permanece en `.env.example`, `docker-compose.yml`, `.github/workflows/ci.yml` y el respaldo de `backend/tests/conftest.py` (excluido del análisis por `sonar.exclusions`) para que Compose, el ejemplo y las pruebas sigan arrancando.

Queda fuera de la línea base, y sin cambio en este entregable, el valor de desarrollo de `JWT_SECRET` (`cambie-esta-clave-en-local`) en `config.py`. El README y `.env.example` piden reemplazarlo en la máquina local. SonarQube no lo marcó. Las pruebas fijan `JWT_SECRET` antes de importar la aplicación.

[← Volver al README Principal](../../../README.md)
