import { FormEvent, useState } from "react";

import { ApiError } from "../api";
import { useAuth } from "../auth";
import { Alerta } from "../avisos";
import { fechaHoy } from "../fechas";
import { errorPeriodo } from "../reporte";
import { numero } from "../numeros";
import type { ConversionGnv as Gnv, PlanAnual, PlanCompensacion as Plan } from "../types";
import { ConversionGnv } from "./ConversionGnv";
import { MetaCarbonoNeutral } from "./MetaCarbonoNeutral";

export function PlanCompensacion() {
  const { llamar } = useAuth();
  const [desde, setDesde] = useState(fechaHoy);
  const [hasta, setHasta] = useState(fechaHoy);
  const [plan, setPlan] = useState<Plan | null>(null);
  const [anual, setAnual] = useState<PlanAnual | null>(null);
  const [gnv, setGnv] = useState<Gnv | null>(null);
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
      const periodo = `desde=${encodeURIComponent(desde)}&hasta=${encodeURIComponent(hasta)}`;
      const [datos, proyeccion, conversion] = await Promise.all([
        llamar<Plan>(`/indicadores/compensacion?${periodo}`, { cache: "no-cache" }),
        llamar<PlanAnual>(`/indicadores/compensacion/anual?${periodo}`, { cache: "no-cache" }),
        llamar<Gnv>(`/indicadores/gnv?${periodo}`, { cache: "no-cache" }),
      ]);
      setPlan(datos);
      setAnual(proyeccion);
      setGnv(conversion);
    } catch (err) {
      setPlan(null);
      setAnual(null);
      setGnv(null);
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
        necesarios con el factor de captura (RN-018) y sugiere proyectos locales. También proyecta
        el año, propone el plan para ser carbono neutral en 3 años y evalúa el ROI de convertir la
        flota a GNV. Si un dato no está ratificado, se muestra como pendiente y no se inventa la
        cifra. Hasta 31 días.
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
                <dt>Factor de captura por árbol</dt>
                <dd>
                  {plan.factor_captura_arbol_kg == null
                    ? "Pendiente"
                    : `${numero(plan.factor_captura_arbol_kg, 0)} kg/árbol/año`}
                </dd>
              </div>
              <div className="panel metrica">
                <dt>Costo por árbol</dt>
                <dd>
                  {plan.costo_por_arbol_soles == null
                    ? "Pendiente"
                    : `S/ ${numero(plan.costo_por_arbol_soles, 2)}`}
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
            {anual ? <MetaCarbonoNeutral anual={anual} /> : null}
            {gnv ? <ConversionGnv gnv={gnv} /> : null}
          </div>
        ) : null}
      </div>
    </section>
  );
}
