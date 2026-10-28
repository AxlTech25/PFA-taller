import { cleanup, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import { App } from "./App";
import { instalarFetch, montar } from "./test/pagina";

describe("App y la sesión", () => {
  it("manda al login cuando no hay sesión", async () => {
    montar(<App />, null, "/flota");
    expect(await screen.findByRole("button", { name: "Entrar" })).toBeInTheDocument();
  });

  it("abre la flota del administrador y permite cerrar la sesión", async () => {
    const usuario = userEvent.setup();
    instalarFetch(() => ({ body: [] }));
    montar(<App />, "ADMIN", "/");
    expect(await screen.findByRole("heading", { name: "Flota" })).toBeInTheDocument();
    expect(screen.getAllByRole("link", { name: "Usuarios" })).toHaveLength(2);
    await usuario.click(screen.getByRole("button", { name: "Cerrar sesión" }));
    expect(await screen.findByRole("button", { name: "Entrar" })).toBeInTheDocument();
  });

  it("lleva al conductor a su modo y le niega usuarios", async () => {
    montar(<App />, "CONDUCTOR", "/");
    expect(await screen.findByRole("heading", { name: "Modo conductor" })).toBeInTheDocument();
    expect(screen.getByText("No tiene una ruta confirmada para hoy.")).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Usuarios" })).not.toBeInTheDocument();

    cleanup();
    montar(<App />, "CONDUCTOR", "/usuarios");
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "No tiene permiso para acceder a este módulo.",
    );
  });

  it("una ruta desconocida vuelve al inicio de quien tiene sesión", async () => {
    instalarFetch(() => ({ body: [] }));
    montar(<App />, "GERENTE", "/no-existe");
    expect(await screen.findByRole("heading", { name: "Flota" })).toBeInTheDocument();
  });
});
