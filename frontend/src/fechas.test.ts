import { describe, expect, it } from "vitest";

import { fechaHoy, fechaHoraLocal } from "./fechas";

describe("fechas con Intl", () => {
  it("arma la fecha local sin una librería", () => {
    const dia = new Date(2026, 10, 12, 8, 30);
    expect(fechaHoy(dia)).toBe("2026-11-12");
    expect(fechaHoraLocal("08:00", dia)).toBe("2026-11-12T08:00");
  });
});
