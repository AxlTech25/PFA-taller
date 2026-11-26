import { FormEvent, KeyboardEvent, useEffect, useId, useRef, useState } from "react";

import { ApiError } from "../api";
import { useAuth } from "../auth";
import { Alerta } from "../avisos";
import type { MotivoReoptimizacion, PedidoDisponible, Reoptimizacion, Ruta } from "../types";

export const ESTADOS_REOPTIMIZABLES = ["CONFIRMADA", "EN_EJECUCION"];
const RESUELTAS = ["ENTREGADO", "FALLIDO"];

export const MOTIVOS: { valor: MotivoReoptimizacion; texto: string }[] = [
  { valor: "NUEVO_PEDIDO", texto: "Pedido nuevo" },
  { valor: "CANCELACION", texto: "Pedido cancelado" },
  { valor: "PARADA_FALLIDA", texto: "Entrega fallida" },
  { valor: "ACCIDENTE_TRANSITO", texto: "Vía o zona bloqueada" },
  { valor: "CONGESTION", texto: "Congestión" },
];

export function paradasPendientes(ruta: Ruta) {
  return ruta.paradas.filter((parada) => !RESUELTAS.includes(parada.estado_entrega ?? ""));
}

function alternar(lista: string[], id: string): string[] {
  return lista.includes(id) ? lista.filter((valor) => valor !== id) : [...lista, id];
}

type Props = Readonly<{
  ruta: Ruta;
  nombre: string;
  onListo: (resultado: Reoptimizacion) => Promise<void> | void;
}>;

export function ReoptimizarRuta({ ruta, nombre, onListo }: Props) {
  const { llamar } = useAuth();
  const base = useId();
  const idPanel = `${base}-panel`;
  const idError = `${base}-error`;
  const idAyuda = `${base}-ayuda`;
  const boton = useRef<HTMLButtonElement>(null);
  const motivoRef = useRef<HTMLSelectElement>(null);
  const [abierto, setAbierto] = useState(false);
  const [motivo, setMotivo] = useState<MotivoReoptimizacion>("NUEVO_PEDIDO");
  const [descripcion, setDescripcion] = useState("");
  const [agregar, setAgregar] = useState<string[]>([]);
  const [cancelar, setCancelar] = useState<string[]>([]);
  const [disponibles, setDisponibles] = useState<PedidoDisponible[] | null>(null);
  const [error, setError] = useState("");
  const [ocupado, setOcupado] = useState(false);
  const [resultado, setResultado] = useState<Reoptimizacion | null>(null);
  const pendientes = paradasPendientes(ruta);

  useEffect(() => {
    if (!abierto) return;
    motivoRef.current?.focus();
    let vigente = true;
    setDisponibles(null);
    llamar<PedidoDisponible[]>(`/rutas/${ruta.id_ruta}/pedidos-disponibles`, { cache: "no-cache" })
      .then((lista) => {
        if (vigente) setDisponibles(Array.isArray(lista) ? lista : []);
      })
      .catch(() => {
        if (vigente) setDisponibles([]);
      });
    return () => {
      vigente = false;
    };
  }, [abierto, llamar, ruta.id_ruta]);

  function cerrar() {
    setAbierto(false);
    setError("");
    boton.current?.focus();
  }

  function teclado(event: KeyboardEvent<HTMLElement>) {
    if (event.key === "Escape" && !ocupado) {
      event.stopPropagation();
      cerrar();
    }
  }

  async function enviar(event: FormEvent) {
    event.preventDefault();
    setError("");
    if (motivo === "NUEVO_PEDIDO" && agregar.length === 0) {
      setError("Marque al menos un pedido nuevo para agregar.");
      return;
    }
    if (motivo === "CANCELACION" && cancelar.length === 0) {
      setError("Marque al menos una parada pendiente para cancelar.");
      return;
    }
    setOcupado(true);
    try {
      const respuesta = await llamar<Reoptimizacion>(`/rutas/${ruta.id_ruta}/reoptimizar`, {
        method: "POST",
        body: JSON.stringify({
          motivo,
          descripcion: descripcion.trim() || null,
          agregar,
          cancelar,
        }),
      });
      setResultado(respuesta);
      setAgregar([]);
      setCancelar([]);
      setDescripcion("");
      setAbierto(false);
      await onListo(respuesta);
      boton.current?.focus();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo re-optimizar la ruta.");
    } finally {
      setOcupado(false);
    }
  }

  return (
    <div className="reoptimizar">
      <button
        ref={boton}
        type="button"
        className="secundario"
        aria-expanded={abierto}
        aria-controls={idPanel}
        aria-label={`Re-optimizar paradas pendientes de ${nombre}`}
        onClick={() => (abierto ? cerrar() : setAbierto(true))}
      >
        Re-optimizar paradas pendientes
      </button>
      {resultado ? (
        <output className="exito" aria-atomic="true">
          {resultado.mensaje} Tiempo medido: {resultado.segundos.toFixed(2)} s (tope{" "}
          {resultado.presupuesto_s} s). Paradas entregadas o fallidas conservadas:{" "}
          {resultado.paradas_fijas}. Paradas reordenadas: {resultado.paradas_reordenadas}.
        </output>
      ) : null}
      {abierto ? (
        <form
          id={idPanel}
          className="panel"
          aria-label={`Re-optimizar ${nombre}`}
          aria-describedby={idAyuda}
          onSubmit={enviar}
          onKeyDown={teclado}
          noValidate
        >
          <p id={idAyuda} className="ayuda">
            Solo se recalculan las paradas pendientes de esta ruta. Las entregadas o fallidas
            conservan su orden. El cálculo se corta a los 30 s como máximo y nunca atraviesa una
            reserva ecológica (RN-013). Escape cierra el formulario.
          </p>
          {error ? <Alerta id={idError}>{error}</Alerta> : null}
          <div className="grilla">
            <label htmlFor={`${base}-motivo`}>
              Motivo del cambio{/*
              */}<select
                ref={motivoRef}
                id={`${base}-motivo`}
                value={motivo}
                onChange={(event) => setMotivo(event.target.value as MotivoReoptimizacion)}
              >
                {MOTIVOS.map((opcion) => (
                  <option key={opcion.valor} value={opcion.valor}>
                    {opcion.texto}
                  </option>
                ))}
              </select>
            </label>
            <label htmlFor={`${base}-descripcion`}>
              Detalle (opcional){/*
              */}<input
                id={`${base}-descripcion`}
                type="text"
                maxLength={255}
                autoComplete="off"
                value={descripcion}
                onChange={(event) => setDescripcion(event.target.value)}
              />
            </label>
          </div>
          <fieldset className="opciones">
            <legend>Pedidos nuevos para agregar</legend>
            {disponibles === null ? (
              <p className="muted">Cargando pedidos pendientes…</p>
            ) : disponibles.length === 0 ? (
              <p className="muted">No hay pedidos pendientes para la fecha de esta ruta.</p>
            ) : (
              disponibles.map((pedido) => (
                <label key={pedido.id_pedido} className="opcion">
                  <input
                    type="checkbox"
                    checked={agregar.includes(pedido.id_pedido)}
                    onChange={() => setAgregar((lista) => alternar(lista, pedido.id_pedido))}
                  />
                  <span>
                    {pedido.nombre_cliente ?? "Cliente"} · {pedido.peso_kg} kg
                    {pedido.punto_referencia ? ` · ${pedido.punto_referencia}` : ""}
                  </span>
                </label>
              ))
            )}
          </fieldset>
          <fieldset className="opciones">
            <legend>Paradas pendientes para cancelar</legend>
            {pendientes.length === 0 ? (
              <p className="muted">No quedan paradas pendientes.</p>
            ) : (
              pendientes.map((parada) => (
                <label key={parada.id_pedido} className="opcion">
                  <input
                    type="checkbox"
                    checked={cancelar.includes(parada.id_pedido)}
                    onChange={() => setCancelar((lista) => alternar(lista, parada.id_pedido))}
                  />
                  <span>
                    Parada {parada.secuencia} · {parada.nombre_cliente ?? "Cliente"}
                  </span>
                </label>
              ))
            )}
          </fieldset>
          <div className="fila-acciones">
            <button type="submit" disabled={ocupado}>
              {ocupado ? "Re-optimizando…" : "Re-optimizar ahora"}
            </button>
            <button type="button" className="secundario" disabled={ocupado} onClick={cerrar}>
              Cerrar
            </button>
          </div>
        </form>
      ) : null}
    </div>
  );
}
