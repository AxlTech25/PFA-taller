import { render, type RenderResult } from "@testing-library/react";
import type { ReactElement } from "react";
import { MemoryRouter } from "react-router-dom";
import { vi } from "vitest";

import { AuthProvider } from "../auth";
import type { Sesion } from "../types";

export const CLAVE = "ecologistica.sesion";

export type Respuesta = { status?: number; body?: unknown };

export function sesion(rol = "ADMIN", extra: Partial<Sesion> = {}): Sesion {
  return {
    access_token: "token-prueba",
    id_usuario: "11111111-1111-1111-1111-111111111111",
    email: `${rol.toLowerCase()}@distrirapido.example.com`,
    rol,
    ...extra,
  };
}

export function guardarSesion(rol: string | null) {
  sessionStorage.clear();
  if (rol) sessionStorage.setItem(CLAVE, JSON.stringify(sesion(rol)));
}

export function montar(ui: ReactElement, rol: string | null = "ADMIN", ruta = "/"): RenderResult {
  guardarSesion(rol);
  return render(
    <MemoryRouter initialEntries={[ruta]}>
      <AuthProvider>{ui}</AuthProvider>
    </MemoryRouter>,
  );
}

export function instalarFetch(
  resolver: (path: string, init?: RequestInit) => Respuesta | Promise<Respuesta>,
) {
  const llamadas: { path: string; init?: RequestInit }[] = [];
  const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const path = String(input);
    llamadas.push({ path, init });
    const resultado = await resolver(path, init);
    const status = resultado.status ?? 200;
    return {
      ok: status >= 200 && status < 300,
      status,
      json: async () => resultado.body ?? {},
    };
  });
  vi.stubGlobal("fetch", fetchMock);
  return { fetchMock, llamadas };
}

export function cuerpoDe(init?: RequestInit): unknown {
  return JSON.parse(String(init?.body ?? "{}"));
}
