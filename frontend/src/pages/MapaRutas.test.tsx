import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { MENSAJE_TILES, olvidarGeometrias } from "../mapa";
import type { Ruta } from "../types";
import { MapaRutas } from "./MapaRutas";

const estado = vi.hoisted(() => ({
  tileerror: null as null | (() => void),
  fitBounds: vi.fn(),
  remove: vi.fn(),
  enableZoom: vi.fn(),
  disableZoom: vi.fn(),
  conControles: true,
  lineas: [] as [number, number][][],
  punteadas: [] as [number, number][][],
}));

vi.mock("leaflet", () => ({
  default: {
    map: (nodo: HTMLElement) => {
      nodo.setAttribute("tabindex", "0");
      if (estado.conControles) {
        const acercar = document.createElement("a");
        acercar.className = "leaflet-control-zoom-in";
        acercar.href = "#";
        acercar.textContent = "+";
        acercar.setAttribute("title", "Zoom in");
        const alejar = document.createElement("a");
        alejar.className = "leaflet-control-zoom-out";
        alejar.href = "#";
        alejar.textContent = "−";
        alejar.setAttribute("title", "Zoom out");
        nodo.append(acercar, alejar);
      }
      return {
        remove: estado.remove,
        fitBounds: estado.fitBounds,
        scrollWheelZoom: { enable: estado.enableZoom, disable: estado.disableZoom },
      };
    },
    tileLayer: () => ({
      on: (_evento: string, aviso: () => void) => {
        estado.tileerror = aviso;
      },
      addTo: () => undefined,
    }),
    polyline: (puntos: [number, number][], opciones: { dashArray?: string }) => {
      (opciones.dashArray ? estado.punteadas : estado.lineas).push(puntos);
      return { addTo: () => undefined };
    },
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
        punto_referencia: "frente a la bodega",
      },
      { secuencia: 2, id_pedido: "p2", latitud: null, longitud: null },
    ],
    ...parcial,
  };
}

describe("MapaRutas", () => {
  beforeEach(() => {
    estado.tileerror = null;
    estado.conControles = true;
    estado.fitBounds.mockClear();
    estado.remove.mockClear();
    estado.enableZoom.mockClear();
    estado.disableZoom.mockClear();
    estado.lineas = [];
    estado.punteadas = [];
    olvidarGeometrias();
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("sin red")));
  });

  it("traza la ruta por las calles que devuelve OSRM", async () => {
    const calles: [number, number][] = [
      [-76.98, -12.01],
      [-76.981, -12.013],
      [-76.99, -12.02],
    ];
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({
          code: "Ok",
          routes: [{ geometry: { coordinates: calles } }],
          waypoints: [
            { location: [-76.98, -12.01], distance: 0 },
            { location: [-76.99, -12.0205], distance: 55 },
          ],
        }),
      }),
    );
    render(<MapaRutas rutas={[ruta()]} seleccionada={null} />);
    await waitFor(() => expect(estado.fitBounds).toHaveBeenCalled());
    expect(estado.lineas[0]).toEqual([
      [-12.01, -76.98],
      [-12.013, -76.981],
      [-12.02, -76.99],
    ]);
    expect(estado.punteadas).toEqual([
      [
        [-12.0205, -76.99],
        [-12.02, -76.99],
      ],
    ]);
  });

  it("dibuja la línea recta si OSRM no responde", async () => {
    render(<MapaRutas rutas={[ruta()]} seleccionada={null} />);
    await waitFor(() => expect(estado.fitBounds).toHaveBeenCalled());
    expect(estado.lineas[0]).toEqual([
      [-12.01, -76.98],
      [-12.02, -76.99],
    ]);
  });

  it("avisa si no hay coordenadas para el trazado", () => {
    render(
      <MapaRutas
        rutas={[ruta({ origen_lat: null, origen_lon: null, paradas: [] })]}
        seleccionada={null}
      />,
    );
    expect(screen.getByText(/No hay coordenadas/)).toBeInTheDocument();
    expect(screen.getByText(/Sin punto de partida/)).toBeInTheDocument();
    expect(screen.getByText(/Sin paradas en el trazado/)).toBeInTheDocument();
  });

  it("describe en texto cuando no llega ninguna ruta", () => {
    render(<MapaRutas rutas={[]} seleccionada={null} />);
    expect(screen.getByText("No hay rutas para describir en texto.")).toBeInTheDocument();
  });

  it("describe una partida con una sola coordenada", () => {
    render(
      <MapaRutas
        rutas={[ruta({ origen_lat: -12.01, origen_lon: null, paradas: [] })]}
        seleccionada={null}
      />,
    );
    expect(screen.getByText(/Sin punto de partida/)).toBeInTheDocument();
  });

  it("dibuja el plan y cae a la tabla si las teselas fallan", async () => {
    const { unmount } = render(
      <MapaRutas rutas={[ruta(), ruta({ id_ruta: "r2" })]} seleccionada="r2" />,
    );
    expect(
      screen.getByRole("region", { name: "Mapa de rutas optimizadas sobre OpenStreetMap" }),
    ).toBeInTheDocument();
    await waitFor(() => expect(estado.fitBounds).toHaveBeenCalled());
    expect(estado.disableZoom).toHaveBeenCalled();
    expect(screen.getByRole("link", { name: "Acercar" })).toHaveAttribute("title", "Acercar");
    expect(screen.getByRole("link", { name: "Alejar" })).toBeInTheDocument();
    expect(screen.getAllByText(/referencia frente a la bodega/).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/ETA 08:30/).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Semáforo Rojo/).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Parada 2: Entrega/).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Semáforo Sin dato/).length).toBeGreaterThan(0);
    expect(screen.getByText(/Esta ruta está resaltada/)).toBeInTheDocument();
    const region = screen.getByRole("region", { name: "Mapa de rutas optimizadas sobre OpenStreetMap" });
    region.focus();
    region.dispatchEvent(new FocusEvent("focusin", { bubbles: true }));
    expect(document.activeElement).toBe(region);
    region.dispatchEvent(new KeyboardEvent("keydown", { key: "ArrowLeft", bubbles: true }));
    expect(document.activeElement).toBe(region);
    region.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", bubbles: true }));
    expect(document.activeElement).not.toBe(region);
    expect(estado.enableZoom).toHaveBeenCalled();
    estado.tileerror?.();
    expect(await screen.findByRole("alert")).toHaveTextContent(MENSAJE_TILES);
    expect(screen.getByRole("region", { name: "Alternativa textual del mapa" })).toBeInTheDocument();
    unmount();
    expect(estado.remove).toHaveBeenCalled();
  });

  it("dibuja aunque el control de zoom no esté en el DOM", async () => {
    estado.conControles = false;
    render(<MapaRutas rutas={[ruta()]} seleccionada={null} />);
    await waitFor(() => expect(estado.fitBounds).toHaveBeenCalled());
    expect(screen.queryByRole("link", { name: "Acercar" })).not.toBeInTheDocument();
    expect(screen.getByText(/Partida en -12.01, -76.98/)).toBeInTheDocument();
  });

  it("cancela el dibujo si el mapa se desmonta antes de llegar Leaflet", () => {
    const vista = render(<MapaRutas rutas={[ruta()]} seleccionada={null} />);
    vista.unmount();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });
});
