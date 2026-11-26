import { describe, expect, it } from "vitest";

import {
  MENSAJE_MOTIVO,
  MOTIVO_MAXIMO,
  prepararConfirmacionEntrega,
  puedeConfirmar,
  rutaConfirmacion,
} from "./entrega";

describe("confirmación de entrega", () => {
  it("ENTREGADO no lleva motivo", () => {
    expect(prepararConfirmacionEntrega("ENTREGADO", "algo")).toEqual({
      resultado: "ENTREGADO",
      motivo: null,
    });
  });

  it("FALLIDO exige motivo y lo limpia", () => {
    expect(prepararConfirmacionEntrega("FALLIDO", "   ")).toEqual({ error: MENSAJE_MOTIVO });
    expect(prepararConfirmacionEntrega("FALLIDO", "  Cliente \n ausente ")).toEqual({
      resultado: "FALLIDO",
      motivo: "Cliente ausente",
    });
    const largo = prepararConfirmacionEntrega("FALLIDO", "a".repeat(400));
    expect("motivo" in largo && largo.motivo?.length).toBe(MOTIVO_MAXIMO);
  });

  it("solo se confirman paradas pendientes o reprogramadas", () => {
    expect(puedeConfirmar("PENDIENTE")).toBe(true);
    expect(puedeConfirmar("REPROGRAMADO")).toBe(true);
    expect(puedeConfirmar("ENTREGADO")).toBe(false);
    expect(puedeConfirmar("FALLIDO")).toBe(false);
  });

  it("arma la ruta de la API", () => {
    expect(rutaConfirmacion("detalle-1")).toBe("/modo/paradas/detalle-1/confirmacion");
  });
});
