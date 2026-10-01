import { describe, expect, it } from "vitest";

import { mensajeError } from "./api";
import {
  etiquetaRol,
  modulosVisibles,
  puedeEditarFlota,
  puedeGestionarUsuarios,
  puedeRegistrarConductor,
  puedeRegistrarFlota,
  puedeRegistrarPedido,
} from "./permissions";

describe("permisos de Sprint 2", () => {
  it("solo administrador y operador registran vehículos", () => {
    expect(puedeRegistrarFlota("ADMIN")).toBe(true);
    expect(puedeRegistrarFlota("OPERADOR")).toBe(true);
    expect(puedeRegistrarFlota("GERENTE")).toBe(false);
    expect(puedeRegistrarFlota("CONDUCTOR")).toBe(false);
    expect(puedeRegistrarFlota("AUDITOR")).toBe(false);
  });

  it("el conductor no edita flota ni abre usuarios", () => {
    expect(puedeEditarFlota("GERENTE")).toBe(true);
    expect(puedeEditarFlota("CONDUCTOR")).toBe(false);
    expect(puedeGestionarUsuarios("ADMIN")).toBe(true);
    expect(puedeGestionarUsuarios("OPERADOR")).toBe(false);
    expect(puedeRegistrarConductor("OPERADOR")).toBe(true);
    expect(puedeRegistrarPedido("OPERADOR")).toBe(true);
    expect(puedeRegistrarPedido("CONDUCTOR")).toBe(false);
    expect(modulosVisibles("ADMIN")).toEqual(["flota", "conductores", "pedidos", "usuarios"]);
    expect(modulosVisibles("OPERADOR")).toEqual(["flota", "conductores", "pedidos"]);
    expect(modulosVisibles("CONDUCTOR")).toEqual(["flota", "modo"]);
    expect(modulosVisibles("CONDUCTOR")).not.toContain("usuarios");
  });

  it("traduce el rol y los mensajes de la API", () => {
    expect(etiquetaRol("OPERADOR")).toBe("Operador");
    expect(mensajeError({ detail: "La placa ya se encuentra registrada" })).toBe(
      "La placa ya se encuentra registrada",
    );
    expect(mensajeError({})).toBe("No se pudo completar la operación.");
  });
});
