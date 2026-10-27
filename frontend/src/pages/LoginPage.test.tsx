import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import { AuthProvider } from "../auth";
import { instalarFetch, sesion, type Respuesta } from "../test/pagina";
import { LoginPage } from "./LoginPage";

function montarLogin(rol: string | null = null) {
  sessionStorage.clear();
  if (rol) sessionStorage.setItem("ecologistica.sesion", JSON.stringify(sesion(rol)));
  return render(
    <MemoryRouter initialEntries={["/login"]}>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/flota" element={<h1>destino flota</h1>} />
          <Route path="/modo" element={<h1>destino modo</h1>} />
        </Routes>
      </AuthProvider>
    </MemoryRouter>,
  );
}

describe("LoginPage", () => {
  it("entra y lleva al administrador a la flota", async () => {
    const usuario = userEvent.setup();
    instalarFetch(() => ({ body: sesion("ADMIN") }));
    montarLogin();
    await usuario.type(screen.getByLabelText("Correo"), "admin@distrirapido.example.com");
    await usuario.type(screen.getByLabelText("Contraseña"), "clave-segura");
    await usuario.click(screen.getByRole("button", { name: "Entrar" }));
    expect(await screen.findByRole("heading", { name: "destino flota" })).toBeInTheDocument();
  });

  it("muestra el mensaje del API y un fallo genérico", async () => {
    const usuario = userEvent.setup();
    instalarFetch(() => ({ status: 401, body: { detail: "Credenciales inválidas" } }));
    montarLogin();
    await usuario.type(screen.getByLabelText("Correo"), "admin@distrirapido.example.com");
    await usuario.type(screen.getByLabelText("Contraseña"), "clave-segura");
    await usuario.click(screen.getByRole("button", { name: "Entrar" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Credenciales inválidas");

    vi.unstubAllGlobals();
    instalarFetch(() => {
      throw new Error("red");
    });
    await usuario.click(screen.getByRole("button", { name: "Entrar" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("No se pudo iniciar sesión.");
  });

  it("deshabilita el botón mientras la petición sigue abierta", async () => {
    let soltar: (valor: Respuesta) => void = () => undefined;
    instalarFetch(
      () =>
        new Promise((resolve) => {
          soltar = resolve;
        }),
    );
    montarLogin();
    fireEvent.change(screen.getByLabelText("Correo"), {
      target: { value: "admin@distrirapido.example.com" },
    });
    fireEvent.change(screen.getByLabelText("Contraseña"), { target: { value: "clave-segura" } });
    fireEvent.submit(screen.getByRole("button", { name: "Entrar" }).closest("form") as HTMLFormElement);
    expect(screen.getByRole("button", { name: "Ingresando…" })).toBeDisabled();
    soltar({ body: sesion("CONDUCTOR") });
    expect(await screen.findByRole("heading", { name: "destino modo" })).toBeInTheDocument();
  });

  it("si ya hay sesión no vuelve a pedir la clave", () => {
    montarLogin("OPERADOR");
    expect(screen.getByRole("heading", { name: "destino flota" })).toBeInTheDocument();
    cleanup();
    montarLogin("CONDUCTOR");
    expect(screen.getByRole("heading", { name: "destino modo" })).toBeInTheDocument();
  });
});
