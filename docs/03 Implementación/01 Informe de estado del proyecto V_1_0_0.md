[← Volver al README Principal](../../README.md)

# Informe de estado del proyecto

**Nombre del Proyecto:** EcoLogística Lima – Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Líder del Proyecto:** Carhuapoma Fano, Eilene Elizabeth  
**Sprint:** 1  
**Fechas planificadas:** 02/09/2026 – 15/09/2026  
**Fecha del informe:** 02/10/2026  
**Versión:** 1.0.0

---

## 1. Estado general de la iteración

El Sprint 1 cerró el **100 % del compromiso de 26 SP** (ENB-003, ENB-002, US-001, US-004, ENB-007). El incremento está en `main` desde el merge del [PR #9](https://github.com/AxlTech25/PFA-taller/pull/9) (30/09/2026).

| Indicador | Plan | Real al cierre |
|---|---|---|
| Story Points comprometidos | 26 | 26 aceptados en código y pruebas |
| Sprint Goal | Login + flota + esquema + OpenAPI + CI | Cumplido en entorno local (Docker Compose) |
| Quality Gate | Pytest cobertura ≥ 80 %, Ruff, build del frontend | Job `CI` en GitHub Actions (`.github/workflows/ci.yml`) |
| Staging en la nube | DoD D4 (Railway/Render) | **No desplegado.** El “Staging” de este sprint es Compose en máquina del equipo (`localhost:5173` / `localhost:8000`) |
| Desfase calendario | Cierre 15/09/2026 | Implementación fusionada el 30/09/2026 (15 días de retraso; ver impedimento IMP-03) |

El repositorio ya contiene además el Sprint 2 (PR #10, 01/10/2026). **Este informe cubre solo el alcance del Sprint 1.** El estado de usuarios, conductores y pedidos se documentará en los artefactos del Sprint 2.

---

## Historias de Usuario completadas en este Sprint

Compromiso del artefacto [01 Transformando a ágil V_1_0_5.md](../02%20Planificaci%C3%B3n/01%20Transformando%20a%20%C3%A1gil%20V_1_0_5.md), sección 9.

| ID | Título | SP | Estado | Evidencia en el repositorio |
|---|---|---|---|---|
| ENB-003 | Esquema PostgreSQL + PostGIS | 8 | Completado | `backend/alembic/versions/001_esquema_inicial.py` (extensiones PostGIS y `uuid-ossp`, tablas del documento 11, índice GIST `idx_zona_geometria`). Prueba `backend/tests/test_esquema.py`. |
| ENB-002 | Pipeline CI/CD y Quality Gate | 5 | Completado con deuda | `.github/workflows/ci.yml`: Ruff, Pytest `--cov-fail-under=80`, `npm test` y `npm run build`. No incluye CodeQL/SonarQube ni deploy automático a Staging (DoD D2/D4 parcial). |
| US-001 | Autenticación JWT | 5 | Completado | `POST /auth/login` (`backend/app/api/routes/auth.py`), pantalla `frontend/src/pages/LoginPage.tsx`. Entrega Bearer JWT, audita `login`, responde 401 sin revelar si el correo existe. |
| US-004 | Registrar vehículo | 5 | Completado | `POST /vehiculos`, placa única, capacidad > 0, UI `frontend/src/pages/FlotaPage.tsx`. Semilla de flota demo en migración `002_vehiculos_demo.py`. |
| ENB-007 | OpenAPI vivo | 3 | Completado | FastAPI expone `/docs` y `/openapi.json`. Prueba `backend/tests/test_openapi.py`. |

**Total: 26 / 26 SP.**

Criterio de éxito declarado: un Operador inicia sesión, registra un vehículo con factor de CO₂ y `/docs` lista los endpoints. Se verifica en local con `docker compose up --build` y usuarios `SEED_*` del `.env`.

---

## Demostración del trabajo completado

Demostración a los stakeholders de las funcionalidades implementadas.

**Stakeholders:** docente del curso (I-04, Registro de interesados) y el equipo EcoLogística Lima. Entorno: Docker Compose, no un Staging público.

**Guion ejecutado (Sprint 1):**

1. `cp .env.example .env`, definir `JWT_SECRET` y contraseñas `SEED_OPERADOR_*`.
2. `docker compose up --build`.
3. Abrir http://localhost:5173, iniciar sesión como Operador.
4. En **Flota**, dar de alta un vehículo (placa, tipo, capacidad, consumo, factor de CO₂, año).
5. Cerrar sesión, volver a entrar: el vehículo persiste (PostgreSQL).
6. Abrir http://localhost:8000/docs: aparecen `/auth/login` y `/vehiculos`.
7. Mostrar el check verde de GitHub Actions en el PR #9.

No se demostró en este sprint el dashboard de sostenibilidad, el mapa ni el motor de rutas (fuera de alcance).

---

## Pendientes

Pendientes **del Sprint 1** (no del producto completo):

| Ítem | Tipo | Destino |
|---|---|---|
| Despliegue a Staging en la nube (DoD D4) | Técnico | Sigue abierto al cierre del Sprint 2 (IMP-04; destino Sprint 3 / Hito 3) |
| CodeQL o SonarQube en el Quality Gate (DoD D2) | Técnico | Sigue abierto (IMP-04) |
| Automatizar escenarios Gherkin además de Pytest (DoD D6) | Calidad | Transversal |
| Impedimento IMP-03 (desfase de calendario) | Proceso | Retrospectiva: arrancar el sprint en la fecha del Acta |

Alcance de producto que **no** pertenecía al Sprint 1: US-002, US-003, US-005, US-006, US-008 A y ENB-004 se cerraron en el Sprint 2 ([informe V_1_1_0](./01%20Informe%20de%20estado%20del%20proyecto%20V_1_1_0.md)). El motor VRPTW sigue en Sprints 3–4.

---

## 2. Organización del código (criterio 5 de la rúbrica)

La consigna ilustra `src/frontend` y `src/backend`. El equipo adoptó carpetas hermanas en la raíz, equivalentes y alineadas a Docker:

| Carpeta | Contenido |
|---|---|
| `frontend/` | SPA React 18 + TypeScript + Vite |
| `backend/` | API FastAPI, Alembic, Pytest |
| `.github/workflows/` | Pipeline CI |
| `docs/` | Artefactos académicos |

`.gitignore` en la raíz excluye `.env`, `node_modules/`, `.venv/`, coberturas y cachés. Las variables de entorno se documentan en `.env.example` (no se versionan secretos).

---

## 3. Historial de control de cambios

| Versión | Fecha | Autor | Descripción |
|---|---|---|---|
| 1.0.0 | 02/10/2026 | Equipo EcoLogística Lima | Estado al cierre del Sprint 1: 26/26 SP, PR #9, deuda de Staging cloud y CodeQL. |

---

[← Volver al README Principal](../../README.md)
