import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { MENSAJE_TILES } from "../mapa";
import type { Ruta } from "../types";
import { MapaRutas } from "./MapaRutas";

const estado = vi.hoisted(() => ({
  tileerror: null as null | (() => void),
  fitBounds: vi.fn(),
  remove: vi.fn(),
}));

vi.mock("leaflet", () => ({
  default: {
    map: () => ({ remove: estado.remove, fitBounds: estado.fitBounds }),
    tileLayer: () => ({
      on: (_evento: string, aviso: () => void) => {
        estado.tileerror = aviso;
      },
      addTo: () => undefined,
    }),
    polyline: () => ({ addTo: () => undefined }),
    circleMarker: () => ({
      bindPopup: () => ({ addTo: () => undefined }),
      addTo: () => undefined,
    }),
  },
}));

function ruta(parcial: Partial<Ruta> = {}): Ruta {
  return {
    id_ruta: "r1",
    fecha: "2026-11-02",
    estado: "BORRADOR",
    distancia_total_km: 1,
    tiempo_total_min: 10,
    minutos_conduccion: 10,
    combustible_estimado_l: 1,
    co2_estimado_kg: 1,
    placa: "ABC123",
    conductor: "Ana",
    origen_lat: -12.01,
    origen_lon: -76.98,
    descansos: [],
    paradas: [
      {
        secuencia: 1,
        id_pedido: "p1",
        nombre_cliente: "Bodega",
        eta: "2026-11-02T08:30:00",
        latitud: -12.02,
        longitud: -76.99,
        nivel_congestion: "ROJO",
      },
      { secuencia: 2, id_pedido: "p2", latitud: null, longitud: null },
    ],
    ...parcial,
  };
}

describe("MapaRutas", () => {
  beforeEach(() => {
    estado.tileerror = null;
    estado.fitBounds.mockClear();
    estado.remove.mockClear();
  });

  it("avisa si no hay coordenadas para el trazado", () => {
    render(
      <MapaRutas
        rutas={[ruta({ origen_lat: null, origen_lon: null, paradas: [] })]}
        seleccionada={null}
      />,
    );
    expect(screen.getByText(/No hay coordenadas/)).toBeInTheDocument();
  });

  it("dibuja el plan y cae a la tabla si las teselas fallan", async () => {
    const { unmount } = render(
      <MapaRutas rutas={[ruta(), ruta({ id_ruta: "r2" })]} seleccionada="r2" />,
    );
    expect(
      screen.getByRole("region", { name: "Mapa de rutas optimizadas sobre OpenStreetMap" }),
    ).toBeInTheDocument();
    await waitFor(() => expect(estado.fitBounds).toHaveBeenCalled());
    estado.tileerror?.();
    expect(await screen.findByRole("alert")).toHaveTextContent(MENSAJE_TILES);
    unmount();
  });

  it("cancela el dibujo si el mapa se desmonta antes de llegar Leaflet", () => {
    const vista = render(<MapaRutas rutas={[ruta()]} seleccionada={null} />);
    vista.unmount();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });
});
