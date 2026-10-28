import { fireEvent, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { App } from "./App";
import { violacionesDe } from "./test/axe";
import { instalarFetch, montar } from "./test/pagina";
import type { Cliente, Conductor, Indicadores, Pedido, Ruta, Usuario, Vehiculo } from "./types";

vi.mock("leaflet", () => ({
  default: {
    map: (nodo: HTMLElement) => {
      nodo.setAttribute("tabindex", "0");
      const acercar = document.createElement("a");
      acercar.className = "leaflet-control-zoom-in";
      acercar.href = "#";
      acercar.textContent = "+";
      const alejar = document.createElement("a");
      alejar.className = "leaflet-control-zoom-out";
      alejar.href = "#";
      alejar.textContent = "−";
      nodo.append(acercar, alejar);
      return {
        remove: () => undefined,
        fitBounds: () => undefined,
        scrollWheelZoom: { enable: () => undefined, disable: () => undefined },
      };
    },
    tileLayer: () => ({
      on: () => undefined,
      addTo: () => undefined,
    }),
    polyline: () => ({ addTo: () => undefined }),
    circleMarker: () => ({
      bindPopup: () => ({ addTo: () => undefined }),
      addTo: () => undefined,
    }),
  },
}));

const vehiculo: Vehiculo = {
  id_vehiculo: "v1",
  placa: "DMO-101",
  tipo: "CAMIONETA",
  capacidad_kg: 1500,
  capacidad_m3: 8,
  consumo_km_l: 12.5,
  factor_emision_co2: 0.27,
  anio_fabricacion: 2022,
  estado: "ACTIVO",
};

const conductor: Conductor = {
  id_conductor: "c1",
  nombre: "Ana Ramos",
  dni: "12345678",
  licencia_categoria: "A-IIIb",
  anios_experiencia: 4,
  disponibilidad_inicio: "06:00:00",
  disponibilidad_fin: "14:00:00",
  lat_punto_partida: -12.01,
  lon_punto_partida: -76.98,
  estado: "ACTIVO",
};

const cliente: Cliente = {
  id_cliente: "cli-1",
  nombre: "Bodega El Ahorro",
  telefono: null,
  email: null,
  consentimiento_datos: true,
};

const pedido: Pedido = {
  id_pedido: "p1",
  id_cliente: "cli-1",
  nombre_cliente: "Bodega El Ahorro",
  punto_referencia: "frente a la bodega",
  latitud: -12.0025,
  longitud: -76.9901,
  peso_kg: 8,
  volumen_m3: 0.4,
  ventana_inicio: "2026-11-02T08:00",
  ventana_fin: "2026-11-02T12:00",
  prioridad: "ESTANDAR",
  tipo_producto: "NO_PERECEDERO",
  estado: "PENDIENTE",
  distrito: "San Juan de Lurigancho",
  georreferencia_aproximada: true,
};

const ruta: Ruta = {
  id_ruta: "r1",
  fecha: "2026-11-02",
  estado: "BORRADOR",
  distancia_total_km: 10,
  tiempo_total_min: 40,
  minutos_conduccion: 30,
  combustible_estimado_l: 2,
  co2_estimado_kg: 1.2,
  placa: "DMO-101",
  conductor: "Ana Ramos",
  origen_lat: -12.01,
  origen_lon: -76.98,
  descansos: [],
  paradas: [
    {
      secuencia: 1,
      id_pedido: "p1",
      nombre_cliente: "Bodega El Ahorro",
      eta: "2026-11-02T08:30:00",
      latitud: -12.02,
      longitud: -76.99,
      punto_referencia: "frente a la bodega",
      minutos_tramo: 12,
      nivel_congestion: "VERDE",
    },
  ],
};

const indicadores: Indicadores = {
  fecha: "2026-11-02",
  hay_datos: true,
  mensaje: null,
  rutas: 1,
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
};

const cuenta: Usuario = {
  id_usuario: "u1",
  email: "zoe@distrirapido.example.com",
  rol: "OPERADOR",
  estado: "ACTIVO",
  intentos_fallidos: 0,
};

function instalarDatos() {
  instalarFetch((path) => {
    if (path.includes("/vehiculos")) return { body: [vehiculo] };
    if (path.includes("/conductores")) return { body: [conductor] };
    if (path.includes("/clientes")) return { body: [cliente] };
    if (path.includes("/pedidos")) return { body: [pedido] };
    if (path.includes("/rutas")) return { body: [ruta] };
    if (path.includes("/indicadores")) return { body: indicadores };
    if (path.includes("/usuarios")) return { body: [cuenta] };
    return { body: [] };
  });
}

async function sinViolaciones() {
  expect(await violacionesDe(document.body)).toBe("");
}

describe("accesibilidad WCAG AA", () => {
  it("el login no tiene violaciones de axe", async () => {
    montar(<App />, null, "/login");
    expect(await screen.findByRole("heading", { name: "EcoLogística Lima" })).toBeInTheDocument();
    expect(document.title).toBe("Iniciar sesión · EcoLogística Lima");
    await sinViolaciones();
  });

  it("la flota, con tabla y formulario, no tiene violaciones de axe", async () => {
    instalarDatos();
    montar(<App />, "ADMIN", "/flota");
    expect(await screen.findByRole("heading", { name: "Flota" })).toBeInTheDocument();
    expect(await screen.findByRole("button", { name: "Guardar DMO-101" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Saltar al contenido" })).toHaveAttribute("href", "#contenido");
    expect(screen.getByRole("link", { name: "Contenido principal" })).toHaveAttribute("id", "contenido");
    fireEvent.click(screen.getByRole("button", { name: /Desplazar la tabla a la izquierda/ }));
    fireEvent.click(screen.getByRole("button", { name: /Desplazar la tabla a la derecha/ }));
    expect(screen.getByRole("navigation", { name: "Módulos" })).toBeInTheDocument();
    expect(screen.getByRole("navigation", { name: "Accesos directos" })).toBeInTheDocument();
    await sinViolaciones();
  });

  it("conductores no tiene violaciones de axe", async () => {
    instalarDatos();
    montar(<App />, "OPERADOR", "/conductores");
    expect(await screen.findByText("Ana Ramos")).toBeInTheDocument();
    await sinViolaciones();
  });

  it("pedidos no tiene violaciones de axe", async () => {
    instalarDatos();
    montar(<App />, "OPERADOR", "/pedidos");
    expect(await screen.findByText("Bodega El Ahorro")).toBeInTheDocument();
    await sinViolaciones();
  });

  it("rutas, el mapa y su alternativa textual no tienen violaciones de axe", async () => {
    instalarDatos();
    montar(<App />, "OPERADOR", "/rutas");
    expect(await screen.findByRole("link", { name: "Acercar" })).toBeInTheDocument();
    expect(screen.getByRole("region", { name: "Alternativa textual del mapa" })).toHaveTextContent("Bodega El Ahorro");
    expect(screen.getByRole("button", { name: "Confirmar ruta DMO-101 · Ana Ramos" })).toBeInTheDocument();
    await sinViolaciones();
  });

  it("el tablero no tiene violaciones de axe", async () => {
    instalarDatos();
    montar(<App />, "GERENTE", "/dashboard");
    expect(await screen.findByRole("heading", { name: "Kilómetros" })).toBeInTheDocument();
    await sinViolaciones();
  });

  it("usuarios no tiene violaciones de axe", async () => {
    instalarDatos();
    montar(<App />, "ADMIN", "/usuarios");
    expect(await screen.findByRole("button", { name: "Desactivar zoe@distrirapido.example.com" })).toBeInTheDocument();
    await sinViolaciones();
  });

  it("el modo conductor no tiene violaciones de axe", async () => {
    montar(<App />, "CONDUCTOR", "/modo");
    expect(await screen.findByRole("heading", { name: "Modo conductor" })).toBeInTheDocument();
    await sinViolaciones();
  });

  it("el acceso denegado tiene encabezado y no tiene violaciones de axe", async () => {
    montar(<App />, "CONDUCTOR", "/usuarios");
    expect(await screen.findByRole("heading", { name: "Acceso denegado" })).toBeInTheDocument();
    expect(screen.getByRole("alert")).toHaveTextContent("No tiene permiso para acceder a este módulo.");
    await sinViolaciones();
  });
});
