import { useEffect, useState } from "react";

import { ApiError } from "../api";
import { useAuth } from "../auth";
import { Alerta } from "../avisos";
import { prepararConfirmacionEntrega } from "../entrega";
import { fechaVisible, horaVisible } from "../fechas";
import { etiqueta } from "../permissions";
import type { JornadaModo, ParadaModo } from "../types";

type Pendiente = { idDetalle: string; texto: string };

function nombreConfirmacion(parada: ParadaModo): string {
  return `Confirmar entrega de la parada ${parada.secuencia}, ${parada.cliente}`;
}

function puedeConfirmar(parada: ParadaModo): boolean {
  return parada.estado_entrega === "PENDIENTE" || parada.estado_entrega === "REPROGRAMADO";
}

export function ModoConductorPage() {
  const { llamar } = useAuth();
  const [jornada, setJornada] = useState<JornadaModo | null>(null);
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(true);
  const [pendiente, setPendiente] = useState<Pendiente | null>(null);

  useEffect(() => {
    document.title = "Modo conductor · EcoLogística Lima";
    let vigente = true;
    llamar<JornadaModo>("/modo/jornada")
      .then((datos) => {
        if (vigente) setJornada(datos);
      })
      .catch((err: unknown) => {
        if (!vigente) return;
        setError(err instanceof ApiError ? err.message : "No se pudo cargar su ruta.");
      })
      .finally(() => {
        if (vigente) setCargando(false);
      });
    return () => {
      vigente = false;
    };
  }, [llamar]);

  function confirmar(parada: ParadaModo) {
    const preparado = prepararConfirmacionEntrega(parada.id_detalle);
    setPendiente({
      idDetalle: preparado.idDetalle,
      texto: `Parada ${parada.secuencia}, ${parada.cliente}: ${preparado.mensaje}`,
    });
  }

  const siguiente = jornada?.paradas.find((parada) => puedeConfirmar(parada));

  return (
    <>
      <header>
        <h1>Modo conductor</h1>
        <p id="ayuda-modo" className="ayuda">
          Su ruta confirmada de hoy: la secuencia de paradas, la hora estimada y las alertas.
          No incluye indicadores de gerencia.
        </p>
      </header>
      {error ? <Alerta id="alerta-modo">{error}</Alerta> : null}
      {cargando ? (
        <p className="jornada" role="status">
          Cargando su ruta…
        </p>
      ) : null}
      {jornada && !jornada.hay_ruta ? (
        <section className="panel jornada" aria-labelledby="titulo-jornada">
          <h2 id="titulo-jornada">Su jornada</h2>
          <output className="aviso">{jornada.mensaje ?? "No tiene una ruta confirmada para hoy."}</output>
        </section>
      ) : null}
      {jornada?.hay_ruta ? (
        <section className="panel jornada" aria-labelledby="titulo-jornada">
          <h2 id="titulo-jornada">Ruta del {fechaVisible(jornada.fecha)}</h2>
          {jornada.placa ? <p>Unidad {jornada.placa}</p> : null}
          <section aria-labelledby="titulo-alertas">
            <h3 id="titulo-alertas">Alertas</h3>
            {jornada.alertas.length === 0 ? <p>No hay alertas para esta ruta.</p> : null}
            {jornada.alertas.length > 0 ? (
              <ul className="lista-alertas">
                {jornada.alertas.map((alerta) => (
                  <li key={`${alerta.codigo}-${alerta.secuencia ?? "ruta"}-${alerta.texto}`}>
                    <p className="aviso">{alerta.texto}</p>
                  </li>
                ))}
              </ul>
            ) : null}
          </section>
          <p id="nota-confirmacion" className="ayuda">
            Confirmar entrega no guarda el resultado. El registro de entregado o fallido llega en
            una versión siguiente.
          </p>
          {pendiente ? <output className="aviso">{pendiente.texto}</output> : null}
          <ol className="lista-paradas">
            {jornada.paradas.map((parada) => {
              const titulo = `parada-${parada.id_detalle}`;
              return (
                <li key={parada.id_detalle}>
                  <article className="parada-conductor" aria-labelledby={titulo}>
                    <div className="parada-cabecera">
                      <span className="parada-numero" aria-hidden="true">
                        {parada.secuencia}
                      </span>
                      <h3 id={titulo}>
                        Parada {parada.secuencia}. {parada.cliente}
                        {siguiente?.id_detalle === parada.id_detalle ? (
                          <span className="insignia PENDIENTE"> Siguiente entrega</span>
                        ) : null}
                      </h3>
                    </div>
                    <p className="parada-hora">
                      Llegada estimada:{" "}
                      <time dateTime={parada.eta ?? undefined}>{horaVisible(parada.eta)}</time>
                    </p>
                    {parada.direccion ? <p>{parada.direccion}</p> : null}
                    {parada.punto_referencia ? <p>Referencia: {parada.punto_referencia}</p> : null}
                    <p>
                      Semáforo{" "}
                      <span className={`insignia semaforo ${parada.nivel_congestion ?? ""}`}>
                        {etiqueta(parada.nivel_congestion ?? "")}
                      </span>
                      {" · "}
                      <span className={`insignia ${parada.estado_entrega}`}>
                        {etiqueta(parada.estado_entrega)}
                      </span>
                    </p>
                    {puedeConfirmar(parada) ? (
                      <button
                        type="button"
                        aria-pressed={pendiente?.idDetalle === parada.id_detalle}
                        aria-describedby="nota-confirmacion"
                        aria-label={nombreConfirmacion(parada)}
                        onClick={() => confirmar(parada)}
                      >
                        Confirmar entrega
                      </button>
                    ) : null}
                  </article>
                </li>
              );
            })}
          </ol>
        </section>
      ) : null}
    </>
  );
}
