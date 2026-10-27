import { cleanup, fireEvent, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { instalarFetch, montar, cuerpoDe } from "../test/pagina";
import type { Vehiculo } from "../types";
import { FlotaPage } from "./FlotaPage";

function vehiculo(parcial: Partial<Vehiculo> = {}): Vehiculo {
  return {
    id_vehiculo: "v1",
    placa: "XYZ789",
    tipo: "FURGON",
    capacidad_kg: 800,
    capacidad_m3: 6,
    consumo_km_l: 10,
    factor_emision_co2: 0.2,
    anio_fabricacion: 2020,
    estado: "ACTIVO",
    ...parcial,
  };
}

function llenarRegistro() {
  fireEvent.change(screen.getByLabelText("Placa"), { target: { value: "AAA111" } });
  fireEvent.change(screen.getByLabelText("Tipo"), { target: { value: "MOTO" } });
  fireEvent.change(screen.getByLabelText("Capacidad (kg)"), { target: { value: "120" } });
  fireEvent.change(screen.getByLabelText("Capacidad (m³)"), { target: { value: "1.5" } });
  fireEvent.change(screen.getByLabelText("Consumo (km/L)"), { target: { value: "30" } });
  fireEvent.change(screen.getByLabelText("Factor de emisión (kg CO₂/km)"), { target: { value: "0.11" } });
  fireEvent.submit(screen.getByRole("button", { name: "Registrar vehículo" }).closest("form") as HTMLFormElement);
}

describe("FlotaPage", () => {
  it("lista la flota y registra una unidad", async () => {
    const { llamadas } = instalarFetch((_path, init) => {
      if ((init?.method ?? "GET") === "POST") {
        return {
          body: vehiculo({
            id_vehiculo: "v2",
            placa: "AAA111",
            tipo: "MOTO",
            mensaje: "Vehículo registrado correctamente",
          }),
        };
      }
      return { body: [vehiculo()] };
    });
    montar(<FlotaPage />);
    expect(await screen.findByText("XYZ789")).toBeInTheDocument();
    expect(document.title).toBe("Flota · EcoLogística Lima");
    llenarRegistro();
    expect(await screen.findByText("Vehículo registrado correctamente")).toBeInTheDocument();
    const filas = screen.getAllByRole("row");
    expect(filas[1]).toHaveTextContent("AAA111");
    expect(filas[2]).toHaveTextContent("XYZ789");
    const alta = llamadas.find((llamada) => llamada.init?.method === "POST");
    expect(cuerpoDe(alta?.init)).toMatchObject({ placa: "AAA111", tipo: "MOTO", capacidad_kg: 120 });
  });

  it("actualiza estado y factor, y muestra el error del API", async () => {
    let guardar = false;
    instalarFetch((_path, init) => {
      if (init?.method === "PUT") {
        guardar = true;
        return { status: 422, body: { detail: "Factor fuera de rango" } };
      }
      return { body: [vehiculo()] };
    });
    montar(<FlotaPage />);
    const estado = await screen.findByLabelText("Estado de XYZ789");
    fireEvent.change(estado, { target: { value: "MANTENIMIENTO" } });
    fireEvent.change(screen.getByLabelText("Factor de emisión de XYZ789"), {
      target: { value: "0.4" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Guardar" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Factor fuera de rango");
    expect(guardar).toBe(true);
  });

  it("confirma la actualización y el fallo genérico", async () => {
    let veces = 0;
    instalarFetch((_ruta, init) => {
      if (init?.method === "PUT") {
        veces += 1;
        if (veces === 1) {
          return {
            body: vehiculo({ estado: "MANTENIMIENTO", factor_emision_co2: 0.4 }),
          };
        }
        throw new Error("red");
      }
      return { body: [vehiculo()] };
    });
    montar(<FlotaPage />);
    await screen.findByLabelText("Estado de XYZ789");
    fireEvent.click(screen.getByRole("button", { name: "Guardar" }));
    expect(await screen.findByText("Vehículo actualizado correctamente")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Guardar" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("No se pudo actualizar el vehículo.");
  });

  it("muestra la flota vacía y el error de carga", async () => {
    instalarFetch(() => ({ body: [] }));
    montar(<FlotaPage />, "AUDITOR");
    expect(await screen.findByText("No hay vehículos registrados.")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Registrar vehículo" })).not.toBeInTheDocument();

    cleanup();
    instalarFetch(() => ({ status: 503, body: { detail: "Flota no disponible" } }));
    montar(<FlotaPage />);
    expect(await screen.findByRole("alert")).toHaveTextContent("Flota no disponible");

    cleanup();
    instalarFetch(() => {
      throw new Error("red");
    });
    montar(<FlotaPage />);
    expect(await screen.findByRole("alert")).toHaveTextContent("No se pudo cargar la flota.");
  });

  it("informa si el registro falla", async () => {
    instalarFetch((_path, init) => {
      if (init?.method === "POST") return { status: 409, body: { detail: "La placa ya existe" } };
      return { body: [] };
    });
    montar(<FlotaPage />, "OPERADOR");
    await screen.findByRole("button", { name: "Registrar vehículo" });
    llenarRegistro();
    expect(await screen.findByRole("alert")).toHaveTextContent("La placa ya existe");

    cleanup();
    instalarFetch((_path, init) => {
      if (init?.method === "POST") throw new Error("red");
      return { body: [] };
    });
    montar(<FlotaPage />, "OPERADOR");
    await screen.findByRole("button", { name: "Registrar vehículo" });
    llenarRegistro();
    expect(await screen.findByRole("alert")).toHaveTextContent("No se pudo registrar el vehículo.");
  });
});
