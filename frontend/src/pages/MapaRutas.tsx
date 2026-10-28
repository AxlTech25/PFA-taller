import { useEffect, useRef, useState, type ReactNode } from "react";
import "leaflet/dist/leaflet.css";

import { Alerta } from "../avisos";
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
  scrollWheelZoom: { enable: () => void; disable: () => void };
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

function prepararInteraccion(lienzo: Lienzo, nodo: HTMLElement) {
  lienzo.scrollWheelZoom.disable();
  etiquetarZoom(nodo);
  const alEntrar = () => lienzo.scrollWheelZoom.enable();
  const alSalir = () => lienzo.scrollWheelZoom.disable();
  const alTecla = (evento: KeyboardEvent) => {
    if (evento.key === "Escape") nodo.blur();
  };
  nodo.addEventListener("focusin", alEntrar);
  nodo.addEventListener("focusout", alSalir);
  nodo.addEventListener("keydown", alTecla);
  return () => {
    nodo.removeEventListener("focusin", alEntrar);
    nodo.removeEventListener("focusout", alSalir);
    nodo.removeEventListener("keydown", alTecla);
  };
}

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
  const lienzo = L.map(nodo, { scrollWheelZoom: false });
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
  return { lienzo, limpiar: prepararInteraccion(lienzo, nodo) };
}

function textoPartida(ruta: Ruta): string {
  if (ruta.origen_lat == null || ruta.origen_lon == null) {
    return "Sin punto de partida en el trazado.";
  }
  return `Partida en ${ruta.origen_lat}, ${ruta.origen_lon}.`;
}

function textoParada(parada: ParadaRuta): string {
  const cliente = parada.nombre_cliente ?? "Entrega";
  const referencia = parada.punto_referencia ? `, referencia ${parada.punto_referencia}` : "";
  const eta = parada.eta ? `, ETA ${parada.eta.slice(11, 16)}` : "";
  return `Parada ${parada.secuencia}: ${cliente}${referencia}${eta}. Semáforo ${etiquetaCongestion(parada.nivel_congestion)}.`;
}

function ListaTextual({ rutas, seleccionada }: Props) {
  return (
    <section id="alternativa-mapa" className="alternativa-mapa" aria-labelledby="titulo-alternativa-mapa">
      <h3 id="titulo-alternativa-mapa">Alternativa textual del mapa</h3>
      {rutas.length === 0 ? (
        <p>No hay rutas para describir en texto.</p>
      ) : (
        <ol>
          {rutas.map((ruta) => (
            <li key={ruta.id_ruta} aria-current={ruta.id_ruta === seleccionada ? "true" : undefined}>
              <p>
                {ruta.placa ?? "Vehículo"} · {ruta.conductor ?? "Conductor"}. {textoPartida(ruta)}
                {ruta.id_ruta === seleccionada ? " Esta ruta está resaltada en el mapa." : ""}
              </p>
              {ruta.paradas.length === 0 ? (
                <p>Sin paradas en el trazado.</p>
              ) : (
                <ol>
                  {ruta.paradas.map((parada) => (
                    <li key={`${ruta.id_ruta}-${parada.secuencia}`}>{textoParada(parada)}</li>
                  ))}
                </ol>
              )}
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}

export function MapaRutas({ rutas, seleccionada }: Props) {
  const contenedor = useRef<HTMLElement>(null);
  const [tilesCaidos, setTilesCaidos] = useState(false);
  const activas = rutas.filter(
    (ruta) => trazado(ruta.origen_lat, ruta.origen_lon, ruta.paradas).length >= 2,
  );

  useEffect(() => {
    const nodo = contenedor.current;
    if (!nodo || tilesCaidos || activas.length === 0) return undefined;
    let cancelado = false;
    let mapa: Lienzo | null = null;
    let limpiar = () => {};

    void import("leaflet")
      .then((modulo) => {
        if (cancelado || !contenedor.current) return;
        const dibujo = dibujar(
          modulo.default as unknown as LeafletApi,
          contenedor.current,
          activas,
          seleccionada,
          () => setTilesCaidos(true),
        );
        mapa = dibujo.lienzo;
        limpiar = dibujo.limpiar;
      })
      .catch(() => {
        if (!cancelado) setTilesCaidos(true);
      });

    return () => {
      cancelado = true;
      limpiar();
      mapa?.remove();
    };
  }, [activas, seleccionada, tilesCaidos]);

  let cuerpo: ReactNode;
  if (activas.length === 0) {
    cuerpo = (
      <output className="aviso">
        No hay coordenadas para dibujar el trazado. La secuencia de entregas sigue en la tabla.
      </output>
    );
  } else if (tilesCaidos) {
    cuerpo = <Alerta id="alerta-mapa">{MENSAJE_TILES}</Alerta>;
  } else {
    cuerpo = (
      <section
        ref={contenedor}
        className="mapa"
        aria-label="Mapa de rutas optimizadas sobre OpenStreetMap"
        aria-describedby="alternativa-mapa"
      />
    );
  }

  return (
    <div className="mapa-y-texto">
      <ListaTextual rutas={rutas} seleccionada={seleccionada} />
      {cuerpo}
    </div>
  );
}
