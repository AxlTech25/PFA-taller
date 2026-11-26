import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

vi.mock("./ModoMapa", () => ({
  ModoMapa: () => <p role="region" aria-label="Mapa diferido">Mapa diferido</p>,
}));

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
    expect(primero).toHaveAttribute("aria-expanded", "false");
    const consulta = llamadas.find((llamada) => llamada.path.includes("/modo/jornada"));
    expect(consulta?.init?.cache).toBe("no-cache");
    expect(segundo).toHaveAttribute("aria-expanded", "false");
    expect(llamadas.every((llamada) => (llamada.init?.method ?? "GET").toUpperCase() === "GET")).toBe(true);
    expect(llamadas.some((llamada) => llamada.path.includes("/modo/mapa"))).toBe(false);

    segundo.focus();
    await usuario.tab();
    const mapa = screen.getByRole("button", { name: "Ver mapa" });
    expect(mapa).toHaveFocus();
    await usuario.click(mapa);
    expect(await screen.findByRole("region", { name: "Mapa diferido" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /Parada 1/ })).toBeInTheDocument();
    expect(llamadas.some((llamada) => llamada.path.includes("/modo/mapa"))).toBe(false);
  });

  it("registra ENTREGADO con el teclado y actualiza la lista", async () => {
    const usuario = userEvent.setup();
    const { llamadas } = instalarFetch((path, init) => {
      if (path.includes("/modo/jornada")) return { body: jornada };
      if (path.includes("/modo/paradas/detalle-1/confirmacion") && init?.method === "POST") {
        return {
          body: {
            id_detalle: "detalle-1",
            secuencia: 1,
            estado_entrega: "ENTREGADO",
            motivo_fallo: null,
            confirmada_en: "2026-11-21T13:20:00+00:00",
            mensaje: "Parada 1 registrada como entregada.",
          },
        };
      }
      return { status: 500, body: {} };
    });
    montar(<ModoConductorPage />, "CONDUCTOR", "/modo");
    const boton = await screen.findByRole("button", {
      name: "Confirmar entrega de la parada 1, Bodega El Ahorro",
    });
    boton.focus();
    await usuario.keyboard("{Enter}");
    expect(boton).toHaveAttribute("aria-expanded", "true");
    const formulario = screen.getByRole("form", { name: "Resultado de la parada 1" });
    expect(boton).toHaveAttribute("aria-controls", formulario.id);
    const entregado = screen.getByRole("radio", { name: "Entregado" });
    expect(entregado).toBeChecked();
    expect(screen.queryByRole("textbox", { name: /Motivo/ })).not.toBeInTheDocument();
    await usuario.tab();
    expect(entregado).toHaveFocus();
    await usuario.tab();
    expect(screen.getByRole("button", { name: "Guardar resultado" })).toHaveFocus();
    await usuario.keyboard("{Enter}");

    const aviso = await screen.findByText("Parada 1, Bodega El Ahorro: registrada como entregada.");
    expect(aviso).toHaveFocus();
    expect(screen.queryByRole("form")).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Confirmar entrega de la parada 1, Bodega El Ahorro" }),
    ).not.toBeInTheDocument();
    expect(screen.getByText("Entregado")).toBeInTheDocument();
    const post = llamadas.find((llamada) => llamada.init?.method === "POST");
    expect(post?.path).toContain("/modo/paradas/detalle-1/confirmacion");
    expect(JSON.parse(String(post?.init?.body))).toEqual({ resultado: "ENTREGADO", motivo: null });
    const siguiente = screen.getByRole("heading", { name: /Parada 2/ });
    expect(siguiente).toHaveTextContent("Siguiente entrega");
  });

  it("FALLIDO exige motivo y lo envía", async () => {
    const usuario = userEvent.setup();
    const { llamadas } = instalarFetch((path, init) => {
      if (path.includes("/modo/jornada")) return { body: jornada };
      if (init?.method === "POST") {
        return {
          body: {
            id_detalle: "detalle-2",
            secuencia: 2,
            estado_entrega: "FALLIDO",
            motivo_fallo: "Cliente ausente",
            confirmada_en: "2026-11-21T13:20:00+00:00",
            mensaje: "Parada 2 registrada como fallida.",
          },
        };
      }
      return { status: 500, body: {} };
    });
    montar(<ModoConductorPage />, "CONDUCTOR", "/modo");
    await usuario.click(
      await screen.findByRole("button", { name: "Confirmar entrega de la parada 2, Bodega El Ahorro" }),
    );
    await usuario.click(screen.getByRole("radio", { name: "Fallido" }));
    const motivo = screen.getByRole("textbox", { name: "Motivo del fallo (obligatorio)" });
    expect(motivo).toBeRequired();
    await usuario.click(screen.getByRole("button", { name: "Guardar resultado" }));
    expect(screen.getByText("Indique el motivo cuando la entrega es fallida.")).toBeInTheDocument();
    expect(motivo).toHaveAttribute("aria-invalid", "true");
    expect(motivo).toHaveFocus();
    expect(llamadas.some((llamada) => llamada.init?.method === "POST")).toBe(false);

    await usuario.type(motivo, "  Cliente   ausente ");
    await usuario.click(screen.getByRole("button", { name: "Guardar resultado" }));
    expect(await screen.findByText("Parada 2, Bodega El Ahorro: registrada como fallida.")).toBeInTheDocument();
    expect(screen.getByText("Motivo: Cliente ausente")).toBeInTheDocument();
    expect(screen.getByText("Fallido")).toBeInTheDocument();
    const post = llamadas.find((llamada) => llamada.init?.method === "POST");
    expect(JSON.parse(String(post?.init?.body))).toEqual({ resultado: "FALLIDO", motivo: "Cliente ausente" });
  });

  it("Escape cancela y devuelve el foco al botón", async () => {
    const usuario = userEvent.setup();
    instalarFetch(() => ({ body: jornada }));
    montar(<ModoConductorPage />, "CONDUCTOR", "/modo");
    const boton = await screen.findByRole("button", {
      name: "Confirmar entrega de la parada 1, Bodega El Ahorro",
    });
    await usuario.click(boton);
    await usuario.click(screen.getByRole("radio", { name: "Fallido" }));
    await usuario.keyboard("{Escape}");
    expect(screen.queryByRole("form")).not.toBeInTheDocument();
    expect(boton).toHaveFocus();
    await usuario.click(boton);
    expect(boton).toHaveFocus();
    await usuario.keyboard("{Escape}");
    expect(screen.queryByRole("form")).not.toBeInTheDocument();
    await usuario.click(boton);
    await usuario.click(screen.getByRole("button", { name: "Cancelar" }));
    expect(screen.queryByRole("form")).not.toBeInTheDocument();
    expect(boton).toHaveFocus();
  });

  it("muestra el error de la API y recarga la lista si la parada ya tenía resultado", async () => {
    const usuario = userEvent.setup();
    let consultas = 0;
    instalarFetch((path, init) => {
      if (path.includes("/modo/jornada")) {
        consultas += 1;
        if (consultas === 1) return { body: jornada };
        return {
          body: {
            ...jornada,
            paradas: jornada.paradas.map((parada, indice) =>
              indice === 0 ? { ...parada, estado_entrega: "ENTREGADO" } : parada,
            ),
          },
        };
      }
      if (init?.method === "POST") {
        return { status: 409, body: { detail: "La parada ya fue registrada como ENTREGADO" } };
      }
      return { body: {} };
    });
    montar(<ModoConductorPage />, "CONDUCTOR", "/modo");
    await usuario.click(
      await screen.findByRole("button", { name: "Confirmar entrega de la parada 1, Bodega El Ahorro" }),
    );
    await usuario.click(screen.getByRole("button", { name: "Guardar resultado" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("La parada ya fue registrada como ENTREGADO");
    expect(await screen.findByText("Entregado")).toBeInTheDocument();
    expect(screen.queryByRole("form")).not.toBeInTheDocument();
    expect(consultas).toBe(2);
  });

  it("avisa si no se pudo guardar por la red", async () => {
    const usuario = userEvent.setup();
    instalarFetch((_path, init) => {
      if (init?.method === "POST") throw new Error("red");
      return { body: jornada };
    });
    montar(<ModoConductorPage />, "CONDUCTOR", "/modo");
    await usuario.click(
      await screen.findByRole("button", { name: "Confirmar entrega de la parada 1, Bodega El Ahorro" }),
    );
    await usuario.click(screen.getByRole("button", { name: "Guardar resultado" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("No se pudo guardar el resultado.");
    expect(screen.getByRole("button", { name: "Guardar resultado" })).toBeEnabled();
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
