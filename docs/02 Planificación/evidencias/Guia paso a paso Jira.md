[← Volver al README Principal](../../../README.md)

# Guía paso a paso: configurar Jira y sacar las 5 evidencias

Esta guía es el instructivo operativo. **No reemplaza** el artefacto 02: es para que el equipo deje el sitio Jira igual a lo que pide la consigna y capture las cinco fotos recortadas.

Tiempo estimado: **45–70 minutos** la primera vez.  
Plan recomendado: **Jira Cloud Free** (hasta 10 usuarios).  
Plantilla: **Scrum administrado por la empresa** (*company-managed*).

Datos maestros: [02 Artefactos Jira V_1_0_0.md](../02%20Artefactos%20Jira%20V_1_0_0.md).

---

## 0. Qué pide la consigna (para no desviarse)

Hay que dejar en Jira, visible y fotografiable:

1. **Jerarquía:** Épica → Historia / Tarea (enabler) → Subtarea → Error.
2. **Backlog priorizado** con **Story Points** Fibonacci (1, 2, 3, 5, 8, 13).
3. **Roadmap / Timeline** con las 7 épicas en una línea de tiempo.
4. **Release** `v1.0.0-MVP`.
5. **Sprint 1** de **2 semanas** con **Sprint Goal** escrito.
6. **Tablero** con columnas exactas: `To Do` → `In Progress` → `In Review / QA` → `Done`.

Luego cinco PNG recortadas **solo al panel de Jira** (sin barra de Windows/macOS, sin pestaña del navegador). Si se ve el escritorio o el Chrome completo, restan el 50 % de ese ítem.

| # | Foto | Archivo |
|---|---|---|
| 1 | Timeline con las 7 épicas | `evidencia-01-roadmap.png` |
| 2 | Backlog con SP y responsables | `evidencia-02-backlog.png` |
| 3 | Sprint 1 + Sprint Goal en la cabecera | `evidencia-03-sprint-1.png` |
| 4 | Tablero con las 4 columnas y tarjetas en más de una | `evidencia-04-tablero.png` |
| 5 | Release `v1.0.0-MVP` | `evidencia-05-release.png` |

---

## 1. Crear el sitio (una sola persona)

1. Entra a [jira.atlassian.com](https://www.atlassian.com/software/jira/free) y crea una cuenta (el correo de la universidad sirve).
2. Crea el sitio. Nombre sugerido: `ecologistica` → quedará `ecologistica.atlassian.net`.
3. Elige **Jira** (no Confluence, no Jira Service Management).
4. Plan **Free**.
5. Invita al resto del equipo: engranaje (⚙️) → **User management** / **Administración de usuarios** → **Invite**. No es obligatorio para las fotos, pero sí para asignar responsables.

---

## 2. Crear el proyecto Scrum

1. Arriba a la izquierda: **Projects** / **Proyectos** → **Create project** / **Crear proyecto**.
2. Categoría **Software development** / **Desarrollo de software**.
3. Plantilla **Scrum**.
4. Tipo de proyecto:
   - Elige **Company-managed** / **Administrado por la empresa**.
   - Si solo ves *Team-managed*, busca el enlace **Change template** / **Más plantillas** o **Company-managed**.
5. Completa:
   - **Name / Nombre:** `EcoLogística Lima`
   - **Key / Clave:** `ECO`
6. **Create**.

Si la clave `ECO` está ocupada, usa `ELL` y no pasa nada: en las fotos debe leerse el nombre del proyecto y las épicas, no obligatoriamente la key.

---

## 3. Activar Timeline, Backlog, Sprints y Releases

En la barra izquierda del proyecto deben aparecer **Timeline** (o **Cronograma**), **Backlog**, **Board** / **Tablero** y **Releases** / **Lanzamientos**.

Si falta alguna:

1. Abre el proyecto → **Project settings** / **Configuración del proyecto** (••• al lado del nombre).
2. **Features** / **Funciones**.
3. Activa:
   - Backlog
   - Sprints
   - Timeline / Roadmap
   - Releases

---

## 4. Estimación en Story Points

Sin esto la evidencia 2 no muestra puntos.

1. Entra al **Board**.
2. **•••** (esquina del tablero) → **Board settings** / **Configuración del tablero**.
3. **Estimation** / **Estimación**.
4. **Estimation statistic:** `Story points`.
5. **Save**.

En *company-managed* a veces está en **Project settings → Features → Estimation**.

Comprueba: al abrir una Historia debe existir el campo **Story point estimate** / **Puntos de historia**.

---

## 5. Columnas del tablero (texto exacto de la consigna)

Jira suele crear `To Do`, `In Progress` y `Done` (o *Por hacer / En curso / Listo*). Hay que dejar **cuatro** columnas con estos nombres en inglés:

`To Do` → `In Progress` → `In Review / QA` → `Done`

### 5.1 Crear el estado que falta

1. **Project settings** → **Workflows** / **Flujos de trabajo**.
2. En el flujo del proyecto, **Edit**.
3. **Add status** / **Añadir estado**.
4. Nombre: `In Review / QA`.
5. Categoría: **In Progress**.
6. Conecta transiciones desde `In Progress` hacia `In Review / QA` y desde ahí hacia `Done` (y de vuelta, si Jira lo pide).
7. **Publish**.

### 5.2 Mapear columnas

1. **Board** → **•••** → **Board settings** → **Columns**.
2. **Add column** y nómbrala `In Review / QA`.
3. Arrastra el estado `In Review / QA` a esa columna.
4. Renombra las otras si están en español:
   - Por hacer → `To Do`
   - En curso → `In Progress`
   - Listo → `Done`
5. Orden de izquierda a derecha: **To Do | In Progress | In Review / QA | Done**.
6. La columna **Done** debe contener solo estados verdes de completado.

---

## 6. Componentes

1. **Project settings** → **Components**.
2. Crea uno por uno:

| Componente | Descripción |
|---|---|
| Backend | API FastAPI |
| Frontend | SPA React |
| Optimizer | Motor VRPTW / Green VRP |
| DB | PostgreSQL + PostGIS |
| DevOps | CI/CD y Staging |

---

## 7. Crear las 7 épicas (hace falta para el Roadmap)

Entra a **Backlog** (o **Timeline**) → **Create** / **Crear**.

- **Type:** Epic / Épica.
- Pega el **Summary** de la tabla.
- Abre la épica y carga **Start date** y **Due date**. Sin fechas, el Timeline sale vacío o en una sola columna: la evidencia 1 no sirve.

| Summary (copiar) | Inicio | Fin |
|---|---|---|
| EP-01 Identidad, acceso y cumplimiento | 14/09/2026 | 11/10/2026 |
| EP-02 Gestión de flota | 14/09/2026 | 11/10/2026 |
| EP-03 Gestión de conductores y jornadas | 28/09/2026 | 25/10/2026 |
| EP-04 Pedidos y preferencias de clientes | 28/09/2026 | 25/10/2026 |
| EP-05 Optimización y re-optimización de rutas | 12/10/2026 | 22/11/2026 |
| EP-06 Visualización geoespacial | 26/10/2026 | 22/11/2026 |
| EP-07 Sostenibilidad, dashboard y reportes | 09/11/2026 | 14/12/2026 |

Color distinto por épica (el Timeline se lee mejor).

---

## 8. Crear historias y enablers

**Create** → tipo **Story** (usuario) o **Task** (enabler). En cada ficha:

1. **Parent / Epic link:** la épica de la tabla.
2. **Story points:** el número Fibonacci.
3. **Assignee:** un integrante (si aún no están invitados, asígnate tú).
4. **Component:** el de la tabla.
5. **Fix version / Versión:** `v1.0.0-MVP` (si todavía no existe, créala en el paso 9 y vuelve).
6. Descripción: al menos el *Como / quiero / para* de una línea.

### 8.1 Mínimo para las cinco fotos (Sprint 1 + algo de backlog)

Crea **por lo menos** estos 10 ítems. El resto se puede cargar después.

| Tipo | Summary | Épica | SP | Assignee | Componente |
|---|---|---|---|---|---|
| Task | ENB-003 Esquema PostgreSQL + PostGIS | — | 8 | Brayan | DB |
| Task | ENB-002 Pipeline CI/CD y Quality Gate | — | 5 | Axel | DevOps |
| Story | US-001 Autenticación JWT | EP-01 | 5 | Axel | Backend |
| Story | US-004 Registrar vehículo | EP-02 | 5 | Katheryn | Frontend |
| Task | ENB-007 OpenAPI vivo | — | 3 | Jorge | Backend |
| Story | US-002 Usuarios y roles RBAC | EP-01 | 5 | Axel | Backend |
| Story | US-006 Registrar conductor | EP-03 | 5 | Brayan | DB |
| Story | US-008 Registrar pedido | EP-04 | 8 | Katheryn | Frontend |
| Task | ENB-001 Motor metaheurístico SLA | EP-05 | 13 | Jorge | Optimizer |
| Story | US-010 Generar rutas VRPTW | EP-05 | 13 | Jorge | Optimizer |

Los cinco primeros (ENB-003, ENB-002, US-001, US-004, ENB-007) son el **Sprint 1** (26 SP).

### 8.2 Una subtarea (para cumplir la jerarquía)

Abre **ENB-003** → **Add sub-task** / **Crear subtarea**:

- `Extensión PostGIS y uuid-ossp`

Con eso ya existen Epic, Story, Task, Sub-task. El tipo **Bug** no hace falta crearlo ahora; el proyecto Scrum ya lo trae.

### 8.3 Ordenar el backlog

En **Backlog**, arrastra las tarjetas. Arriba = más prioridad. Orden sugerido: primero los del Sprint 1, después US-002, US-006, US-008, ENB-001, US-010.

Lista completa de 26 ítems: sección 4 del [artefacto 02](../02%20Artefactos%20Jira%20V_1_0_0.md).

---

## 9. Crear la release `v1.0.0-MVP`

1. Menú izquierdo → **Releases** / **Lanzamientos**.
2. **Create version**.
3. Pega:

| Campo | Valor |
|---|---|
| Name | `v1.0.0-MVP` |
| Release date | `14/12/2026` |
| Description | MVP EcoLogística Lima: flota, pedidos, ruteo VRPTW/Green VRP, mapa, dashboard y re-optimización. Umbral de aceptación: ≥ 70 % de RF de prioridad Alta. |

4. **Save**. **No pulses Release** (debe quedar **Unreleased**).
5. Vuelve a cada issue (o usa el panel **Versions** del Backlog) y asígnalos a `v1.0.0-MVP`.

---

## 10. Crear el Sprint 1 y escribir el Sprint Goal

Haz esto **antes** de iniciar el sprint. La foto 3 se toma en la vista **Backlog**.

1. **Backlog** → **Create sprint**.
2. Click en el lápiz del nombre → `ECO Sprint 1`.
3. **Edit sprint** / **•••** del sprint:
   - Duración: **2 weeks**.
   - Fechas: `16/09/2026` – `29/09/2026` (o 14/09–27/09 si quieren calzar el documento).
   - **Sprint goal** (pegar tal cual):

```
Dejar operativa en Staging la plataforma base de EcoLogística Lima: esquema de datos desplegado por pipeline, autenticación JWT y registro de vehículos de la flota de DistriRápido.
```

4. Arrastra al sprint **solo** estas 5:

- ENB-003 (8)
- ENB-002 (5)
- US-001 (5)
- US-004 (5)
- ENB-007 (3)

Arriba a la derecha del sprint debe sumar **26 SP**.

5. **Todavía no inicies el sprint.**

---

## 11. Orden de las fotos (importante)

| Orden | Qué haces | Evidencia |
|---|---|---|
| A | Backlog con sprint creado, Goal visible, 5 ítems dentro, **sin** Start | **3** y luego **2** |
| B | Timeline con las 7 barras de épicas | **1** |
| C | Releases con `v1.0.0-MVP` abierta | **5** |
| D | **Start sprint** → mueves tarjetas → Board | **4** |

Si inicias el sprint antes de la foto 3, el bloque del Sprint Goal desaparece del Backlog y cuesta más demostrarlo.

---

## 12. Cómo recortar (si fallas aquí, pierdes la mitad del puntaje)

**Windows:** `Win + Shift + S` → selecciona solo el panel.  
**macOS:** `Cmd + Shift + 4` → arrastra solo el panel.

### Debe entrar en el recorte

- El widget de Jira: Timeline, lista del Backlog, cabecera+lista del Sprint, las 4 columnas, o la ficha de la versión.

### No debe entrar

- Barra de tareas de Windows / Dock de Mac
- Reloj, fondo de escritorio, íconos
- Pestaña del navegador, barra de favoritos, URL
- Margen blanco grande alrededor

Zoom del navegador: **100 %**. Ventana maximizada. Exporta **PNG** (no JPG).

Comprueba que en la foto se lea al menos: nombres de épicas o issues, números de SP, las columnas o el texto `v1.0.0-MVP`.

---

## 13. Receta de cada evidencia

### Evidencia 1 — Roadmap

1. Menú **Timeline** / **Cronograma**.
2. Vista **Weeks** o **Months** de modo que se vean Sprint 1…7 (sep–dic 2026).
3. Las 7 épicas a la izquierda y una barra cada una.
4. Recorta el Timeline (títulos + barras). Nada del menú de Chrome.
5. Guarda como `evidencia-01-roadmap.png`.

Si las barras no aparecen: faltan Start/Due date en las épicas (paso 7).

### Evidencia 2 — Backlog priorizado

1. **Backlog**.
2. Abre el panel izquierdo de **Epics** (y **Versions** si cabe) para que se vean las épicas.
3. Baja el zoom de la página solo si hace falta que entren varios issues **con el número de SP** a la derecha.
4. Recorta el listado (keys, summaries, SP). No recortes solo el menú.
5. Guarda como `evidencia-02-backlog.png`.

### Evidencia 3 — Sprint 1 + Sprint Goal

1. Sigue en **Backlog**.
2. El bloque **ECO Sprint 1** debe mostrar el Goal completo y los 5 issues.
3. Recorta **ese bloque** (cabecera + Goal + lista). No hace falta toda la página.
4. Guarda como `evidencia-03-sprint-1.png`.
5. Recién ahora: **Start sprint**.

### Evidencia 4 — Tablero activo

1. **Board**.
2. Confirma los títulos: `To Do` · `In Progress` · `In Review / QA` · `Done`.
3. Arrastra así (para que no salga un tablero vacío):

| Columna | Issue |
|---|---|
| To Do | ENB-007 OpenAPI |
| In Progress | ENB-003 PostgreSQL **y** US-004 Vehículo |
| In Review / QA | US-001 JWT |
| Done | ENB-002 CI/CD |

4. Recorta las cuatro columnas con tarjetas.
5. Guarda como `evidencia-04-tablero.png`.

### Evidencia 5 — Release

1. **Releases** → click en **v1.0.0-MVP**.
2. Debe verse el nombre, fecha 14/12/2026, estado Unreleased y issues asociados.
3. Recorta el panel de la versión (no toda la app).
4. Guarda como `evidencia-05-release.png`.

---

## 14. Subir las fotos al repositorio

1. Copia los cinco PNG a:

`docs/02 Planificación/evidencias/`

2. En [02 Artefactos Jira V_1_0_0.md](../02%20Artefactos%20Jira%20V_1_0_0.md) pega, debajo de cada “Captura requerida”:

```markdown
![Evidencia 1: Roadmap del proyecto](./evidencias/evidencia-01-roadmap.png)
```

(cambia el número y el nombre de archivo en las otras cuatro).

3. Commit y push a la rama del equipo.

---

## 15. Checklist rápido antes de entregar

- [ ] Proyecto Scrum `EcoLogística Lima`
- [ ] 7 épicas con fechas en Timeline
- [ ] Historias/tareas con SP Fibonacci
- [ ] Sprint 1 de 2 semanas y Goal pegado
- [ ] Columnas en inglés, las cuatro, con al menos una tarjeta en cada una
- [ ] Versión `v1.0.0-MVP` sin lanzar
- [ ] Cinco PNG recortadas al panel, sin escritorio ni pestaña
- [ ] Se leen SP, nombres de issues y `v1.0.0-MVP`

---

## 16. Si la interfaz no coincide

Jira cambia textos según el idioma y la versión.

| Lo que buscas | Dónde suele estar |
|---|---|
| Company-managed | Al crear el proyecto, “Administrado por la empresa” |
| Timeline vacío | Fechas de inicio/fin en cada épica |
| No hay Story Points | Board settings → Estimation |
| No hay Releases | Project settings → Features → Releases |
| No puedo crear `In Review / QA` | Workflows → Add status, luego Columns |
| Sprint Goal no se ve | Backlog, bloque del sprint, **antes** de Start sprint |
| Tablero vacío | Hay que **Start sprint**; el backlog no mueve solo las tarjetas |

Atajo opcional (sitio admin): ⚙️ → **System** → **External system import** → CSV. Plantilla parcial: [`jira-import-sprint1.csv`](./jira-import-sprint1.csv). Después igual hay que poner fechas a las épicas, columnas, Goal y mover el tablero.

---

[← Volver al README Principal](../../../README.md)
