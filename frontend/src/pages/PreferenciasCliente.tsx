import { FormEvent, useEffect, useState } from "react";

import { ApiError } from "../api";
import { useAuth } from "../auth";
import { Alerta } from "../avisos";
import type { Cliente, PreferenciaCliente } from "../types";

export const MENSAJE_HORARIO =
  "La hora de inicio debe ser anterior a la hora de fin. Corrija el horario preferido.";

const vacio = { hora_inicio: "", hora_fin: "", punto_referencia: "", restricciones_acceso: "" };

function hora(valor: string | null): string {
  return valor ? valor.slice(0, 5) : "";
}

function comoFormulario(datos: PreferenciaCliente) {
  return {
    hora_inicio: hora(datos.hora_inicio),
    hora_fin: hora(datos.hora_fin),
    punto_referencia: datos.punto_referencia ?? "",
    restricciones_acceso: datos.restricciones_acceso ?? "",
  };
}

export function horarioContradictorio(inicio: string, fin: string): boolean {
  return Boolean(inicio && fin && inicio >= fin);
}

type Props = Readonly<{ clientes: Cliente[]; editable: boolean }>;

export function PreferenciasCliente({ clientes, editable }: Props) {
  const { llamar } = useAuth();
  const [idCliente, setIdCliente] = useState("");
  const [ficha, setFicha] = useState<PreferenciaCliente | null>(null);
  const [formulario, setFormulario] = useState(vacio);
  const [error, setError] = useState("");
  const [exito, setExito] = useState("");
  const [ocupado, setOcupado] = useState(false);
  const seleccionado = idCliente || clientes[0]?.id_cliente || "";
  const cliente = clientes.find((item) => item.id_cliente === seleccionado);

  useEffect(() => {
    if (!seleccionado) return;
    let vigente = true;
    setError("");
    setExito("");
    llamar<PreferenciaCliente>(`/clientes/${encodeURIComponent(seleccionado)}/preferencia`, {
      cache: "no-cache",
    })
      .then((datos) => {
        if (!vigente) return;
        setFicha(datos);
        setFormulario(datos?.registrada ? comoFormulario(datos) : vacio);
      })
      .catch((err: unknown) => {
        if (!vigente) return;
        setFicha(null);
        setFormulario(vacio);
        setError(err instanceof ApiError ? err.message : "No se pudo cargar la ficha del cliente.");
      });
    return () => {
      vigente = false;
    };
  }, [llamar, seleccionado]);

  function actualizar(campo: keyof typeof vacio, valor: string) {
    setFormulario((actual) => ({ ...actual, [campo]: valor }));
  }

  async function guardar(event: FormEvent) {
    event.preventDefault();
    setError("");
    setExito("");
    if (!formulario.hora_inicio || !formulario.hora_fin) {
      setError("Ingrese la hora de inicio y la hora de fin del horario preferido.");
      return;
    }
    if (horarioContradictorio(formulario.hora_inicio, formulario.hora_fin)) {
      setError(MENSAJE_HORARIO);
      return;
    }
    setOcupado(true);
    try {
      const datos = await llamar<PreferenciaCliente>(
        `/clientes/${encodeURIComponent(seleccionado)}/preferencia`,
        {
          method: "PUT",
          body: JSON.stringify({
            hora_inicio: formulario.hora_inicio,
            hora_fin: formulario.hora_fin,
            punto_referencia: formulario.punto_referencia || null,
            restricciones_acceso: formulario.restricciones_acceso || null,
          }),
        },
      );
      setFicha(datos);
      setFormulario(comoFormulario(datos));
      setExito(datos.mensaje ?? "Preferencia guardada.");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo guardar la preferencia.");
    } finally {
      setOcupado(false);
    }
  }

  const contradictorio = horarioContradictorio(formulario.hora_inicio, formulario.hora_fin);

  return (
    <section className="panel" aria-labelledby="titulo-preferencias">
      <h2 id="titulo-preferencias">Preferencias de entrega del cliente</h2>
      <p id="ayuda-preferencias" className="ayuda">
        Horario preferido, referencia y restricción de acceso de la bodega. El optimizador usa el
        horario como restricción suave: intenta llegar dentro de él sin dejar pedidos fuera. La
        ventana del pedido sigue siendo obligatoria.
      </p>
      {error ? <Alerta id="alerta-preferencias">{error}</Alerta> : null}
      {exito ? (
        <output id="exito-preferencias" className="exito" aria-atomic="true">
          {exito}
        </output>
      ) : null}
      <label htmlFor="pref-cliente">
        Cliente de la ficha{/*
        */}<select
          id="pref-cliente"
          value={seleccionado}
          onChange={(event) => setIdCliente(event.target.value)}
        >
          {clientes.map((item) => (
            <option key={item.id_cliente} value={item.id_cliente}>
              {item.nombre}
              {item.consentimiento_datos ? " (con consentimiento)" : " (sin consentimiento)"}
            </option>
          ))}
        </select>
      </label>
      {ficha && !ficha.registrada ? (
        <p className="muted">Este cliente aún no tiene preferencias de entrega registradas.</p>
      ) : null}
      {editable ? (
        <form
          className="grilla"
          aria-labelledby="titulo-preferencias"
          aria-describedby="ayuda-preferencias"
          onSubmit={guardar}
          noValidate
        >
          <label htmlFor="pref-hora-inicio">
            Hora preferida desde{/*
            */}<input
              id="pref-hora-inicio"
              type="time"
              required
              value={formulario.hora_inicio}
              aria-invalid={contradictorio}
              onChange={(event) => actualizar("hora_inicio", event.target.value)}
            />
          </label>
          <label htmlFor="pref-hora-fin">
            Hora preferida hasta{/*
            */}<input
              id="pref-hora-fin"
              type="time"
              required
              value={formulario.hora_fin}
              aria-invalid={contradictorio}
              onChange={(event) => actualizar("hora_fin", event.target.value)}
            />
          </label>
          <label htmlFor="pref-referencia">
            Referencia habitual{/*
            */}<input
              id="pref-referencia"
              maxLength={255}
              placeholder="frente a la bodega El Ahorro"
              value={formulario.punto_referencia}
              onChange={(event) => actualizar("punto_referencia", event.target.value)}
            />
          </label>
          <label htmlFor="pref-restricciones">
            Restricción de acceso{/*
            */}<textarea
              id="pref-restricciones"
              maxLength={500}
              placeholder="Calle angosta: solo moto o camioneta pequeña"
              value={formulario.restricciones_acceso}
              onChange={(event) => actualizar("restricciones_acceso", event.target.value)}
            />
          </label>
          <button type="submit" disabled={ocupado || !seleccionado}>
            {ocupado ? "Guardando…" : "Guardar preferencias"}
          </button>
        </form>
      ) : ficha?.registrada ? (
        <dl className="metricas preferencia-lectura">
          <div className="metrica">
            <dt>Horario preferido</dt>
            <dd>
              {hora(ficha.hora_inicio)} – {hora(ficha.hora_fin)}
            </dd>
          </div>
          <div className="metrica">
            <dt>Referencia habitual</dt>
            <dd>{ficha.punto_referencia ?? "—"}</dd>
          </div>
          <div className="metrica">
            <dt>Restricción de acceso</dt>
            <dd>{ficha.restricciones_acceso ?? "—"}</dd>
          </div>
        </dl>
      ) : null}
      {editable && cliente && !cliente.consentimiento_datos ? (
        <output className="aviso">
          Este cliente no tiene consentimiento. El sistema no guardará sus preferencias (Ley N.º
          29733).
        </output>
      ) : null}
    </section>
  );
}
