import { FormEvent, useEffect, useState } from "react";

import { ApiError } from "../api";
import { useAuth } from "../auth";
import { Alerta } from "../avisos";
import type { Indicadores } from "../types";

function fechaHoy(): string {
  const fecha = new Date();
  const mes = String(fecha.getMonth() + 1).padStart(2, "0");
  const dia = String(fecha.getDate()).padStart(2, "0");
  return `${fecha.getFullYear()}-${mes}-${dia}`;
}

function soles(valor: number): string {
  return new Intl.NumberFormat("es-PE", {
    style: "currency",
    currency: "PEN",
    minimumFractionDigits: 2,
  }).format(valor);
}

export function DashboardPage() {
  const { llamar } = useAuth();
  const [fecha, setFecha] = useState(fechaHoy);
  const [datos, setDatos] = useState<Indicadores | null>(null);
  const [error, setError] = useState("");

  async function cargar(dia: string) {
    const cuerpo = await llamar<Indicadores>(`/indicadores?fecha=${dia}`);
    setDatos(cuerpo);
  }

  useEffect(() => {
    document.title = "Tablero · EcoLogística Lima";
    cargar(fecha).catch((err: unknown) =>
      setError(err instanceof ApiError ? err.message : "No se pudo cargar el tablero."),
    );
  }, [llamar, fecha]);

  function consultar(event: FormEvent) {
    event.preventDefault();
    setError("");
    cargar(fecha).catch((err: unknown) =>
      setError(err instanceof ApiError ? err.message : "No se pudo cargar el tablero."),
    );
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
