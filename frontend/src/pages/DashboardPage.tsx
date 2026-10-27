import { FormEvent, useEffect, useState } from "react";

import { ApiError } from "../api";
import { useAuth } from "../auth";
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
      {error ? (
        <p className="alerta" role="alert">
          {error}
        </p>
      ) : null}
      <section className="panel">
        <form className="grilla" onSubmit={consultar}>
          <label htmlFor="fecha-tablero">
            Fecha{/*
            */}<input
              id="fecha-tablero"
              type="date"
              required
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
        <section className="metricas" aria-label="Indicadores del día">
          <article className="panel metrica">
            <span>Kilómetros</span>
            <strong>{datos.km}</strong>
          </article>
          <article className="panel metrica">
            <span>CO₂</span>
            <strong>{datos.co2_kg} kg</strong>
          </article>
          <article className="panel metrica">
            <span>Combustible</span>
            <strong>{datos.combustible_l} L</strong>
          </article>
          <article className="panel metrica">
            <span>Ventanas cumplidas</span>
            <strong>{datos.cumplimiento_ventanas_pct} %</strong>
          </article>
          <article className="panel metrica">
            <span>Soles de combustible</span>
            <strong>{soles(datos.soles_combustible)}</strong>
          </article>
          <article className="panel metrica">
            <span>Soles de mantenimiento</span>
            <strong>{soles(datos.soles_mantenimiento)}</strong>
          </article>
          <article className="panel metrica">
            <span>Soles ahorrados</span>
            <strong>{soles(datos.soles_ahorrados)}</strong>
          </article>
          <article className="panel metrica">
            <span>Árboles equivalentes</span>
            <strong>{datos.arboles ?? "—"}</strong>
          </article>
        </section>
      ) : null}
      {datos?.nota_arboles ? <p className="ayuda">{datos.nota_arboles}</p> : null}
    </>
  );
}
