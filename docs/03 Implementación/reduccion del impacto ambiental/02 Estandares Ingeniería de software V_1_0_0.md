[← Volver al README Principal](../../../README.md) · [Informe de reducción del impacto ambiental](./01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md)

# Estándares de ingeniería de software y guía de desarrollo verde

**Proyecto:** EcoLogística Lima – optimizador de rutas sostenibles para DistriRápido S.A.C.  
**Líder del Proyecto:** Carhuapoma Fano, Eilene Elizabeth  
**Versión:** 1.0.2  
**Fecha:** 12 de noviembre de 2026  
**Fecha de modificación:** 13/11/2026  
**Equipo:** EcoLogística Lima — Carhuapoma Fano, Eilene Elizabeth; Cruz Salazar, Jorge Luiz; Estrada Flores, Axel Sebastian; Huaman Baldeon, Katheryn Elena; Leon Taza, Brayan Angel.

Este documento justifica las ocho refactorizaciones del [informe de impacto](./01%20Informe%20de%20reduccion%20del%20impacto%20ambiental%20V_1_0_0.md) frente a ISO/IEC 25010, los cuatro principios de la Green Software Foundation y las Web Sustainability Guidelines (WSG) 1.0. La numeración de las pautas se tomó del Draft Note del 21 de mayo de 2026, [https://www.w3.org/TR/2026/DNOTE-web-sustainability-guidelines-20260521/](https://www.w3.org/TR/2026/DNOTE-web-sustainability-guidelines-20260521/), que es la edición numerada más reciente consultada. El ejemplo de cátedra asigna a 1.2, 2.4 y 3.1 unos títulos que ese documento no usa. Abajo se cita lo que cada identificador dice en realidad y, además, la pauta cuyo texto gobierna cada cambio.

## 2.1 Estándares aplicados

### ISO/IEC 25010

Se usa el modelo de calidad del producto. La característica de eficiencia de desempeño comprende comportamiento temporal, utilización de recursos y capacidad. La de mantenibilidad comprende modularidad, reusabilidad, analizabilidad, modificabilidad y capacidad de ser probado. Esas subcaracterísticas existen en la edición de 2011 y se mantienen, con el mismo sentido, en la revisión de 2023.

| Subcaracterística | Qué cambió en EcoLogística |
|---|---|
| Comportamiento temporal | La pantalla de acceso baja de 80 875 a 67 259 bytes. El LCP de escritorio permanece en 0,37 s. |
| Utilización de recursos | El listado de usuarios ya no lee `password_hash`. Los pedidos dejan de hacer una consulta de cliente y otra de distrito por fila. |
| Capacidad | El listado responde 12 filas, con tope de 50, en lugar de hasta 200. La compresión reduce OpenAPI de 32 944 a 4 075 bytes en Brotli. |
| Modularidad | Las rutas secundarias son módulos diferidos con `React.lazy`. |
| Analizabilidad | No se añaden Moment, Lodash ni TanStack Query. La fecha vive en un solo módulo que usa `Intl`. |
| Capacidad de ser probado | Hay pruebas de paginación, del SQL sin hash, del ETag 304, de Brotli/Gzip, del `<picture>` y del paginador. |

### Green Software Foundation

Los cuatro principios que usa este informe están publicados, en ese orden, en la introducción del material de formación de la Green Software Foundation: [introduction.md](https://github.com/Green-Software-Foundation/training/blob/main/docs/introduction.md). Son eficiencia de carbono, eficiencia energética, conciencia de carbono y eficiencia de hardware. El mismo archivo añade la medición y los compromisos climáticos; la rúbrica pide los cuatro primeros. El dominio `principles.green`, citado en la versión 1.0.0, ya no muestra esos principios.

| Principio | Aplicación en este trabajo | Límite declarado |
|---|---|---|
| Eficiencia de carbono | Menos bytes por visita. El SWDM v4 pasa de 0,009049 g a 0,007526 g CO₂e por visita media. | El modelo no mide el CPU del worker de optimización de rutas. |
| Eficiencia energética | Consultas con menos columnas, una sola consulta de distritos, compresión por encima de 1 KiB y caché de 30 s. | En localhost, el 13/11/2026, el ETag sube la media de los listados de 2,7300 ms a 3,6340 ms. Se informa así. |
| Conciencia de carbono | El informe fija el factor de red en 494 g/kWh y el de hosting verde en 0, porque el host no está verificado. | La API no desplaza trabajos según la intensidad horaria de la red. Una ruta se calcula cuando el operador la pide. |
| Eficiencia de hardware | El navegador del puesto de planificación no descarga Leaflet ni las páginas secundarias al iniciar sesión. `detectRetina: false` evita el PNG de tesela al doble de resolución. | El mapa sigue necesitando Leaflet cuando el operador abre Rutas. |

### W3C WSG 1.0, con la numeración verificada

En el Draft Note del 21 de mayo de 2026 los identificadores que pide la rúbrica significan lo siguiente.

| Id. real | Título en el Draft Note | Uso en este trabajo |
|---|---|---|
| 1.2 | WSG layers of guidance | Es una sección introductoria: pauta, criterio de éxito e información adicional. No es una pauta de imágenes. Este informe se organiza en ese orden: decisión, código e evidencia medida. |
| 2.4 | Minimize non-essential content, interactivity, or journeys | Justifica no añadir fotografías decorativas, partir las rutas que el operador aún no visita y pedir 12 filas en lugar de la colección. |
| 3.1 | Set goals based on performance and energy impact | Justifica los presupuestos de Lighthouse (90 puntos, 1,0 s de FCP, 1,4 s de LCP, 85 ms de TBT, CLS 0,02 y 1,1 MB) y el cálculo SWDM v4. |

Las pautas cuyo enunciado cubre el cambio técnico, y que el ejemplo de cátedra nombraba con otro número, son estas:

| Id. real | Título en el Draft Note del 21 de mayo de 2026 | Optimización que la cumple |
|---|---|---|
| 2.11 | Optimize media to reduce resource use | No se publican rásteres de producto. El `<picture>` AVIF/WebP queda definido para cuando haya una fotografía. Las teselas no piden la variante retina. |
| 3.3 | Modularize bandwidth-heavy components | `React.lazy` y `Suspense` en las rutas secundarias. |
| 3.8 | Defer the loading of non-critical resources | Leaflet y su CSS salen del documento de acceso. |
| 3.14 | Use standards-based JavaScript and APIs | `fetch` e `Intl.DateTimeFormat` en lugar de una biblioteca de fechas o de HTTP. |
| 3.20 | Reduce the number and complexity of database queries | `load_only`, unión del cliente y un solo `LATERAL` para los distritos. |
| 4.2 | Optimize caching and support offline access | `Cache-Control`, ETag y el caché de cliente de 30 s. No se añadió un service worker: la consola autenticada no debe quedar usable sin red con datos de otra persona. |
| 4.3 | Reduce data transfer with compression | Brotli calidad 5 y Gzip nivel 5 en la API y en los activos que sirve el repositorio. |

En el Draft Note de octubre de 2025 la pauta 2.4 era otra («Integrate sustainability into every stage of the ideation process») y la de consultas llevaba el 3.22. Por eso el informe fija la edición del 21 de mayo de 2026 y no mezcla las dos numeraciones.

## 2.2 Guía de desarrollo verde

Las reglas siguientes obligan al código nuevo de este repositorio. Clean Code aporta nombres del dominio y funciones cortas. SOLID separa la compresión de la regla de negocio. DRY concentra la paginación y la fecha. YAGNI prohíbe una dependencia cuyo peso no paga el uso que el producto hace de ella.

### Backend (FastAPI, SQLAlchemy, PostgreSQL)

1. Un listado de lectura proyecta columnas con `load_only`. No se ejecuta `select(Entidad)` completo si la respuesta no usa el hash de contraseña ni las marcas de tiempo.
2. Todo `GET` de colección acepta `page` y `limite`, responde el sobre `Pagina` y usa 12 como tamaño predeterminado, con tope de 50.
3. Toda columna que un listado filtra u ordena tiene índice. Si la migración `001` ya lo creó, no se duplica. Los que faltaban quedaron en la migración `005`.
4. La compresión Brotli o Gzip se aplica a cuerpos de al menos 1 024 bytes. Por debajo de ese umbral el CPU no se justifica.
5. Un `GET` autenticado lleva `ETag`, `Cache-Control: private` y `Vary: Authorization`. `/health` permanece en `no-store`.
6. Una consulta espacial que se repetiría por fila se resuelve en una sentencia. El distrito de un pedido suelto puede seguir usando `distrito_en`.

### Frontend (React, TypeScript, Vite)

1. La ruta de acceso permanece en el grafo inicial. El resto de páginas entra con `React.lazy` y un `<Suspense>` con texto de estado.
2. No se incorpora Moment, Lodash, Axios ni TanStack Query. La fecha usa `Intl`. El HTTP usa `fetch`. El caché de lectura es el módulo `consulta`, 30 segundos, y se vacía al mutar o al cerrar la sesión.
3. No se sube un PNG o un JPEG de interfaz. Si en el futuro hay una fotografía, se publica con `ImagenAdaptativa` (AVIF, WebP y respaldo) y con ancho y alto. Mientras no exista, el componente no se monta.
4. El SVG de la marca va en línea, con `width` y `height`, y `aria-hidden` si el título ya nombra el producto.
5. Leaflet no se importa en estático. Las teselas se piden con `detectRetina: false`.
6. El listado pide `limite=12` y muestra el paginador solo cuando `total_pages` es mayor que 1.

## 2.3 Integración continua y versiones

El flujo `.github/workflows/green-audit.yml` levanta PostgreSQL/PostGIS, migra, siembra los usuarios `admin.lhci` y `conductor.lhci` con la clave de prueba `clave-segura`, arranca la API y ejecuta `lhci autorun` con `lighthouserc.cjs`. Audita `/login`, `/dashboard`, `/flota`, `/conductores`, `/pedidos`, `/usuarios`, `/modo` y `/rutas`. No hay `|| true`. Las aserciones son de error: performance al menos 0,90, FCP como máximo 1 000 ms, LCP como máximo 1 400 ms, TBT como máximo 85 ms, CLS como máximo 0,02 y peso como máximo 1 100 000 bytes. En `/rutas` el CLS admite hasta 0,1: la medición del 13 de noviembre dio 0,038150, por encima de 0,02 y dentro de la banda que Lighthouse puntúa como buena. El servidor es `frontend/scripts/servir.mjs`, que negocia Brotli y Gzip y, si `API_UPSTREAM` está definido, reenvía la API salvo cuando el navegador pide `text/html`.

El preset de esa auditoría es el de escritorio, el mismo del informe. En el preset móvil simulado el FCP medido fue 1,352 s y esa aserción fallaría. El flujo no usa el preset móvil porque la consola se evalúa como puesto de trabajo y porque el par antes/después se tomó en escritorio.

### Secuencia Git usada para versionar este entregable

Los comandos se ejecutaron en la raíz del repositorio, sobre la rama `cursor/green-it-impacto-7721`, con `main` como base del pull request. No se empujó directamente a `main`.

```bash
mkdir -p "docs/03 Implementación/reduccion del impacto ambiental/evidencias"

git add "docs/03 Implementación/reduccion del impacto ambiental/" \
  "docs/03 Implementación/README.md" \
  README.md \
  .github/workflows/green-audit.yml \
  .gitignore \
  lighthouserc.cjs \
  frontend \
  backend

git commit -m "feat(green-it): reducir la transferencia de EcoLogística y documentar el SWDM v4"

git push -u origin cursor/green-it-impacto-7721
```

`mkdir` crea la carpeta exigida. `git add` incluye los dos Markdown de la versión 1.0.0, las evidencias, el flujo y el código. `git commit` registra el cambio. `git push` publica la rama en la que se abre el pull request.

## 2.4 Matriz de las ocho optimizaciones

La columna WSG cita la pauta del Draft Note del 21 de mayo de 2026 cuyo texto corresponde al cambio. Las pautas 1.2, 2.4 y 3.1, con el sentido real descrito en la sección 2.1, atraviesan el conjunto: 1.2 ordena la evidencia, 2.4 cubre las filas 2, 3 y 4, y 3.1 cubre la medición de todas.

| # | Optimización | ISO/IEC 25010 | Principio GSF | WSG 1.0 (id. real) |
|---|---|---|---|---|
| 1 | Consulta con `load_only`, sin `password_hash`, e índices de listado | Eficiencia: utilización de recursos | Eficiencia energética | 3.20 Reduce the number and complexity of database queries |
| 2 | Paginación de 12 en API y en React | Eficiencia: capacidad | Eficiencia energética | 2.4 Minimize non-essential content, interactivity, or journeys |
| 3 | Sin ráster de producto; `<picture>` preparado; tesela sin retina | Eficiencia: comportamiento temporal | Eficiencia de carbono | 2.11 Optimize media to reduce resource use |
| 4 | `React.lazy` y `Suspense` en rutas secundarias | Mantenibilidad: modularidad | Eficiencia de hardware | 3.3 Modularize bandwidth-heavy components |
| 5 | `Intl.DateTimeFormat` en lugar de tres copias manuales; sin Moment ni Lodash | Mantenibilidad: analizabilidad | Eficiencia energética | 3.14 Use standards-based JavaScript and APIs |
| 6 | Marca SVG en línea, 32×32, sin petición extra | Eficiencia: comportamiento temporal | Eficiencia de carbono | 2.11 Optimize media to reduce resource use |
| 7 | ETag, `Cache-Control` y caché de cliente de 30 s | Eficiencia: comportamiento temporal | Eficiencia energética | 4.2 Optimize caching and support offline access |
| 8 | Brotli calidad 5 y Gzip nivel 5 en API y en activos propios | Eficiencia: capacidad | Eficiencia de carbono | 4.3 Reduce data transfer with compression |

La fila 6 comparte la pauta 2.11 con la fila 3 porque ambas deciden el formato del gráfico: una no introduce un ráster y la otra incrusta el vector crítico. La fila 4 también se apoya en la pauta 3.8 (diferir lo no crítico), que no se repite en la celda para mantener un identificador principal por fila.

## Historial de control de cambios

El nombre del archivo sigue en `V_1_0_0`, igual que el resto de los informes de `docs/03 Implementación`. La versión vive en la cabecera.

| Versión | Fecha | Autor | Descripción |
|---|---|---|---|
| 1.0.0 | 12/11/2026 | Equipo EcoLogística Lima | Estándares, guía verde, flujo de Lighthouse CI y matriz de las ocho optimizaciones. |
| 1.0.1 | 13/11/2026 | Equipo EcoLogística Lima | Líder del proyecto. La fuente de los cuatro principios pasa al `introduction.md` del material de la Green Software Foundation. La media de los listados queda en la medición del 13/11/2026. |
| 1.0.2 | 13/11/2026 | Equipo EcoLogística Lima | El flujo de Lighthouse cubre las ocho pantallas. El CLS de `/rutas` queda en 0,1 porque el mapa mide 0,038. |
