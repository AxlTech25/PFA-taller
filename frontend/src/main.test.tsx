import { waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

describe("arranque", () => {
  it("monta la aplicación en el nodo raíz", async () => {
    document.body.innerHTML = '<div id="root"></div>';
    vi.resetModules();
    await import("./main");
    await waitFor(() => expect(document.body.textContent).toContain("Entrar"));
  });

  it("se detiene si no está el nodo raíz", async () => {
    document.body.innerHTML = "";
    vi.resetModules();
    await expect(import("./main")).rejects.toThrow("No se encontró el nodo raíz");
  });
});
