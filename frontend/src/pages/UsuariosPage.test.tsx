import { cleanup, fireEvent, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { cuerpoDe, instalarFetch, montar } from "../test/pagina";
import type { Usuario } from "../types";
import { UsuariosPage } from "./UsuariosPage";

function usuario(parcial: Partial<Usuario> = {}): Usuario {
  return {
    id_usuario: "u1",
    email: "zoe@distrirapido.example.com",
    rol: "OPERADOR",
    estado: "ACTIVO",
    intentos_fallidos: 0,
    ...parcial,
  };
}

function llenar() {
  fireEvent.change(screen.getByLabelText("Correo"), { target: { value: "ana@distrirapido.example.com" } });
  fireEvent.change(screen.getByLabelText("Contraseña inicial"), { target: { value: "clave-segura" } });
  fireEvent.change(screen.getByLabelText("Rol"), { target: { value: "AUDITOR" } });
  fireEvent.change(screen.getByLabelText("Estado"), { target: { value: "INACTIVO" } });
  fireEvent.submit(
    screen.getByRole("button", { name: "Registrar usuario" }).closest("form") as HTMLFormElement,
  );
}

describe("UsuariosPage", () => {
  it("crea una cuenta, cambia el rol y activa o desactiva", async () => {
    const cuentas = [usuario(), usuario({ id_usuario: "u2", email: "bloqueado@distrirapido.example.com", estado: "BLOQUEADO" })];
    const { llamadas } = instalarFetch((_path, init) => {
      const metodo = init?.method ?? "GET";
      if (metodo === "POST") {
        return {
          body: usuario({
            id_usuario: "u3",
            email: "ana@distrirapido.example.com",
            rol: "AUDITOR",
            estado: "INACTIVO",
            mensaje: "Usuario registrado correctamente",
          }),
        };
      }
      if (metodo === "PATCH" && String(init?.body).includes("GERENTE")) {
        return { body: usuario({ rol: "GERENTE" }) };
      }
      if (metodo === "PATCH" && String(init?.body).includes("INACTIVO")) {
        return { body: usuario({ estado: "INACTIVO" }) };
      }
      if (metodo === "PATCH") return { body: usuario({ id_usuario: "u2", email: "bloqueado@distrirapido.example.com", estado: "ACTIVO" }) };
      return { body: cuentas };
    });
    montar(<UsuariosPage />);
    expect(await screen.findByText("zoe@distrirapido.example.com")).toBeInTheDocument();
    expect(document.title).toBe("Usuarios · EcoLogística Lima");
    llenar();
    expect(await screen.findByText("Usuario registrado correctamente")).toBeInTheDocument();
    const filas = screen.getAllByRole("row");
    expect(filas[1]).toHaveTextContent("ana@distrirapido.example.com");
    fireEvent.change(screen.getByLabelText("Rol de zoe@distrirapido.example.com"), {
      target: { value: "GERENTE" },
    });
    expect(await screen.findByText("Rol actualizado correctamente")).toBeInTheDocument();
    fireEvent.click(screen.getAllByRole("button", { name: /^Desactivar/ })[0]);
    expect(await screen.findByText("Usuario desactivado")).toBeInTheDocument();
    fireEvent.click(screen.getAllByRole("button", { name: /^Activar/ })[0]);
    expect(await screen.findByText("Usuario activado")).toBeInTheDocument();
    const alta = llamadas.find((llamada) => llamada.init?.method === "POST");
    expect(cuerpoDe(alta?.init)).toMatchObject({ email: "ana@distrirapido.example.com", rol: "AUDITOR" });
  });

  it("el gerente consulta y no modifica", async () => {
    instalarFetch(() => ({ body: [] }));
    montar(<UsuariosPage />, "GERENTE");
    expect(await screen.findByText("Su rol puede consultar usuarios, no modificarlos.")).toBeInTheDocument();
    expect(screen.getByText("No hay usuarios registrados.")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Registrar usuario" })).not.toBeInTheDocument();
  });

  it("muestra errores de carga, alta, rol y estado", async () => {
    instalarFetch(() => ({ status: 500, body: { detail: "Directorio caído" } }));
    montar(<UsuariosPage />);
    expect(await screen.findByRole("alert")).toHaveTextContent("Directorio caído");

    cleanup();
    instalarFetch(() => {
      throw new Error("red");
    });
    montar(<UsuariosPage />);
    expect(await screen.findByRole("alert")).toHaveTextContent("No se pudo cargar los usuarios.");

    cleanup();
    instalarFetch((_path, init) => {
      if (init?.method === "POST") return { status: 409, body: { detail: "Correo duplicado" } };
      return { body: [usuario()] };
    });
    montar(<UsuariosPage />);
    await screen.findByText("zoe@distrirapido.example.com");
    llenar();
    expect(await screen.findByRole("alert")).toHaveTextContent("Correo duplicado");

    cleanup();
    instalarFetch((_path, init) => {
      if (init?.method === "POST") throw new Error("red");
      if (init?.method === "PATCH" && String(init.body).includes("rol")) {
        return { status: 403, body: { detail: "No puede asignar ese rol" } };
      }
      if (init?.method === "PATCH") throw new Error("red");
      return { body: [usuario()] };
    });
    montar(<UsuariosPage />);
    await screen.findByLabelText("Rol de zoe@distrirapido.example.com");
    fireEvent.submit(
      screen.getByRole("button", { name: "Registrar usuario" }).closest("form") as HTMLFormElement,
    );
    expect(await screen.findByRole("alert")).toHaveTextContent("No se pudo registrar el usuario.");
    fireEvent.change(screen.getByLabelText("Rol de zoe@distrirapido.example.com"), {
      target: { value: "GERENTE" },
    });
    expect(await screen.findByRole("alert")).toHaveTextContent("No puede asignar ese rol");
    fireEvent.click(screen.getByRole("button", { name: /^Desactivar/ }));
    expect(await screen.findByRole("alert")).toHaveTextContent("No se pudo cambiar el estado.");
  });
});
