import { FormEvent, useState } from "react";

import { ApiError } from "../api";
import { useAuth } from "../auth";
import { Alerta } from "../avisos";
import { fechaHoy } from "../fechas";
import { errorPeriodo } from "../reporte";
import type { PlanCompensacion as Plan } from "../types";

function numero(valor: number, decimales: number): string {
  // Sin Intl: mismo criterio del tablero para no cargar datos ICU.
  const [entero, fraccion] = valor.toFixed(decimales).split(".");
  const grupos = entero.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  return fraccion ? `${grupos}.${fraccion}` : grupos;
}

export function PlanCompensacion() {
  const { llamar } = useAuth();
  const [desde, setDesde] = useState(fechaHoy);
  const [hasta, setHasta] = useState(fechaHoy);
  const [plan, setPlan] = useState<Plan | null>(null);
  const [error, setError] = useState("");
  const [ocupado, setOcupado] = useState(false);

  async function calcular(event: FormEvent) {
    event.preventDefault();
    setError("");
    const invalido = errorPeriodo(desde, hasta);
    if (invalido) {
      setError(invalido);
      return;
    }
    setOcupado(true);
    try {
      const datos = await llamar<Plan>(
        `/indicadores/compensacion?desde=${encodeURIComponent(desde)}&hasta=${encodeURIComponent(hasta)}`,
        { cache: "no-cache" },
      );
      setPlan(datos);
    } catch (err) {
      setPlan(null);
      setError(err instanceof ApiError ? err.message : "No se pudo calcular el plan de compensación.");
    } finally {
      setOcupado(false);
    }
  }

  return (
    <section className="panel" aria-labelledby="titulo-compensacion">
      <h2 id="titulo-compensacion">Plan de compensación de carbono</h2>
      <p id="ayuda-compensacion" className="ayuda">
        Suma el CO₂ emitido del período con el mismo cálculo del tablero, estima los árboles
        necesarios con el factor de captura (RN-018) y sugiere proyectos locales. Si un factor no
        está ratificado, se muestra como pendiente y no se inventa la cifra. Hasta 31 días.
      </p>
      {error ? <Alerta id="alerta-compensacion">{error}</Alerta> : null}
      <form
        className="grilla"
        aria-labelledby="titulo-compensacion"
        aria-describedby="ayuda-compensacion"
        onSubmit={calcular}
        noValidate
      >
        <label htmlFor="compensacion-desde">
          Inicio del período{/*
          */}<input
            id="compensacion-desde"
            type="date"
            required
            value={desde}
            onChange={(event) => setDesde(event.target.value)}
          />
        </label>
        <label htmlFor="compensacion-hasta">
          Fin del período{/*
          */}<input
            id="compensacion-hasta"
            type="date"
            required
            value={hasta}
            onChange={(event) => setHasta(event.target.value)}
          />
        </label>
        <button type="submit" disabled={ocupado} aria-busy={ocupado}>
          {ocupado ? "Calculando…" : "Calcular plan de compensación"}
        </button>
      </form>
      <div aria-live="polite">
        {plan && !plan.calculable ? <output className="aviso">{plan.mensaje}</output> : null}
        {plan?.calculable ? (
          <div className="compensacion-resultado">
            <dl className="metricas" aria-label="Resultado del plan de compensación">
              <div className="panel metrica">
                <dt>CO₂ emitido</dt>
                <dd>{numero(plan.co2_emitido_kg, 3)} kg</dd>
              </div>
              <div className="panel metrica">
                <dt>Árboles necesarios</dt>
                <dd>
                  {plan.arboles_necesarios == null
                    ? "Pendiente"
                    : numero(plan.arboles_necesarios, 0)}
                </dd>
              </div>
              <div className="panel metrica">
                <dt>Costo estimado</dt>
                <dd>
                  {plan.costo_estimado_soles == null
                    ? "Pendiente"
                    : `S/ ${numero(plan.costo_estimado_soles, 2)}`}
                </dd>
              </div>
              <div className="panel metrica">
                <dt>Rutas del período</dt>
                <dd>
                  {plan.rutas} en {plan.dias_con_operacion}{" "}
                  {plan.dias_con_operacion === 1 ? "día" : "días"}
                </dd>
              </div>
            </dl>
            {plan.notas.map((nota) => (
              <p key={nota} className="ayuda">
                {nota}
              </p>
            ))}
            <h3 id="titulo-proyectos">Proyectos locales sugeridos</h3>
            <ul aria-labelledby="titulo-proyectos">
              {plan.proyectos.map((proyecto) => (
                <li key={proyecto.nombre}>{proyecto.nombre}</li>
              ))}
            </ul>
          </div>
        ) : null}
      </div>
    </section>
  );
}
