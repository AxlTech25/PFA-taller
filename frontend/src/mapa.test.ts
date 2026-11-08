import { beforeEach, describe, expect, it, vi } from "vitest";

import {
  MENSAJE_TILES,
  OSRM_URL,
  etiquetaCongestion,
  nivelCongestion,
  olvidarGeometrias,
  trazado,
  trazadoPorCalles,
} from "./mapa";

function respuestaOsrm(coordenadas: [number, number][], code = "Ok", ok = true) {
  return {
    ok,
    status: ok ? 200 : 500,
    json: async () => ({ code, routes: [{ geometry: { coordinates: coordenadas } }] }),
  };
}

describe("trazado por calles", () => {
  beforeEach(() => olvidarGeometrias());

  it("pide la ruta a OSRM y devuelve la geometría en latitud, longitud", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      respuestaOsrm([
        [-76.98, -12.01],
        [-76.985, -12.012],
        [-76.99, -12.02],
      ]),
    );
    vi.stubGlobal("fetch", fetchMock);
    const linea = await trazadoPorCalles([
      [-12.01, -76.98],
      [-12.02, -76.99],
    ]);
    expect(linea).toEqual([
      [-12.01, -76.98],
      [-12.012, -76.985],
      [-12.02, -76.99],
    ]);
    expect(String(fetchMock.mock.calls[0][0])).toBe(
      `${OSRM_URL}/route/v1/driving/-76.98,-12.01;-76.99,-12.02?overview=full&geometries=geojson`,
    );
    await trazadoPorCalles([
      [-12.01, -76.98],
      [-12.02, -76.99],
    ]);
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("parte las rutas largas en tramos y no repite el punto de unión", async () => {
    const puntos: [number, number][] = Array.from({ length: 30 }, (_, i) => [-12 - i / 100, -77]);
    const fetchMock = vi.fn(async (url: string) => {
      const pares = url.split("/driving/")[1].split("?")[0].split(";");
      return respuestaOsrm(pares.map((par) => par.split(",").map(Number) as [number, number]));
    });
    vi.stubGlobal("fetch", fetchMock);
    const linea = await trazadoPorCalles(puntos, "http://osrm.local");
    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(String(fetchMock.mock.calls[0][0]).split(";")).toHaveLength(25);
    expect(String(fetchMock.mock.calls[1][0]).split(";")).toHaveLength(6);
    expect(linea).toEqual(puntos);
  });

  it("usa la línea recta si OSRM falla o no encuentra ruta", async () => {
    const puntos: [number, number][] = [
      [-12.01, -76.98],
      [-12.02, -76.99],
    ];
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(respuestaOsrm([], "Ok", false)));
    expect(await trazadoPorCalles(puntos)).toEqual(puntos);
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(respuestaOsrm([[-76.98, -12.01]], "NoRoute")));
    expect(await trazadoPorCalles(puntos)).toEqual(puntos);
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, status: 200, json: async () => [] }));
    expect(await trazadoPorCalles(puntos)).toEqual(puntos);
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("sin red")));
    expect(await trazadoPorCalles(puntos)).toEqual(puntos);
  });

  it("no consulta OSRM con menos de dos puntos", async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    expect(await trazadoPorCalles([[-12.01, -76.98]])).toEqual([[-12.01, -76.98]]);
    expect(fetchMock).not.toHaveBeenCalled();
  });
});

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
