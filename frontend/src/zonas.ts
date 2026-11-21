import type { ZonaRestriccion } from "./types";

/** Mismo texto que devuelve el API. Va en el primer render para no mover el mapa al llegar la respuesta. */
export const ADVERTENCIA_ZONAS =
  "Las zonas cuyo nombre empieza por DEMO son polígonos ilustrativos de la demostración. No son el catastro del INEI ni el límite oficial de una reserva ecológica o de una zona de riesgo.";

export function etiquetaZona(tipo: string): string {
  if (tipo === "RESERVA_ECOLOGICA") return "Reserva ecológica";
  if (tipo === "RIESGO_SEGURIDAD") return "Zona de riesgo";
  if (tipo === "RESTRICCION_HORARIA") return "Restricción horaria";
  if (tipo === "CENTRO_HISTORICO") return "Centro histórico";
  if (tipo === "VIA_NO_PAVIMENTADA") return "Vía no pavimentada";
  if (tipo === "BAJA_VISIBILIDAD") return "Baja visibilidad";
  return tipo;
}

export function anilloZona(zona: ZonaRestriccion): [number, number][] {
  const exterior = zona.geometria?.coordinates?.[0] ?? [];
  return exterior
    .filter((par) => Array.isArray(par) && par.length >= 2)
    .map(([lon, lat]) => [lat, lon]);
}

function esZona(valor: unknown): valor is ZonaRestriccion {
  if (!valor || typeof valor !== "object") return false;
  const zona = valor as ZonaRestriccion;
  return (
    typeof zona.id_zona === "string" &&
    typeof zona.nombre === "string" &&
    typeof zona.tipo === "string" &&
    zona.geometria?.type === "Polygon" &&
    Array.isArray(zona.geometria.coordinates)
  );
}

export function comoZonas(data: unknown): { advertencia: string; zonas: ZonaRestriccion[] } {
  if (!data || typeof data !== "object" || Array.isArray(data)) {
    return { advertencia: "", zonas: [] };
  }
  const cuerpo = data as { advertencia?: unknown; zonas?: unknown };
  const zonas = Array.isArray(cuerpo.zonas) ? cuerpo.zonas.filter(esZona) : [];
  const advertencia = typeof cuerpo.advertencia === "string" ? cuerpo.advertencia : "";
  return { advertencia, zonas };
}
