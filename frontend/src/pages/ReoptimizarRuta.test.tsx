import { cleanup, fireEvent, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { violacionesDe } from "../test/axe";
import { cuerpoDe, instalarFetch, montar } from "../test/pagina";
import type { Reoptimizacion, Ruta } from "../types";
import { RutasPage } from "./RutasPage";
import { paradasPendientes } from "./ReoptimizarRuta";

vi.mock("./MapaRutas", () => ({
  MapaRutas: () => <div>mapa</div>,
}));

const activa: Ruta = {
  id_ruta: "r1",
  fecha: "2026-11-02",
  estado: "EN_EJECUCION",
  distancia_total_km: 10,
  tiempo_total_min: 40,
  minutos_conduccion: 30,
  combustible_estimado_l: 2,
  co2_estimado_kg: 1.2,
  placa: "ABC123",
  conductor: "Ana Ramos",
  descansos: [],
  paradas: [
    { secuencia: 1, id_pedido: "p1", nombre_cliente: "Bodega Uno", estado_entrega: "ENTREGADO" },
    { secuencia: 2, id_pedido: "p2", nombre_cliente: "Bodega Dos", estado_entrega: "PENDIENTE" },
    { secuencia: 3, id_pedido: "p3", nombre_cliente: null, estado_entrega: null },
  ],
};

const reordenada: Ruta = {
  ...activa,
  paradas: [
    activa.paradas[0],
    { secuencia: 2, id_pedido: "p9", nombre_cliente: "Cliente Nuevo", estado_entrega: "PENDIENTE" },
    { ...activa.paradas[1], secuencia: 3 },
  ],
};

const respuesta: Reoptimizacion = {
  mensaje: "Ruta re-optimizada en 0.04 s (tope 30 s).",
  segundos: 0.0412,
  presupuesto_s: 30,
  cortado: false,
  estrategia: "insercion_mas_barata",
  paradas_fijas: 1,
  paradas_reordenadas: 2,
  agregadas: 1,
  canceladas: 1,
  ruta: reordenada,
};

const NOMBRE = "Re-optimizar paradas pendientes de ABC123 · Ana Ramos";

function datos(post: (init?: RequestInit) => { status?: number; body?: unknown }) {
  let reoptimizada = false;
  return instalarFetch((path, init) => {
    if (path === "/rutas/r1/pedidos-disponibles") {
      return {
        body: [
          { id_pedido: "p9", nombre_cliente: "Cliente Nuevo", punto_referencia: "Mercado", peso_kg: 4, prioridad: "ESTANDAR" },
          { id_pedido: "p8", nombre_cliente: null, punto_referencia: null, peso_kg: 2, prioridad: "EXPRESS" },
        ],
      };
    }
    if (path === "/rutas/r1/reoptimizar") {
      const salida = post(init);
      if ((salida.status ?? 200) < 300) reoptimizada = true;
      return salida;
    }
    return { body: [reoptimizada ? reordenada : activa] };
  });
}

async function abrir() {
  const boton = await screen.findByRole("button", { name: NOMBRE });
  expect(boton).toHaveAttribute("aria-expanded", "false");
  fireEvent.click(boton);
  expect(boton).toHaveAttribute("aria-expanded", "true");
  await screen.findByRole("checkbox", { name: /Cliente Nuevo · 4 kg · Mercado/ });
}

describe("Re-optimización de ruta (US-011)", () => {
  it("solo deja pendientes las paradas no resueltas", () => {
    expect(paradasPendientes(activa).map((parada) => parada.id_pedido)).toEqual(["p2", "p3"]);
  });

  it("agrega y cancela pedidos, muestra el tiempo medido y la ruta nueva", async () => {
    const { llamadas } = datos(() => ({ body: respuesta }));
    montar(<RutasPage />, "OPERADOR");
    await abrir();
    expect(screen.getByRole("combobox", { name: "Motivo del cambio" })).toHaveFocus();
    expect(screen.queryByRole("checkbox", { name: /Bodega Uno/ })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("checkbox", { name: /Cliente Nuevo/ }));
    fireEvent.click(screen.getByRole("checkbox", { name: /Cliente · 2 kg/ }));
    fireEvent.click(screen.getByRole("checkbox", { name: /Cliente · 2 kg/ }));
    fireEvent.click(screen.getByRole("checkbox", { name: "Parada 3 · Cliente" }));
    fireEvent.change(screen.getByLabelText("Detalle (opcional)"), { target: { value: "  Llamó el cliente " } });
    fireEvent.click(screen.getByRole("button", { name: "Re-optimizar ahora" }));

    expect(await screen.findByText(/Tiempo medido: 0.04 s \(tope 30 s\)/)).toBeInTheDocument();
    const post = llamadas.find((llamada) => llamada.path === "/rutas/r1/reoptimizar");
    expect(cuerpoDe(post?.init)).toEqual({
      motivo: "NUEVO_PEDIDO",
      descripcion: "Llamó el cliente",
      agregar: ["p9"],
      cancelar: ["p3"],
    });
    expect(await screen.findByRole("cell", { name: "Cliente Nuevo" })).toBeInTheDocument();
    expect(screen.getAllByRole("cell", { name: "Entregado" })).toHaveLength(1);
    expect(screen.queryByRole("form", { name: /Re-optimizar ABC123/ })).not.toBeInTheDocument();
    await waitFor(() => expect(screen.getByRole("button", { name: NOMBRE })).toHaveFocus());
  });

  it("valida el motivo antes de enviar y muestra los errores de la API", async () => {
    const { llamadas } = datos(() => ({ status: 422, body: { detail: "No hay solución factible" } }));
    montar(<RutasPage />);
    await abrir();
    fireEvent.click(screen.getByRole("button", { name: "Re-optimizar ahora" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Marque al menos un pedido nuevo");

    fireEvent.change(screen.getByRole("combobox", { name: "Motivo del cambio" }), {
      target: { value: "CANCELACION" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Re-optimizar ahora" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Marque al menos una parada pendiente");
    expect(llamadas.some((llamada) => llamada.path === "/rutas/r1/reoptimizar")).toBe(false);

    fireEvent.change(screen.getByRole("combobox", { name: "Motivo del cambio" }), {
      target: { value: "ACCIDENTE_TRANSITO" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Re-optimizar ahora" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("No hay solución factible");

    cleanup();
    datos(() => {
      throw new Error("red");
    });
    montar(<RutasPage />);
    await abrir();
    fireEvent.change(screen.getByRole("combobox", { name: "Motivo del cambio" }), {
      target: { value: "CONGESTION" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Re-optimizar ahora" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("No se pudo re-optimizar la ruta.");
  });

  it("Escape y Cerrar cierran el formulario y devuelven el foco", async () => {
    datos(() => ({ body: respuesta }));
    montar(<RutasPage />);
    await abrir();
    fireEvent.keyDown(screen.getByRole("combobox", { name: "Motivo del cambio" }), { key: "Escape" });
    const boton = screen.getByRole("button", { name: NOMBRE });
    expect(boton).toHaveAttribute("aria-expanded", "false");
    expect(boton).toHaveFocus();
    await abrir();
    fireEvent.keyDown(screen.getByRole("combobox", { name: "Motivo del cambio" }), { key: "Enter" });
    expect(boton).toHaveAttribute("aria-expanded", "true");
    fireEvent.click(screen.getByRole("button", { name: "Cerrar" }));
    expect(boton).toHaveAttribute("aria-expanded", "false");
    fireEvent.click(boton);
    fireEvent.click(boton);
    expect(boton).toHaveAttribute("aria-expanded", "false");
  });

  it("muestra los avisos cuando no hay pedidos ni paradas pendientes", async () => {
    const terminada: Ruta = { ...activa, estado: "CONFIRMADA", paradas: [activa.paradas[0]] };
    instalarFetch((path) => {
      if (path.endsWith("/pedidos-disponibles")) return { status: 500, body: { detail: "caído" } };
      return { body: [terminada] };
    });
    montar(<RutasPage />);
    fireEvent.click(await screen.findByRole("button", { name: NOMBRE }));
    expect(await screen.findByText("No hay pedidos pendientes para la fecha de esta ruta.")).toBeInTheDocument();
    expect(screen.getByText("No quedan paradas pendientes.")).toBeInTheDocument();

    cleanup();
    instalarFetch((path) => {
      if (path.endsWith("/pedidos-disponibles")) return { body: {} };
      return { body: [terminada] };
    });
    montar(<RutasPage />);
    fireEvent.click(await screen.findByRole("button", { name: NOMBRE }));
    expect(await screen.findByText("No hay pedidos pendientes para la fecha de esta ruta.")).toBeInTheDocument();
  });

  it("no ofrece la acción a gerencia ni a rutas en borrador", async () => {
    datos(() => ({ body: respuesta }));
    montar(<RutasPage />, "GERENTE");
    expect(await screen.findByRole("cell", { name: "Bodega Dos" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: NOMBRE })).not.toBeInTheDocument();

    cleanup();
    instalarFetch(() => ({ body: [{ ...activa, estado: "BORRADOR" }] }));
    montar(<RutasPage />);
    expect(await screen.findByRole("button", { name: "Confirmar ruta ABC123 · Ana Ramos" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: NOMBRE })).not.toBeInTheDocument();
  });

  it("el formulario abierto y el resultado no tienen violaciones de axe", async () => {
    datos(() => ({ body: respuesta }));
    const { container } = montar(<RutasPage />);
    await abrir();
    fireEvent.click(screen.getByRole("button", { name: "Re-optimizar ahora" }));
    expect(await screen.findByRole("alert")).toBeInTheDocument();
    expect(await violacionesDe(container)).toBe("");
    fireEvent.click(screen.getByRole("checkbox", { name: /Cliente Nuevo/ }));
    fireEvent.click(screen.getByRole("button", { name: "Re-optimizar ahora" }));
    expect(await screen.findByText(/Tiempo medido/)).toBeInTheDocument();
    expect(await violacionesDe(container)).toBe("");
  });
});
