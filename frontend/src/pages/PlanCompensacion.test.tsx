import { fireEvent, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { violacionesDe } from "../test/axe";
import { instalarFetch, montar } from "../test/pagina";
import type { PlanCompensacion as Plan } from "../types";
import { PlanCompensacion } from "./PlanCompensacion";

const PROYECTOS = [
  { nombre: "Lomas de Lima" },
  { nombre: "Parque Zonal Huáscar" },
  { nombre: "Árboles para Lima" },
];

function plan(parcial: Partial<Plan> = {}): Plan {
  return {
    desde: "2026-11-01",
    hasta: "2026-11-07",
    calculable: true,
    mensaje: null,
    dias_con_operacion: 2,
    rutas: 3,
    co2_emitido_kg: 1234.5,
    factor_captura_arbol_kg: null,
    estado_factor: "PENDIENTE",
    arboles_necesarios: null,
    costo_por_arbol_soles: null,
    estado_costo: "PENDIENTE",
    costo_estimado_soles: null,
    notas: ["Pendiente: factor RN-018", "Pendiente: costo por árbol"],
    proyectos: PROYECTOS,
    ...parcial,
  };
}

function calcular() {
  const boton = screen.getByRole("button", { name: "Calcular plan de compensación" });
  boton.focus();
  fireEvent.submit(boton.closest("form") as HTMLFormElement);
}

describe("PlanCompensacion (US-017)", () => {
  it("muestra CO₂, árboles y costo pendientes y los proyectos, sin violaciones de axe", async () => {
    const { llamadas } = instalarFetch(() => ({ body: plan() }));
    const { container } = montar(<PlanCompensacion />, "GERENTE");
    expect(await violacionesDe(container)).toBe("");
    fireEvent.change(screen.getByLabelText("Inicio del período"), { target: { value: "2026-11-01" } });
    fireEvent.change(screen.getByLabelText("Fin del período"), { target: { value: "2026-11-07" } });
    calcular();
    expect(await screen.findByText("1,234.500 kg")).toBeInTheDocument();
    expect(llamadas[0].path).toBe("/indicadores/compensacion?desde=2026-11-01&hasta=2026-11-07");
    expect(llamadas[0].init?.cache).toBe("no-cache");
    expect(screen.getByText("Árboles necesarios").nextSibling).toHaveTextContent("Pendiente");
    expect(screen.getByText("Costo estimado").nextSibling).toHaveTextContent("Pendiente");
    expect(screen.getByText("3 en 2 días")).toBeInTheDocument();
    expect(screen.getByText("Pendiente: factor RN-018")).toBeInTheDocument();
    const lista = screen.getByRole("list", { name: "Proyectos locales sugeridos" });
    expect(lista).toHaveTextContent("Lomas de Lima");
    expect(lista).toHaveTextContent("Parque Zonal Huáscar");
    expect(lista).toHaveTextContent("Árboles para Lima");
    expect(await violacionesDe(container)).toBe("");
  });

  it("muestra árboles y costo cuando los factores están configurados", async () => {
    instalarFetch(() => ({
      body: plan({
        dias_con_operacion: 1,
        rutas: 1,
        estado_factor: "CONFIGURADO",
        factor_captura_arbol_kg: 20,
        arboles_necesarios: 1250,
        estado_costo: "CONFIGURADO",
        costo_por_arbol_soles: 5,
        costo_estimado_soles: 6250,
        notas: [],
      }),
    }));
    montar(<PlanCompensacion />);
    calcular();
    expect(await screen.findByText("1,250")).toBeInTheDocument();
    expect(screen.getByText("S/ 6,250.00")).toBeInTheDocument();
    expect(screen.getByText("1 en 1 día")).toBeInTheDocument();
  });

  it("informa que no es posible calcular sin emisiones", async () => {
    instalarFetch(() => ({
      body: plan({
        calculable: false,
        mensaje: "No es posible calcular la compensación: no hay datos de emisiones en el período.",
        proyectos: [],
        notas: [],
      }),
    }));
    const { container } = montar(<PlanCompensacion />);
    calcular();
    expect(await screen.findByText(/No es posible calcular la compensación/)).toBeInTheDocument();
    expect(screen.queryByText("Proyectos locales sugeridos")).not.toBeInTheDocument();
    expect(await violacionesDe(container)).toBe("");
  });

  it("valida el período y muestra los errores de la API", async () => {
    const { llamadas } = instalarFetch(() => ({ status: 403, body: { detail: "Sin permiso" } }));
    montar(<PlanCompensacion />);
    fireEvent.change(screen.getByLabelText("Inicio del período"), { target: { value: "2026-11-08" } });
    fireEvent.change(screen.getByLabelText("Fin del período"), { target: { value: "2026-11-01" } });
    calcular();
    expect(await screen.findByRole("alert")).toHaveTextContent("anterior a la inicial");
    expect(llamadas).toHaveLength(0);
    fireEvent.change(screen.getByLabelText("Fin del período"), { target: { value: "2026-11-09" } });
    calcular();
    expect(await screen.findByRole("alert")).toHaveTextContent("Sin permiso");

    instalarFetch(() => {
      throw new Error("red");
    });
    calcular();
    expect(await screen.findByRole("alert")).toHaveTextContent("No se pudo calcular el plan de compensación.");
  });
});
