import { cleanup, fireEvent, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { instalarFetch, montar } from "../test/pagina";
import type { Indicadores } from "../types";
import { DashboardPage } from "./DashboardPage";

function indicadores(parcial: Partial<Indicadores> = {}): Indicadores {
  return {
    fecha: "2026-11-02",
    hay_datos: true,
    mensaje: null,
    rutas: 2,
    km: 12.5,
    co2_kg: 3.2,
    combustible_l: 1.1,
    soles_combustible: 10,
    soles_mantenimiento: 15,
    soles_ahorrados: 4,
    co2_ahorrado_kg: 0.5,
    arboles: null,
    nota_arboles: "RN-018 pendiente",
    cumplimiento_ventanas_pct: 80,
    mejora_porcentaje: 12,
    ...parcial,
  };
}

describe("DashboardPage", () => {
  it("muestra las métricas del día y el equivalente vacío", async () => {
    instalarFetch(() => ({ body: indicadores() }));
    montar(<DashboardPage />);
    expect(await screen.findByText("12.5")).toBeInTheDocument();
    expect(document.title).toBe("Tablero · EcoLogística Lima");
    expect(screen.getByText("80 %")).toBeInTheDocument();
    expect(screen.getByText("Árboles equivalentes").closest("article")).toHaveTextContent("—");
    expect(screen.getByText("RN-018 pendiente")).toBeInTheDocument();
    expect(screen.getByLabelText("Indicadores del día").textContent).toMatch(/10/);
  });

  it("avisa cuando el período no tiene operación", async () => {
    instalarFetch(() => ({
      body: indicadores({
        hay_datos: false,
        mensaje: "Sin datos de operación para el período seleccionado.",
        nota_arboles: null,
        arboles: 3,
      }),
    }));
    montar(<DashboardPage />);
    expect(
      await screen.findByText("Sin datos de operación para el período seleccionado."),
    ).toBeInTheDocument();
    expect(screen.queryByLabelText("Indicadores del día")).not.toBeInTheDocument();
  });

  it("vuelve a consultar y muestra el error", async () => {
    let fallo = false;
    instalarFetch(() => {
      if (fallo) return { status: 500, body: { detail: "Tablero caído" } };
      return { body: indicadores({ arboles: 2, nota_arboles: null }) };
    });
    montar(<DashboardPage />);
    expect(await screen.findByText("Árboles equivalentes")).toBeInTheDocument();
    expect(screen.getByText("Árboles equivalentes").closest("article")).toHaveTextContent("2");
    fallo = true;
    fireEvent.change(screen.getByLabelText("Fecha"), { target: { value: "2026-11-03" } });
    expect(await screen.findByRole("alert")).toHaveTextContent("Tablero caído");

    cleanup();
    instalarFetch(() => {
      throw new Error("red");
    });
    montar(<DashboardPage />);
    expect(await screen.findByRole("alert")).toHaveTextContent("No se pudo cargar el tablero.");

    cleanup();
    let consultas = 0;
    instalarFetch(() => {
      consultas += 1;
      if (consultas > 1) return { status: 503, body: { detail: "Reintento fallido" } };
      return { body: indicadores() };
    });
    montar(<DashboardPage />);
    await screen.findByText("12.5");
    fireEvent.submit(screen.getByRole("button", { name: "Consultar" }).closest("form") as HTMLFormElement);
    expect(await screen.findByRole("alert")).toHaveTextContent("Reintento fallido");
  });
});
