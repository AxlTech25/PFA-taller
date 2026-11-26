import { FormEvent, useEffect, useRef, useState } from "react";

import { ApiError } from "../api";
import { useAuth } from "../auth";
import { Alerta } from "../avisos";
import { fechaHoy } from "../fechas";
import type { Indicadores } from "../types";
import { ReportePdf } from "./ReportePdf";

function soles(valor: number): string {
  // Sin Intl.NumberFormat: el primer `es-PE` + moneda carga datos ICU en el
  // hilo principal y empuja el TBT del tablero por encima del presupuesto.
  const negativo = valor < 0;
  const [entero, fraccion] = Math.abs(valor).toFixed(2).split(".");
  const grupos = entero.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  return `${negativo ? "-" : ""}S/ ${grupos}.${fraccion}`;
}

export function DashboardPage() {
  const { llamar } = useAuth();
  const [fecha, setFecha] = useState(fechaHoy);
  const [datos, setDatos] = useState<Indicadores | null>(null);
  const [error, setError] = useState("");
  const consulta = useRef(0);

  async function cargar(dia: string) {
    const actual = consulta.current + 1;
    consulta.current = actual;
    try {
      const cuerpo = await llamar<Indicadores>(`/indicadores?fecha=${dia}`);
      if (consulta.current !== actual) return;
      setDatos(cuerpo);
      setError("");
    } catch (err: unknown) {
      if (consulta.current !== actual) return;
      setError(err instanceof ApiError ? err.message : "No se pudo cargar el tablero.");
    }
  }

  useEffect(() => {
    document.title = "Tablero · EcoLogística Lima";
    cargar(fecha);
  }, [llamar, fecha]);

  function consultar(event: FormEvent) {
    event.preventDefault();
    cargar(fecha);
  }

  return (
    <>
      <header>
        <h1>Tablero</h1>
        <p className="ayuda">
          Inicio del tablero de sostenibilidad del día. Muestra kilómetros, CO₂, combustible,
          soles y el cumplimiento de ventanas del último plan. El equivalente en árboles espera
          el factor de captura (RN-018). El cierre del dashboard queda para el siguiente sprint.
        </p>
      </header>
      {error ? <Alerta id="alerta-tablero">{error}</Alerta> : null}
      <section className="panel" aria-labelledby="titulo-periodo">
        <h2 id="titulo-periodo">Período</h2>
        <p id="aviso-fecha-tablero" className="ayuda">
          Al cambiar la fecha o pulsar Consultar se actualizan los indicadores.
        </p>
        <form className="grilla" aria-labelledby="titulo-periodo" onSubmit={consultar}>
          <label htmlFor="fecha-tablero">
            Fecha{/*
            */}<input
              id="fecha-tablero"
              type="date"
              required
              aria-describedby="aviso-fecha-tablero"
              value={fecha}
              onChange={(event) => setFecha(event.target.value)}
            />
          </label>
          <button type="submit">Consultar</button>
        </form>
      </section>
      <ReportePdf />
      {datos && !datos.hay_datos ? (
        <output className="aviso">{datos.mensaje}</output>
      ) : null}
      {datos?.hay_datos ? (
        <section className="panel" aria-label="Indicadores del día">
          <h2>Indicadores del día</h2>
          <div className="metricas">
            <article className="panel metrica" aria-labelledby="metrica-km">
              <h3 id="metrica-km">Kilómetros</h3>
              <p>{datos.km}</p>
            </article>
            <article className="panel metrica" aria-labelledby="metrica-co2">
              <h3 id="metrica-co2">CO₂</h3>
              <p>{datos.co2_kg} kg</p>
            </article>
            <article className="panel metrica" aria-labelledby="metrica-combustible">
              <h3 id="metrica-combustible">Combustible</h3>
              <p>{datos.combustible_l} L</p>
            </article>
            <article className="panel metrica" aria-labelledby="metrica-ventanas">
              <h3 id="metrica-ventanas">Ventanas cumplidas</h3>
              <p>{datos.cumplimiento_ventanas_pct} %</p>
            </article>
            <article className="panel metrica" aria-labelledby="metrica-soles-combustible">
              <h3 id="metrica-soles-combustible">Soles de combustible</h3>
              <p>{soles(datos.soles_combustible)}</p>
            </article>
            <article className="panel metrica" aria-labelledby="metrica-soles-mantenimiento">
              <h3 id="metrica-soles-mantenimiento">Soles de mantenimiento</h3>
              <p>{soles(datos.soles_mantenimiento)}</p>
            </article>
            <article className="panel metrica" aria-labelledby="metrica-soles-ahorrados">
              <h3 id="metrica-soles-ahorrados">Soles ahorrados</h3>
              <p>{soles(datos.soles_ahorrados)}</p>
            </article>
            <article className="panel metrica" aria-labelledby="metrica-arboles">
              <h3 id="metrica-arboles">Árboles equivalentes</h3>
              <p>{datos.arboles ?? "—"}</p>
            </article>
          </div>
        </section>
      ) : null}
      {datos?.nota_arboles ? <p className="ayuda">{datos.nota_arboles}</p> : null}
    </>
  );
}
