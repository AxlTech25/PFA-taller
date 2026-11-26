import { FormEvent, useState } from "react";

import { ApiError } from "../api";
import { useAuth } from "../auth";
import { Alerta } from "../avisos";
import { fechaHoy } from "../fechas";
import { errorPeriodo, guardarArchivo, nombreReporte, pedirReporte } from "../reporte";

export function ReportePdf() {
  const { sesion, cerrar } = useAuth();
  const [desde, setDesde] = useState(fechaHoy);
  const [hasta, setHasta] = useState(fechaHoy);
  const [ocupado, setOcupado] = useState(false);
  const [error, setError] = useState("");
  const [aviso, setAviso] = useState("");

  async function descargar(event: FormEvent) {
    event.preventDefault();
    setError("");
    setAviso("");
    const invalido = errorPeriodo(desde, hasta);
    if (invalido) {
      setError(invalido);
      return;
    }
    setOcupado(true);
    try {
      const archivo = await pedirReporte(desde, hasta, sesion?.access_token);
      const nombre = nombreReporte(desde, hasta);
      guardarArchivo(archivo, nombre);
      setAviso(`Reporte listo: ${nombre}.`);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) cerrar();
      setError(err instanceof ApiError ? err.message : "No se pudo generar el reporte PDF.");
    } finally {
      setOcupado(false);
    }
  }

  return (
    <section className="panel" aria-labelledby="titulo-reporte">
      <h2 id="titulo-reporte">Reporte PDF de sostenibilidad</h2>
      <p id="ayuda-reporte" className="ayuda">
        Descarga un PDF con emisiones por ruta, combustible, costos locales (RN-017), ahorro frente
        al vecino más cercano y cumplimiento de ventanas, con las mismas cifras del tablero. Hasta{" "}
        31 días. Si el período no tiene rutas, no se genera archivo.
      </p>
      {error ? <Alerta id="alerta-reporte">{error}</Alerta> : null}
      <form
        className="grilla"
        aria-labelledby="titulo-reporte"
        aria-describedby="ayuda-reporte"
        onSubmit={descargar}
        noValidate
      >
        <label htmlFor="reporte-desde">
          Desde{/*
          */}<input
            id="reporte-desde"
            type="date"
            required
            value={desde}
            onChange={(event) => setDesde(event.target.value)}
          />
        </label>
        <label htmlFor="reporte-hasta">
          Hasta{/*
          */}<input
            id="reporte-hasta"
            type="date"
            required
            value={hasta}
            onChange={(event) => setHasta(event.target.value)}
          />
        </label>
        <button type="submit" disabled={ocupado} aria-busy={ocupado}>
          {ocupado ? "Generando PDF…" : "Descargar reporte PDF"}
        </button>
      </form>
      <output className={aviso ? "exito" : undefined} aria-live="polite">
        {aviso}
      </output>
    </section>
  );
}
