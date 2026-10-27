import { useEffect, useRef, useState } from "react";
import "leaflet/dist/leaflet.css";

import { MENSAJE_TILES, etiquetaCongestion, trazado } from "../mapa";
import type { ParadaRuta, Ruta } from "../types";

const COLORES = ["#08553d", "#0b3a66", "#7a1b1b", "#6a4b00", "#3d5248"];

const PINTURA: Record<string, string> = {
  VERDE: "#0d5c32",
  AMARILLO: "#8a6a00",
  ROJO: "#7a1b1b",
};

type Props = Readonly<{
  rutas: Ruta[];
  seleccionada: string | null;
}>;

type Marcador = {
  bindPopup: (texto: string) => { addTo: (lienzo: Lienzo) => void };
  addTo: (lienzo: Lienzo) => void;
};

type Lienzo = {
  remove: () => void;
  fitBounds: (grupo: [number, number][], opciones: { padding: [number, number] }) => void;
};

type LeafletApi = {
  map: (nodo: HTMLElement, opciones: { scrollWheelZoom: boolean }) => Lienzo;
  tileLayer: (
    url: string,
    opciones: { attribution: string; maxZoom: number },
  ) => { on: (evento: "tileerror", aviso: () => void) => void; addTo: (lienzo: Lienzo) => void };
  polyline: (
    puntos: [number, number][],
    opciones: { color: string; weight: number; opacity: number },
  ) => { addTo: (lienzo: Lienzo) => void };
  circleMarker: (
    punto: [number, number],
    estilo: { radius: number; color: string; fillColor: string; fillOpacity: number },
  ) => Marcador;
};

function pintarParada(L: LeafletApi, lienzo: Lienzo, parada: ParadaRuta, enfatizada: boolean) {
  if (parada.latitud == null || parada.longitud == null) return;
  const nivel = parada.nivel_congestion ?? "VERDE";
  const color = PINTURA[nivel] ?? PINTURA.VERDE;
  L.circleMarker([parada.latitud, parada.longitud], {
    radius: enfatizada ? 8 : 5,
    color,
    fillColor: color,
    fillOpacity: 0.9,
  })
    .bindPopup(
      `#${parada.secuencia} ${parada.nombre_cliente ?? "Entrega"}<br/>ETA ${
        parada.eta ? parada.eta.slice(11, 16) : "—"
      } · ${etiquetaCongestion(nivel)}`,
    )
    .addTo(lienzo);
}

function pintarRuta(
  L: LeafletApi,
  lienzo: Lienzo,
  ruta: Ruta,
  indice: number,
  seleccionada: string | null,
  grupo: [number, number][],
) {
  const puntos = trazado(ruta.origen_lat, ruta.origen_lon, ruta.paradas);
  const enfatizada = ruta.id_ruta === seleccionada || seleccionada == null;
  L.polyline(puntos, {
    color: COLORES[indice % COLORES.length],
    weight: enfatizada ? 5 : 2,
    opacity: enfatizada ? 0.95 : 0.35,
  }).addTo(lienzo);
  grupo.push(...puntos);
  if (puntos.length > 0) {
    L.circleMarker(puntos[0], {
      radius: 7,
      color: "#10241c",
      fillColor: "#ffffff",
      fillOpacity: 1,
    })
      .bindPopup("Punto de partida")
      .addTo(lienzo);
  }
  for (const parada of ruta.paradas) {
    pintarParada(L, lienzo, parada, enfatizada);
  }
}

function dibujar(
  L: LeafletApi,
  nodo: HTMLElement,
  activas: Ruta[],
  seleccionada: string | null,
  alFallarTesela: () => void,
) {
  const lienzo = L.map(nodo, { scrollWheelZoom: true });
  const teselas = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap",
    maxZoom: 18,
  });
  teselas.on("tileerror", alFallarTesela);
  teselas.addTo(lienzo);
  const grupo: [number, number][] = [];
  activas.forEach((ruta, indice) => {
    pintarRuta(L, lienzo, ruta, indice, seleccionada, grupo);
  });
  if (grupo.length > 0) lienzo.fitBounds(grupo, { padding: [24, 24] });
  return lienzo;
}

export function MapaRutas({ rutas, seleccionada }: Props) {
  const contenedor = useRef<HTMLElement>(null);
  const [tilesCaidos, setTilesCaidos] = useState(false);
  const activas = rutas.filter(
    (ruta) => trazado(ruta.origen_lat, ruta.origen_lon, ruta.paradas).length >= 2,
  );

  useEffect(() => {
    const nodo = contenedor.current;
    if (!nodo || tilesCaidos || activas.length === 0) return;
    let cancelado = false;
    let mapa: { remove: () => void } | null = null;

    void import("leaflet")
      .then((modulo) => {
        if (cancelado || !contenedor.current) return;
        mapa = dibujar(
          modulo.default as unknown as LeafletApi,
          contenedor.current,
          activas,
          seleccionada,
          () => setTilesCaidos(true),
        );
      })
      .catch(() => {
        if (!cancelado) setTilesCaidos(true);
      });

    return () => {
      cancelado = true;
      mapa?.remove();
    };
  }, [activas, seleccionada, tilesCaidos]);

  if (activas.length === 0) {
    return (
      <output className="aviso">
        No hay coordenadas para dibujar el trazado. La secuencia de entregas sigue en la tabla.
      </output>
    );
  }
  if (tilesCaidos) {
    return (
      <p className="alerta" role="alert">
        {MENSAJE_TILES}
      </p>
    );
  }
  return (
    <section
      ref={contenedor}
      className="mapa"
      aria-label="Mapa de rutas optimizadas sobre OpenStreetMap"
    />
  );
}
