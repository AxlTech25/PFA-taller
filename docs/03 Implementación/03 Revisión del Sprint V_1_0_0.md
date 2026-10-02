[← Volver al README Principal](../../README.md)

# Revisión del sprint

**Nombre del Proyecto:** EcoLogística Lima – Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Líder del Proyecto:** Carhuapoma Fano, Eilene Elizabeth  
**Sprint:** 1 — Plataforma base  
**Fecha de la revisión:** 30/09/2026 (merge del PR #9) / informe 02/10/2026  
**Versión:** 1.0.0

---

## Historias de Usuario completadas en este Sprint

El Sprint Goal era: *dejar operativa la plataforma base: esquema de datos, autenticación JWT y registro de vehículos*.

| ID | Historia / Enabler | SP | MoSCoW | ¿Done según DoD? | Comentario de la Review |
|---|---|---|---|---|---|
| ENB-003 | Esquema PostgreSQL + PostGIS | 8 | Must | Sí, con evidencia de prueba | Migración 001 crea extensiones, tablas 3FN y GIST de `zona_restriccion`. `test_postgis_y_tablas_del_modelo` y unicidad de placa en PostgreSQL. |
| ENB-002 | Pipeline CI/CD y Quality Gate | 5 | Must | Parcial | CI en GitHub Actions (Ruff + Pytest ≥ 80 % + build frontend). Falta CodeQL/Sonar y deploy a Staging cloud. Se acepta el incremento para no bloquear el Goal; la deuda es IMP-04. |
| US-001 | Iniciar sesión con correo y JWT | 5 | Must | Sí | Login 200 + Bearer; 401 en credencial inválida; evento `login` en `log_auditoria`. Pantalla `LoginPage`. |
| US-004 | Registrar vehículo | 5 | Must | Sí | Alta 201, placa duplicada 409, capacidad inválida 422. El Conductor no registra (403) — anticipo de RBAC que el Sprint 2 endurece. |
| ENB-007 | OpenAPI / Swagger vivo | 3 | Must | Sí | `/docs` y `/openapi.json` listan `/auth/login` y `/vehiculos`. |

**Resultado de la Review:** 26 SP de compromiso **aceptados** para el incremento de producto. ENB-002 se marca Completado-con-deuda (no se rechaza el sprint).

No se mostraron ni se dieron por hechas las historias del Sprint 2 (US-002, US-003, US-005, US-006, US-008, ENB-004), aunque a la fecha de este documento ya existen en `main`.

---

## Demostración del trabajo completado

Demostración a los stakeholders de las funcionalidades implementadas.

**Audiencia:** docente (interesado I-04) y el equipo. **Ambiente:** `docker compose up --build` (API :8000, web :5173, PostGIS :5433).

| Paso | Qué se vio | Historia |
|---|---|---|
| 1 | Arranque de db + api + web sin error de `entrypoint.sh` | ENB-003 / IMP-02 |
| 2 | Login Operador en http://localhost:5173/login | US-001 |
| 3 | Alta de un vehículo (placa nueva, factor de CO₂ > 0) y persistencia al recargar | US-004 |
| 4 | Intento de placa repetida → mensaje “La placa ya se encuentra registrada” | US-004 (Gherkin infeliz) |
| 5 | http://localhost:8000/docs con `POST /auth/login` y `POST /vehiculos` | ENB-007 |
| 6 | Check de CI del PR #9 (Pytest con `--cov-fail-under=80`) | ENB-002 |

**Feedback de stakeholders (equipo + criterio académico):** el Goal es visible sin explicar JWT ni PostGIS: “entro, grabo un vehículo, sigue ahí, Swagger lista la API”. Se pidió dejar documentado que Staging no es un URL público (IMP-04).

---

## Pendientes

| Pendiente | Dueño | Sprint destino |
|---|---|---|
| Staging cloud y CodeQL/Sonar (cierre de DoD D2/D4) | Jorge / Axel | Mejora de ENB-002, no reabre el Sprint 1 |
| Historias de usuarios, bloqueo, conductores y pedidos | Equipo | Sprint 2 (plan sección 10 del artefacto 01) |
| Motor VRPTW, mapa, dashboard | Jorge / Katheryn | Sprints 3–5 |
| Recuperar el desfase de 15 días del calendario | Eilene (PM) | Ritual de arranque en el próximo sprint |

**Incremento B no pedido en esta Review:** cobertura geográfica de pedidos, jornada de 8 h, Leaflet, PDF.

---

## Historial de control de cambios

| Versión | Fecha | Autor | Descripción |
|---|---|---|---|
| 1.0.0 | 02/10/2026 | Equipo EcoLogística Lima | Review del Sprint 1 alineada al PR #9 y al Goal de 26 SP. |

---

[← Volver al README Principal](../../README.md)
