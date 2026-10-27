import { describe, expect, it } from "vitest";

import { mensajeError } from "./api";
import {
  etiqueta,
  etiquetaRol,
  modulosVisibles,
  puedeEditarFlota,
  puedeGestionarUsuarios,
  puedeRegistrarConductor,
  puedeRegistrarFlota,
  puedeGenerarRutas,
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
    expect(puedeGenerarRutas("OPERADOR")).toBe(true);
    expect(puedeGenerarRutas("GERENTE")).toBe(false);
    expect(puedeGenerarRutas("CONDUCTOR")).toBe(false);
    expect(modulosVisibles("ADMIN")).toEqual([
      "flota",
      "conductores",
      "pedidos",
      "rutas",
      "dashboard",
      "usuarios",
    ]);
    expect(modulosVisibles("OPERADOR")).toEqual([
      "flota",
      "conductores",
      "pedidos",
      "rutas",
      "dashboard",
    ]);
    expect(modulosVisibles("CONDUCTOR")).toEqual(["flota", "modo"]);
    expect(modulosVisibles("CONDUCTOR")).not.toContain("dashboard");
    expect(modulosVisibles("CONDUCTOR")).not.toContain("usuarios");
  });

  it("abre el tablero al gerente y al auditor, y deja la flota si el rol no existe", () => {
    expect(modulosVisibles("GERENTE")).toEqual([
      "flota",
      "conductores",
      "pedidos",
      "rutas",
      "dashboard",
      "usuarios",
    ]);
    expect(modulosVisibles("AUDITOR")).toEqual([
      "flota",
      "conductores",
      "pedidos",
      "rutas",
      "dashboard",
    ]);
    expect(modulosVisibles("DESCONOCIDO")).toEqual(["flota"]);
    expect(puedeEditarFlota("AUDITOR")).toBe(false);
    expect(puedeRegistrarConductor("GERENTE")).toBe(false);
    expect(puedeRegistrarFlota("")).toBe(false);
  });

  it("traduce el rol y los mensajes de la API", () => {
    expect(etiquetaRol("OPERADOR")).toBe("Operador");
    expect(etiqueta("PERECEDERO")).toBe("Perecedero");
    expect(etiqueta("codigo-libre")).toBe("codigo-libre");
    expect(etiquetaRol("codigo-libre")).toBe("codigo-libre");
    expect(mensajeError({ detail: "La placa ya se encuentra registrada" })).toBe(
      "La placa ya se encuentra registrada",
    );
    expect(mensajeError({})).toBe("No se pudo completar la operación.");
  });
});
