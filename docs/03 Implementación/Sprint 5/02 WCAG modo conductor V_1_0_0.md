[← Volver al índice de implementación](../README.md)

# ENB-005 Accesibilidad del modo conductor

**Proyecto:** EcoLogística Lima  
**Historia técnica:** ENB-005 / ECO-29  
**Nivel:** WCAG 2.2 AA  
**Versión:** V_1_0_0  
**Fecha de la revisión:** 21/11/2026

El criterio pide contraste, nombres accesibles y un recorrido por teclado hasta confirmar la entrega, con el foco visible y en un orden lógico. Confirmar no guarda el resultado: persistir ENTREGADO o FALLIDO sigue siendo US-018. Esta revisión audita la acción que ya existe.

## 1. Alcance

Pantalla `/modo` con el conductor de demostración (`conductor@distrirapido.example.com`) y su ruta de tres paradas. La ruta de 12 paradas del presupuesto usa los mismos controles. No se auditó el resto de módulos: eso está en [05 WCAG V_1_0_0](../Sprint%203/05%20WCAG%20V_1_0_0.md).

## 2. axe-core en el navegador

`@axe-core/playwright` 4.10.2 sobre axe-core 4.10.3, etiquetas `wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa` y `wcag22aa`. A diferencia del Vitest en jsdom, aquí `color-contrast` queda activa.

Ejecución local del 21/11/2026, Chromium for Testing 159.0.8154.6, Playwright 1.65.1, prueba `el modo conductor no tiene violaciones WCAG 2.2 AA`: **0 violaciones**. La misma prueba corre en CI en Chromium, Firefox y WebKit. Esta cifra local es solo la de Chromium.

Vitest sigue auditando la misma pantalla en jsdom, con el contraste apagado porque ahí no hay diseño real. El botón **Ver mapa** entra en ese árbol.

## 3. Contraste calculado

Relación de contraste WCAG a partir de los hexadecimales de `frontend/src/styles.css`, con la luminancia relativa del criterio 1.4.3. No es una captura de WAVE. El mínimo AA para texto normal es 4,5:1.

| Par | Relación |
|---|---|
| `#10241c` sobre `#ffffff` | 16,26:1 |
| `#10241c` sobre `#f4f7f5` | 15,08:1 |
| `#3d5248` sobre `#ffffff` | 8,40:1 |
| `#3d5248` sobre `#f4f7f5` | 7,79:1 |
| `#6a4b00` sobre `#fff6df` (aviso y semáforo amarillo) | 7,44:1 |
| `#0d5c32` sobre `#e7f6ee` (pendiente y semáforo verde) | 7,25:1 |
| `#ffffff` sobre `#08553d` (botón y número de parada) | 8,83:1 |
| `#7a1b1b` sobre `#fdecec` | 9,19:1 |

## 4. Teclado y foco

La prueba `el teclado llega a confirmar entrega antes que al mapa` tabula desde el inicio de `/modo`. El primer control de la tarea que recibe el foco es **Confirmar entrega de la parada 1**. **Ver mapa** no aparece antes. Enter deja el aviso de que la confirmación no se guarda. Seguir tabulando llega a **Ver mapa** después de los botones de las paradas.

En ese foco, Chromium reportó:

| Propiedad | Valor medido |
|---|---|
| Ancho del botón | 1 208 px |
| Alto del botón | 44 px |
| `outline-style` | `solid` |
| `outline-width` | `3px` |
| `outline-color` | `rgb(16, 36, 28)` (`#10241c`) |

El alto medido es 44 px. El mínimo de 2.5.8 es 24 px. El anillo de la hoja es el mismo de 3 px que ya usa el resto de la aplicación, con una sombra blanca de 3 px para separarlo del fondo.

## 5. Mapa opcional

**Ver mapa** está después de la lista y lleva la descripción «El mapa es opcional. La lista de paradas no lo espera y no se descarga hasta abrirlo». Al abrirlo, Acercar y Alejar reciben nombre en español. La lista no se retira. No se auditó con axe el mapa ya abierto: las teselas y la atribución de OpenStreetMap quedan fuera de esta pasada.

## 6. Qué no se midió

No hay captura WAVE ni puntuación de Lighthouse Accessibility de esta pantalla en esta versión. No se usó un lector de pantalla. Firefox y WebKit no se ejecutaron en la máquina de la medición local; la prueba de axe y la de teclado forman parte del job de Playwright, que sí los abre.

| Versión | Fecha | Autor | Cambio |
|---|---|---|---|
| 1.0.0 | 21/11/2026 | Equipo EcoLogística Lima | Primera auditoría WCAG 2.2 AA del modo conductor real. |
