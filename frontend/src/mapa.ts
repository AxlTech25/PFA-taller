/** Reglas de dibujo del mapa (US-012). El semáforo replica el criterio del API. */

export type NivelCongestion = "VERDE" | "AMARILLO" | "ROJO";

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
