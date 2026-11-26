/**
 * Confirmación de entrega (US-018).
 *
 * El conductor registra ENTREGADO o FALLIDO en una parada de su ruta.
 * FALLIDO exige motivo. La API responde 403 si la parada es de otro
 * conductor, 404 si no existe y 409 si ya tenía resultado.
 */
export type ResultadoEntrega = "ENTREGADO" | "FALLIDO";

export const MOTIVO_MAXIMO = 250;
export const MENSAJE_MOTIVO = "Indique el motivo cuando la entrega es fallida.";

export type ConfirmacionEntrega = {
  resultado: ResultadoEntrega;
  motivo: string | null;
};

export type ConfirmacionEntregaOut = {
  id_detalle: string;
  secuencia: number;
  estado_entrega: ResultadoEntrega;
  motivo_fallo?: string | null;
  confirmada_en: string;
  mensaje: string;
};

export function rutaConfirmacion(idDetalle: string): string {
  return `/modo/paradas/${encodeURIComponent(idDetalle)}/confirmacion`;
}

/** Normaliza el formulario. Devuelve el texto del error si falta el motivo. */
export function prepararConfirmacionEntrega(
  resultado: ResultadoEntrega,
  motivo: string,
): ConfirmacionEntrega | { error: string } {
  if (resultado === "ENTREGADO") return { resultado, motivo: null };
  const limpio = motivo.replace(/\s+/g, " ").trim();
  if (!limpio) return { error: MENSAJE_MOTIVO };
  return { resultado, motivo: limpio.slice(0, MOTIVO_MAXIMO) };
}

export function puedeConfirmar(estado: string): boolean {
  return estado === "PENDIENTE" || estado === "REPROGRAMADO";
}
