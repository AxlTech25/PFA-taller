import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError, api, mensajeError } from "./api";

describe("mensajes y cliente HTTP", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("une el detalle de validación cuando llega en lista", () => {
    expect(
      mensajeError({
        detail: ["correo", { msg: "obligatorio" }, { campo: "otro" }, "fin"],
      }),
    ).toBe("correo obligatorio Dato inválido fin");
    expect(mensajeError({ detail: 12 })).toBe("No se pudo completar la operación.");
  });

  it("envía JSON y el token, y devuelve el cuerpo", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      status: 200,
      ok: true,
      json: async () => ({ status: "ok" }),
    });
    vi.stubGlobal("fetch", fetchMock);
    await expect(api("/health", { method: "POST", body: "{}" }, "abc")).resolves.toEqual({
      status: "ok",
    });
    const init = fetchMock.mock.calls[0][1] as RequestInit;
    const headers = init.headers as Headers;
    expect(headers.get("Authorization")).toBe("Bearer abc");
    expect(headers.get("Content-Type")).toBe("application/json");
  });

  it("no interpreta un 204", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        status: 204,
        ok: true,
        json: async () => {
          throw new Error("no debería leerse");
        },
      }),
    );
    await expect(api("/x", { method: "DELETE" })).resolves.toBeUndefined();
  });

  it("traduce un error HTTP", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        status: 422,
        ok: false,
        json: async () => ({ detail: "rechazado" }),
      }),
    );
    await expect(api("/pedidos", { method: "POST", body: "{}" })).rejects.toMatchObject({
      status: 422,
      message: "rechazado",
    });
  });

  it("usa el mensaje genérico si el cuerpo no es JSON", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        status: 500,
        ok: false,
        json: async () => {
          throw new Error("no json");
        },
      }),
    );
    await expect(api("/health")).rejects.toBeInstanceOf(ApiError);
  });
});
