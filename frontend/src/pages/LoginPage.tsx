import { FormEvent, useEffect, useState } from "react";
import { Navigate } from "react-router-dom";

import { ApiError } from "../api";
import { useAuth } from "../auth";
import { Alerta } from "../avisos";

export function LoginPage() {
  const { sesion, iniciar } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [enviando, setEnviando] = useState(false);

  useEffect(() => {
    document.title = "Iniciar sesión · EcoLogística Lima";
  }, []);

  if (sesion) {
    return <Navigate to={sesion.rol === "CONDUCTOR" ? "/modo" : "/flota"} replace />;
  }

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
      <section className="tarjeta" aria-labelledby="titulo-login">
        <p className="muted">DistriRápido S.A.C.</p>
        <h1 id="titulo-login" className="marca">EcoLogística Lima</h1>
        <p className="subtitulo">Inicie sesión para gestionar la operación de reparto.</p>
        <form
          className="formulario"
          onSubmit={onSubmit}
          aria-label="Iniciar sesión"
          aria-describedby={error ? "alerta-login" : undefined}
        >
          <label htmlFor="email">
            Correo{/*
            */}<input
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
            Contraseña{/*
            */}<input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </label>
          {error ? <Alerta id="alerta-login">{error}</Alerta> : null}
          <button type="submit" disabled={enviando}>
            {enviando ? "Ingresando…" : "Entrar"}
          </button>
        </form>
      </section>
    </main>
  );
}
