import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";

import { ApiError, api } from "./api";
import type { Sesion } from "./types";

const CLAVE = "ecologistica.sesion";

type AuthContextValue = {
  sesion: Sesion | null;
  iniciar: (email: string, password: string) => Promise<void>;
  cerrar: () => void;
  llamar: <T>(path: string, options?: RequestInit) => Promise<T>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

function leer(): Sesion | null {
  const crudo = sessionStorage.getItem(CLAVE);
  if (!crudo) return null;
  try {
    return JSON.parse(crudo) as Sesion;
  } catch {
    sessionStorage.removeItem(CLAVE);
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [sesion, setSesion] = useState<Sesion | null>(() => leer());

  const cerrar = useCallback(() => {
    sessionStorage.removeItem(CLAVE);
    setSesion(null);
  }, []);

  const iniciar = useCallback(async (email: string, password: string) => {
    const datos = await api<Sesion>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    sessionStorage.setItem(CLAVE, JSON.stringify(datos));
    setSesion(datos);
  }, []);

  const llamar = useCallback(
    async <T,>(path: string, options: RequestInit = {}) => {
      try {
        return await api<T>(path, options, sesion?.access_token);
      } catch (error) {
        if (error instanceof ApiError && error.status === 401) cerrar();
        throw error;
      }
    },
    [cerrar, sesion],
  );

  const value = useMemo(
    () => ({ sesion, iniciar, cerrar, llamar }),
    [sesion, iniciar, cerrar, llamar],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const contexto = useContext(AuthContext);
  if (!contexto) throw new Error("useAuth debe usarse dentro de AuthProvider");
  return contexto;
}
