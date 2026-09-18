# EcoLogística Lima

Plataforma web de optimización de rutas sostenibles (VRPTW + Green VRP) para DistriRápido S.A.C., desarrollada como Proyecto Final de Carrera en el curso **Taller de Proyectos 2** de la Universidad Continental.

**Repositorio:** [AxlTech25/PFA-taller](https://github.com/AxlTech25/PFA-taller)  
**Enfoque de gestión:** Híbrido (predictivo + ágil)  
**Duración del MVP:** 14 semanas / 4 iteraciones / 7 sprints de 2 semanas  
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

Documentos de constitución, visión, requisitos, arquitectura y restricciones.

| # | Artefacto | Archivo |
|---|---|---|
| 01 | Selección del enfoque | [01. Selección del enfoque del proyecto V_1_0_0.md](./01%20Inicio/01.%20Selecci%C3%B3n%20del%20enfoque%20del%20proyecto%20V_1_0_0.md) |
| 02 | Acta de constitución | [02. Acta de constitución V_1_0_0.md](./01%20Inicio/02.%20Acta%20de%20constituci%C3%B3n%20V_1_0_0.md) |
| 03 | Declaración de la visión | [03. Declaración de la visión V_1_0_0.md](./01%20Inicio/03.%20Declaraci%C3%B3n%20de%20la%20visi%C3%B3n%20V_1_0_0.md) |
| 04 | Supuestos y restricciones | [04. Registro de supuestos y restricciones V_1_0_0.md](./01%20Inicio/04.%20Registro%20de%20supuestos%20y%20restricciones%20V_1_0_0.md) |
| 05 | Registro de interesados | [05. Registro de interesados V_1_0_0.md](./01%20Inicio/05.%20Registro%20de%20interesados%20V_1_0_0.md) |
| 06 | Requisitos funcionales | [06. Requisitos funcionales V_1_0_0.md](./01%20Inicio/06.%20Requisitos%20funcionales%20V_1_0_0.md) |
| 07 | Requisitos no funcionales | [07. Requisitos no funcionales V_1_0_0.md](./01%20Inicio/07.%20Requisitos%20no%20funcionales%20V_1_0_0.md) |
| 08 | Usuarios | [08. Usuarios V_1_0_0.md](./01%20Inicio/08.%20Usuarios%20V_1_0_0.md) |
| 09 | Reglas de negocio | [09. Reglas de negocio V_1_0_0.md](./01%20Inicio/09.%20Reglas%20de%20negocio%20V_1_0_0.md) |
| 10 | Stack tecnológico | [10. Stack tecnológico V_1_0_0.md](./01%20Inicio/10.%20Stack%20tecnol%C3%B3gico%20V_1_0_0.md) |
| 11 | Base de datos | [11. Base de datos V_1_0_0.md](./01%20Inicio/11.%20Base%20de%20datos%20V_1_0_0.md) |
| 12 | Modelo C4 | [12. Modelo C4 V_1_0_0.md](./01%20Inicio/12.%20Modelo%20C4%20V_1_0_0.md) |
| 13 | Restricciones | [13. Restricciones V_1_0_0.md](./01%20Inicio/13.%20Restricciones%20V_1_0_0.md) |

---

## Fase 02: Planificación del Proyecto

Transformación de la línea base de requisitos a backlog ágil, configuración de Jira Software, gestión cuantitativa de riesgos y presupuesto del PFA.

| # | Artefacto | Archivo | Puntaje |
|---|---|---|---|
| 01 | Transformación a ágil (Épicas, US, Enablers, DoD) | [01 Transformando a ágil V_1_0_0.md](./docs/02%20Planificaci%C3%B3n/01%20Transformando%20a%20%C3%A1gil%20V_1_0_0.md) | 5.0 |
| 02 | Configuración y evidencias de Jira Software | [02 Artefactos Jira V_1_0_0.md](./docs/02%20Planificaci%C3%B3n/02%20Artefactos%20Jira%20V_1_0_0.md) | 5.0 |
| 03 | Registro de riesgos (PMBOK / CMMI) | [03 Registro de riesgos V_1_0_3.md](./docs/02%20Planificaci%C3%B3n/03%20Registro%20de%20riesgos%20V_1_0_3.md) | 3.0 |
| 04 | Presupuesto del proyecto | [04 Presupuesto del proyecto V_1_0_0.md](./docs/02%20Planificaci%C3%B3n/04%20Presupuesto%20del%20proyecto%20V_1_0_0.md) | 3.0 |

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

## Convención de versionado

Los artefactos documentales usan versionado semántico en el nombre de archivo: `Nombre V_X_Y_Z.md`.
