import { useEffect, useRef, useState } from "react";
import "leaflet/dist/leaflet.css";

import { MENSAJE_TILES, etiquetaCongestion, trazado } from "../mapa";
import type { Ruta } from "../types";

const COLORES = ["#08553d", "#0b3a66", "#7a1b1b", "#6a4b00", "#3d5248"];

const PINTURA: Record<string, string> = {
  VERDE: "#0d5c32",
  AMARILLO: "#8a6a00",
  ROJO: "#7a1b1b",
};

type Props = {
  rutas: Ruta[];
  seleccionada: string | null;
};

export function MapaRutas({ rutas, seleccionada }: Props) {
  const contenedor = useRef<HTMLDivElement>(null);
  const [tilesCaidos, setTilesCaidos] = useState(false);
  const activas = rutas.filter((ruta) => trazado(ruta.origen_lat, ruta.origen_lon, ruta.paradas).length >= 2);

  useEffect(() => {
    if (!contenedor.current || tilesCaidos || activas.length === 0) return;
    let cancelado = false;
    let mapa: { remove: () => void } | null = null;

    import("leaflet").then((modulo) => {
      if (cancelado || !contenedor.current) return;
      const L = modulo.default;
      const lienzo = L.map(contenedor.current, { scrollWheelZoom: true });
      mapa = lienzo;
      const teselas = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap",
        maxZoom: 18,
      });
      teselas.on("tileerror", () => setTilesCaidos(true));
      teselas.addTo(lienzo);
      const grupo: [number, number][] = [];
      activas.forEach((ruta, indice) => {
        const puntos = trazado(ruta.origen_lat, ruta.origen_lon, ruta.paradas);
        const enfatizada = ruta.id_ruta === seleccionada || seleccionada == null;
        const linea = L.polyline(puntos, {
          color: COLORES[indice % COLORES.length],
          weight: enfatizada ? 5 : 2,
          opacity: enfatizada ? 0.95 : 0.35,
        });
        linea.addTo(lienzo);
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
        ruta.paradas.forEach((parada) => {
          if (parada.latitud == null || parada.longitud == null) return;
          const nivel = parada.nivel_congestion ?? "VERDE";
          L.circleMarker([parada.latitud, parada.longitud], {
            radius: enfatizada ? 8 : 5,
            color: PINTURA[nivel] ?? PINTURA.VERDE,
            fillColor: PINTURA[nivel] ?? PINTURA.VERDE,
            fillOpacity: 0.9,
          })
            .bindPopup(
              `#${parada.secuencia} ${parada.nombre_cliente ?? "Entrega"}<br/>ETA ${
                parada.eta ? parada.eta.slice(11, 16) : "—"
              } · ${etiquetaCongestion(nivel)}`,
            )
            .addTo(lienzo);
        });
      });
      if (grupo.length > 0) lienzo.fitBounds(grupo, { padding: [24, 24] });
    });

    return () => {
      cancelado = true;
      mapa?.remove();
    };
  }, [activas, seleccionada, tilesCaidos]);

  if (activas.length === 0) {
    return (
      <p className="aviso" role="status">
        No hay coordenadas para dibujar el trazado. La secuencia de entregas sigue en la tabla.
      </p>
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
    <div
      ref={contenedor}
      className="mapa"
      role="region"
      aria-label="Mapa de rutas optimizadas sobre OpenStreetMap"
    />
  );
}
