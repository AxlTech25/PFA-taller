import { FormEvent, useState } from "react";
import { Navigate } from "react-router-dom";

import { ApiError } from "../api";
import { useAuth } from "../auth";

export function LoginPage() {
  const { sesion, iniciar } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [enviando, setEnviando] = useState(false);

  if (sesion) return <Navigate to="/flota" replace />;

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setEnviando(true);
    try {
      await iniciar(email, password);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo iniciar sesión.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <main className="login">
      <section className="tarjeta">
        <p className="muted">DistriRápido S.A.C.</p>
        <h1 className="marca">EcoLogística Lima</h1>
        <p className="subtitulo">Inicie sesión para gestionar la operación de reparto.</p>
        <form className="formulario" onSubmit={onSubmit}>
          <label htmlFor="email">
            Correo
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="username"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
            />
          </label>
          <label htmlFor="password">
            Contraseña
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </label>
          {error ? (
            <p className="alerta" role="alert">
              {error}
            </p>
          ) : null}
          <button type="submit" disabled={enviando}>
            {enviando ? "Ingresando…" : "Entrar"}
          </button>
        </form>
      </section>
    </main>
  );
}
