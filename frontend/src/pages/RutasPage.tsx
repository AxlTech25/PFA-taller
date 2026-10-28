import { FormEvent, useEffect, useState } from "react";

import { ApiError } from "../api";
import { useAuth } from "../auth";
import { Alerta, Exito, TablaDesplazable } from "../avisos";
import { etiquetaCongestion } from "../mapa";
import { etiqueta, puedeGenerarRutas } from "../permissions";
import type { JobOptimizacion, Ruta } from "../types";
import { MapaRutas } from "./MapaRutas";

function fechaHoy(): string {
  const fecha = new Date();
  const mes = String(fecha.getMonth() + 1).padStart(2, "0");
  const dia = String(fecha.getDate()).padStart(2, "0");
  return `${fecha.getFullYear()}-${mes}-${dia}`;
}

function nombreRuta(ruta: Ruta): string {
  return `${ruta.placa ?? "Vehículo"} · ${ruta.conductor ?? "Conductor"}`;
}

function esperar(ms: number): Promise<void> {
  return new Promise((resolver) => {
    globalThis.setTimeout(resolver, ms);
  });
}

export function RutasPage() {
  const { llamar, sesion } = useAuth();
  const generar = sesion ? puedeGenerarRutas(sesion.rol) : false;
  const [fecha, setFecha] = useState(fechaHoy);
  const [rutas, setRutas] = useState<Ruta[]>([]);
  const [seleccion, setSeleccion] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [aviso, setAviso] = useState("");
  const [ocupado, setOcupado] = useState(false);

  async function cargar(dia: string) {
    const lista = await llamar<Ruta[]>(`/rutas?fecha=${dia}`);
    setRutas(lista);
    setSeleccion((actual) =>
      actual && lista.some((ruta) => ruta.id_ruta === actual) ? actual : (lista[0]?.id_ruta ?? null),
    );
  }

  useEffect(() => {
    document.title = "Rutas · EcoLogística Lima";
    cargar(fecha).catch((err: unknown) =>
      setError(err instanceof ApiError ? err.message : "No se pudo cargar las rutas."),
    );
  }, [llamar, fecha]);

  async function solicitar(event: FormEvent) {
    event.preventDefault();
    setError("");
    setAviso("");
    setOcupado(true);
    try {
      const job = await llamar<JobOptimizacion>("/optimizaciones", {
        method: "POST",
        body: JSON.stringify({ fecha }),
      });
      setAviso(job.mensaje ?? "Trabajo en cola.");
      let ultimo = job;
      for (let intento = 0; intento < 40 && (ultimo.estado === "ENCOLADO" || ultimo.estado === "EN_PROCESO"); intento += 1) {
        await esperar(1000);
        ultimo = await llamar<JobOptimizacion>(`/optimizaciones/${job.id_job}`);
      }
      setAviso(ultimo.mensaje ?? "");
      if (ultimo.estado === "FALLIDO") {
        setError(ultimo.mensaje ?? "No se pudo generar el plan.");
      }
      if (ultimo.estado === "ENCOLADO") {
        setError(
          "El trabajo sigue en cola. Verifique que el worker de optimización esté en ejecución.",
        );
      }
      await cargar(fecha);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo encolar la optimización.");
    } finally {
      setOcupado(false);
    }
  }

  async function confirmar(idRuta: string) {
    setError("");
    setAviso("");
    try {
      const ruta = await llamar<Ruta>(`/rutas/${idRuta}/confirmar`, { method: "POST" });
      setAviso(ruta.mensaje ?? "Ruta confirmada.");
      await cargar(fecha);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo confirmar la ruta.");
    }
  }

  return (
    <>
      <header>
        <h1>Rutas</h1>
        <p id="ayuda-rutas" className="ayuda">
          El operador encola el plan del día. Un worker aparte ejecuta el algoritmo genético
          (VRPTW + Green VRP) y lo compara con el vecino más cercano. La confirmación rechaza
          jornadas de más de 8 horas e inserta un descanso de 1 hora cada 4 horas de conducción
          (Ley N.º 30224). Los vehículos con el último dígito restringido ese día no entran al plan.
          El mapa usa OpenStreetMap. Si las teselas no cargan, queda la tabla de paradas.
          Al cambiar la fecha se actualiza el plan mostrado.
        </p>
      </header>
      {error ? <Alerta id="alerta-rutas">{error}</Alerta> : null}
      {aviso ? <Exito>{aviso}</Exito> : null}
      {generar ? (
        <section className="panel" aria-labelledby="titulo-generar">
          <h2 id="titulo-generar">Generar plan del día</h2>
          <form className="grilla" aria-labelledby="titulo-generar" onSubmit={solicitar}>
            <label htmlFor="fecha">
              Fecha de reparto{/*
              */}<input
                id="fecha"
                type="date"
                required
                aria-describedby="ayuda-rutas"
                value={fecha}
                onChange={(event) => setFecha(event.target.value)}
              />
            </label>
            <button type="submit" disabled={ocupado}>
              {ocupado ? "En cola…" : "Generar rutas"}
            </button>
          </form>
        </section>
      ) : null}
      <section className="panel" aria-labelledby="titulo-mapa">
        <h2 id="titulo-mapa">Mapa del plan</h2>
        <p id="ayuda-mapa" className="ayuda">
          El punto blanco es la partida del conductor. Cada parada lleva el color del semáforo y
          también su nombre: verde fuera de hora punta, amarillo con factor de congestión o en hora
          punta (07:00–09:00 y 17:00–20:00) y rojo si ambos se juntan o el factor llega a 1.35. Con
          teclado, tabule hasta el mapa, use las flechas para desplazarlo y los botones Acercar y
          Alejar para el zoom. Escape suelta el mapa. La rueda del mouse solo acerca cuando el mapa
          tiene el foco, para no trabar el desplazamiento de la página. Si no puede usar el mapa,
          lea la alternativa textual y la tabla de paradas.
        </p>
        <MapaRutas rutas={rutas} seleccionada={seleccion} />
      </section>
      <section className="panel" aria-labelledby="titulo-plan">
        <h2 id="titulo-plan">Plan generado</h2>
        {rutas[0]?.comparacion ? (
          <output className="exito">
            Costo verde frente al vecino más cercano: {rutas[0].comparacion.mejora_porcentaje ?? 0} %.
            Distancia {rutas[0].comparacion.distancia_km ?? 0} km (base{" "}
            {rutas[0].comparacion.distancia_base_km ?? 0} km). CO₂ {rutas[0].comparacion.co2_kg ?? 0} kg
            (base {rutas[0].comparacion.co2_base_kg ?? 0} kg).
          </output>
        ) : null}
        {rutas.length === 0 ? (
          <p>No hay rutas para la fecha seleccionada.</p>
        ) : (
          rutas.map((ruta) => (
            <article key={ruta.id_ruta} className="panel" aria-labelledby={`titulo-${ruta.id_ruta}`}>
              <h3 id={`titulo-${ruta.id_ruta}`}>
                {nombreRuta(ruta)}{" "}
                <span className={`insignia ${ruta.estado}`}>{etiqueta(ruta.estado)}</span>
              </h3>
              <p>
                {ruta.distancia_total_km ?? 0} km · {ruta.minutos_conduccion ?? 0} min de conducción
                · {ruta.combustible_estimado_l ?? 0} L · {ruta.co2_estimado_kg ?? 0} kg CO₂
              </p>
              {ruta.descansos.length > 0 ? (
                <p>
                  Descansos:{" "}
                  {ruta.descansos
                    .map((descanso) => `${descanso.duracion_min} min (Ley N.º 30224)`)
                    .join(", ")}
                </p>
              ) : (
                <p className="muted">Sin descanso insertado: la conducción continua es menor a 4 horas.</p>
              )}
              <button
                type="button"
                className="secundario"
                aria-pressed={seleccion === ruta.id_ruta}
                aria-label={`${
                  seleccion === ruta.id_ruta ? "Visible en el mapa" : "Ver en el mapa"
                } ${nombreRuta(ruta)}`}
                onClick={() => setSeleccion(ruta.id_ruta)}
              >
                {seleccion === ruta.id_ruta ? "Visible en el mapa" : "Ver en el mapa"}
              </button>
              <TablaDesplazable
                etiqueta={`Secuencia de ${nombreRuta(ruta)}. Si no cabe, desplácela en horizontal con el teclado.`}
              >
                <table>
                  <caption className="muted">Secuencia de entregas</caption>
                  <thead>
                    <tr>
                      <th scope="col">#</th>
                      <th scope="col">Cliente</th>
                      <th scope="col">Referencia</th>
                      <th scope="col">ETA</th>
                      <th scope="col">Tramo</th>
                      <th scope="col">Congestión</th>
                    </tr>
                  </thead>
                  <tbody>
                    {ruta.paradas.map((parada) => (
                      <tr key={`${ruta.id_ruta}-${parada.secuencia}`}>
                        <td>{parada.secuencia}</td>
                        <td>{parada.nombre_cliente ?? "Cliente"}</td>
                        <td>{parada.punto_referencia ?? "—"}</td>
                        <td>{parada.eta ? parada.eta.slice(0, 16).replace("T", " ") : "—"}</td>
                        <td>{parada.minutos_tramo == null ? "—" : `${parada.minutos_tramo} min`}</td>
                        <td>
                          <span className={`insignia semaforo ${parada.nivel_congestion ?? ""}`}>
                            {etiquetaCongestion(parada.nivel_congestion)}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </TablaDesplazable>
              {generar && ruta.estado === "BORRADOR" ? (
                <button
                  type="button"
                  aria-label={`Confirmar ruta ${nombreRuta(ruta)}`}
                  onClick={() => confirmar(ruta.id_ruta)}
                >
                  Confirmar ruta
                </button>
              ) : null}
            </article>
          ))
        )}
      </section>
    </>
  );
}
