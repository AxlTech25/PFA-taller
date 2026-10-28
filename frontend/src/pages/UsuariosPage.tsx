import { FormEvent, useEffect, useState } from "react";

import { ApiError } from "../api";
import { useAuth } from "../auth";
import { Alerta, Exito, TablaDesplazable } from "../avisos";
import { etiquetaRol, puedeGestionarUsuarios } from "../permissions";
import type { Usuario } from "../types";

const ROLES = ["ADMIN", "GERENTE", "OPERADOR", "CONDUCTOR", "AUDITOR"] as const;

const vacio = {
  email: "",
  password: "",
  rol: "CONDUCTOR",
  estado: "ACTIVO",
};

export function UsuariosPage() {
  const { llamar, sesion } = useAuth();
  const gestionar = sesion ? puedeGestionarUsuarios(sesion.rol) : false;
  const [usuarios, setUsuarios] = useState<Usuario[]>([]);
  const [formulario, setFormulario] = useState(vacio);
  const [error, setError] = useState("");
  const [exito, setExito] = useState("");

  useEffect(() => {
    document.title = "Usuarios · EcoLogística Lima";
    llamar<Usuario[]>("/usuarios")
      .then(setUsuarios)
      .catch((err: unknown) =>
        setError(err instanceof ApiError ? err.message : "No se pudo cargar los usuarios."),
      );
  }, [llamar]);

  function actualizarCampo(campo: string, valor: string) {
    setFormulario((actual) => ({ ...actual, [campo]: valor }));
  }

  function reemplazar(actualizado: Usuario) {
    setUsuarios((actual) =>
      actual.map((usuario) =>
        usuario.id_usuario === actualizado.id_usuario ? actualizado : usuario,
      ),
    );
  }

  async function enviar(event: FormEvent) {
    event.preventDefault();
    setError("");
    setExito("");
    try {
      const creado = await llamar<Usuario>("/usuarios", {
        method: "POST",
        body: JSON.stringify(formulario),
      });
      setUsuarios((actual) =>
        [...actual, creado].sort((a, b) => a.email.localeCompare(b.email)),
      );
      setFormulario(vacio);
      setExito(creado.mensaje ?? "Usuario registrado correctamente");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo registrar el usuario.");
    }
  }

  async function cambiarRol(usuario: Usuario, rol: string) {
    setError("");
    setExito("");
    try {
      const actualizado = await llamar<Usuario>(`/usuarios/${usuario.id_usuario}`, {
        method: "PATCH",
        body: JSON.stringify({ rol }),
      });
      reemplazar(actualizado);
      setExito("Rol actualizado correctamente");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo cambiar el rol.");
    }
  }

  async function cambiarEstado(usuario: Usuario) {
    setError("");
    setExito("");
    const estado = usuario.estado === "ACTIVO" ? "INACTIVO" : "ACTIVO";
    try {
      const actualizado = await llamar<Usuario>(`/usuarios/${usuario.id_usuario}`, {
        method: "PATCH",
        body: JSON.stringify({ estado }),
      });
      reemplazar(actualizado);
      setExito(estado === "ACTIVO" ? "Usuario activado" : "Usuario desactivado");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo cambiar el estado.");
    }
  }

  return (
    <>
      <header>
        <h1>Usuarios</h1>
        <p className="ayuda">
          Cree cuentas, asigne un rol y desactive accesos. El operador no administra usuarios.
        </p>
      </header>
      {error ? <Alerta id="alerta-usuarios">{error}</Alerta> : null}
      {exito ? <Exito>{exito}</Exito> : null}
      {gestionar ? (
        <section className="panel" aria-labelledby="titulo-registrar-usuario">
          <h2 id="titulo-registrar-usuario">Registrar usuario</h2>
          <form className="grilla" aria-labelledby="titulo-registrar-usuario" onSubmit={enviar}>
            <label htmlFor="email-usuario">
              Correo{/*
              */}<input
                id="email-usuario"
                type="email"
                required
                value={formulario.email}
                onChange={(event) => actualizarCampo("email", event.target.value)}
              />
            </label>
            <label htmlFor="password-usuario">
              Contraseña inicial{/*
              */}<input
                id="password-usuario"
                type="password"
                autoComplete="new-password"
                required
                minLength={8}
                value={formulario.password}
                onChange={(event) => actualizarCampo("password", event.target.value)}
              />
            </label>
            <label htmlFor="rol-usuario">
              Rol{/*
              */}<select
                id="rol-usuario"
                value={formulario.rol}
                onChange={(event) => actualizarCampo("rol", event.target.value)}
              >
                {ROLES.map((rol) => (
                  <option key={rol} value={rol}>
                    {etiquetaRol(rol)}
                  </option>
                ))}
              </select>
            </label>
            <label htmlFor="estado-usuario">
              Estado{/*
              */}<select
                id="estado-usuario"
                value={formulario.estado}
                onChange={(event) => actualizarCampo("estado", event.target.value)}
              >
                <option value="ACTIVO">Activo</option>
                <option value="INACTIVO">Inactivo</option>
              </select>
            </label>
            <button type="submit">Registrar usuario</button>
          </form>
        </section>
      ) : (
        <p className="aviso">Su rol puede consultar usuarios, no modificarlos.</p>
      )}
      <section className="panel" aria-labelledby="titulo-cuentas">
        <h2 id="titulo-cuentas">Cuentas</h2>
        {gestionar ? (
          <p id="aviso-cambio-usuario" className="ayuda">
            Al cambiar el rol o pulsar Activar o Desactivar, el cambio se guarda enseguida.
          </p>
        ) : null}
        {usuarios.length === 0 ? (
          <p>No hay usuarios registrados.</p>
        ) : (
          <TablaDesplazable etiqueta="Tabla de cuentas de usuario. Si no cabe, desplácela en horizontal con el teclado.">
            <table>
              <caption className="muted">Usuarios y roles del sistema</caption>
              <thead>
                <tr>
                  <th scope="col">Correo</th>
                  <th scope="col">Rol</th>
                  <th scope="col">Estado</th>
                  {gestionar ? <th scope="col">Acciones</th> : null}
                </tr>
              </thead>
              <tbody>
                {usuarios.map((usuario) => (
                  <tr key={usuario.id_usuario}>
                    <td>{usuario.email}</td>
                    <td>
                      {gestionar ? (
                        <select
                          aria-label={`Rol de ${usuario.email}`}
                          aria-describedby="aviso-cambio-usuario"
                          value={usuario.rol}
                          onChange={(event) => cambiarRol(usuario, event.target.value)}
                        >
                          {ROLES.map((rol) => (
                            <option key={rol} value={rol}>
                              {etiquetaRol(rol)}
                            </option>
                          ))}
                        </select>
                      ) : (
                        etiquetaRol(usuario.rol)
                      )}
                    </td>
                    <td>
                      <span className={`insignia ${usuario.estado}`}>{etiquetaRol(usuario.estado)}</span>
                    </td>
                    {gestionar ? (
                      <td>
                        <button
                          type="button"
                          className="secundario"
                          aria-label={`${usuario.estado === "ACTIVO" ? "Desactivar" : "Activar"} ${usuario.email}`}
                          onClick={() => cambiarEstado(usuario)}
                        >
                          {usuario.estado === "ACTIVO" ? "Desactivar" : "Activar"}
                        </button>
                      </td>
                    ) : null}
                  </tr>
                ))}
              </tbody>
            </table>
          </TablaDesplazable>
        )}
      </section>
    </>
  );
}
