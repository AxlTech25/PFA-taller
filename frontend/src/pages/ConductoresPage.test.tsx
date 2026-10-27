import { cleanup, fireEvent, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { cuerpoDe, instalarFetch, montar } from "../test/pagina";
import type { Conductor } from "../types";
import { ConductoresPage } from "./ConductoresPage";

function conductor(parcial: Partial<Conductor> = {}): Conductor {
  return {
    id_conductor: "c1",
    nombre: "Zoe Quispe",
    dni: null,
    licencia_categoria: "A-IIIb",
    anios_experiencia: 4,
    disponibilidad_inicio: "06:00:00",
    disponibilidad_fin: "14:00:00",
    lat_punto_partida: null,
    lon_punto_partida: null,
    estado: "ACTIVO",
    ...parcial,
  };
}

function llenar() {
  fireEvent.change(screen.getByLabelText("Nombre"), { target: { value: "Ana Ramos" } });
  fireEvent.change(screen.getByLabelText("DNI"), { target: { value: "12345678" } });
  fireEvent.change(screen.getByLabelText("Licencia"), { target: { value: "A-I" } });
  fireEvent.change(screen.getByLabelText("Años de experiencia"), { target: { value: "3" } });
  fireEvent.submit(
    screen.getByRole("button", { name: "Registrar conductor" }).closest("form") as HTMLFormElement,
  );
}

describe("ConductoresPage", () => {
  it("lista huecos con raya y registra ordenando por nombre", async () => {
    const { llamadas } = instalarFetch((_path, init) => {
      if (init?.method === "POST") {
        return {
          body: conductor({
            id_conductor: "c2",
            nombre: "Ana Ramos",
            dni: "12345678",
            lat_punto_partida: -12.01,
            lon_punto_partida: -76.98,
            mensaje: "Conductor registrado correctamente",
          }),
        };
      }
      return { body: [conductor()] };
    });
    montar(<ConductoresPage />);
    expect(await screen.findByText("Zoe Quispe")).toBeInTheDocument();
    expect(document.title).toBe("Conductores · EcoLogística Lima");
    expect(screen.getAllByText("—").length).toBeGreaterThan(0);
    expect(screen.getByText("06:00 – 14:00")).toBeInTheDocument();
    llenar();
    expect(await screen.findByText("Conductor registrado correctamente")).toBeInTheDocument();
    const filas = screen.getAllByRole("row");
    expect(filas[1]).toHaveTextContent("Ana Ramos");
    expect(filas[1]).toHaveTextContent("-12.01, -76.98");
    const alta = llamadas.find((llamada) => llamada.init?.method === "POST");
    expect(cuerpoDe(alta?.init)).toMatchObject({ nombre: "Ana Ramos", dni: "12345678" });
  });

  it("el gerente consulta y no registra", async () => {
    instalarFetch(() => ({ body: [] }));
    montar(<ConductoresPage />, "GERENTE");
    expect(await screen.findByText("No hay conductores registrados.")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Registrar conductor" })).not.toBeInTheDocument();
  });

  it("muestra errores de carga y de registro", async () => {
    instalarFetch(() => ({ status: 500, body: { detail: "Nómina caída" } }));
    montar(<ConductoresPage />);
    expect(await screen.findByRole("alert")).toHaveTextContent("Nómina caída");

    cleanup();
    instalarFetch(() => {
      throw new Error("red");
    });
    montar(<ConductoresPage />);
    expect(await screen.findByRole("alert")).toHaveTextContent("No se pudo cargar los conductores.");

    cleanup();
    instalarFetch((_path, init) => {
      if (init?.method === "POST") return { status: 409, body: { detail: "DNI duplicado" } };
      return { body: [] };
    });
    montar(<ConductoresPage />);
    await screen.findByRole("button", { name: "Registrar conductor" });
    llenar();
    expect(await screen.findByRole("alert")).toHaveTextContent("DNI duplicado");

    cleanup();
    instalarFetch((_path, init) => {
      if (init?.method === "POST") throw new Error("red");
      return { body: [] };
    });
    montar(<ConductoresPage />);
    await screen.findByRole("button", { name: "Registrar conductor" });
    llenar();
    expect(await screen.findByRole("alert")).toHaveTextContent("No se pudo registrar el conductor.");
  });
});
