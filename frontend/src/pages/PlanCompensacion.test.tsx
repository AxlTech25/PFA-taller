import { fireEvent, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { violacionesDe } from "../test/axe";
import { instalarFetch, montar } from "../test/pagina";
import type { ConversionGnv, PlanAnual, PlanCompensacion as Plan } from "../types";
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

const AVISO = "Proyección lineal a 365 días a partir de 2 día(s) con operación dentro de 7 día(s).";

function anual(parcial: Partial<PlanAnual> = {}): PlanAnual {
  const plan = (nombre: string, factor: number, arboles: number) => ({
    nombre,
    clave_factor: `factor_${factor}`,
    fuente: "fuente",
    factor_kg_arbol_anio: factor,
    estado_factor: "CONFIGURADO" as const,
    arboles_anuales: arboles,
    costo_por_arbol_soles: 94,
    estado_costo: "CONFIGURADO" as const,
    costo_total_soles: arboles * 94,
    arboles_por_anio: Math.ceil(arboles / 3),
    plan: [1, 2, 3].map((n) => ({
      anio: n,
      arboles_a_plantar: Math.ceil(arboles / 3),
      arboles_acumulados: Math.ceil(arboles / 3) * n,
      cobertura_pct: n === 3 ? 100 : n * 33.3,
      costo_soles: Math.ceil(arboles / 3) * 94,
    })),
  });
  return {
    desde: "2026-11-01",
    hasta: "2026-11-07",
    calculable: true,
    mensaje: null,
    dias_calendario: 7,
    dias_con_operacion: 2,
    co2_periodo_kg: 10,
    co2_anual_kg: 521.4,
    aviso: AVISO,
    anios_meta: 3,
    escenarios: [plan("EPA (referencia)", 60, 9), plan("Pesimista (tesis UPN 2024)", 15, 35)],
    avance: { arboles_registrados: 0, estado_registro: "PENDIENTE", avance_pct: 0, nota: "Pendiente: sin árboles registrados." },
    ...parcial,
  };
}

function gnv(parcial: Partial<ConversionGnv> = {}): ConversionGnv {
  return {
    desde: "2026-11-01",
    hasta: "2026-11-07",
    calculable: true,
    mensaje: null,
    vehiculos: 2,
    dias_calendario: 7,
    dias_con_operacion: 2,
    litros_periodo: 100,
    aviso_proyeccion: AVISO,
    inversion_soles: 10000,
    equivalencia_m3_por_galon: 3.8087,
    co2_evitado_anual_kg: 147.3,
    reduccion_co2_pct: 28.3,
    anios_roi: 3,
    escenarios: [
      {
        nombre: "Consigna (S/ 12.50 por m³)",
        clave_precio: "precio_gnv_m3_soles",
        fuente: "Consigna",
        precio_gnv_m3: 12.5,
        estado_precio: "CONFIGURADO",
        costo_gnv_anual_soles: 65579.47,
        ahorro_anual_soles: -41473.77,
        recuperacion_meses: null,
        roi_3_anios_pct: -1344.2,
        ahorro_3_anios_soles: -124421.32,
        se_recupera: false,
      },
      {
        nombre: "Mercado Lima (referencial)",
        clave_precio: "gnv_precio_mercado_m3_soles",
        fuente: "Osinergmin",
        precio_gnv_m3: 1.68,
        estado_precio: "CONFIGURADO",
        costo_gnv_anual_soles: 8813.88,
        ahorro_anual_soles: 15291.82,
        recuperacion_meses: 7.8,
        roi_3_anios_pct: 358.8,
        ahorro_3_anios_soles: 45875.46,
        se_recupera: true,
      },
    ],
    notas: ["Con el precio de la consigna el GNV cuesta más que el diésel."],
    ...parcial,
  };
}

function api(principal: Partial<Plan> = {}, extra: { anual?: PlanAnual; gnv?: ConversionGnv } = {}) {
  return (path: string) => {
    if (path.startsWith("/indicadores/compensacion/anual")) return { body: extra.anual ?? anual() };
    if (path.startsWith("/indicadores/gnv")) return { body: extra.gnv ?? gnv() };
    return { body: plan(principal) };
  };
}

function calcular() {
  const boton = screen.getByRole("button", { name: "Calcular plan de compensación" });
  boton.focus();
  fireEvent.submit(boton.closest("form") as HTMLFormElement);
}

describe("PlanCompensacion (US-017)", () => {
  it("muestra CO₂, árboles y costo pendientes y los proyectos, sin violaciones de axe", async () => {
    const { llamadas } = instalarFetch(api());
    const { container } = montar(<PlanCompensacion />, "GERENTE");
    expect(await violacionesDe(container)).toBe("");
    fireEvent.change(screen.getByLabelText("Inicio del período"), { target: { value: "2026-11-01" } });
    fireEvent.change(screen.getByLabelText("Fin del período"), { target: { value: "2026-11-07" } });
    calcular();
    expect(await screen.findByText("1,234.500 kg")).toBeInTheDocument();
    const rutas = llamadas.map((llamada) => llamada.path).sort();
    expect(rutas).toEqual([
      "/indicadores/compensacion/anual?desde=2026-11-01&hasta=2026-11-07",
      "/indicadores/compensacion?desde=2026-11-01&hasta=2026-11-07",
      "/indicadores/gnv?desde=2026-11-01&hasta=2026-11-07",
    ]);
    expect(llamadas.every((llamada) => llamada.init?.cache === "no-cache")).toBe(true);
    expect(screen.getByText("Factor de captura por árbol").nextSibling).toHaveTextContent("Pendiente");
    expect(screen.getByText("Costo por árbol").nextSibling).toHaveTextContent("Pendiente");
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
    instalarFetch(
      api({
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
    );
    montar(<PlanCompensacion />);
    calcular();
    expect(await screen.findByText("1,250")).toBeInTheDocument();
    expect(screen.getByText("Factor de captura por árbol").nextSibling).toHaveTextContent("20 kg/árbol/año");
    expect(screen.getByText("Costo por árbol").nextSibling).toHaveTextContent("S/ 5.00");
    expect(screen.getByText("S/ 6,250.00")).toBeInTheDocument();
    expect(screen.getByText("1 en 1 día")).toBeInTheDocument();
  });

  it("informa que no es posible calcular sin emisiones", async () => {
    instalarFetch(
      api({
        calculable: false,
        mensaje: "No es posible calcular la compensación: no hay datos de emisiones en el período.",
        proyectos: [],
        notas: [],
      }),
    );
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

  it("muestra la proyección anual, el plan a 3 años y el ROI de GNV con avisos claros", async () => {
    instalarFetch(api());
    const { container } = montar(<PlanCompensacion />, "GERENTE");
    calcular();
    expect(await screen.findByText("521.4 kg")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /carbono neutral a 3 años/ })).toBeInTheDocument();
    // El aviso de proyección corta aparece en la meta anual y en el ROI de GNV.
    expect(screen.getAllByText(AVISO)).toHaveLength(2);
    const escenarios = screen.getByRole("table", {
      name: "Árboles y costo para compensar las emisiones anuales",
    });
    expect(escenarios).toHaveTextContent("EPA (referencia)60 kg/árbol/añoS/ 94.009S/ 846.003");
    expect(escenarios).toHaveTextContent("Pesimista (tesis UPN 2024)15 kg/árbol/añoS/ 94.0035S/ 3,290.0012");
    const plan = screen.getByRole("table", {
      name: "Plan de plantación a 3 años, escenario Pesimista (tesis UPN 2024)",
    });
    expect(plan).toHaveTextContent("Año 1121233.3 %S/ 1,128.00");
    expect(plan).toHaveTextContent("100.0 %");
    expect(screen.getByText("Avance hacia la meta").nextSibling).toHaveTextContent(
      "0.0 % (0 árboles registrados)",
    );
    expect(screen.getByText("Pendiente: sin árboles registrados.")).toBeInTheDocument();
    const tablaGnv = screen.getByRole("table", {
      name: "Ahorro, recuperación y ROI a 3 años de convertir a GNV",
    });
    expect(tablaGnv).toHaveTextContent("Consigna (S/ 12.50 por m³)S/ 12.50 por m³-S/ 41,473.77No se recupera-1,344.2 %");
    expect(tablaGnv).toHaveTextContent("Mercado Lima (referencial)S/ 1.68 por m³S/ 15,291.827.8 meses358.8 %");
    expect(screen.getByText("Inversión").nextSibling).toHaveTextContent("S/ 10,000.00");
    expect(screen.getByText("Equivalencia diésel-GNV").nextSibling).toHaveTextContent("3.81 m³ por galón");
    expect(screen.getByText("CO₂ evitado al año").nextSibling).toHaveTextContent("147.3 kg (28.3 %)");
    expect(screen.getByText(/Con el precio de la consigna el GNV cuesta más/)).toBeInTheDocument();
    expect(await violacionesDe(container)).toBe("");
  });

  it("marca como pendientes los datos de la meta y del GNV que no están configurados", async () => {
    const pendiente = anual().escenarios[1];
    instalarFetch(
      api(
        {},
        {
          anual: anual({
            escenarios: [
              {
                ...pendiente,
                estado_factor: "PENDIENTE",
                factor_kg_arbol_anio: null,
                arboles_anuales: null,
                costo_total_soles: null,
                arboles_por_anio: null,
                plan: [],
              },
            ],
            avance: { arboles_registrados: 4, estado_registro: "CONFIGURADO", avance_pct: null, nota: null },
          }),
          gnv: gnv({
            inversion_soles: null,
            equivalencia_m3_por_galon: null,
            co2_evitado_anual_kg: null,
            escenarios: [
              {
                ...gnv().escenarios[0],
                precio_gnv_m3: null,
                estado_precio: "PENDIENTE",
                ahorro_anual_soles: null,
                roi_3_anios_pct: null,
              },
            ],
            notas: [],
          }),
        },
      ),
    );
    const { container } = montar(<PlanCompensacion />);
    calcular();
    expect(await screen.findByText("521.4 kg")).toBeInTheDocument();
    expect(screen.queryByRole("table", { name: /Plan de plantación/ })).not.toBeInTheDocument();
    expect(screen.getByText("Avance hacia la meta").nextSibling).toHaveTextContent(
      "Pendiente (4 árboles registrados)",
    );
    expect(screen.getByText("Inversión").nextSibling).toHaveTextContent("Pendiente");
    expect(screen.getByText("Equivalencia diésel-GNV").nextSibling).toHaveTextContent("Pendiente");
    expect(screen.getByText("CO₂ evitado al año").nextSibling).toHaveTextContent("Pendiente");
    expect(await violacionesDe(container)).toBe("");
  });

  it("muestra el aviso de las vistas anual y GNV cuando no son calculables", async () => {
    const vacio = "No es posible calcular la compensación: no hay datos de emisiones en el período.";
    instalarFetch(
      api(
        {},
        {
          anual: anual({ calculable: false, mensaje: vacio, escenarios: [], avance: null }),
          gnv: gnv({ calculable: false, mensaje: "Sin diésel en el período.", escenarios: [] }),
        },
      ),
    );
    montar(<PlanCompensacion />);
    calcular();
    expect(await screen.findByText(vacio)).toBeInTheDocument();
    expect(screen.getByText("Sin diésel en el período.")).toBeInTheDocument();
  });
});
