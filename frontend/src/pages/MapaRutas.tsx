import { useEffect, useRef, useState, type ReactNode } from "react";
import "leaflet/dist/leaflet.css";

import { Alerta } from "../avisos";
import { opcionesTesela } from "../imagen";
import {
  MENSAJE_TILES,
  etiquetaCongestion,
  trazado,
  trazadoPorCalles,
  type Trazado,
} from "../mapa";
import type { ParadaRuta, Ruta, ZonaRestriccion } from "../types";
import { anilloZona, etiquetaZona } from "../zonas";

const COLORES = ["#08553d", "#0b3a66", "#7a1b1b", "#6a4b00", "#3d5248"];

const PINTURA: Record<string, string> = {
  VERDE: "#0d5c32",
  AMARILLO: "#8a6a00",
  ROJO: "#7a1b1b",
};

const ZONAS_VACIAS: ZonaRestriccion[] = [];

const ESTILO_ZONA: Record<string, { color: string; fill: string }> = {
  RESERVA_ECOLOGICA: { color: "#0d5c32", fill: "#b7dfc8" },
  RIESGO_SEGURIDAD: { color: "#7a1b1b", fill: "#f3c1bc" },
};

type Props = Readonly<{
  rutas: Ruta[];
  seleccionada: string | null;
  zonas?: ZonaRestriccion[];
  advertencia?: string;
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
  ) => { on: (evento: "tileerror", aviso: () => void) => void; addTo: (lienzo: Lienzo) => void };
  polyline: (
    puntos: [number, number][],
    opciones: { color: string; weight: number; opacity: number; dashArray?: string },
  ) => { addTo: (lienzo: Lienzo) => void };
  circleMarker: (
    punto: [number, number],
    estilo: { radius: number; color: string; fillColor: string; fillOpacity: number },
  ) => Marcador;
  polygon: (
    anillo: [number, number][],
    estilo: { color: string; weight: number; fillColor: string; fillOpacity: number },
  ) => { bindPopup: (texto: string) => { addTo: (lienzo: Lienzo) => void } };
};

function escapar(texto: string): string {
  return texto
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function sePuedeDibujar(ruta: Ruta): boolean {
  if ((ruta.trazado?.length ?? 0) >= 2) return true;
  return trazado(ruta.origen_lat, ruta.origen_lon, ruta.paradas).length >= 2;
}

function geometriaDe(ruta: Ruta): Promise<Trazado> {
  if (ruta.trazado && ruta.trazado.length >= 2) {
    return Promise.resolve({ linea: ruta.trazado, enlaces: [] });
  }
  return trazadoPorCalles(trazado(ruta.origen_lat, ruta.origen_lon, ruta.paradas));
}

function pintarZonas(L: LeafletApi, lienzo: Lienzo, zonas: ZonaRestriccion[], grupo: [number, number][]) {
  for (const zona of zonas) {
    const anillo = anilloZona(zona);
    if (anillo.length < 3) continue;
    const estilo = ESTILO_ZONA[zona.tipo] ?? { color: "#6a4b00", fill: "#f3e6b8" };
    const demo = zona.es_demostracion ? "<br/>Polígono de demostración, no es un límite oficial." : "";
    L.polygon(anillo, { color: estilo.color, weight: 2, fillColor: estilo.fill, fillOpacity: 0.35 })
      .bindPopup(`${escapar(zona.nombre)}<br/>${escapar(etiquetaZona(zona.tipo))}${demo}`)
      .addTo(lienzo);
    grupo.push(...anillo);
  }
}

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
  calles: Trazado,
  indice: number,
  seleccionada: string | null,
  grupo: [number, number][],
) {
  const puntos = trazado(ruta.origen_lat, ruta.origen_lon, ruta.paradas);
  const enfatizada = ruta.id_ruta === seleccionada || seleccionada == null;
  const color = COLORES[indice % COLORES.length];
  L.polyline(calles.linea, {
    color,
    weight: enfatizada ? 5 : 2,
    opacity: enfatizada ? 0.95 : 0.35,
  }).addTo(lienzo);
  for (const enlace of calles.enlaces) {
    L.polyline(enlace, {
      color,
      weight: enfatizada ? 3 : 2,
      opacity: enfatizada ? 0.9 : 0.35,
      dashArray: "4 6",
    }).addTo(lienzo);
  }
  grupo.push(...calles.linea, ...puntos);
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
  calles: Trazado[],
  zonas: ZonaRestriccion[],
  seleccionada: string | null,
  alFallarTesela: () => void,
) {
  const lienzo = L.map(nodo, {
    scrollWheelZoom: false,
    fadeAnimation: false,
    zoomAnimation: false,
    markerZoomAnimation: false,
  });
  const teselas = L.tileLayer(
    "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
    opcionesTesela("&copy; OpenStreetMap"),
  );
  teselas.on("tileerror", alFallarTesela);
  teselas.addTo(lienzo);
  const grupo: [number, number][] = [];
  pintarZonas(L, lienzo, zonas, grupo);
  activas.forEach((ruta, indice) => {
    pintarRuta(L, lienzo, ruta, calles[indice], indice, seleccionada, grupo);
  });
  if (grupo.length > 0) lienzo.fitBounds(grupo, { padding: [24, 24] });
  return { lienzo, limpiar: prepararInteraccion(lienzo, nodo) };
}

function textoRestriccion(ruta: Ruta): string {
  const partes: string[] = [];
  if (ruta.evita_riesgo) partes.push("Trazado alternativo que evita zonas de riesgo.");
  if (ruta.zonas_cruzadas?.some((zona) => zona.tipo === "RESERVA_ECOLOGICA")) {
    partes.push("Atraviesa una reserva ecológica.");
  }
  return partes.length ? ` ${partes.join(" ")}` : "";
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

function ListaZonas({ zonas, advertencia }: { zonas: ZonaRestriccion[]; advertencia: string }) {
  if (zonas.length === 0) return null;
  return (
    <section aria-labelledby="titulo-zonas" className="zonas-mapa">
      <h3 id="titulo-zonas">Zonas de restricción</h3>
      {advertencia ? <p>{advertencia}</p> : null}
      <ul className="leyenda-zonas">
        <li>
          <span className="muestra reserva" aria-hidden="true" />
          Reserva ecológica, restricción dura
        </li>
        <li>
          <span className="muestra riesgo" aria-hidden="true" />
          Zona de riesgo
        </li>
      </ul>
      <ul>
        {zonas.map((zona) => (
          <li key={zona.id_zona}>
            {zona.nombre}. {etiquetaZona(zona.tipo)}. Severidad {zona.severidad.toLowerCase()}.
            {zona.es_demostracion ? " Polígono de demostración, no es un límite oficial." : ""}
          </li>
        ))}
      </ul>
    </section>
  );
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
                {textoRestriccion(ruta)}
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

export function MapaRutas({ rutas, seleccionada, zonas, advertencia = "" }: Props) {
  const contenedor = useRef<HTMLElement>(null);
  const [tilesCaidos, setTilesCaidos] = useState(false);
  const capas = zonas ?? ZONAS_VACIAS;
  const activas = rutas.filter(sePuedeDibujar);
  const hayDibujo = activas.length > 0 || capas.length > 0;

  useEffect(() => {
    const nodo = contenedor.current;
    if (!nodo || tilesCaidos || !hayDibujo) return undefined;
    let cancelado = false;
    let mapa: Lienzo | null = null;
    let limpiar = () => {};

    const calles = Promise.all(activas.map((ruta) => geometriaDe(ruta)));

    void Promise.all([import("leaflet"), calles])
      .then(([modulo, geometrias]) => {
        if (cancelado || !contenedor.current) return;
        const dibujo = dibujar(
          modulo.default as unknown as LeafletApi,
          contenedor.current,
          activas,
          geometrias,
          capas,
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
  }, [activas, capas, hayDibujo, seleccionada, tilesCaidos]);

  let cuerpo: ReactNode;
  if (!hayDibujo) {
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
      <ListaZonas zonas={capas} advertencia={advertencia} />
      <ListaTextual rutas={rutas} seleccionada={seleccionada} />
      <div className="mapa-reserva">{cuerpo}</div>
    </div>
  );
}
