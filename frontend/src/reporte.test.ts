import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError } from "./api";
import { errorPeriodo, guardarArchivo, nombreReporte, pedirReporte } from "./reporte";

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("reporte PDF", () => {
  it("valida el período como la API", () => {
    expect(errorPeriodo("2026-11-01", "2026-11-01")).toBeNull();
    expect(errorPeriodo("2026-11-01", "2026-12-01")).toBeNull();
    expect(errorPeriodo("2026-11-01", "2026-12-02")).toMatch(/31 días/);
    expect(errorPeriodo("2026-11-02", "2026-11-01")).toMatch(/anterior a la inicial/);
    expect(errorPeriodo("", "2026-11-01")).toMatch(/fecha inicial y la final/);
    expect(errorPeriodo("x", "2026-11-01")).toMatch(/fechas válidas/);
    expect(nombreReporte("2026-11-01", "2026-11-02")).toBe(
      "reporte-sostenibilidad-2026-11-01_2026-11-02.pdf",
    );
  });

  it("pide el PDF con el token y sin caché", async () => {
    const blob = new Blob(["%PDF-1.4"], { type: "application/pdf" });
    const fetchMock = vi.fn(async () => ({ ok: true, status: 200, blob: async () => blob }));
    vi.stubGlobal("fetch", fetchMock);
    expect(await pedirReporte("2026-11-01", "2026-11-02", "tok")).toBe(blob);
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toBe("/indicadores/reporte.pdf?desde=2026-11-01&hasta=2026-11-02");
    expect(init.cache).toBe("no-store");
    expect(new Headers(init.headers).get("Authorization")).toBe("Bearer tok");

    await pedirReporte("2026-11-01", "2026-11-02", null);
    const [, sinToken] = fetchMock.mock.calls[1] as unknown as [string, RequestInit];
    expect(new Headers(sinToken.headers).has("Authorization")).toBe(false);
  });

  it("convierte el 404 sin datos y las respuestas sin JSON en ApiError", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => ({
        ok: false,
        status: 404,
        json: async () => ({ detail: "Sin datos de operación para el período seleccionado." }),
      })),
    );
    await expect(pedirReporte("2099-01-01", "2099-01-02", "tok")).rejects.toEqual(
      new ApiError(404, "Sin datos de operación para el período seleccionado."),
    );
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => ({ ok: false, status: 502, json: async () => Promise.reject(new Error("html")) })),
    );
    await expect(pedirReporte("2026-11-01", "2026-11-01", "tok")).rejects.toMatchObject({ status: 502 });
  });

  it("descarga el archivo con un enlace temporal", () => {
    const crear = vi.fn(() => "blob:reporte");
    const revocar = vi.fn();
    vi.stubGlobal("URL", { ...URL, createObjectURL: crear, revokeObjectURL: revocar });
    const clic = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {});
    vi.useFakeTimers();
    guardarArchivo(new Blob(["x"]), "r.pdf");
    expect(crear).toHaveBeenCalled();
    expect(clic).toHaveBeenCalledTimes(1);
    expect(document.querySelector("a[download]")).toBeNull();
    vi.runAllTimers();
    expect(revocar).toHaveBeenCalledWith("blob:reporte");
    vi.useRealTimers();
  });
});
