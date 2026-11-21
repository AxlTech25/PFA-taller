[← Volver al índice de implementación](../README.md)

# ENB-008 Presupuesto de datos del modo conductor

**Proyecto:** EcoLogística Lima  
**Historia técnica:** ENB-008 / ECO-30  
**Versión:** V_1_0_0  
**Fecha de la medición:** 21/11/2026

El criterio de [01 Transformando a ágil V_1_0_10](../../02%20Planificación/01%20Transformando%20a%20ágil%20V_1_0_10.md) pide dos cosas. La transferencia de la consulta de una ruta de 12 paradas pesa como máximo 150 KB. En 2G la secuencia tabular carga primero y el mapa queda opcional. RNF-009 añade que la carga inicial en 3G simulada sea de como máximo 5 s.

## 1. Qué se midió

La sesión es la navegación a `/modo` ya autenticada, hasta que la lista `ol.lista-paradas` está visible. El byte contado es `responseBodySize + responseHeadersSize` de Playwright 1.65.1 (cuerpo codificado más cabeceras). El reloj es el de la prueba, desde `goto` hasta esa lista.

El servidor es `frontend/scripts/servir.mjs` con Brotli de los artefactos de `npm run build` y la API en `http://127.0.0.1:8000`. Delante hay un proxy del propio test que aplica latencia y un techo de bajada por respuesta. Chromium no aplicó `Network.emulateNetworkConditions` a `127.0.0.1`: en un intento previo, 3G y 2G tardaron 1 443 ms y 1 444 ms. Esas dos cifras no se usan como tiempo de red. El tiempo de esta sección sale del proxy.

Perfiles, en bytes por segundo = bits por segundo / 8:

| Perfil | Bajada | Latencia | Origen del número |
|---|---|---|---|
| 3G rápida | 1,6 Mbit/s | 150 ms | Fast 3G de Chrome DevTools |
| 2G | 250 kbit/s | 300 ms | Regular 2G, perfil que DevTools ya no muestra |

La ruta es la del usuario `conductor.presupuesto@distrirapido.example.com`: 12 paradas, unidad DMO-101, cliente Bodega El Ahorro, sin kilómetros ni CO₂. La crea la carga inicial cuando `SEED_CONDUCTOR_PASSWORD` tiene al menos 8 caracteres.

Navegador de la corrida: Chromium for Testing 159.0.8154.6, el que instala Playwright 1.65.1. Node v22.23.4. Una sola pasada, la del 21/11/2026 que dejó el test en verde.

## 2. Resultados

| Medición | Valor |
|---|---|
| Paradas visibles | 12 |
| Bytes de la sesión en 3G rápida | 69 027 |
| Tiempo hasta la lista en 3G rápida | 1 328 ms |
| Bytes de la sesión en 2G | 69 027 |
| Tiempo hasta la lista en 2G | 3 737 ms |
| Peticiones a mapa, Leaflet o teselas antes de la lista | 0 |
| Tope de bytes | 153 600 (150 × 1 024) |
| Tope de tiempo en 3G | 5 000 ms |

69 027 bytes son 67,4 KB (69 027 / 1 024). Cabe en el tope. El tiempo de 3G también.

La consulta `GET /modo/jornada` de esas 12 paradas, sola, midió 3 802 bytes sin compresión (`Accept-Encoding: identity`, `content-length: 3802`) y 814 bytes con Brotli (`content-encoding: br`, `content-length: 814`). No trae coordenadas ni indicadores de gerencia.

Al pulsar **Ver mapa**, todavía con el ritmo 2G, el navegador pidió recién entonces `GET /modo/mapa`, el archivo `leaflet-src-Cwq2at8A.js` y 12 teselas `https://tile.openstreetmap.org/14/...png`. La lista seguía visible. Esas teselas no entran en los 69 027 bytes.

## 3. Artefactos de la compilación

`vite build` 8.3.6, la misma corrida. Tamaños que imprime Vite, no la transferencia de la sesión:

| Archivo | Tamaño | Gzip que imprime Vite |
|---|---|---|
| `index-QLnrNcxA.js` | 188,48 kB | 62,66 kB |
| `ModoConductorPage-CGchr88t.js` | 4,76 kB | 1,80 kB |
| `ModoMapa-C22xw1cJ.js` | 2,50 kB | 1,27 kB |
| `leaflet-src-Cwq2at8A.js` | 148,61 kB | 43,33 kB |
| `index-DgVz3HfY.css` | 7,53 kB | 2,34 kB |

Leaflet y `ModoMapa` son chunks aparte. No se piden hasta **Ver mapa**.

## 4. Qué no se midió

No hay una pasada en una red móvil real ni en el sitio de Vercel. No se sumó el login: la sesión medida empieza en `/modo` con la sesión ya guardada. No se afirmó un tope de tiempo para 2G; el criterio de 5 s es el de 3G. El perfil 2G es el Regular 2G histórico, no un perfil con nombre dentro de Chrome DevTools actual.

## 5. Cómo repetirlo

Con la API en el puerto 8000, la base migrada y `SEED_CONDUCTOR_PASSWORD` definida:

```bash
cd backend && python -m app.seed
cd ../frontend && npm run build
npx playwright test e2e/modo-presupuesto.spec.ts --project=chromium
```

La prueba escribe `frontend/test-results/modo-presupuesto.json` y falla si la sesión pasa de 150 KB, si la lista tarda más de 5 s en 3G rápida, o si antes de la lista hay una petición de mapa, de Leaflet o de tesela.

| Versión | Fecha | Autor | Cambio |
|---|---|---|---|
| 1.0.0 | 21/11/2026 | Equipo EcoLogística Lima | Primera medición de ENB-008 sobre el modo conductor. |
