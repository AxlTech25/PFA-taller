import { cleanup, fireEvent, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { cuerpoDe, instalarFetch, montar } from "../test/pagina";
import type { Cliente, Pedido } from "../types";
import { PedidosPage } from "./PedidosPage";

const clienteOk: Cliente = {
  id_cliente: "cli-1",
  nombre: "Bodega El Ahorro",
  telefono: null,
  email: null,
  consentimiento_datos: true,
};

const clienteNo: Cliente = {
  ...clienteOk,
  id_cliente: "cli-2",
  nombre: "Puesto sin ficha",
  consentimiento_datos: false,
};

function pedido(parcial: Partial<Pedido> = {}): Pedido {
  return {
    id_pedido: "p1",
    id_cliente: "cli-1",
    nombre_cliente: "Bodega El Ahorro",
    punto_referencia: "frente a la bodega",
    latitud: -12.0,
    longitud: -76.99,
    peso_kg: 12,
    volumen_m3: 0.2,
    ventana_inicio: "2026-11-02T08:00:00",
    ventana_fin: "2026-11-02T12:30:00",
    prioridad: "ESTANDAR",
    tipo_producto: "NO_PERECEDERO",
    estado: "PENDIENTE",
    georreferencia_aproximada: true,
    distrito: "Ate",
    ...parcial,
  };
}

function responder(lista: Pedido[] = [pedido()]) {
  return (path: string, init?: RequestInit) => {
    if (init?.method === "POST") {
      return { body: pedido({ id_pedido: "p2", mensaje: "Pedido registrado correctamente" }) };
    }
    if (path.startsWith("/clientes")) return { body: [clienteOk, clienteNo] };
    return { body: lista };
  };
}

describe("PedidosPage", () => {
  it("lista la georreferencia y registra un pedido", async () => {
    const { llamadas } = instalarFetch(responder());
    montar(<PedidosPage />);
    expect(await screen.findByText("Bodega El Ahorro")).toBeInTheDocument();
    expect(document.title).toBe("Pedidos · EcoLogística Lima");
    expect(screen.getByText(/frente a la bodega/)).toHaveTextContent("(aproximada)");
    expect(screen.getByText("2026-11-02 08:00 – 12:30")).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText("Cliente"), { target: { value: "cli-2" } });
    expect(screen.getByText(/no tiene consentimiento/)).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText("Cliente"), { target: { value: "cli-1" } });
    fireEvent.change(screen.getByLabelText("Peso (kg)"), { target: { value: "8" } });
    fireEvent.change(screen.getByLabelText("Volumen (m³)"), { target: { value: "0.4" } });
    fireEvent.change(screen.getByLabelText("Prioridad"), { target: { value: "EXPRESS" } });
    fireEvent.change(screen.getByLabelText("Tipo de producto"), { target: { value: "PERECEDERO" } });
    fireEvent.change(screen.getByLabelText("Dirección"), { target: { value: "Av. Los Álamos 120" } });
    fireEvent.change(screen.getByLabelText("Punto de referencia"), {
      target: { value: "frente a la bodega El Ahorro" },
    });
    fireEvent.submit(
      screen.getByRole("button", { name: "Registrar pedido" }).closest("form") as HTMLFormElement,
    );
    expect(await screen.findByText("Pedido registrado correctamente")).toBeInTheDocument();
    const alta = llamadas.find((llamada) => llamada.init?.method === "POST");
    expect(cuerpoDe(alta?.init)).toMatchObject({
      id_cliente: "cli-1",
      prioridad: "EXPRESS",
      direccion: "Av. Los Álamos 120",
      peso_kg: 8,
    });
  });

  it("rechaza una ventana invertida sin llamar al API", async () => {
    const { llamadas } = instalarFetch(responder([]));
    montar(<PedidosPage />);
    await screen.findByRole("button", { name: "Registrar pedido" });
    expect(screen.getByText("No hay pedidos registrados.")).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText("Ventana desde"), { target: { value: "2026-11-02T18:00" } });
    fireEvent.change(screen.getByLabelText("Ventana hasta"), { target: { value: "2026-11-02T08:00" } });
    fireEvent.change(screen.getByLabelText("Peso (kg)"), { target: { value: "1" } });
    fireEvent.change(screen.getByLabelText("Volumen (m³)"), { target: { value: "0.1" } });
    fireEvent.submit(
      screen.getByRole("button", { name: "Registrar pedido" }).closest("form") as HTMLFormElement,
    );
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "La ventana de inicio debe ser anterior a la ventana de fin.",
    );
    expect(llamadas.some((llamada) => llamada.init?.method === "POST")).toBe(false);
  });

  it("el auditor solo consulta", async () => {
    instalarFetch(responder([]));
    montar(<PedidosPage />, "AUDITOR");
    expect(await screen.findByText("No hay pedidos registrados.")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Registrar pedido" })).not.toBeInTheDocument();
  });

  it("muestra errores de carga y de alta", async () => {
    instalarFetch((path) => {
      if (path.startsWith("/clientes")) return { status: 500, body: { detail: "Clientes caídos" } };
      return { body: [] };
    });
    montar(<PedidosPage />);
    expect(await screen.findByRole("alert")).toHaveTextContent("Clientes caídos");

    cleanup();
    instalarFetch(() => {
      throw new Error("red");
    });
    montar(<PedidosPage />);
    expect(await screen.findByRole("alert")).toHaveTextContent("No se pudo cargar los pedidos.");

    cleanup();
    instalarFetch((path, init) => {
      if (init?.method === "POST") return { status: 422, body: { detail: "Fuera de cobertura" } };
      return responder()(path, init);
    });
    montar(<PedidosPage />);
    await screen.findByRole("button", { name: "Registrar pedido" });
    fireEvent.change(screen.getByLabelText("Peso (kg)"), { target: { value: "1" } });
    fireEvent.change(screen.getByLabelText("Volumen (m³)"), { target: { value: "0.1" } });
    fireEvent.submit(
      screen.getByRole("button", { name: "Registrar pedido" }).closest("form") as HTMLFormElement,
    );
    expect(await screen.findByRole("alert")).toHaveTextContent("Fuera de cobertura");

    cleanup();
    instalarFetch((path, init) => {
      if (init?.method === "POST") throw new Error("red");
      return responder()(path, init);
    });
    montar(<PedidosPage />);
    await screen.findByRole("button", { name: "Registrar pedido" });
    fireEvent.change(screen.getByLabelText("Peso (kg)"), { target: { value: "1" } });
    fireEvent.change(screen.getByLabelText("Volumen (m³)"), { target: { value: "0.1" } });
    fireEvent.submit(
      screen.getByRole("button", { name: "Registrar pedido" }).closest("form") as HTMLFormElement,
    );
    expect(await screen.findByRole("alert")).toHaveTextContent("No se pudo registrar el pedido.");
  });
});
