import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";

import { ApiError, api } from "./api";
import { vaciarConsultas } from "./consulta";
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

export function AuthProvider({ children }: Readonly<{ children: ReactNode }>) {
  const [sesion, setSesion] = useState<Sesion | null>(() => leer());
  const tokenVisto = useRef(sesion?.access_token ?? "");
  const tokenActual = sesion?.access_token ?? "";
  if (tokenVisto.current !== tokenActual) {
    tokenVisto.current = tokenActual;
    vaciarConsultas();
  }

  const cerrar = useCallback(() => {
    sessionStorage.removeItem(CLAVE);
    vaciarConsultas();
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
        const datos = await api<T>(path, options, sesion?.access_token);
        const metodo = (options.method ?? "GET").toUpperCase();
        if (metodo !== "GET" && metodo !== "HEAD") vaciarConsultas();
        return datos;
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
