import { cleanup, fireEvent, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { instalarFetch, montar } from "../test/pagina";
import type { Ruta } from "../types";
import { RutasPage } from "./RutasPage";

vi.mock("./MapaRutas", () => ({
  MapaRutas: ({ seleccionada }: { seleccionada: string | null }) => (
    <div>mapa {seleccionada ?? "ninguno"}</div>
  ),
}));

const originalTimeout = globalThis.setTimeout;

const ruta: Ruta = {
  id_ruta: "r1",
  fecha: "2026-11-02",
  estado: "BORRADOR",
  distancia_total_km: 10,
  tiempo_total_min: 40,
  minutos_conduccion: 30,
  combustible_estimado_l: 2,
  co2_estimado_kg: 1.2,
  placa: "ABC123",
  conductor: "Ana Ramos",
  origen_lat: -12.01,
  origen_lon: -76.98,
  descansos: [{ despues_de_secuencia: 1, duracion_min: 60, motivo: "Ley" }],
  paradas: [
    {
      secuencia: 1,
      id_pedido: "p1",
      nombre_cliente: null,
      eta: "2026-11-02T08:15:00",
      punto_referencia: null,
      minutos_tramo: 12,
      nivel_congestion: "AMARILLO",
    },
    {
      secuencia: 2,
      id_pedido: "p2",
      nombre_cliente: "Bodega",
      eta: null,
      punto_referencia: "paradero",
      minutos_tramo: null,
      nivel_congestion: null,
    },
  ],
  comparacion: {
    mejora_porcentaje: 15,
    distancia_km: 10,
    distancia_base_km: 12,
    co2_kg: 1.2,
    co2_base_kg: 1.5,
  },
};

const segunda: Ruta = {
  ...ruta,
  id_ruta: "r2",
  placa: null,
  conductor: null,
  estado: "CONFIRMADA",
  descansos: [],
  comparacion: null,
  paradas: [],
};

beforeEach(() => {
  vi.spyOn(globalThis, "setTimeout").mockImplementation((handler, timeout, ...resto) => {
    if (timeout === 1000 && typeof handler === "function" && handler.name === "") {
      handler();
      return 0 as unknown as ReturnType<typeof setTimeout>;
    }
    return originalTimeout(handler as TimerHandler, timeout as number, ...(resto as []));
  });
});

describe("RutasPage", () => {
  it("muestra el plan, el mapa y confirma el borrador", async () => {
    instalarFetch((_path, init) => {
      if (init?.method === "POST") {
        return { body: { ...ruta, mensaje: "Ruta confirmada.", estado: "CONFIRMADA" } };
      }
      return { body: [ruta, segunda] };
    });
    montar(<RutasPage />);
    expect(await screen.findByText(/Costo verde frente al vecino/)).toHaveTextContent("15 %");
    expect(document.title).toBe("Rutas · EcoLogística Lima");
    expect(screen.getByText("mapa r1")).toBeInTheDocument();
    expect(screen.getByText(/60 min \(Ley/)).toBeInTheDocument();
    expect(screen.getByText("Sin descanso insertado: la conducción continua es menor a 4 horas.")).toBeInTheDocument();
    expect(screen.getAllByText("Cliente").length).toBeGreaterThan(0);
    expect(screen.getAllByText("—").length).toBeGreaterThan(0);
    expect(screen.getByText("12 min")).toBeInTheDocument();
    expect(screen.getByText("Sin dato")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /Vehículo · Conductor/ })).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText("Fecha de reparto"), { target: { value: "2026-11-03" } });
    expect(await screen.findByText("mapa r1")).toBeInTheDocument();
    fireEvent.click(screen.getAllByRole("button", { name: "Ver en el mapa" })[1]);
    expect(screen.getByText("mapa r2")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Confirmar ruta" }));
    expect(await screen.findByText("Ruta confirmada.")).toBeInTheDocument();
  });

  it("avisa si no hay rutas y el gerente no genera", async () => {
    instalarFetch(() => ({ body: [] }));
    montar(<RutasPage />, "GERENTE");
    expect(await screen.findByText("No hay rutas para la fecha seleccionada.")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Generar rutas" })).not.toBeInTheDocument();
  });

  it("encola un plan completado, fallido o todavía en cola", async () => {
    instalarFetch((_path, init) => {
      if (init?.method === "POST") {
        return {
          body: {
            id_job: "j1",
            estado: "COMPLETADO",
            mensaje: "Plan listo",
            fecha: "2026-11-02",
            rutas: [],
          },
        };
      }
      return { body: [] };
    });
    montar(<RutasPage />);
    await screen.findByRole("button", { name: "Generar rutas" });
    fireEvent.submit(
      screen.getByRole("button", { name: "Generar rutas" }).closest("form") as HTMLFormElement,
    );
    expect(await screen.findByText("Plan listo")).toBeInTheDocument();

    cleanup();
    instalarFetch((_path, init) => {
      if (init?.method === "POST") {
        return {
          body: {
            id_job: "j2",
            estado: "FALLIDO",
            mensaje: "No hubo flota",
            fecha: "2026-11-02",
            rutas: [],
          },
        };
      }
      return { body: [] };
    });
    montar(<RutasPage />);
    await screen.findByRole("button", { name: "Generar rutas" });
    fireEvent.submit(
      screen.getByRole("button", { name: "Generar rutas" }).closest("form") as HTMLFormElement,
    );
    expect(await screen.findByRole("alert")).toHaveTextContent("No hubo flota");

    cleanup();
    let lecturas = 0;
    instalarFetch((path, init) => {
      if (init?.method === "POST" && path === "/optimizaciones") {
        return {
          body: {
            id_job: "j3",
            estado: "EN_PROCESO",
            mensaje: "Trabajo en cola.",
            fecha: "2026-11-02",
            rutas: [],
          },
        };
      }
      if (path.startsWith("/optimizaciones/")) {
        lecturas += 1;
        const estado = lecturas === 1 ? "EN_PROCESO" : "COMPLETADO";
        return {
          body: {
            id_job: "j3",
            estado,
            mensaje: "Plan listo tras espera",
            fecha: "2026-11-02",
            rutas: [],
          },
        };
      }
      return { body: [] };
    });
    montar(<RutasPage />);
    await screen.findByRole("button", { name: "Generar rutas" });
    fireEvent.submit(
      screen.getByRole("button", { name: "Generar rutas" }).closest("form") as HTMLFormElement,
    );
    expect(await screen.findByText("Plan listo tras espera")).toBeInTheDocument();
    expect(lecturas).toBeGreaterThan(0);

    cleanup();
    instalarFetch((path, _init) => {
      const job = {
        id_job: "j4",
        estado: "ENCOLADO",
        mensaje: "Sigue en cola",
        fecha: "2026-11-02",
        rutas: [],
      };
      if (path.startsWith("/optimizaciones")) return { body: job };
      return { body: [] };
    });
    montar(<RutasPage />);
    await screen.findByRole("button", { name: "Generar rutas" });
    fireEvent.submit(
      screen.getByRole("button", { name: "Generar rutas" }).closest("form") as HTMLFormElement,
    );
    expect(await screen.findByRole("alert")).toHaveTextContent("El trabajo sigue en cola");
  });

  it("informa errores de carga, de cola y de confirmación", async () => {
    instalarFetch(() => ({ status: 500, body: { detail: "Rutas caídas" } }));
    montar(<RutasPage />);
    expect(await screen.findByRole("alert")).toHaveTextContent("Rutas caídas");

    cleanup();
    instalarFetch(() => {
      throw new Error("red");
    });
    montar(<RutasPage />);
    expect(await screen.findByRole("alert")).toHaveTextContent("No se pudo cargar las rutas.");

    cleanup();
    instalarFetch((_path, init) => {
      if (init?.method === "POST") throw new Error("red");
      return { body: [ruta] };
    });
    montar(<RutasPage />);
    await screen.findByRole("button", { name: "Generar rutas" });
    fireEvent.submit(
      screen.getByRole("button", { name: "Generar rutas" }).closest("form") as HTMLFormElement,
    );
    expect(await screen.findByRole("alert")).toHaveTextContent("No se pudo encolar la optimización.");

    cleanup();
    instalarFetch((_path, init) => {
      if (init?.method === "POST") return { status: 409, body: { detail: "Jornada excedida" } };
      return { body: [ruta] };
    });
    montar(<RutasPage />);
    await screen.findByRole("button", { name: "Confirmar ruta" });
    fireEvent.click(screen.getByRole("button", { name: "Confirmar ruta" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Jornada excedida");

    cleanup();
    instalarFetch((_path, init) => {
      if (init?.method === "POST") throw new Error("red");
      return { body: [ruta] };
    });
    montar(<RutasPage />);
    await screen.findByRole("button", { name: "Confirmar ruta" });
    fireEvent.click(screen.getByRole("button", { name: "Confirmar ruta" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("No se pudo confirmar la ruta.");
  });
});
