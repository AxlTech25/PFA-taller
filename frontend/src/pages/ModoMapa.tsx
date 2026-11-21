import { useEffect, useRef, useState } from "react";
import "leaflet/dist/leaflet.css";

import { ApiError } from "../api";
import { useAuth } from "../auth";
import { Alerta } from "../avisos";
import { opcionesTesela } from "../imagen";

const MENSAJE_TILES =
  "No se pudo cargar el mapa. La lista de paradas sigue disponible.";

type Punto = {
  secuencia: number;
  latitud: number;
  longitud: number;
  cliente: string;
};

type Mapa = {
  hay_ruta: boolean;
  placa?: string | null;
  puntos: Punto[];
};

type Lienzo = {
  remove: () => void;
  fitBounds: (grupo: [number, number][], opciones: { padding: [number, number] }) => void;
  scrollWheelZoom: { enable: () => void; disable: () => void };
};

type LeafletApi = {
  map: (
    nodo: HTMLElement,
    opciones: {
      scrollWheelZoom: boolean;
      fadeAnimation: boolean;
      zoomAnimation: boolean;
      markerZoomAnimation: boolean;
    },
  ) => Lienzo;
  tileLayer: (
    url: string,
    opciones: { attribution: string; maxZoom: number; detectRetina: false; updateWhenIdle: boolean },
  ) => {
    on: (evento: "tileerror", aviso: () => void) => { addTo: (lienzo: Lienzo) => void };
    addTo: (lienzo: Lienzo) => void;
  };
  polyline: (
    puntos: [number, number][],
    opciones: { color: string; weight: number },
  ) => { addTo: (lienzo: Lienzo) => void };
  circleMarker: (
    punto: [number, number],
    estilo: { radius: number; color: string; fillColor: string; fillOpacity: number },
  ) => { bindPopup: (texto: string) => { addTo: (lienzo: Lienzo) => void }; addTo: (lienzo: Lienzo) => void };
};

function etiquetarZoom(nodo: HTMLElement) {
  const acercar = nodo.querySelector(".leaflet-control-zoom-in");
  const alejar = nodo.querySelector(".leaflet-control-zoom-out");
  if (acercar) {
    acercar.setAttribute("aria-label", "Acercar");
    acercar.setAttribute("title", "Acercar");
  }
  if (alejar) {
    alejar.setAttribute("aria-label", "Alejar");
    alejar.setAttribute("title", "Alejar");
  }
}

export function ModoMapa() {
  const { llamar } = useAuth();
  const nodo = useRef<HTMLDivElement>(null);
  const [error, setError] = useState("");
  const [tiles, setTiles] = useState("");

  useEffect(() => {
    const destino = nodo.current;
    if (!destino) return;
    let vigente = true;
    let limpiar = () => {};
    llamar<Mapa>("/modo/mapa", { headers: { Accept: "application/json" } })
      .then(async (mapa) => {
        if (!vigente || !destino) return;
        const puntos = mapa.puntos.filter(
          (punto) => Number.isFinite(punto.latitud) && Number.isFinite(punto.longitud),
        );
        if (puntos.length === 0) {
          setError("Esta ruta no tiene coordenadas para el mapa.");
          return;
        }
        const leaflet = (await import("leaflet")).default as unknown as LeafletApi;
        if (!vigente) return;
        const lienzo = leaflet.map(destino, {
          scrollWheelZoom: false,
          fadeAnimation: false,
          zoomAnimation: false,
          markerZoomAnimation: false,
        });
        const grupo: [number, number][] = [];
        leaflet
          .tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
            ...opcionesTesela('© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'),
          })
          .on("tileerror", () => {
            if (vigente) setTiles(MENSAJE_TILES);
          })
          .addTo(lienzo);
        for (const punto of puntos) {
          const par: [number, number] = [punto.latitud, punto.longitud];
          grupo.push(par);
          leaflet
            .circleMarker(par, {
              radius: 7,
              color: "#08553d",
              fillColor: "#ffffff",
              fillOpacity: 1,
            })
            .bindPopup(`Parada ${punto.secuencia}. ${punto.cliente}`)
            .addTo(lienzo);
        }
        if (grupo.length >= 2) {
          leaflet.polyline(grupo, { color: "#08553d", weight: 3 }).addTo(lienzo);
          lienzo.fitBounds(grupo, { padding: [24, 24] });
        }
        etiquetarZoom(destino);
        lienzo.scrollWheelZoom.disable();
        const alEntrar = () => lienzo.scrollWheelZoom.enable();
        const alSalir = () => lienzo.scrollWheelZoom.disable();
        destino.addEventListener("focusin", alEntrar);
        destino.addEventListener("focusout", alSalir);
        limpiar = () => {
          destino.removeEventListener("focusin", alEntrar);
          destino.removeEventListener("focusout", alSalir);
          lienzo.remove();
        };
      })
      .catch((err: unknown) => {
        if (!vigente) return;
        setError(err instanceof ApiError ? err.message : "No se pudo abrir el mapa.");
      });
    return () => {
      vigente = false;
      limpiar();
    };
  }, [llamar]);

  return (
    <section aria-label="Mapa opcional de la ruta">
      {error ? <Alerta id="alerta-mapa-modo">{error}</Alerta> : null}
      {tiles ? <p className="aviso">{tiles}</p> : null}
      <div ref={nodo} className="mapa mapa-modo" role="application" aria-label="Mapa de las paradas" />
    </section>
  );
}
