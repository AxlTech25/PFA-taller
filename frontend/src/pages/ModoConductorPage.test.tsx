import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import type { JornadaModo } from "../types";
import { instalarFetch, montar } from "../test/pagina";
import { ModoConductorPage } from "./ModoConductorPage";

const jornada: JornadaModo = {
  hay_ruta: true,
  fecha: "2026-11-21",
  mensaje: null,
  id_ruta: "ruta-1",
  placa: "DMO-101",
  paradas: [
    {
      secuencia: 1,
      id_detalle: "detalle-1",
      cliente: "Bodega El Ahorro",
      direccion: "Av. Próceres de la Independencia 2450",
      punto_referencia: "frente a la bodega El Ahorro",
      eta: "2026-11-21T08:15:00+00:00",
      estado_entrega: "PENDIENTE",
      nivel_congestion: "AMARILLO",
    },
    {
      secuencia: 2,
      id_detalle: "detalle-2",
      cliente: "Bodega El Ahorro",
      direccion: "Jr. Los Jardines 180",
      punto_referencia: "paradero del mercado",
      eta: "2026-11-21T10:40:00+00:00",
      estado_entrega: "PENDIENTE",
      nivel_congestion: "VERDE",
    },
  ],
  alertas: [
    {
      codigo: "CONGESTION",
      secuencia: 1,
      texto: "Parada 1: semáforo amarillo en la llegada estimada.",
    },
    {
      codigo: "VENTANA",
      secuencia: 2,
      texto: "Parada 2: la llegada estimada queda fuera de la ventana del cliente.",
    },
  ],
};

describe("modo conductor", () => {
  it("muestra la secuencia, la hora, las alertas y la acción de confirmar", async () => {
    const usuario = userEvent.setup();
    const { llamadas } = instalarFetch((path) => {
      if (path.includes("/modo/jornada")) return { body: jornada };
      return { body: {} };
    });
    montar(<ModoConductorPage />, "CONDUCTOR", "/modo");

    expect(await screen.findByRole("heading", { name: /Parada 1/ })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Ruta del 21/11/2026" })).toBeInTheDocument();
    expect(screen.getByText("Unidad DMO-101")).toBeInTheDocument();
    expect(screen.getByText("08:15")).toBeInTheDocument();
    expect(screen.getByText("10:40")).toBeInTheDocument();
    expect(screen.getByText("Parada 1: semáforo amarillo en la llegada estimada.")).toBeInTheDocument();
    expect(screen.getByText(/fuera de la ventana/)).toBeInTheDocument();
    expect(screen.getByText("Siguiente entrega")).toBeInTheDocument();
    expect(screen.getByText("Av. Próceres de la Independencia 2450")).toBeInTheDocument();
    expect(screen.queryByText(/CO₂|S\/|árbol/)).not.toBeInTheDocument();

    const primero = screen.getByRole("button", {
      name: "Confirmar entrega de la parada 1, Bodega El Ahorro",
    });
    const segundo = screen.getByRole("button", {
      name: "Confirmar entrega de la parada 2, Bodega El Ahorro",
    });
    expect(primero).toHaveAttribute("aria-describedby", "nota-confirmacion");
    expect(primero).toHaveAttribute("aria-pressed", "false");
    primero.focus();
    await usuario.keyboard("{Enter}");
    expect(
      await screen.findByText(
        "Parada 1, Bodega El Ahorro: la confirmación quedó en esta pantalla y todavía no se guarda.",
      ),
    ).toBeInTheDocument();
    expect(primero).toHaveAttribute("aria-pressed", "true");
    expect(screen.getAllByText("Pendiente").length).toBeGreaterThan(0);

    await usuario.tab();
    expect(segundo).toHaveFocus();
    await usuario.keyboard("{Enter}");
    expect(
      screen.getByText(
        "Parada 2, Bodega El Ahorro: la confirmación quedó en esta pantalla y todavía no se guarda.",
      ),
    ).toBeInTheDocument();
    expect(llamadas.every((llamada) => (llamada.init?.method ?? "GET").toUpperCase() === "GET")).toBe(true);
  });

  it("avisa cuando no hay ruta confirmada para hoy", async () => {
    instalarFetch(() => ({
      body: {
        hay_ruta: false,
        fecha: "2026-11-21",
        mensaje: "No tiene una ruta confirmada para hoy.",
        paradas: [],
        alertas: [],
      },
    }));
    montar(<ModoConductorPage />, "CONDUCTOR", "/modo");
    expect(await screen.findByText("No tiene una ruta confirmada para hoy.")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Confirmar entrega/ })).not.toBeInTheDocument();
    expect(screen.queryByText(/CO₂/)).not.toBeInTheDocument();
  });

  it("muestra el error de la API sin inventar una ruta", async () => {
    instalarFetch(() => ({ status: 500, body: { detail: "Fallo de jornada" } }));
    montar(<ModoConductorPage />, "CONDUCTOR", "/modo");
    expect(await screen.findByRole("alert")).toHaveTextContent("Fallo de jornada");
    expect(screen.queryByText("No tiene una ruta confirmada para hoy.")).not.toBeInTheDocument();
  });

  it("avisa si la red no responde", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => {
        throw new Error("red");
      }),
    );
    montar(<ModoConductorPage />, "CONDUCTOR", "/modo");
    expect(await screen.findByRole("alert")).toHaveTextContent("No se pudo cargar su ruta.");
  });
});
