/** Reglas de dibujo del mapa (US-012). El semáforo replica el criterio del API. */

export type NivelCongestion = "VERDE" | "AMARILLO" | "ROJO";

type Punto = [number, number];

export const OSRM_URL: string =
  import.meta.env.VITE_OSRM_URL || "https://router.project-osrm.org";

/** El servidor público de OSRM rechaza pedidos con demasiadas coordenadas. */
const MAX_PUNTOS_POR_PEDIDO = 25;
const ESPERA_MAXIMA_MS = 8000;

const geometrias = new Map<string, Punto[]>();

export const MENSAJE_TILES =
  "No se pudo cargar el mapa de OpenStreetMap. La secuencia de entregas sigue disponible en la tabla.";

export function nivelCongestion(factor: number, eta: string | null): NivelCongestion {
  const hora = eta ? Number(eta.slice(11, 13)) : null;
  const punta = hora != null && !Number.isNaN(hora) && ((hora >= 7 && hora < 9) || (hora >= 17 && hora < 20));
  if (factor >= 1.35 || (punta && factor >= 1.15)) return "ROJO";
  if (factor >= 1.15 || punta) return "AMARILLO";
  return "VERDE";
}

export function etiquetaCongestion(nivel: string | null | undefined): string {
  if (nivel === "VERDE") return "Verde";
  if (nivel === "AMARILLO") return "Amarillo";
  if (nivel === "ROJO") return "Rojo";
  return "Sin dato";
}

export function trazado(
  origenLat: number | null | undefined,
  origenLon: number | null | undefined,
  paradas: { latitud?: number | null; longitud?: number | null }[],
): [number, number][] {
  const puntos: [number, number][] = [];
  if (origenLat != null && origenLon != null) puntos.push([origenLat, origenLon]);
  for (const parada of paradas) {
    if (parada.latitud != null && parada.longitud != null) {
      puntos.push([parada.latitud, parada.longitud]);
    }
  }
  return puntos;
}

function tramos(puntos: Punto[]): Punto[][] {
  const resultado: Punto[][] = [];
  for (let inicio = 0; inicio < puntos.length - 1; inicio += MAX_PUNTOS_POR_PEDIDO - 1) {
    resultado.push(puntos.slice(inicio, inicio + MAX_PUNTOS_POR_PEDIDO));
  }
  return resultado;
}

async function geometriaDeTramo(base: string, tramo: Punto[], senal: AbortSignal): Promise<Punto[]> {
  const coordenadas = tramo.map(([lat, lon]) => `${lon},${lat}`).join(";");
  const respuesta = await fetch(
    `${base}/route/v1/driving/${coordenadas}?overview=full&geometries=geojson`,
    { signal: senal },
  );
  if (!respuesta.ok) throw new Error(`OSRM respondió ${respuesta.status}`);
  const cuerpo = (await respuesta.json()) as {
    code?: string;
    routes?: { geometry?: { coordinates?: unknown } }[];
  };
  const linea = cuerpo.routes?.[0]?.geometry?.coordinates;
  if (cuerpo.code !== "Ok" || !Array.isArray(linea) || linea.length < 2) {
    throw new Error("OSRM no devolvió una ruta");
  }
  return (linea as [number, number][]).map(([lon, lat]) => [lat, lon]);
}

/**
 * Geometría siguiendo las calles (OSRM sobre OpenStreetMap). Si el servicio
 * falla o tarda, devuelve los mismos puntos para no dejar el mapa sin trazado.
 */
export async function trazadoPorCalles(puntos: Punto[], base = OSRM_URL): Promise<Punto[]> {
  if (puntos.length < 2) return puntos;
  const clave = `${base}|${puntos.map((punto) => punto.join(",")).join(";")}`;
  const guardada = geometrias.get(clave);
  if (guardada) return guardada;

  const control = new AbortController();
  const reloj = setTimeout(() => control.abort(), ESPERA_MAXIMA_MS);
  try {
    const partes = await Promise.all(
      tramos(puntos).map((tramo) => geometriaDeTramo(base, tramo, control.signal)),
    );
    const linea = partes.flatMap((parte, indice) => (indice === 0 ? parte : parte.slice(1)));
    geometrias.set(clave, linea);
    return linea;
  } catch {
    return puntos;
  } finally {
    clearTimeout(reloj);
  }
}

export function olvidarGeometrias() {
  geometrias.clear();
}
