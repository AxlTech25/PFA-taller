# EcoLogística Lima

Plataforma web de optimización de rutas sostenibles (VRPTW + Green VRP) para DistriRápido S.A.C., desarrollada como Proyecto Final de Carrera en el curso **Taller de Proyectos 2** de la Universidad Continental.

**Repositorio:** [AxlTech25/PFA-taller](https://github.com/AxlTech25/PFA-taller)  
**Enfoque de gestión:** Híbrido (predictivo + ágil)  
**Duración del MVP:** 12.4 semanas / 6 sprints + cierre (02/09/2026 – 27/11/2026)  
**Versión objetivo:** `v1.0.0-MVP`

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
| 02 | Acta de constitución | [02. Acta de constitución V_1_0_5.md](./docs/01%20Inicio/02.%20Acta%20de%20constituci%C3%B3n%20V_1_0_5.md) |
| 03 | Declaración de la visión | [03. Declaración de la visión V_1_0_1.md](./docs/01%20Inicio/03.%20Declaraci%C3%B3n%20de%20la%20visi%C3%B3n%20V_1_0_1.md) |
| 04 | Supuestos y restricciones | [04. Registro de supuestos y restricciones V_1_0_2.md](./docs/01%20Inicio/04.%20Registro%20de%20supuestos%20y%20restricciones%20V_1_0_2.md) |
| 05 | Registro de interesados | [05. Registro de interesados V_1_0_1.md](./docs/01%20Inicio/05.%20Registro%20de%20interesados%20V_1_0_1.md) |
| 06 | Requisitos funcionales | [06. Requisitos funcionales V_1_0_1.md](./docs/01%20Inicio/06.%20Requisitos%20funcionales%20V_1_0_1.md) |
| 07 | Requisitos no funcionales | [07. Requisitos no funcionales V_1_0_1.md](./docs/01%20Inicio/07.%20Requisitos%20no%20funcionales%20V_1_0_1.md) |
| 08 | Usuarios | [08. Usuarios V_1_0_1.md](./docs/01%20Inicio/08.%20Usuarios%20V_1_0_1.md) |
| 09 | Reglas de negocio | [09. Reglas de negocio V_1_0_1.md](./docs/01%20Inicio/09.%20Reglas%20de%20negocio%20V_1_0_1.md) |
| 10 | Stack tecnológico | [10. Stack tecnológico V_1_0_2.md](./docs/01%20Inicio/10.%20Stack%20tecnol%C3%B3gico%20V_1_0_2.md) |
| 11 | Base de datos | [11. Base de datos V_1_0_1.md](./docs/01%20Inicio/11.%20Base%20de%20datos%20V_1_0_1.md) |
| 12 | Modelo C4 | [12. Modelo C4 V_1_0_1.md](./docs/01%20Inicio/12.%20Modelo%20C4%20V_1_0_1.md) |
| 13 | Restricciones | [13. Restricciones V_1_0_2.md](./docs/01%20Inicio/13.%20Restricciones%20V_1_0_2.md) |

---

## Fase 02: Planificación del Proyecto

Transformación de la línea base de requisitos a backlog ágil, configuración de Jira Software, gestión cuantitativa de riesgos y presupuesto del PFA. Carpeta: [`docs/02 Planificación/`](./docs/02%20Planificaci%C3%B3n/).

| # | Artefacto | Archivo | Puntaje |
|---|---|---|---|
| 01 | Transformación a ágil (Épicas, US, Enablers, DoD) | [01 Transformando a ágil V_1_0_3.md](./docs/02%20Planificaci%C3%B3n/01%20Transformando%20a%20%C3%A1gil%20V_1_0_3.md) | 5.0 |
| 02 | Configuración y evidencias de Jira Software | [02 Artefactos Jira V_1_0_5.md](./docs/02%20Planificaci%C3%B3n/02%20Artefactos%20Jira%20V_1_0_5.md) | 5.0 |
| 03 | Registro de riesgos (PMBOK / CMMI) | [03 Registro de riesgos V_1_0_4.md](./docs/02%20Planificaci%C3%B3n/03%20Registro%20de%20riesgos%20V_1_0_4.md) | 3.0 |
| 04 | Presupuesto del proyecto | [04 Presupuesto del proyecto V_1_0_2.md](./docs/02%20Planificaci%C3%B3n/04%20Presupuesto%20del%20proyecto%20V_1_0_2.md) | 3.0 |
| — | Evidencias Jira (capturas recortadas) | [evidencias/](./docs/02%20Planificaci%C3%B3n/evidencias/) | — |

---

## Stack del MVP

| Capa | Tecnología |
|---|---|
| Backend | Python 3.11+ / FastAPI |
| Frontend | React 18 + TypeScript + Vite |
| Base de datos | PostgreSQL 16 + PostGIS |
| Optimización | DEAP / OR-Tools (VRPTW + Green VRP) |
| Mapas | Leaflet + OpenStreetMap |
| ALM | Jira Software + GitHub |

---

## Alcance implementado (Sprint 1)

Esta entrega cubre el esquema de base de datos y el backlog del Sprint 1. El Sprint 2 (usuarios y roles, bloqueo de 15 minutos, edición de flota, conductores, pedidos y el endurecimiento completo de ENB-004) queda diferido, igual que el motor de optimización, el mapa y el dashboard.

| ID | Entrega |
|---|---|
| ENB-003 | Migraciones Alembic del modelo PostgreSQL 16 + PostGIS (tablas de seguridad y flota, índices espaciales) y cuatro vehículos de demostración (`DMO-101`, `DMO-102`, `DMO-201`, `DMO-301`) |
| ENB-002 | GitHub Actions con Ruff, Pytest (cobertura mínima 80 %) y la compilación del frontend |
| US-001 | `POST /auth/login` con JWT. Un intento fallido incrementa `intentos_fallidos` y deja un evento `login_fallido`; el éxito registra `login`. El bloqueo automático de 15 minutos (US-003) no está activo |
| US-004 | Alta de vehículo para Administrador u Operador, con listado de la flota |
| ENB-007 | OpenAPI en vivo en `/docs` |

Las tablas de conductor, cliente, pedido, ruta y auditoría existen en el esquema porque el documento de base de datos las define. Sus pantallas y endpoints llegan en sprints posteriores.

## Cómo ejecutarlo

### 1. Variables de entorno

```bash
cp .env.example .env
```

Edite `.env` y defina `JWT_SECRET` y las contraseñas `SEED_*` (mínimo 8 caracteres). Esas contraseñas solo sirven para la demostración en su máquina. Si una contraseña queda vacía, la carga inicial omite ese usuario. Use caracteres seguros para una URL en `POSTGRES_PASSWORD` si va a levantar Docker Compose.

Los vehículos de demostración no dependen de esas contraseñas: la migración `002` los inserta al aplicar Alembic.

### 2. Con Docker Compose

Requiere Docker con el complemento Compose.

```bash
docker compose up --build
```

- Interfaz: http://localhost:5173
- API y Swagger: http://localhost:8000/docs
- PostgreSQL 16 + PostGIS: puerto 5432

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

En otra terminal:

```bash
cd frontend
npm install
npm run dev
```

El servidor de Vite reenvía las llamadas de la interfaz hacia `http://localhost:8000`.

### 4. Recorrido de punta a punta

1. Abra http://localhost:5173 e inicie sesión con `SEED_OPERADOR_EMAIL` y la contraseña que definió.
2. En **Flota** aparecen las unidades de demostración `DMO-101`, `DMO-102`, `DMO-201` y `DMO-301`.
3. Registre un vehículo. La API confirma el alta y la placa queda en el listado. Una placa repetida responde «La placa ya se encuentra registrada».
4. Abra http://localhost:8000/docs para consultar el contrato OpenAPI de login y vehículos.

Un conductor puede consultar la flota y recibe HTTP 403 si intenta registrarla. Una cuenta ya marcada como bloqueada o inactiva también recibe HTTP 403.

### Pruebas

```bash
cd backend && pytest --cov=app --cov-fail-under=80
cd frontend && npm test && npm run build
```

`TEST_DATABASE_URL` apunta a una base de pruebas. El conftest la crea si el usuario de PostgreSQL puede hacerlo y luego aplica Alembic. No use la base de desarrollo como base de pruebas: los tests revierten sus datos, pero la migración sí permanece.

## Convención de versionado

Los artefactos documentales usan versionado semántico en el nombre de archivo: `Nombre V_X_Y_Z.md`.
