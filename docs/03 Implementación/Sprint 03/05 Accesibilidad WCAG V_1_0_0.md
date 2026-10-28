[← Volver al README Principal](../../../README.md)

# Evaluación de accesibilidad WCAG 2.2 AA

**Nombre del Proyecto:** EcoLogística Lima – Optimizador de Rutas Sostenibles para DistriRápido S.A.C.  
**Fecha de la evaluación:** 2026-10-28  
**Versión del análisis:** V_1_0_0  
**Nivel objetivo:** WCAG 2.2, nivel AA (incluye los criterios A y AA de 2.0, 2.1 y 2.2)

El acta de constitución cita WCAG 2.1 AA. Esta evaluación cubre 2.2 AA, que añade a ese conjunto los criterios 2.4.11, 2.5.7, 2.5.8, 3.2.6, 3.3.7 y 3.3.8. El criterio 4.1.1 (Parsing) se retiró en WCAG 2.2 y no se puntúa.

## 1. Alcance y metodología

### Pantallas

| Pantalla | Ruta | Quién la ve |
|---|---|---|
| Iniciar sesión | `/login` | Sin sesión |
| Flota | `/flota` | Todos los roles autenticados. El conductor y el auditor consultan; administrador, gerente y operador editan |
| Conductores | `/conductores` | Administrador, gerente, operador y auditor |
| Pedidos | `/pedidos` | Administrador, gerente, operador y auditor |
| Rutas (mapa Leaflet) | `/rutas` | Administrador, gerente, operador y auditor |
| Tablero | `/dashboard` | Administrador, gerente, operador y auditor |
| Usuarios | `/usuarios` | Administrador (escribe) y gerente (consulta) |
| Modo conductor | `/modo` | Conductor |
| Acceso denegado | cualquier módulo fuera del rol | Por ejemplo, el conductor en `/usuarios` |

### Herramientas

| Herramienta | Uso en esta evaluación |
|---|---|
| axe-core 4.10.3 | Mismo motor que axe DevTools 4.10.3. Corre en Vitest (jsdom) sobre las nueve superficies, con las etiquetas `wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa` y `wcag22aa`. Entra en `npm test` y, por tanto, en la CI |
| axe DevTools 4.10.3 | Línea base manual de Flota en el equipo, WCAG 2.1 AA, 0 issues. Captura en la sección 2 |
| WAVE | Línea base manual de Flota: 0 errores, 0 errores de contraste, 0 alertas, AIM 10/10 |
| Lighthouse | Línea base manual de Flota: Accessibility 100, Best Practices 100, SEO 91, Performance 59 |
| Revisión de código | Teclado, foco, etiquetas, tablas, mapa, zoom y tamaño de objetivo |
| Chrome headless sobre `npm run build` | Orden de tabulador, enlace «Saltar al contenido», reflow a 320 px y zoom 200 % con el espaciado de texto de la técnica WCAG 1.4.12 |

La regla `color-contrast` de axe queda apagada en jsdom: ahí no hay diseño real y el resultado sería falso. El contraste se revisó con la paleta calculada y con la captura WAVE de Flota. La regla `target-size` (2.5.8) viene desactivada de fábrica en axe-core 4.10.3; el tamaño se revisó en CSS (mínimo 44 px) y en el código de Leaflet.

**Pendiente: completar por el equipo** la pasada con NVDA real. Ningún motor automático sustituye al lector de pantalla. El guion está en la sección 7.

## 2. Línea base de la pantalla Flota

Capturas tomadas en el equipo sobre `http://localhost:5173/flota`, con el servidor de desarrollo de Vite, antes de las correcciones de este documento. Sirven de línea base de Flota. No son el estado posterior al cambio: el pie de accesos directos, la alternativa textual del mapa y los botones de desplazamiento de las tablas se agregan después. La sección 6 pide las capturas nuevas.

WAVE: 0 errores, 0 errores de contraste, 0 alertas, 1 feature (idioma), 16 elementos estructurales, 10 ARIA, AIM score 10/10.

![WAVE sobre Flota: 0 errores, 0 contrastes, 0 alertas, AIM 10/10](./img/wave-flota.png)

Lighthouse: Accessibility 100, Best Practices 100, SEO 91, Performance 59.

![Lighthouse sobre Flota: Accessibility 100, Best Practices 100, SEO 91, Performance 59](./img/lighthouse-flota.png)

Métricas de esa misma pasada: First Contentful Paint 6.8 s, Largest Contentful Paint 11.8 s, Total Blocking Time 20 ms, Cumulative Layout Shift 0, Speed Index 6.8 s. Esas cifras salen del servidor de desarrollo de Vite, no de `npm run build`. **Performance no es un criterio WCAG.** El 59 de rendimiento no baja el nivel AA. Accessibility 100 sí entra en esta evaluación.

![Métricas Lighthouse de Flota medidas en el servidor de desarrollo](./img/lighthouse-metricas-flota.png)

axe DevTools 4.10.3, WCAG 2.1 AA: 0 issues automáticos.

![axe DevTools 4.10.3 sobre Flota: 0 issues WCAG 2.1 AA](./img/axe-flota.png)

Lo que esa pasada de una sola pantalla no ve, y la revisión del resto del sistema sí encontró: el anillo de foco del mismo verde que la barra, botones «Guardar», «Activar» y «Confirmar ruta» repetidos, el mapa sin alternativa textual enlazada, el título de la pestaña en el login y el desborde horizontal del formulario cuando el correo es largo y la ventana mide 320 px.

## 3. Hallazgos y correcciones

| Criterio | Pantalla | Descripción | Severidad | Corrección | Archivo | Estado |
|---|---|---|---|---|---|---|
| 2.4.7 Foco visible, 1.4.11 Contraste no textual | Barra de todas las pantallas autenticadas | El anillo usaba `#08553d`, el mismo verde del fondo. Sobre la barra el foco no se distinguía (contraste 1:1) | Alta | Anillo doble: 3 px blancos pegados al control y 3 px `#10241c` por fuera. El blanco contrasta 8.83:1 con la barra; el oscuro, 16:1 con el fondo claro | `frontend/src/styles.css` | Corregido |
| 2.4.1 Evitar bloques | Todas las autenticadas | Existía «Saltar al contenido», pero el destino `#contenido` no era enfocable: al activarlo el foco seguía en el enlace | Alta | El destino es un enlace real «Contenido principal». Enter lo enfoca. Está oculto hasta que recibe el foco, para no usar `tabIndex` en un elemento estático | `frontend/src/pages/Shell.tsx`, `styles.css` | Corregido |
| 2.4.6, 4.1.2, 2.5.3 Nombre del control | Flota, Usuarios, Rutas | Varios botones se llamaban igual: «Guardar», «Activar» / «Desactivar», «Ver en el mapa», «Confirmar ruta». El texto visible no decía de qué fila se trataba | Media | El nombre accesible añade placa, correo o vehículo y conductor. El texto visible sigue dentro de ese nombre | `FlotaPage.tsx`, `UsuariosPage.tsx`, `RutasPage.tsx` | Corregido |
| 1.1.1 Contenido no textual, 3.1.2 Idioma de un fragmento | Rutas | El mapa no apuntaba a un recorrido en texto. Los botones de Leaflet se llamaban «Zoom in» y «Zoom out» | Media | Lista «Alternativa textual del mapa» (partida, paradas, ETA y semáforo en palabras) referenciada con `aria-describedby`. Los controles quedan en «Acercar» y «Alejar» | `MapaRutas.tsx`, `RutasPage.tsx` | Corregido |
| 2.1.1 Teclado, 2.1.2 Sin trampa, 2.5.7 Arrastrar | Rutas | La rueda del mouse hacía zoom aunque el mapa no tuviera el foco y se comía el scroll de la página. No había forma explícita de soltar el mapa | Media | El zoom con rueda solo se enciende con el foco y se apaga al salir. Escape suelta el mapa. Las flechas de Leaflet y la tabla siguen siendo la alternativa al arrastre | `MapaRutas.tsx` | Corregido |
| 1.4.10 Reflow | Login y tablas | A 320 px de ancho el correo largo impedía que el campo encogiera y la página crecía a 343 px. El grid de las tablas podía empujar el ancho de toda la página | Media | `min-width: 0` en tarjeta, etiquetas y campos. El scroll horizontal queda dentro de la tabla. Comprobado en Chrome sobre el build: login, Flota, Conductores, Pedidos, Rutas, Tablero y Usuarios quedan en 320/320 | `styles.css` | Corregido |
| 2.1.1 Teclado en la tabla | Flota, Conductores, Pedidos, Usuarios, Rutas | La tabla ancha se desplaza en un contenedor que el teclado no alcanzaba | Media | Botones «Desplazar la tabla a la izquierda» y «Desplazar la tabla a la derecha», con el nombre de la tabla en el nombre accesible. Son botones nativos, sin `tabIndex` en un `div` | `frontend/src/avisos.tsx` | Corregido |
| 3.3.1 Identificación del error, 4.1.3 Mensajes de estado | Login y todos los módulos | El `role="alert"` ya existía. El foco no se movía al mensaje, así que quien usa solo teclado no aterrizaba en él | Media | El mensaje es un enlace dentro del aviso. Al aparecer, recibe el foco. El texto del enlace es el error. El acierto sigue en `<output>` (región viva, sin robar el foco de un selector) | `avisos.tsx` y páginas | Corregido |
| 2.4.2 Página titulada | Login y acceso denegado | El login dejaba el título genérico. Si el rol no entra al módulo, el título seguía siendo el de la pantalla anterior | Baja | «Iniciar sesión · EcoLogística Lima» y «Acceso denegado · EcoLogística Lima» | `LoginPage.tsx`, `App.tsx` | Corregido |
| 1.3.1, 2.4.6 Encabezados | Acceso denegado, Tablero, regiones | El rechazo de permiso era un párrafo suelto. Los indicadores eran `span` y `strong` sin encabezado | Baja | `h1` «Acceso denegado». En el tablero, `h2` «Período» e «Indicadores del día», y cada cifra en un `h3` dentro de un `article` con nombre | `App.tsx`, `DashboardPage.tsx` | Corregido |
| 1.3.1 Tablas | Todas las tablas | Los `th` no declaraban `scope` | Baja | `scope="col"` en cada encabezado. Las captions se mantienen | Páginas de listado | Corregido |
| 1.4.1 Uso del color, 4.1.2 Estado | Rutas | La ruta elegida solo se notaba en el dibujo del mapa | Baja | El botón pasa a «Visible en el mapa» y `aria-pressed`. El semáforo ya tenía el texto Verde, Amarillo o Rojo, no solo el color | `RutasPage.tsx` | Corregido |
| 1.3.2 Secuencia | Rutas | «Ver en el mapa» estaba antes del encabezado de la ruta | Baja | Primero el `h3` con vehículo y conductor, después la acción | `RutasPage.tsx` | Corregido |
| 2.4.5 Múltiples vías | Autenticadas | La única lista de módulos era la barra | Baja | El pie «Accesos directos» repite los módulos del rol, con otro `nav` y otro nombre | `Shell.tsx` | Corregido |
| 3.2.2 Al introducir datos | Rutas, Tablero, Usuarios | Cambiar la fecha recarga el plan o los indicadores. Cambiar el rol guarda en el acto | Baja | Un texto visible, antes del control, avisa de ese comportamiento. El selector de rol lo referencia con `aria-describedby` | `RutasPage.tsx`, `DashboardPage.tsx`, `UsuariosPage.tsx` | Corregido |
| 2.5.8 Tamaño del objetivo | Barra, tablas, zoom del mapa | Los controles de formulario ya medían 44 px. Los de la tabla medían 36 px y el zoom de Leaflet 26 px. 26 px cumple el mínimo de 24 px, pero el anillo de foco chocaba con el botón de al lado | Baja | Nav, campos de tabla y botones quedan en 44 px como mínimo. El zoom de Leaflet pasa a 44×44 px con 6 px de separación | `styles.css` | Corregido |
| 1.4.3 Contraste del placeholder | Pedidos | El único placeholder («frente a la bodega El Ahorro») heredaba el gris del navegador, que a menudo no llega a 4.5:1 | Baja | `::placeholder` en `#3d5248` (8.40:1 sobre blanco) | `styles.css` | Corregido |
| 1.3.5 Propósito del campo, 3.3.8 Autenticación accesible | Login y alta de usuario | El login ya tenía `autocomplete="username"` y `current-password`, y no bloquea el pegado. La contraseña inicial de un usuario nuevo no decía que es una clave nueva | Baja | `autoComplete="new-password"` en el alta. No hay captcha ni prueba cognitiva | `LoginPage.tsx`, `UsuariosPage.tsx` | Corregido |
| 2.4.11 Foco no oculto | Todas | La barra no es fija ni sticky. Un foco al borde de la ventana podía quedar pegado al límite | Baja | `scroll-margin: 0.75rem` en `:focus-visible`. No se fijó la barra, para no tapar el foco | `styles.css` | Corregido |

Contraste de la paleta, texto normal (umbral AA 4.5:1) y componentes (umbral 3:1):

| Par | Ratio | Uso |
|---|---|---|
| `#10241c` sobre `#ffffff` | 16.26 | Texto principal |
| `#3d5248` sobre `#ffffff` | 8.40 | Texto secundario y placeholder |
| `#3d5248` sobre `#f4f7f5` | 7.79 | Ayuda sobre el fondo de página |
| `#ffffff` sobre `#08553d` | 8.83 | Barra, botón primario y enlace de salto |
| `#08553d` sobre `#ffffff` | 8.83 | Enlace del pie y página actual de la barra |
| `#7a1b1b` sobre `#fdecec` | 9.19 | Error |
| `#0d5c32` sobre `#e7f6ee` | 7.25 | Éxito y semáforo verde |
| `#6a4b00` sobre `#fff6df` | 7.44 | Aviso y semáforo amarillo |
| `#0b3a66` sobre `#e7f0fa` | 10.07 | Estado Asignado |
| `#6d8178` sobre `#ffffff` | 4.15 | Borde de campos (pasa 3:1, no es texto) |

## 4. Resultado después de las correcciones

- Vitest 2.1.9: **64 pruebas en verde**, 9 de ellas de axe-core 4.10.3 (login, Flota con tabla, Conductores, Pedidos, Rutas con mapa y alternativa textual, Tablero, Usuarios, Modo conductor y acceso denegado). Violaciones: **0**.
- Cobertura `@vitest/coverage-v8` 2.1.9 sobre `frontend/src`: **99.58 %** de líneas y **90.65 %** de ramas.
- `npm run build` (`tsc --noEmit` y Vite) termina sin errores.
- Chrome headless sobre el build de producción:
  - el primer elemento enfocable de Flota es «Saltar al contenido»; Enter deja el foco en «Contenido principal»;
  - a 320 px de ancho no hay scroll horizontal en login, Flota, Conductores, Pedidos, Rutas, Tablero ni Usuarios;
  - con zoom CSS 200 % y el espaciado de la técnica 1.4.12 (interlineado 1.5, tracking 0.12 em, word-spacing 0.16 em, margen de párrafo 2 em), login y Flota siguen en 1280/1280 y el `h1` permanece.

La CI (`.github/workflows/ci.yml`) ejecuta `npm test` y `npm run build` en el job del frontend. No hizo falta tocar el workflow: las pruebas de axe viven junto al resto.

## 5. Checklist de criterios AA

| Criterio | Resultado |
|---|---|
| 1.1.1 Contenido no textual | Revisado. El mapa tiene lista textual y la tabla de paradas. No hay imágenes de interfaz sin alternativa |
| 1.2.1 a 1.2.5 Medios temporales | No aplica. No hay audio ni vídeo |
| 1.3.1 Información y relaciones | Revisado. Etiquetas, captions, `scope`, encabezados y regiones con nombre |
| 1.3.2 Secuencia con significado | Revisado. El encabezado de la ruta va antes de la acción |
| 1.3.3 Características sensoriales | Revisado. El semáforo y la ruta elegida no dependen solo del color o de la posición |
| 1.3.4 Orientación | Revisado. No se bloquea la orientación |
| 1.3.5 Identificar el propósito del campo | Revisado en el login. El alta de otra persona no recoge datos de quien llena el formulario; la clave nueva lleva `new-password` |
| 1.4.1 Uso del color | Revisado |
| 1.4.2 Control del audio | No aplica |
| 1.4.3 Contraste mínimo | Revisado en la paleta y en WAVE (línea base de Flota). **Pendiente: completar por el equipo** la captura WAVE del resto de pantallas después del cambio |
| 1.4.4 Cambio de tamaño del texto | Revisado. Sin `maximum-scale`. Zoom 200 % comprobado en Chrome sobre login y Flota |
| 1.4.5 Imágenes de texto | No aplica |
| 1.4.10 Reflow | Revisado a 320 px en las siete rutas del build |
| 1.4.11 Contraste no textual | Revisado. Borde de campo 4.15:1. Foco doble sobre barra y fondo claro |
| 1.4.12 Espaciado del texto | Revisado en Chrome con la hoja de la técnica, en login y Flota. **Pendiente: completar por el equipo** la misma prueba a mano en el resto de pantallas |
| 1.4.13 Contenido en hover o foco | Revisado. Los popups del mapa se abren al pulsar. El `title` nativo del navegador queda en el agente de usuario |
| 2.1.1 Teclado | Revisado en código y en Chrome (salto, formularios, botones de tabla, zoom del mapa) |
| 2.1.2 Sin trampa de teclado | Revisado. Escape suelta el mapa. Tab sale de él |
| 2.1.4 Atajos de teclado de un carácter | No aplica. Las flechas solo actúan con el mapa enfocado |
| 2.2.1 Tiempo ajustable | No aplica en la interfaz. El bloqueo de 15 minutos es una respuesta del servidor, no un límite de la página |
| 2.2.2 Pausar, detener, ocultar | No aplica. No hay movimiento automático |
| 2.3.1 Tres destellos | No aplica |
| 2.4.1 Evitar bloques | Revisado. El salto mueve el foco |
| 2.4.2 Página titulada | Revisado. Cada módulo, el login y el acceso denegado ponen `document.title` |
| 2.4.3 Orden del foco | Revisado. Salto, módulos, sesión, contenido, pie |
| 2.4.4 Propósito de los enlaces | Revisado. Los enlaces dicen el módulo |
| 2.4.5 Múltiples vías | Revisado. Barra y pie |
| 2.4.6 Encabezados y etiquetas | Revisado |
| 2.4.7 Foco visible | Revisado en CSS. **Pendiente: completar por el equipo** la comprobación visual con el teclado en cada pantalla |
| 2.4.11 Foco no oculto (mínimo) | Revisado. La barra no es fija |
| 2.5.1 Gestos del puntero | Revisado. El pellizco del mapa tiene botones Acercar y Alejar |
| 2.5.2 Cancelación del puntero | Revisado. Se usan `click` y `submit`, que disparan al soltar |
| 2.5.3 Etiqueta en el nombre | Revisado. El texto visible de cada botón está dentro del nombre accesible |
| 2.5.4 Actuación por movimiento | No aplica |
| 2.5.7 Movimientos de arrastre | Revisado. El mapa se mueve con flechas y la información está en la tabla |
| 2.5.8 Tamaño del objetivo (mínimo) | Revisado. Mínimo de diseño 44×44 px, por encima de los 24 px del criterio |
| 3.1.1 Idioma de la página | Revisado. `<html lang="es">` |
| 3.1.2 Idioma de un fragmento | Revisado. Acercar y Alejar en español |
| 3.2.1 Al recibir el foco | Revisado. Enfocar el mapa no cambia de página |
| 3.2.2 Al recibir entradas | Revisado. Hay aviso antes de la fecha y del cambio de rol |
| 3.2.6 Ayuda consistente | No aplica. No hay un mecanismo de ayuda |
| 3.3.1 Identificación del error | Revisado. El aviso recibe el foco |
| 3.3.2 Etiquetas o instrucciones | Revisado |
| 3.3.3 Sugerencia ante errores | Revisado cuando el mensaje del API lo trae (por ejemplo, ventana invertida o jornada de más de 8 h). **Pendiente: completar por el equipo** oír esos mensajes con NVDA |
| 3.3.4 Prevención de errores (legales, financieros) | No aplica. No hay compra ni compromiso legal en el formulario |
| 3.3.7 Entrada redundante | Revisado. No se vuelve a pedir un dato ya capturado en la misma pantalla |
| 3.3.8 Autenticación accesible (mínimo) | Revisado. Sin prueba cognitiva. Se puede pegar la contraseña y usar un gestor |
| 4.1.2 Nombre, función, valor | Revisado con axe (0 violaciones) y con los nombres de botones, selectores y mapa |
| 4.1.3 Mensajes de estado | Revisado. Error con `role="alert"`. Éxito y avisos en `<output>` |

## 6. Capturas por pantalla

La línea base de Flota está en la sección 2. Falta la tanda posterior al cambio, una por pantalla, con WAVE, Lighthouse (Accessibility) y axe DevTools 4.10.3. **Pendiente: completar por el equipo.**

| Pantalla | WAVE | Lighthouse Accessibility | axe DevTools |
|---|---|---|---|
| Login | Pendiente: completar por el equipo | Pendiente: completar por el equipo | Pendiente: completar por el equipo |
| Flota | Línea base en la sección 2. Repetir después del cambio | Línea base en la sección 2. Repetir después del cambio | Línea base en la sección 2. Repetir después del cambio |
| Conductores | Pendiente: completar por el equipo | Pendiente: completar por el equipo | Pendiente: completar por el equipo |
| Pedidos | Pendiente: completar por el equipo | Pendiente: completar por el equipo | Pendiente: completar por el equipo |
| Rutas, con al menos un plan y el mapa | Pendiente: completar por el equipo | Pendiente: completar por el equipo | Pendiente: completar por el equipo |
| Tablero | Pendiente: completar por el equipo | Pendiente: completar por el equipo | Pendiente: completar por el equipo |
| Usuarios | Pendiente: completar por el equipo | Pendiente: completar por el equipo | Pendiente: completar por el equipo |
| Modo conductor | Pendiente: completar por el equipo | Pendiente: completar por el equipo | Pendiente: completar por el equipo |
| Acceso denegado (conductor en Usuarios) | Pendiente: completar por el equipo | Pendiente: completar por el equipo | Pendiente: completar por el equipo |

Sugerencia de nombre al guardarlas en `docs/03 Implementación/Sprint 03/img/`: `wave-login.png`, `lighthouse-rutas.png`, `axe-usuarios.png`, y el mismo patrón para el resto.

## 7. Lector de pantalla

**Pendiente: completar por el equipo.** Hace falta NVDA (o el lector que use el equipo) en Windows, con Firefox o Chrome, sobre `npm run dev`. Esta pasada no lo ejecutó.

Guion mínimo, en cada pantalla de la tabla anterior:

1. NVDA + flechas: el `h1` es el nombre de la pantalla y no se salta de nivel.
2. Tab desde el inicio: primero «Saltar al contenido»; Enter deja el foco al comienzo del contenido.
3. En el login, una contraseña incorrecta se anuncia sola y el foco queda en el mensaje.
4. En Flota, «Guardar» se oye con la placa. El estado y el factor de emisión también.
5. En Usuarios, «Desactivar» o «Activar» se oye con el correo. El aviso de que el rol se guarda al cambiarlo está antes del selector.
6. En Rutas, la alternativa textual se lee sin mirar el mapa: partida, parada, ETA y semáforo. Los botones del mapa se llaman Acercar y Alejar. Escape devuelve el foco a la página.
7. En el Tablero, cada cifra se alcanza como encabezado.
8. Zoom del navegador al 200 % y ancho equivalente a 320 px: no se pierde ningún control y la página no se desplaza en horizontal, salvo el interior de una tabla.

## 8. Cómo repetir la prueba en Windows

Repositorio en `C:\xampp\htdocs\PFA-taller`. Hace falta Node.js 20 o superior. Los comandos son de PowerShell.

```powershell
cd C:\xampp\htdocs\PFA-taller\frontend
npm install
npm test
npx vitest run --coverage
npm run build
npm run dev
```

`npm test` incluye las nueve pruebas de axe-core 4.10.3. Con el servidor en marcha, abra http://localhost:5173 e inicie sesión con un usuario de demostración.

Para las capturas de la sección 6, en cada ruta:

1. WAVE (extensión). Anote errores, contrastes y alertas.
2. Lighthouse, modo Navegación, categoría Accessibility. El rendimiento medido con `npm run dev` no es un criterio WCAG: si hace falta una cifra de Performance, use `npm run build` y `npm run preview`.
3. axe DevTools 4.10.3. En el filtro elija WCAG 2.1 AA y, si la extensión lo ofrece, WCAG 2.2 AA.

NVDA, sección 7. **Pendiente: completar por el equipo.**

[← Volver al README Principal](../../../README.md)
