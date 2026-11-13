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
const COOKIE = "ecologistica_sesion";

type AuthContextValue = {
  sesion: Sesion | null;
  iniciar: (email: string, password: string) => Promise<void>;
  cerrar: () => void;
  llamar: <T>(path: string, options?: RequestInit) => Promise<T>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

function parsear(crudo: string | null): Sesion | null {
  if (!crudo) return null;
  try {
    const datos = JSON.parse(crudo) as Sesion;
    if (!datos.access_token || !datos.rol) return null;
    return datos;
  } catch {
    return null;
  }
}

function leerCookie(): string | null {
  const prefijo = `${COOKIE}=`;
  const parte = document.cookie.split("; ").find((item) => item.startsWith(prefijo));
  if (!parte) return null;
  try {
    return decodeURIComponent(parte.slice(prefijo.length));
  } catch {
    return null;
  }
}

function leer(): Sesion | null {
  const guardado = sessionStorage.getItem(CLAVE);
  const deSesion = parsear(guardado);
  if (deSesion) return deSesion;
  if (guardado) sessionStorage.removeItem(CLAVE);
  // La auditoría de Lighthouse deja la sesión en una cookie: sessionStorage
  // no sobrevive al cambio de pestaña que hace Lighthouse CI.
  return parsear(leerCookie());
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
