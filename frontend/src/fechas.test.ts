import { describe, expect, it } from "vitest";

import { fechaHoy, fechaHoraLocal, fechaVisible, horaVisible } from "./fechas";

describe("fechas con Intl", () => {
  it("arma la fecha local sin una librería", () => {
    const dia = new Date(2026, 10, 12, 8, 30);
    expect(fechaHoy(dia)).toBe("2026-11-12");
    expect(fechaHoraLocal("08:00", dia)).toBe("2026-11-12T08:00");
  });

  it("muestra fecha y hora de la jornada sin Intl", () => {
    expect(fechaVisible("2026-11-21")).toBe("21/11/2026");
    expect(fechaVisible("2026-11-21T08:15:00+00:00")).toBe("21/11/2026");
    expect(fechaVisible("hoy")).toBe("hoy");
    expect(horaVisible("2026-11-21T08:15:00Z")).toBe("08:15");
    expect(horaVisible("2026-11-21T10:40:00+00:00")).toBe("10:40");
    expect(horaVisible(null)).toBe("Sin hora");
    expect(horaVisible("sin-hora")).toBe("Sin hora");
  });
});
