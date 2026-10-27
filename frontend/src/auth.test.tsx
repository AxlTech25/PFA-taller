import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState } from "react";
import { describe, expect, it } from "vitest";

import { ApiError } from "./api";
import { AuthProvider, useAuth } from "./auth";
import { CLAVE, instalarFetch, sesion } from "./test/pagina";

function Panel() {
  const auth = useAuth();
  const [texto, setTexto] = useState("");
  return (
    <>
      <span>{auth.sesion?.email ?? "sin sesion"}</span>
      <span>{texto}</span>
      <button
        type="button"
        onClick={() =>
          void auth.iniciar("a@b.c", "clave-segura").catch((error: unknown) => {
            setTexto(error instanceof ApiError ? error.message : "falla");
          })
        }
      >
        entrar
      </button>
      <button
        type="button"
        onClick={() =>
          void auth.llamar<{ ok: boolean }>("/salud").then(
            (dato) => setTexto(dato.ok ? "ok" : "no"),
            (error: unknown) => setTexto(error instanceof ApiError ? `e${error.status}` : "falla"),
          )
        }
      >
        pedir
      </button>
    </>
  );
}

function montarPanel() {
  return render(
    <AuthProvider>
      <Panel />
    </AuthProvider>,
  );
}

describe("auth", () => {
  it("descarta una sesión que no es JSON", () => {
    sessionStorage.setItem(CLAVE, "{");
    montarPanel();
    expect(screen.getByText("sin sesion")).toBeInTheDocument();
    expect(sessionStorage.getItem(CLAVE)).toBeNull();
  });

  it("guarda la sesión al entrar y la suelta si el API responde 401", async () => {
    const usuario = userEvent.setup();
    const datos = sesion("OPERADOR");
    instalarFetch(() => ({ body: datos }));
    montarPanel();
    await usuario.click(screen.getByRole("button", { name: "entrar" }));
    expect(await screen.findByText(datos.email)).toBeInTheDocument();
    expect(sessionStorage.getItem(CLAVE)).toContain(datos.access_token);

    viResetFetch(() => ({ status: 401, body: { detail: "No autenticado" } }));
    await usuario.click(screen.getByRole("button", { name: "pedir" }));
    expect(await screen.findByText("sin sesion")).toBeInTheDocument();
    expect(screen.getByText("e401")).toBeInTheDocument();
  });

  it("devuelve el cuerpo y distingue un fallo que no es del API", async () => {
    const usuario = userEvent.setup();
    sessionStorage.setItem(CLAVE, JSON.stringify(sesion("ADMIN")));
    instalarFetch(() => ({ body: { ok: true } }));
    montarPanel();
    await usuario.click(screen.getByRole("button", { name: "pedir" }));
    expect(await screen.findByText("ok")).toBeInTheDocument();

    viResetFetch(() => {
      throw new Error("red");
    });
    await usuario.click(screen.getByRole("button", { name: "pedir" }));
    expect(await screen.findByText("falla")).toBeInTheDocument();
    expect(screen.getByText("admin@distrirapido.example.com")).toBeInTheDocument();
  });

  it("exige el proveedor", () => {
    function Roto() {
      useAuth();
      return null;
    }
    expect(() => render(<Roto />)).toThrow("useAuth debe usarse dentro de AuthProvider");
  });
});

function viResetFetch(
  resolver: Parameters<typeof instalarFetch>[0],
) {
  instalarFetch(resolver);
}
