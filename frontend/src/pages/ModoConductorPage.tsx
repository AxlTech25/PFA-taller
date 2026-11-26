import {
  lazy,
  Suspense,
  useCallback,
  useEffect,
  useRef,
  useState,
  type FormEvent,
  type KeyboardEvent,
  type RefObject,
} from "react";

import { ApiError } from "../api";
import { useAuth } from "../auth";
import { Alerta } from "../avisos";
import {
  MOTIVO_MAXIMO,
  prepararConfirmacionEntrega,
  puedeConfirmar,
  rutaConfirmacion,
  type ConfirmacionEntregaOut,
  type ResultadoEntrega,
} from "../entrega";
import { fechaVisible, horaVisible } from "../fechas";
import { etiqueta } from "../permissions";
import type { JornadaModo, ParadaModo } from "../types";

const ModoMapa = lazy(() => import("./ModoMapa").then((modulo) => ({ default: modulo.ModoMapa })));

const TEXTO_RESULTADO: Record<ResultadoEntrega, string> = {
  ENTREGADO: "entregada",
  FALLIDO: "fallida",
};

function nombreConfirmacion(parada: ParadaModo): string {
  return `Confirmar entrega de la parada ${parada.secuencia}, ${parada.cliente}`;
}

type Formulario = {
  idDetalle: string;
  resultado: ResultadoEntrega;
  motivo: string;
  error: string;
  guardando: boolean;
};

export function ModoConductorPage() {
  const { llamar } = useAuth();
  const [jornada, setJornada] = useState<JornadaModo | null>(null);
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(true);
  const [formulario, setFormulario] = useState<Formulario | null>(null);
  const [aviso, setAviso] = useState("");
  const [errorGuardar, setErrorGuardar] = useState("");
  const [mapa, setMapa] = useState(false);
  const avisoRef = useRef<HTMLOutputElement>(null);
  const motivoRef = useRef<HTMLTextAreaElement>(null);
  const enfocarAviso = useRef(false);

  const cargar = useCallback(
    (vigente: () => boolean) =>
      // no-cache: el navegador revalida con el ETag (304 si nada cambió) y no muestra
      // durante 30 s una parada ya confirmada como pendiente.
      llamar<JornadaModo>("/modo/jornada", { cache: "no-cache" })
        .then((datos) => {
          if (vigente()) setJornada(datos);
        })
        .catch((err: unknown) => {
          if (!vigente()) return;
          setError(err instanceof ApiError ? err.message : "No se pudo cargar su ruta.");
        })
        .finally(() => {
          if (vigente()) setCargando(false);
        }),
    [llamar],
  );

  useEffect(() => {
    document.title = "Modo conductor · EcoLogística Lima";
    let vigente = true;
    void cargar(() => vigente);
    return () => {
      vigente = false;
    };
  }, [cargar]);

  useEffect(() => {
    if (aviso && enfocarAviso.current) {
      enfocarAviso.current = false;
      avisoRef.current?.focus();
    }
  }, [aviso]);

  function abrir(parada: ParadaModo) {
    setErrorGuardar("");
    setFormulario((actual) =>
      actual?.idDetalle === parada.id_detalle
        ? null
        : { idDetalle: parada.id_detalle, resultado: "ENTREGADO", motivo: "", error: "", guardando: false },
    );
  }

  function cerrar(parada: ParadaModo) {
    setFormulario(null);
    setErrorGuardar("");
    document.getElementById(`confirmar-${parada.id_detalle}`)?.focus();
  }

  function teclaParada(evento: KeyboardEvent<HTMLElement>, parada: ParadaModo) {
    if (evento.key === "Escape" && formulario?.idDetalle === parada.id_detalle) {
      evento.preventDefault();
      cerrar(parada);
    }
  }

  async function guardar(evento: FormEvent<HTMLFormElement>, parada: ParadaModo) {
    evento.preventDefault();
    if (!formulario || formulario.guardando) return;
    const preparado = prepararConfirmacionEntrega(formulario.resultado, formulario.motivo);
    if ("error" in preparado) {
      setFormulario({ ...formulario, error: preparado.error });
      motivoRef.current?.focus();
      return;
    }
    setFormulario({ ...formulario, error: "", guardando: true });
    setErrorGuardar("");
    try {
      const respuesta = await llamar<ConfirmacionEntregaOut>(rutaConfirmacion(parada.id_detalle), {
        method: "POST",
        body: JSON.stringify(preparado),
      });
      setJornada((actual) =>
        actual
          ? {
              ...actual,
              paradas: actual.paradas.map((item) =>
                item.id_detalle === parada.id_detalle
                  ? { ...item, estado_entrega: respuesta.estado_entrega, motivo_fallo: respuesta.motivo_fallo ?? null }
                  : item,
              ),
            }
          : actual,
      );
      setFormulario(null);
      enfocarAviso.current = true;
      setAviso(
        `Parada ${parada.secuencia}, ${parada.cliente}: registrada como ${TEXTO_RESULTADO[respuesta.estado_entrega]}.`,
      );
    } catch (err: unknown) {
      setErrorGuardar(err instanceof ApiError ? err.message : "No se pudo guardar el resultado.");
      if (err instanceof ApiError && err.status === 409) {
        // La parada ya tenía resultado: se cierra el formulario y se relee la lista.
        setFormulario(null);
        void cargar(() => true);
        return;
      }
      setFormulario((actual) => (actual ? { ...actual, guardando: false } : actual));
    }
  }

  const siguiente = jornada?.paradas.find((parada) => puedeConfirmar(parada.estado_entrega));

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
            Confirmar entrega registra la parada como entregada o fallida. Si falla, indique el
            motivo.
          </p>
          {errorGuardar ? <Alerta id="alerta-entrega">{errorGuardar}</Alerta> : null}
          <output ref={avisoRef} className={aviso ? "exito" : undefined} tabIndex={-1} aria-atomic="true">
            {aviso}
          </output>
          <ol className="lista-paradas">
            {jornada.paradas.map((parada) => {
              const titulo = `parada-${parada.id_detalle}`;
              return (
                <li key={parada.id_detalle}>
                  <article
                    className="parada-conductor"
                    aria-labelledby={titulo}
                    onKeyDown={(evento) => teclaParada(evento, parada)}
                  >
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
                    {parada.estado_entrega === "FALLIDO" && parada.motivo_fallo ? (
                      <p>Motivo: {parada.motivo_fallo}</p>
                    ) : null}
                    {puedeConfirmar(parada.estado_entrega) ? (
                      <button
                        id={`confirmar-${parada.id_detalle}`}
                        type="button"
                        aria-expanded={formulario?.idDetalle === parada.id_detalle}
                        aria-controls={`form-${parada.id_detalle}`}
                        aria-describedby="nota-confirmacion"
                        aria-label={nombreConfirmacion(parada)}
                        onClick={() => abrir(parada)}
                      >
                        Confirmar entrega
                      </button>
                    ) : null}
                    {formulario?.idDetalle === parada.id_detalle ? (
                      <FormularioEntrega
                        parada={parada}
                        formulario={formulario}
                        motivoRef={motivoRef}
                        onCambiar={(cambios) => setFormulario({ ...formulario, ...cambios })}
                        onGuardar={(evento) => void guardar(evento, parada)}
                        onCancelar={() => cerrar(parada)}
                      />
                    ) : null}
                  </article>
                </li>
              );
            })}
          </ol>
          <p id="nota-mapa" className="ayuda">
            El mapa es opcional. La lista de paradas no lo espera y no se descarga hasta abrirlo.
          </p>
          <button type="button" aria-describedby="nota-mapa" onClick={() => setMapa(true)}>
            Ver mapa
          </button>
          {mapa ? (
            <Suspense fallback={<p role="status">Cargando mapa…</p>}>
              <ModoMapa />
            </Suspense>
          ) : null}
        </section>
      ) : null}
    </>
  );
}

type PropsFormulario = {
  parada: ParadaModo;
  formulario: Formulario;
  motivoRef: RefObject<HTMLTextAreaElement>;
  onCambiar: (cambios: Partial<Formulario>) => void;
  onGuardar: (evento: FormEvent<HTMLFormElement>) => void;
  onCancelar: () => void;
};

function FormularioEntrega({
  parada,
  formulario,
  motivoRef,
  onCambiar,
  onGuardar,
  onCancelar,
}: Readonly<PropsFormulario>) {
  const base = parada.id_detalle;
  const errorId = `error-motivo-${base}`;
  const ayudaId = `ayuda-motivo-${base}`;
  return (
    <form
      id={`form-${base}`}
      className="form-entrega"
      noValidate
      aria-label={`Resultado de la parada ${parada.secuencia}`}
      onSubmit={onGuardar}
    >
      <fieldset>
        <legend>Resultado de la parada {parada.secuencia}</legend>
        {(["ENTREGADO", "FALLIDO"] as const).map((valor) => (
          <label key={valor} className="opcion-entrega">
            <input
              type="radio"
              name={`resultado-${base}`}
              value={valor}
              checked={formulario.resultado === valor}
              onChange={() => onCambiar({ resultado: valor, error: "" })}
            />
            {valor === "ENTREGADO" ? "Entregado" : "Fallido"}
          </label>
        ))}
      </fieldset>
      {formulario.resultado === "FALLIDO" ? (
        <label htmlFor={`motivo-${base}`}>
          Motivo del fallo (obligatorio)
          <textarea
            ref={motivoRef}
            id={`motivo-${base}`}
            required
            aria-required="true"
            maxLength={MOTIVO_MAXIMO}
            rows={3}
            value={formulario.motivo}
            aria-invalid={formulario.error ? true : undefined}
            aria-describedby={formulario.error ? `${errorId} ${ayudaId}` : ayudaId}
            onChange={(evento) => onCambiar({ motivo: evento.target.value, error: "" })}
          />
        </label>
      ) : null}
      {formulario.resultado === "FALLIDO" ? (
        <p id={ayudaId} className="ayuda">
          Por ejemplo: cliente ausente o dirección cerrada. Máximo {MOTIVO_MAXIMO} caracteres.
        </p>
      ) : null}
      {formulario.error ? (
        <p id={errorId} className="alerta">
          {formulario.error}
        </p>
      ) : null}
      <div className="acciones-entrega">
        <button type="submit" disabled={formulario.guardando}>
          {formulario.guardando ? "Guardando…" : "Guardar resultado"}
        </button>
        <button type="button" className="secundario" onClick={onCancelar}>
          Cancelar
        </button>
      </div>
    </form>
  );
}
