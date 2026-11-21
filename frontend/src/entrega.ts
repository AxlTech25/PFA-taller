/**
 * Punto de integración de US-018 (Sprint 6).
 *
 * La pantalla deja la acción operable con teclado y conserva `idDetalle`,
 * que es el `id_detalle` de la parada. Persistirlo como ENTREGADO o FALLIDO
 * (y responder 403 si la parada es de otro conductor) no se hace aquí:
 * no hay llamada a la API.
 */
export const MENSAJE_CONFIRMACION_PENDIENTE =
  "la confirmación quedó en esta pantalla y todavía no se guarda.";

export type ConfirmacionPendiente = {
  idDetalle: string;
  mensaje: string;
};

export function prepararConfirmacionEntrega(idDetalle: string): ConfirmacionPendiente {
  return {
    idDetalle,
    mensaje: MENSAJE_CONFIRMACION_PENDIENTE,
  };
}
