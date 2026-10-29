# EcoLogística Lima

Plataforma web de optimización de rutas sostenibles (VRPTW + Green VRP) para DistriRápido S.A.C., desarrollada como Proyecto Final de Carrera en el curso **Taller de Proyectos 2** de la Universidad Continental.

**Repositorio:** [AxlTech25/PFA-taller](https://github.com/AxlTech25/PFA-taller)  
**Enfoque de gestión:** Híbrido (predictivo + ágil)  
**Duración del MVP:** 6 sprints + cierre (02/09/2026 – 13/12/2026)  
**Versión objetivo:** `v1.0.0-MVP`

### Cronograma de sprints

Calendario vigente: [`05 Cronograma de sprints V_1_0_5.md`](./docs/02%20Planificaci%C3%B3n/05%20Cronograma%20de%20sprints%20V_1_0_5.md). El Sprint 3 arranca el **16/10/2026**.

| Sprint | Inicio | Fin | Hito |
|---|---|---|---|
| 1 | 02/09/2026 | 15/09/2026 | Hito 1 (02/09) |
| 2 | 16/09/2026 | 29/09/2026 | Hito 2 (29/09) |
| 3 | 16/10/2026 | 29/10/2026 | — |
| 4 | 30/10/2026 | 12/11/2026 | Hito 3 (12/11) |
| 5 | 13/11/2026 | 26/11/2026 | — |
| 6 | 27/11/2026 | 10/12/2026 | — |
| Cierre | 11/12/2026 | 13/12/2026 | Hito 4 (13/12) |

#### Actividades por sprint

| Sprint | Actividades |
|---|---|
| 1 | Desplegar esquema PostGIS; pipeline CI/CD; login JWT; registrar vehículo; OpenAPI vivo |
| 2 | Usuarios y roles; bloqueo y consentimiento; menú de flota; registrar conductor; alta de pedido (demo); hardening OWASP |
| 3 | Cobertura Lima Este (migración 004); jornada 8 h; worker Redis 202; vecino más cercano; CodeQL |
| 4 | AG DEAP (150×15 factible); inicio mapa Leaflet; inicio dashboard km/CO₂/soles |
| 5 | Zonas y ruta alternativa; factor árboles RN-018; modo conductor; WCAG; payload 2G/3G |
| 6 | Re-optimización; PDF; confirmar entrega; compensación de carbono; preferencias de cliente (US-009, Could) |
| Cierre | UAT, documentación y presentación (sin historias nuevas) |

Cierre en código: Sprint 1 el 30/09/2026; Sprint 2 el 01/10/2026; Sprint 3 el 17/10/2026 (dentro de la ventana 16/10–29/10); Sprint 4 el 18/10/2026 (antes de la ventana 30/10–12/11; el Hito 3 sigue el 12/11). Actividades, ID y SP: [cronograma de sprints](./docs/02%20Planificaci%C3%B3n/05%20Cronograma%20de%20sprints%20V_1_0_5.md) §3. Responsables: misma fuente, §4.

---

## Equipo

| # | Nombre | Rol |
|---|---|---|
| 1 | Carhuapoma Fano, Eilene Elizabeth | Project Manager / Líder del Equipo |
| 2 | Cruz Salazar, Jorge Luiz | Software Architect / Integrador IA y ML |
| 3 | Estrada Flores, Axel Sebastian | Senior Full-Stack / QA |
| 4 | Huaman Baldeon, Katheryn Elena | Frontend / UI-UX / Optimización |
| 5 | Leon Taza, Brayan Angel | Analista de Base de Datos / Junior Developer |

---

## Fase 01: Inicio del Proyecto

Documentos de constitución, visión, requisitos, arquitectura y restricciones. Carpeta: [`docs/01 Inicio/`](./docs/01%20Inicio/).

| # | Artefacto | Archivo |
|---|---|---|
| 01 | Selección del enfoque | [01. Selección del enfoque del proyecto V_1_0_2.md](./docs/01%20Inicio/01.%20Selecci%C3%B3n%20del%20enfoque%20del%20proyecto%20V_1_0_2.md) |
| 02 | Acta de constitución | [02. Acta de constitución V_1_0_7.md](./docs/01%20Inicio/02.%20Acta%20de%20constituci%C3%B3n%20V_1_0_7.md) |
| 03 | Declaración de la visión | [03. Declaración de la visión V_1_0_1.md](./docs/01%20Inicio/03.%20Declaraci%C3%B3n%20de%20la%20visi%C3%B3n%20V_1_0_1.md) |
| 04 | Supuestos y restricciones | [04. Registro de supuestos y restricciones V_1_0_3.md](./docs/01%20Inicio/04.%20Registro%20de%20supuestos%20y%20restricciones%20V_1_0_3.md) |
| 05 | Registro de interesados | [05. Registro de interesados V_1_0_1.md](./docs/01%20Inicio/05.%20Registro%20de%20interesados%20V_1_0_1.md) |
| 06 | Requisitos funcionales | [06. Requisitos funcionales V_1_0_2.md](./docs/01%20Inicio/06.%20Requisitos%20funcionales%20V_1_0_2.md) |
| 07 | Requisitos no funcionales | [07. Requisitos no funcionales V_1_0_2.md](./docs/01%20Inicio/07.%20Requisitos%20no%20funcionales%20V_1_0_2.md) |
| 08 | Usuarios | [08. Usuarios V_1_0_1.md](./docs/01%20Inicio/08.%20Usuarios%20V_1_0_1.md) |
| 09 | Reglas de negocio | [09. Reglas de negocio V_1_0_1.md](./docs/01%20Inicio/09.%20Reglas%20de%20negocio%20V_1_0_1.md) |
| 10 | Stack tecnológico | [10. Stack tecnológico V_1_0_3.md](./docs/01%20Inicio/10.%20Stack%20tecnol%C3%B3gico%20V_1_0_3.md) |
| 11 | Base de datos | [11. Base de datos V_1_0_1.md](./docs/01%20Inicio/11.%20Base%20de%20datos%20V_1_0_1.md) |
| 12 | Modelo C4 | [12. Modelo C4 V_1_0_1.md](./docs/01%20Inicio/12.%20Modelo%20C4%20V_1_0_1.md) |
| 13 | Restricciones | [13. Restricciones V_1_0_2.md](./docs/01%20Inicio/13.%20Restricciones%20V_1_0_2.md) |

---

## Fase 02: Planificación del Proyecto

Transformación de la línea base de requisitos a backlog ágil, configuración de Jira Software, gestión cuantitativa de riesgos y presupuesto del PFA. Carpeta: [`docs/02 Planificación/`](./docs/02%20Planificaci%C3%B3n/).

| # | Artefacto | Archivo | Puntaje |
|---|---|---|---|
| 01 | Transformación a ágil (Épicas, US, Enablers, DoD) | [01 Transformando a ágil V_1_0_9.md](./docs/02%20Planificaci%C3%B3n/01%20Transformando%20a%20%C3%A1gil%20V_1_0_9.md) | 5.0 |
| 02 | Configuración y evidencias de Jira Software | [02 Artefactos Jira V_1_0_10.md](./docs/02%20Planificaci%C3%B3n/02%20Artefactos%20Jira%20V_1_0_10.md) | 5.0 |
| 03 | Registro de riesgos (PMBOK / CMMI) | [03 Registro de riesgos V_1_0_4.md](./docs/02%20Planificaci%C3%B3n/03%20Registro%20de%20riesgos%20V_1_0_4.md) | 3.0 |
| 04 | Presupuesto del proyecto | [04 Presupuesto del proyecto V_1_0_2.md](./docs/02%20Planificaci%C3%B3n/04%20Presupuesto%20del%20proyecto%20V_1_0_2.md) | 3.0 |
| 05 | Cronograma de sprints | [05 Cronograma de sprints V_1_0_5.md](./docs/02%20Planificaci%C3%B3n/05%20Cronograma%20de%20sprints%20V_1_0_5.md) | — |
| — | Evidencias Jira (capturas recortadas) | [evidencias/](./docs/02%20Planificaci%C3%B3n/evidencias/) | — |

---

## Fase 03: Implementación

Documentos de gestión **separados por sprint**. Carpeta: [`docs/03 Implementación/`](./docs/03%20Implementaci%C3%B3n/).

Los sprints 1, 2 y 4, y la carpeta de gestión `Sprint 3/`, tienen los cuatro archivos de seguimiento con el nombre `V_1_0_0.md`. La carpeta `Sprint 03/` reúne los entregables de la consigna del curso para ese mismo Sprint 3 (ítems 1 a 5). Fechas: [cronograma de sprints](./docs/02%20Planificaci%C3%B3n/05%20Cronograma%20de%20sprints%20V_1_0_5.md).

### Sprint 4

Carpeta: [`docs/03 Implementación/Sprint 4/`](./docs/03%20Implementaci%C3%B3n/Sprint%204/).

| # | Artefacto | Archivo |
|---|---|---|
| 01 | Informe de estado del proyecto | [01 Informe de estado del proyecto V_1_0_0.md](./docs/03%20Implementaci%C3%B3n/Sprint%204/01%20Informe%20de%20estado%20del%20proyecto%20V_1_0_0.md) |
| 02 | Registro de impedimentos | [02 Registro de Impedimentos V_1_0_0.md](./docs/03%20Implementaci%C3%B3n/Sprint%204/02%20Registro%20de%20Impedimentos%20V_1_0_0.md) |
| 03 | Revisión del Sprint | [03 Revisión del Sprint V_1_0_0.md](./docs/03%20Implementaci%C3%B3n/Sprint%204/03%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md) |
| 04 | Retrospectiva del Sprint | [04 Retrospectiva del Sprint V_1_0_0.md](./docs/03%20Implementaci%C3%B3n/Sprint%204/04%20Retrospectiva%20del%20Sprint%20V_1_0_0.md) |

### Sprint 3

Carpeta de gestión: [`docs/03 Implementación/Sprint 3/`](./docs/03%20Implementaci%C3%B3n/Sprint%203/).

| # | Artefacto | Archivo |
|---|---|---|
| 01 | Informe de estado del proyecto | [01 Informe de estado del proyecto V_1_0_0.md](./docs/03%20Implementaci%C3%B3n/Sprint%203/01%20Informe%20de%20estado%20del%20proyecto%20V_1_0_0.md) |
| 02 | Registro de impedimentos | [02 Registro de Impedimentos V_1_0_0.md](./docs/03%20Implementaci%C3%B3n/Sprint%203/02%20Registro%20de%20Impedimentos%20V_1_0_0.md) |
| 03 | Revisión del Sprint | [03 Revisión del Sprint V_1_0_0.md](./docs/03%20Implementaci%C3%B3n/Sprint%203/03%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md) |
| 04 | Retrospectiva del Sprint | [04 Retrospectiva del Sprint V_1_0_0.md](./docs/03%20Implementaci%C3%B3n/Sprint%203/04%20Retrospectiva%20del%20Sprint%20V_1_0_0.md) |

Entregables de la consigna del curso, en [`docs/03 Implementación/Sprint 03/`](./docs/03%20Implementaci%C3%B3n/Sprint%2003/). `Sprint 03/` y `Sprint 3/` son el mismo calendario: la primera guarda estos ítems y la segunda, los informes de gestión.

| # | Artefacto | Archivo |
|---|---|---|
| 01 | Revisión del Sprint | [01 Revisión del Sprint V_1_0_0.md](./docs/03%20Implementaci%C3%B3n/Sprint%2003/01%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md) |
| 02 | Retrospectiva del Sprint | [02 Retrospectiva del Sprint V_1_0_0.md](./docs/03%20Implementaci%C3%B3n/Sprint%2003/02%20Retrospectiva%20del%20Sprint%20V_1_0_0.md) |
| 03 | Evaluación de calidad de código (SonarQube) | [03 Calidad de código V_1_0_0.md](./docs/03%20Implementaci%C3%B3n/Sprint%2003/03%20Calidad%20de%20c%C3%B3digo%20V_1_0_0.md) |
| 04 | Evaluación OWASP Top 10 2025 | [04 OWASP V_1_0_0.md](./docs/03%20Implementaci%C3%B3n/Sprint%2003/04%20OWASP%20V_1_0_0.md) |
| 05 | Evaluación de accesibilidad WCAG 2.2 AA | [05 WCAG V_1_0_0.md](./docs/03%20Implementaci%C3%B3n/Sprint%2003/05%20WCAG%20V_1_0_0.md) |

### Sprint 2

Carpeta: [`docs/03 Implementación/Sprint 2/`](./docs/03%20Implementaci%C3%B3n/Sprint%202/).

| # | Artefacto | Archivo |
|---|---|---|
| 01 | Informe de estado del proyecto | [01 Informe de estado del proyecto V_1_0_0.md](./docs/03%20Implementaci%C3%B3n/Sprint%202/01%20Informe%20de%20estado%20del%20proyecto%20V_1_0_0.md) |
| 02 | Registro de impedimentos | [02 Registro de Impedimentos V_1_0_0.md](./docs/03%20Implementaci%C3%B3n/Sprint%202/02%20Registro%20de%20Impedimentos%20V_1_0_0.md) |
| 03 | Revisión del Sprint | [03 Revisión del Sprint V_1_0_0.md](./docs/03%20Implementaci%C3%B3n/Sprint%202/03%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md) |
| 04 | Retrospectiva del Sprint | [04 Retrospectiva del Sprint V_1_0_0.md](./docs/03%20Implementaci%C3%B3n/Sprint%202/04%20Retrospectiva%20del%20Sprint%20V_1_0_0.md) |

### Sprint 1

Carpeta: [`docs/03 Implementación/Sprint 1/`](./docs/03%20Implementaci%C3%B3n/Sprint%201/).

| # | Artefacto | Archivo |
|---|---|---|
| 01 | Informe de estado del proyecto | [01 Informe de estado del proyecto V_1_0_0.md](./docs/03%20Implementaci%C3%B3n/Sprint%201/01%20Informe%20de%20estado%20del%20proyecto%20V_1_0_0.md) |
| 02 | Registro de impedimentos | [02 Registro de Impedimentos V_1_0_0.md](./docs/03%20Implementaci%C3%B3n/Sprint%201/02%20Registro%20de%20Impedimentos%20V_1_0_0.md) |
| 03 | Revisión del Sprint | [03 Revisión del Sprint V_1_0_0.md](./docs/03%20Implementaci%C3%B3n/Sprint%201/03%20Revisi%C3%B3n%20del%20Sprint%20V_1_0_0.md) |
| 04 | Retrospectiva del Sprint | [04 Retrospectiva del Sprint V_1_0_0.md](./docs/03%20Implementaci%C3%B3n/Sprint%201/04%20Retrospectiva%20del%20Sprint%20V_1_0_0.md) |

---

## Stack del MVP

| Capa | Tecnología |
|---|---|
| Backend | Python 3.11+ / FastAPI |
| Frontend | React 18 + TypeScript + Vite |
| Base de datos | PostgreSQL 16 + PostGIS |
| Optimización | Worker Python aparte de la API. Sprint 4: algoritmo genético con DEAP, comparado con el vecino más cercano |
| Cola | Redis 7 |
| Mapas | Leaflet + OpenStreetMap |
| ALM | Jira Software + GitHub |

---

## Alcance implementado (Sprint 4)

Los sprints 1 a 3 siguen vigentes. Esta entrega cierra en código el motor (algoritmo genético VRPTW + Green VRP en el worker, comparado con el vecino más cercano) e inicia el mapa Leaflet/OSM y el tablero. US-012 y US-014 no se dan por cerradas. No hay URL de Staging.

| ID | Entrega |
|---|---|
| ENB-003 | Migraciones Alembic del modelo PostgreSQL 16 + PostGIS, cuatro vehículos de demostración y dos clientes de demostración (con y sin consentimiento) |
| ENB-002 | GitHub Actions con Ruff, Pytest (cobertura mínima 80 %) y la compilación del frontend |
| US-001 | `POST /auth/login` con JWT y evento `login` en `log_auditoria` |
| US-002 | Alta, desactivación y cambio de rol. Solo el Administrador escribe; el Gerente consulta; el Operador recibe 403 |
| US-003 | Al tercer intento fallido la cuenta pasa a `BLOQUEADO` por 15 minutos y el login responde 423. Un pedido sin `consentimiento_datos` se rechaza |
| US-004 | Alta de vehículo para Administrador u Operador |
| US-005 | Listado y actualización de estado o factor de CO₂, con menú Flota, Conductores, Pedidos y Usuarios |
| US-006 | Alta de conductor con DNI único, licencia, horario y punto de partida |
| US-008 A | Alta de pedido en estado `PENDIENTE` usando el cliente de demostración. Sin módulo de clientes |
| US-008 B | Cobertura de San Juan de Lurigancho, El Agustino, Santa Anita y Ate; punto de referencia y `georreferencia_aproximada` |
| US-007 | Confirmación de ruta: rechazo si la conducción del día supera 8 h (Ley N.º 30224) y descanso de 1 h cada 4 h |
| ENB-006 | `POST /optimizaciones` responde 202. El worker (`python -m app.worker`) calcula fuera del request. Redis caído → 503, sin job huérfano |
| ENB-001 / US-010 | Algoritmo genético (DEAP) en el worker, rutas en borrador, pico y placa, congestión y comparación con el vecino más cercano. Bench 150×15 en CI. La corrida en Staging sigue pendiente |
| US-012 | Inicio: mapa Leaflet/OSM con trazado, paradas, ETA por tramo y semáforo. Si las teselas fallan, queda la tabla |
| US-014 | Inicio del tablero (km, CO₂, combustible, soles, % de ventanas). El factor de árboles (RN-018) no está ratificado |
| ENB-004 | 403 por rol, rechazo de inyección obvia en formularios y auditoría de login, vehículo, conductor y pedido |
| ENB-007 | OpenAPI en vivo en `/docs`. `GET /clientes` es catálogo de demostración, sin altas |
| IMP-04 | Workflow CodeQL. **Staging en la nube sigue pendiente** (no hay secreto de Railway/Render) |

## Cómo ejecutarlo

### 1. Variables de entorno

```bash
cp .env.example .env
```

Edite `.env` y defina `JWT_SECRET` y las contraseñas `SEED_*` (mínimo 8 caracteres). Esas contraseñas solo sirven para la demostración en su máquina. Si una contraseña queda vacía, la carga inicial omite ese usuario. Use caracteres seguros para una URL en `POSTGRES_PASSWORD` si va a levantar Docker Compose.

Los vehículos de demostración no dependen de esas contraseñas: la migración `002` los inserta al aplicar Alembic. La migración `003` inserta los clientes `Bodega El Ahorro` (con consentimiento) y `Bodega Los Pinos` (sin consentimiento). La migración `004` agrega la cobertura de Lima Este, la cola de optimización y los parámetros de velocidad y congestión.

`REDIS_URL` apunta al Redis de la cola. Compose lo reescribe a `redis://redis:6379/0`.

### 2. Con Docker Compose

Requiere Docker con el complemento Compose.

```bash
docker compose up --build
```

- Interfaz: http://localhost:5173
- API y Swagger: http://localhost:8000/docs
- PostgreSQL 16 + PostGIS en el host: puerto **5433** (el contenedor sigue escuchando 5432 por dentro). Así no choca con otro Postgres local en 5432.
- Redis en el host: puerto 6379. El worker es otro contenedor y no corre dentro del request de la API.

Compose aplica las migraciones y, si `SEED_ON_STARTUP=true`, carga los usuarios cuyas contraseñas estén definidas.

### 3. Sin Docker

Requiere Python 3.11+, Node.js 20+ y PostgreSQL 16 con PostGIS. El usuario de la base debe poder crear las extensiones `postgis` y `uuid-ossp`.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
alembic upgrade head
SEED_ON_STARTUP=true python -m app.seed
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

En otra terminal, el worker (hace falta Redis en `localhost:6379`):

```bash
cd backend
python -m app.worker
```

Y el frontend:

```bash
cd frontend
npm install
npm run dev
```

El servidor de Vite reenvía las llamadas de la interfaz hacia `http://localhost:8000`.

`backend/entrypoint.sh` está versionado con saltos de línea LF (`.gitattributes`). En Windows, conserve ese formato: un CRLF rompe el arranque del contenedor.

### 4. Recorrido de punta a punta

1. Abra http://localhost:5173 e inicie sesión con `SEED_ADMIN_EMAIL`. En **Usuarios** cree una cuenta con rol Conductor.
2. Cierre sesión e ingrese con `SEED_OPERADOR_EMAIL`. El menú muestra Flota, Conductores, Pedidos, Rutas y Tablero.
3. En **Flota** pase `DMO-101` a Mantenimiento o cambie su factor de CO₂ y pulse Guardar.
4. En **Conductores** registre DNI, licencia, horario y coordenadas de partida.
5. En **Pedidos** elija Bodega El Ahorro, escriba el punto de referencia `frente a la bodega El Ahorro` y registre. Queda en Pendiente, en San Juan de Lurigancho, con georreferencia aproximada. Bodega Los Pinos se rechaza por falta de consentimiento. Una coordenada fuera de Lima Este (por ejemplo latitud `-12.1219`, longitud `-77.0300`) no crea el pedido.
6. En **Rutas** elija la fecha del pedido y pulse **Generar rutas**. La API responde enseguida; el worker, en otro proceso, corre el algoritmo genético y compara el costo verde con el vecino más cercano. El plan queda en Borrador. El mapa dibuja la partida y las paradas; si OpenStreetMap no carga, queda la tabla. **Confirmar ruta** asigna los pedidos si la conducción no pasa de 8 horas.
7. En **Tablero**, la misma fecha muestra km, CO₂, combustible, soles y el porcentaje de ventanas. Un día sin rutas dice «Sin datos de operación para el período seleccionado». Los árboles equivalentes quedan en blanco hasta ratificar el factor de RN-018.
8. Tres contraseñas incorrectas bloquean la cuenta: la API responde 423 durante 15 minutos.
9. El usuario Conductor ve Flota (solo consulta) y Modo conductor. No entra a Usuarios, ni a Rutas, ni al Tablero, ni puede editar la flota (HTTP 403).
10. Abra http://localhost:8000/docs para el contrato OpenAPI. `GET /clientes` es solo el catálogo de demostración.

No hay dirección pública de Staging. El análisis CodeQL corre en GitHub Actions (`.github/workflows/codeql.yml`).

Una cuenta inactiva responde HTTP 403. El Administrador no puede desactivar su propia cuenta.

### Pruebas

```bash
cd backend && pytest --cov=app --cov-fail-under=80
cd frontend && npm test && npm run build
```

`TEST_DATABASE_URL` apunta a una base de pruebas. El conftest la crea si el usuario de PostgreSQL puede hacerlo y luego aplica Alembic. No use la base de desarrollo como base de pruebas: los tests revierten sus datos, pero la migración sí permanece.

## Convención de versionado

Los artefactos documentales usan versionado semántico en el encabezado y el historial (`Versión: X.Y.Z`). En la Fase 03 los informes de seguimiento viven en la carpeta del sprint (`Sprint 1/`, `Sprint 2/`, `Sprint 3/`, `Sprint 4/`) con el nombre `V_1_0_0.md`. La consigna del Sprint 3 usa además la carpeta `Sprint 03/`.
