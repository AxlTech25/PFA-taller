import { describe, expect, it } from "vitest";

import { respuestaSpa } from "./proxy";

describe("proxy del servidor de desarrollo", () => {
  it("entrega el SPA al abrir una ruta en el navegador", () => {
    expect(respuestaSpa("GET", "text/html,application/xhtml+xml")).toBe("/index.html");
    expect(respuestaSpa("HEAD", "text/html")).toBe("/index.html");
  });

  it("deja pasar el login aunque el cliente anuncie text/html", () => {
    const accept = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8";
    expect(respuestaSpa("POST", accept)).toBeUndefined();
    expect(respuestaSpa("POST", "*/*")).toBeUndefined();
    expect(respuestaSpa("GET", "*/*")).toBeUndefined();
  });
});
