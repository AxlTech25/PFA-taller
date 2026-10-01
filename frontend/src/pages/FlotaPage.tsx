import { FormEvent, useEffect, useState } from "react";

import { ApiError } from "../api";
import { useAuth } from "../auth";
import { etiqueta, puedeEditarFlota, puedeRegistrarFlota } from "../permissions";
import type { Vehiculo } from "../types";

const TIPOS = [
  { valor: "CAMIONETA", etiqueta: "Camioneta" },
  { valor: "FURGON", etiqueta: "Furgón" },
  { valor: "MOTO", etiqueta: "Moto" },
] as const;

const ESTADOS = [
  { valor: "ACTIVO", etiqueta: "Activo" },
  { valor: "MANTENIMIENTO", etiqueta: "Mantenimiento" },
  { valor: "INACTIVO", etiqueta: "Inactivo" },
] as const;

const vacio = {
  placa: "",
  tipo: "CAMIONETA",
  capacidad_kg: "",
  capacidad_m3: "",
  consumo_km_l: "",
  factor_emision_co2: "",
  anio_fabricacion: String(new Date().getFullYear()),
};

type Edicion = { estado: string; factor: string };

export function FlotaPage() {
  const { llamar, sesion } = useAuth();
  const registrar = sesion ? puedeRegistrarFlota(sesion.rol) : false;
  const editar = sesion ? puedeEditarFlota(sesion.rol) : false;
  const [vehiculos, setVehiculos] = useState<Vehiculo[]>([]);
  const [edicion, setEdicion] = useState<Record<string, Edicion>>({});
  const [formulario, setFormulario] = useState(vacio);
  const [error, setError] = useState("");
  const [exito, setExito] = useState("");

  function recordar(lista: Vehiculo[]) {
    setEdicion(
      Object.fromEntries(
        lista.map((vehiculo) => [
          vehiculo.id_vehiculo,
          { estado: vehiculo.estado, factor: String(vehiculo.factor_emision_co2) },
        ]),
      ),
    );
  }

  useEffect(() => {
    document.title = "Flota · EcoLogística Lima";
    llamar<Vehiculo[]>("/vehiculos")
      .then((lista) => {
        setVehiculos(lista);
        recordar(lista);
      })
      .catch((err: unknown) =>
        setError(err instanceof ApiError ? err.message : "No se pudo cargar la flota."),
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
      const creado = await llamar<Vehiculo>("/vehiculos", {
        method: "POST",
        body: JSON.stringify({
          placa: formulario.placa,
          tipo: formulario.tipo,
          capacidad_kg: Number(formulario.capacidad_kg),
          capacidad_m3: Number(formulario.capacidad_m3),
          consumo_km_l: Number(formulario.consumo_km_l),
          factor_emision_co2: Number(formulario.factor_emision_co2),
          anio_fabricacion: Number(formulario.anio_fabricacion),
        }),
      });
      setVehiculos((actual) => {
        const lista = [...actual, creado].sort((a, b) => a.placa.localeCompare(b.placa));
        recordar(lista);
        return lista;
      });
      setFormulario(vacio);
      setExito(creado.mensaje ?? "Vehículo registrado correctamente");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo registrar el vehículo.");
    }
  }

  async function guardar(id: string) {
    const cambio = edicion[id];
    if (!cambio) return;
    setError("");
    setExito("");
    try {
      const actualizado = await llamar<Vehiculo>(`/vehiculos/${id}`, {
        method: "PUT",
        body: JSON.stringify({
          estado: cambio.estado,
          factor_emision_co2: Number(cambio.factor),
        }),
      });
      setVehiculos((actual) =>
        actual.map((vehiculo) => (vehiculo.id_vehiculo === id ? actualizado : vehiculo)),
      );
      setEdicion((actual) => ({
        ...actual,
        [id]: { estado: actualizado.estado, factor: String(actualizado.factor_emision_co2) },
      }));
      setExito("Vehículo actualizado correctamente");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo actualizar el vehículo.");
    }
  }

  return (
    <>
      <header>
        <h1>Flota</h1>
        <p className="ayuda">
          Consulte la flota, retire unidades a mantenimiento y actualice el factor de emisión de CO₂.
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
          <h2>Registrar vehículo</h2>
          <form className="grilla" onSubmit={enviar}>
            <label htmlFor="placa">
              Placa
              <input
                id="placa"
                required
                maxLength={10}
                value={formulario.placa}
                onChange={(event) => actualizarCampo("placa", event.target.value)}
              />
            </label>
            <label htmlFor="tipo">
              Tipo
              <select
                id="tipo"
                value={formulario.tipo}
                onChange={(event) => actualizarCampo("tipo", event.target.value)}
              >
                {TIPOS.map((tipo) => (
                  <option key={tipo.valor} value={tipo.valor}>
                    {tipo.etiqueta}
                  </option>
                ))}
              </select>
            </label>
            <label htmlFor="capacidad_kg">
              Capacidad (kg)
              <input
                id="capacidad_kg"
                type="number"
                min="0.01"
                step="0.01"
                required
                value={formulario.capacidad_kg}
                onChange={(event) => actualizarCampo("capacidad_kg", event.target.value)}
              />
            </label>
            <label htmlFor="capacidad_m3">
              Capacidad (m³)
              <input
                id="capacidad_m3"
                type="number"
                min="0.01"
                step="0.01"
                required
                value={formulario.capacidad_m3}
                onChange={(event) => actualizarCampo("capacidad_m3", event.target.value)}
              />
            </label>
            <label htmlFor="consumo_km_l">
              Consumo (km/L)
              <input
                id="consumo_km_l"
                type="number"
                min="0.001"
                step="0.001"
                required
                value={formulario.consumo_km_l}
                onChange={(event) => actualizarCampo("consumo_km_l", event.target.value)}
              />
            </label>
            <label htmlFor="factor_emision_co2">
              Factor de emisión (kg CO₂/km)
              <input
                id="factor_emision_co2"
                type="number"
                min="0.0001"
                step="0.0001"
                required
                value={formulario.factor_emision_co2}
                onChange={(event) => actualizarCampo("factor_emision_co2", event.target.value)}
              />
            </label>
            <label htmlFor="anio_fabricacion">
              Año de fabricación
              <input
                id="anio_fabricacion"
                type="number"
                min={1990}
                max={new Date().getFullYear()}
                required
                value={formulario.anio_fabricacion}
                onChange={(event) => actualizarCampo("anio_fabricacion", event.target.value)}
              />
            </label>
            <button type="submit">Registrar vehículo</button>
          </form>
        </section>
      ) : null}
      <section className="panel">
        <h2>Unidades registradas</h2>
        {vehiculos.length === 0 ? (
          <p>No hay vehículos registrados.</p>
        ) : (
          <div className="tabla-contenedor">
            <table>
              <caption className="muted">Flota disponible para el reparto</caption>
              <thead>
                <tr>
                  <th>Placa</th>
                  <th>Tipo</th>
                  <th>Capacidad</th>
                  <th>Consumo</th>
                  <th>Año</th>
                  <th>Estado</th>
                  <th>Factor CO₂</th>
                  {editar ? <th>Acciones</th> : null}
                </tr>
              </thead>
              <tbody>
                {vehiculos.map((vehiculo) => {
                  const cambio = edicion[vehiculo.id_vehiculo];
                  return (
                    <tr key={vehiculo.id_vehiculo}>
                      <td>{vehiculo.placa}</td>
                      <td>{etiqueta(vehiculo.tipo)}</td>
                      <td>
                        {vehiculo.capacidad_kg} kg / {vehiculo.capacidad_m3} m³
                      </td>
                      <td>{vehiculo.consumo_km_l} km/L</td>
                      <td>{vehiculo.anio_fabricacion}</td>
                      <td>
                        {editar && cambio ? (
                          <select
                            aria-label={`Estado de ${vehiculo.placa}`}
                            value={cambio.estado}
                            onChange={(event) =>
                              setEdicion((actual) => ({
                                ...actual,
                                [vehiculo.id_vehiculo]: { ...cambio, estado: event.target.value },
                              }))
                            }
                          >
                            {ESTADOS.map((item) => (
                              <option key={item.valor} value={item.valor}>
                                {item.etiqueta}
                              </option>
                            ))}
                          </select>
                        ) : (
                          <span className={`insignia ${vehiculo.estado}`}>
                            {etiqueta(vehiculo.estado)}
                          </span>
                        )}
                      </td>
                      <td>
                        {editar && cambio ? (
                          <input
                            aria-label={`Factor de emisión de ${vehiculo.placa}`}
                            type="number"
                            min="0.0001"
                            step="0.0001"
                            value={cambio.factor}
                            onChange={(event) =>
                              setEdicion((actual) => ({
                                ...actual,
                                [vehiculo.id_vehiculo]: { ...cambio, factor: event.target.value },
                              }))
                            }
                          />
                        ) : (
                          vehiculo.factor_emision_co2
                        )}
                      </td>
                      {editar ? (
                        <td>
                          <button type="button" onClick={() => guardar(vehiculo.id_vehiculo)}>
                            Guardar
                          </button>
                        </td>
                      ) : null}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </>
  );
}
