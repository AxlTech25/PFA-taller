import { describe, expect, it } from "vitest";

import { mensajeError } from "./api";
import { etiquetaRol, puedeRegistrarFlota } from "./permissions";

describe("permisos de Sprint 1", () => {
  it("solo administrador y operador registran vehículos", () => {
    expect(puedeRegistrarFlota("ADMIN")).toBe(true);
    expect(puedeRegistrarFlota("OPERADOR")).toBe(true);
    expect(puedeRegistrarFlota("GERENTE")).toBe(false);
    expect(puedeRegistrarFlota("CONDUCTOR")).toBe(false);
    expect(puedeRegistrarFlota("AUDITOR")).toBe(false);
  });

  it("traduce el rol y los mensajes de la API", () => {
    expect(etiquetaRol("OPERADOR")).toBe("Operador");
    expect(mensajeError({ detail: "La placa ya se encuentra registrada" })).toBe(
      "La placa ya se encuentra registrada",
    );
    expect(mensajeError({})).toBe("No se pudo completar la operación.");
  });
});
