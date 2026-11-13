import { describe, expect, it } from "vitest";

import { comoPagina, rutaPagina, TAMANO_PAGINA } from "./listado";

describe("listados de 12", () => {
  it("normaliza un arreglo legado y una página del API", () => {
    expect(TAMANO_PAGINA).toBe(12);
    expect(comoPagina([{ id: 1 }]).items).toEqual([{ id: 1 }]);
    expect(comoPagina<number>([]).total_pages).toBe(0);
    const pagina = {
      items: [1],
      total: 20,
      page: 2,
      page_size: 12,
      total_pages: 2,
    };
    expect(comoPagina(pagina)).toBe(pagina);
    expect(rutaPagina("/vehiculos", 2)).toBe("/vehiculos?page=2&limite=12");
    expect(rutaPagina("/rutas?fecha=2026-11-12", 1)).toBe("/rutas?fecha=2026-11-12&page=1&limite=12");
  });
});
