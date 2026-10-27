import { describe, expect, it } from "vitest";

import { MENSAJE_TILES, etiquetaCongestion, nivelCongestion, trazado } from "./mapa";

describe("mapa de rutas", () => {
  it("arma el trazado desde el punto de partida y omite paradas sin coordenada", () => {
    expect(
      trazado(-12.01, -76.98, [
        { latitud: -12.02, longitud: -76.99 },
        { latitud: null, longitud: null },
      ]),
    ).toEqual([
      [-12.01, -76.98],
      [-12.02, -76.99],
    ]);
    expect(trazado(null, null, [])).toEqual([]);
    expect(trazado(-12.01, null, [{ latitud: -12.02, longitud: -76.99 }])).toEqual([
      [-12.02, -76.99],
    ]);
    expect(trazado(null, -76.98, [{ latitud: null, longitud: -76.99 }])).toEqual([]);
  });

  it("pinta el semáforo con el factor y la hora punta", () => {
    expect(nivelCongestion(1, "2026-11-02T11:00:00Z")).toBe("VERDE");
    expect(nivelCongestion(1, "2026-11-02T08:00:00Z")).toBe("AMARILLO");
    expect(nivelCongestion(1.2, "2026-11-02T11:00:00Z")).toBe("AMARILLO");
    expect(nivelCongestion(1.4, "2026-11-02T11:00:00Z")).toBe("ROJO");
    expect(nivelCongestion(1.15, "2026-11-02T08:30:00Z")).toBe("ROJO");
    expect(nivelCongestion(1.15, "2026-11-02T18:00:00Z")).toBe("ROJO");
    expect(nivelCongestion(1.15, "2026-11-02T12:00:00Z")).toBe("AMARILLO");
    expect(nivelCongestion(1, null)).toBe("VERDE");
    expect(nivelCongestion(1, "sin-hora")).toBe("VERDE");
    expect(etiquetaCongestion("VERDE")).toBe("Verde");
    expect(etiquetaCongestion("AMARILLO")).toBe("Amarillo");
    expect(etiquetaCongestion("ROJO")).toBe("Rojo");
    expect(etiquetaCongestion(null)).toBe("Sin dato");
    expect(etiquetaCongestion(undefined)).toBe("Sin dato");
    expect(MENSAJE_TILES).toMatch(/OpenStreetMap/);
    expect(MENSAJE_TILES).toMatch(/tabla/);
  });
});
