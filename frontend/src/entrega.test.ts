import { describe, expect, it } from "vitest";

import { MENSAJE_CONFIRMACION_PENDIENTE, prepararConfirmacionEntrega } from "./entrega";

describe("confirmación de entrega", () => {
  it("conserva el detalle y no describe un guardado", () => {
    const pendiente = prepararConfirmacionEntrega("detalle-1");
    expect(pendiente.idDetalle).toBe("detalle-1");
    expect(pendiente.mensaje).toBe(MENSAJE_CONFIRMACION_PENDIENTE);
    expect(pendiente.mensaje.toLowerCase()).not.toContain("guardó");
    expect(pendiente.mensaje).toContain("no se guarda");
  });
});
