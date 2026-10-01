import { FormEvent, useEffect, useState } from "react";

import { ApiError } from "../api";
import { useAuth } from "../auth";
import { etiqueta, puedeRegistrarPedido } from "../permissions";
import type { Cliente, Pedido } from "../types";

function horaLocal(hora: string): string {
  const fecha = new Date();
  const mes = String(fecha.getMonth() + 1).padStart(2, "0");
  const dia = String(fecha.getDate()).padStart(2, "0");
  return `${fecha.getFullYear()}-${mes}-${dia}T${hora}`;
}

const vacio = {
  id_cliente: "",
  direccion: "",
  peso_kg: "",
  volumen_m3: "",
  ventana_inicio: horaLocal("08:00"),
  ventana_fin: horaLocal("12:00"),
  latitud: "-12.0025",
  longitud: "-76.9901",
  prioridad: "ESTANDAR",
  tipo_producto: "NO_PERECEDERO",
};

export function PedidosPage() {
  const { llamar, sesion } = useAuth();
  const registrar = sesion ? puedeRegistrarPedido(sesion.rol) : false;
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [pedidos, setPedidos] = useState<Pedido[]>([]);
  const [formulario, setFormulario] = useState(vacio);
  const [error, setError] = useState("");
  const [exito, setExito] = useState("");

  useEffect(() => {
    document.title = "Pedidos · EcoLogística Lima";
    Promise.all([llamar<Cliente[]>("/clientes"), llamar<Pedido[]>("/pedidos")])
      .then(([listaClientes, listaPedidos]) => {
        setClientes(listaClientes);
        setPedidos(listaPedidos);
        setFormulario((actual) => ({
          ...actual,
          id_cliente: actual.id_cliente || listaClientes[0]?.id_cliente || "",
        }));
      })
      .catch((err: unknown) =>
        setError(err instanceof ApiError ? err.message : "No se pudo cargar los pedidos."),
      );
  }, [llamar]);

  function actualizarCampo(campo: string, valor: string) {
    setFormulario((actual) => ({ ...actual, [campo]: valor }));
  }

  const clienteSeleccionado = clientes.find((cliente) => cliente.id_cliente === formulario.id_cliente);

  async function enviar(event: FormEvent) {
    event.preventDefault();
    setError("");
    setExito("");
    try {
      const creado = await llamar<Pedido>("/pedidos", {
        method: "POST",
        body: JSON.stringify({
          id_cliente: formulario.id_cliente,
          direccion: formulario.direccion || null,
          latitud: Number(formulario.latitud),
          longitud: Number(formulario.longitud),
          peso_kg: Number(formulario.peso_kg),
          volumen_m3: Number(formulario.volumen_m3),
          ventana_inicio: formulario.ventana_inicio,
          ventana_fin: formulario.ventana_fin,
          prioridad: formulario.prioridad,
          tipo_producto: formulario.tipo_producto,
        }),
      });
      setPedidos((actual) => [creado, ...actual]);
      setFormulario((actual) => ({ ...vacio, id_cliente: actual.id_cliente }));
      setExito(creado.mensaje ?? "Pedido registrado correctamente");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo registrar el pedido.");
    }
  }

  return (
    <>
      <header>
        <h1>Pedidos</h1>
        <p className="ayuda">
          Registre entregas con peso, ventana horaria y coordenadas. El cliente de demostración
          debe tener consentimiento de datos.
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
          <h2>Registrar pedido</h2>
          <form className="grilla" onSubmit={enviar}>
            <label htmlFor="id_cliente">
              Cliente
              <select
                id="id_cliente"
                required
                value={formulario.id_cliente}
                onChange={(event) => actualizarCampo("id_cliente", event.target.value)}
              >
                {clientes.map((cliente) => (
                  <option key={cliente.id_cliente} value={cliente.id_cliente}>
                    {cliente.nombre}
                    {cliente.consentimiento_datos ? " — con consentimiento" : " — sin consentimiento"}
                  </option>
                ))}
              </select>
            </label>
            <label htmlFor="peso_kg">
              Peso (kg)
              <input
                id="peso_kg"
                type="number"
                min="0.01"
                step="0.01"
                required
                value={formulario.peso_kg}
                onChange={(event) => actualizarCampo("peso_kg", event.target.value)}
              />
            </label>
            <label htmlFor="volumen_m3">
              Volumen (m³)
              <input
                id="volumen_m3"
                type="number"
                min="0.001"
                step="0.001"
                required
                value={formulario.volumen_m3}
                onChange={(event) => actualizarCampo("volumen_m3", event.target.value)}
              />
            </label>
            <label htmlFor="ventana_inicio">
              Ventana desde
              <input
                id="ventana_inicio"
                type="datetime-local"
                required
                value={formulario.ventana_inicio}
                onChange={(event) => actualizarCampo("ventana_inicio", event.target.value)}
              />
            </label>
            <label htmlFor="ventana_fin">
              Ventana hasta
              <input
                id="ventana_fin"
                type="datetime-local"
                required
                value={formulario.ventana_fin}
                onChange={(event) => actualizarCampo("ventana_fin", event.target.value)}
              />
            </label>
            <label htmlFor="latitud">
              Latitud
              <input
                id="latitud"
                type="number"
                step="0.0000001"
                required
                value={formulario.latitud}
                onChange={(event) => actualizarCampo("latitud", event.target.value)}
              />
            </label>
            <label htmlFor="longitud">
              Longitud
              <input
                id="longitud"
                type="number"
                step="0.0000001"
                required
                value={formulario.longitud}
                onChange={(event) => actualizarCampo("longitud", event.target.value)}
              />
            </label>
            <label htmlFor="prioridad">
              Prioridad
              <select
                id="prioridad"
                value={formulario.prioridad}
                onChange={(event) => actualizarCampo("prioridad", event.target.value)}
              >
                <option value="EXPRESS">Exprés</option>
                <option value="ESTANDAR">Estándar</option>
                <option value="ECONOMICO">Económico</option>
              </select>
            </label>
            <label htmlFor="tipo_producto">
              Tipo de producto
              <select
                id="tipo_producto"
                value={formulario.tipo_producto}
                onChange={(event) => actualizarCampo("tipo_producto", event.target.value)}
              >
                <option value="NO_PERECEDERO">No perecedero</option>
                <option value="PERECEDERO">Perecedero</option>
              </select>
            </label>
            <label htmlFor="direccion">
              Dirección o referencia
              <input
                id="direccion"
                maxLength={255}
                value={formulario.direccion}
                onChange={(event) => actualizarCampo("direccion", event.target.value)}
              />
            </label>
            <button type="submit">Registrar pedido</button>
          </form>
          {clienteSeleccionado && !clienteSeleccionado.consentimiento_datos ? (
            <p className="aviso" role="status">
              Este cliente no tiene consentimiento. El sistema rechazará el pedido.
            </p>
          ) : null}
        </section>
      ) : null}
      <section className="panel">
        <h2>Pedidos registrados</h2>
        {pedidos.length === 0 ? (
          <p>No hay pedidos registrados.</p>
        ) : (
          <div className="tabla-contenedor">
            <table>
              <caption className="muted">Entregas en estado operativo</caption>
              <thead>
                <tr>
                  <th>Cliente</th>
                  <th>Peso</th>
                  <th>Ventana</th>
                  <th>Prioridad</th>
                  <th>Estado</th>
                </tr>
              </thead>
              <tbody>
                {pedidos.map((pedido) => (
                  <tr key={pedido.id_pedido}>
                    <td>{pedido.nombre_cliente ?? "Cliente"}</td>
                    <td>{pedido.peso_kg} kg</td>
                    <td>
                      {pedido.ventana_inicio.slice(0, 16).replace("T", " ")} –{" "}
                      {pedido.ventana_fin.slice(11, 16)}
                    </td>
                    <td>
                      <span className={`insignia ${pedido.prioridad}`}>{etiqueta(pedido.prioridad)}</span>
                    </td>
                    <td>
                      <span className={`insignia ${pedido.estado}`}>{etiqueta(pedido.estado)}</span>
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
