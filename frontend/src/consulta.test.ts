import { describe, expect, it } from "vitest";

import { consultar, vaciarConsultas } from "./consulta";

describe("caché de consultas", () => {
  it("no repite una lectura vigente y sí la repite si se fuerza", async () => {
    vaciarConsultas();
    let llamadas = 0;
    const pedir = async () => {
      llamadas += 1;
      return "flota";
    };
    expect(await consultar(pedir, "/vehiculos?page=1")).toBe("flota");
    expect(await consultar(pedir, "/vehiculos?page=1")).toBe("flota");
    expect(llamadas).toBe(1);
    expect(await consultar(pedir, "/vehiculos?page=1", true)).toBe("flota");
    expect(llamadas).toBe(2);
    vaciarConsultas();
    expect(await consultar(pedir, "/vehiculos?page=1")).toBe("flota");
    expect(llamadas).toBe(3);
  });
});
