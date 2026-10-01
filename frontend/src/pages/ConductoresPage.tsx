import { FormEvent, useEffect, useState } from "react";

import { ApiError } from "../api";
import { useAuth } from "../auth";
import { etiqueta, puedeRegistrarConductor } from "../permissions";
import type { Conductor } from "../types";

const vacio = {
  nombre: "",
  dni: "",
  licencia_categoria: "A-IIIb",
  anios_experiencia: "0",
  disponibilidad_inicio: "06:00",
  disponibilidad_fin: "14:00",
  lat_punto_partida: "-12.0100",
  lon_punto_partida: "-76.9800",
};

export function ConductoresPage() {
  const { llamar, sesion } = useAuth();
  const registrar = sesion ? puedeRegistrarConductor(sesion.rol) : false;
  const [conductores, setConductores] = useState<Conductor[]>([]);
  const [formulario, setFormulario] = useState(vacio);
  const [error, setError] = useState("");
  const [exito, setExito] = useState("");

  useEffect(() => {
    document.title = "Conductores · EcoLogística Lima";
    llamar<Conductor[]>("/conductores")
      .then(setConductores)
      .catch((err: unknown) =>
        setError(err instanceof ApiError ? err.message : "No se pudo cargar los conductores."),
      );
  }, [llamar]);

  function actualizarCampo(campo: string, valor: string) {
    setFormulario((actual) => ({ ...actual, [campo]: valor }));
  }

  async function enviar(event: FormEvent) {
    event.preventDefault();
    setError("");
    setExito("");
    try {
      const creado = await llamar<Conductor>("/conductores", {
        method: "POST",
        body: JSON.stringify({
          nombre: formulario.nombre,
          dni: formulario.dni,
          licencia_categoria: formulario.licencia_categoria,
          anios_experiencia: Number(formulario.anios_experiencia),
          disponibilidad_inicio: formulario.disponibilidad_inicio,
          disponibilidad_fin: formulario.disponibilidad_fin,
          lat_punto_partida: Number(formulario.lat_punto_partida),
          lon_punto_partida: Number(formulario.lon_punto_partida),
        }),
      });
      setConductores((actual) =>
        [...actual, creado].sort((a, b) => a.nombre.localeCompare(b.nombre)),
      );
      setFormulario(vacio);
      setExito(creado.mensaje ?? "Conductor registrado correctamente");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo registrar el conductor.");
    }
  }

  return (
    <>
      <header>
        <h1>Conductores</h1>
        <p className="ayuda">
          Registre DNI, licencia, horario de disponibilidad y el punto de partida real.
        </p>
      </header>
      {error ? (
        <p className="alerta" role="alert">
          {error}
        </p>
      ) : null}
      {exito ? (
        <p className="exito" role="status">
          {exito}
        </p>
      ) : null}
      {registrar ? (
        <section className="panel">
          <h2>Registrar conductor</h2>
          <form className="grilla" onSubmit={enviar}>
            <label htmlFor="nombre">
              Nombre
              <input
                id="nombre"
                required
                maxLength={150}
                value={formulario.nombre}
                onChange={(event) => actualizarCampo("nombre", event.target.value)}
              />
            </label>
            <label htmlFor="dni">
              DNI
              <input
                id="dni"
                required
                inputMode="numeric"
                pattern="\d{8}"
                maxLength={8}
                value={formulario.dni}
                onChange={(event) => actualizarCampo("dni", event.target.value)}
              />
            </label>
            <label htmlFor="licencia_categoria">
              Licencia
              <input
                id="licencia_categoria"
                required
                maxLength={10}
                value={formulario.licencia_categoria}
                onChange={(event) => actualizarCampo("licencia_categoria", event.target.value)}
              />
            </label>
            <label htmlFor="anios_experiencia">
              Años de experiencia
              <input
                id="anios_experiencia"
                type="number"
                min={0}
                required
                value={formulario.anios_experiencia}
                onChange={(event) => actualizarCampo("anios_experiencia", event.target.value)}
              />
            </label>
            <label htmlFor="disponibilidad_inicio">
              Disponibilidad desde
              <input
                id="disponibilidad_inicio"
                type="time"
                required
                value={formulario.disponibilidad_inicio}
                onChange={(event) => actualizarCampo("disponibilidad_inicio", event.target.value)}
              />
            </label>
            <label htmlFor="disponibilidad_fin">
              Disponibilidad hasta
              <input
                id="disponibilidad_fin"
                type="time"
                required
                value={formulario.disponibilidad_fin}
                onChange={(event) => actualizarCampo("disponibilidad_fin", event.target.value)}
              />
            </label>
            <label htmlFor="lat_punto_partida">
              Latitud de partida
              <input
                id="lat_punto_partida"
                type="number"
                step="0.0000001"
                required
                value={formulario.lat_punto_partida}
                onChange={(event) => actualizarCampo("lat_punto_partida", event.target.value)}
              />
            </label>
            <label htmlFor="lon_punto_partida">
              Longitud de partida
              <input
                id="lon_punto_partida"
                type="number"
                step="0.0000001"
                required
                value={formulario.lon_punto_partida}
                onChange={(event) => actualizarCampo("lon_punto_partida", event.target.value)}
              />
            </label>
            <button type="submit">Registrar conductor</button>
          </form>
        </section>
      ) : null}
      <section className="panel">
        <h2>Conductores registrados</h2>
        {conductores.length === 0 ? (
          <p>No hay conductores registrados.</p>
        ) : (
          <div className="tabla-contenedor">
            <table>
              <caption className="muted">Personal disponible para el reparto</caption>
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th>DNI</th>
                  <th>Licencia</th>
                  <th>Horario</th>
                  <th>Partida</th>
                  <th>Estado</th>
                </tr>
              </thead>
              <tbody>
                {conductores.map((conductor) => (
                  <tr key={conductor.id_conductor}>
                    <td>{conductor.nombre}</td>
                    <td>{conductor.dni ?? "—"}</td>
                    <td>{conductor.licencia_categoria}</td>
                    <td>
                      {conductor.disponibilidad_inicio.slice(0, 5)} –{" "}
                      {conductor.disponibilidad_fin.slice(0, 5)}
                    </td>
                    <td>
                      {conductor.lat_punto_partida == null
                        ? "—"
                        : `${conductor.lat_punto_partida}, ${conductor.lon_punto_partida}`}
                    </td>
                    <td>
                      <span className={`insignia ${conductor.estado}`}>
                        {etiqueta(conductor.estado)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </>
  );
}
