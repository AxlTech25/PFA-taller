import { NavLink, Navigate, Outlet } from "react-router-dom";

import { useAuth } from "../auth";
import { etiquetaRol } from "../permissions";

export function Shell() {
  const { sesion, cerrar } = useAuth();
  if (!sesion) return <Navigate to="/login" replace />;

  return (
    <div className="layout">
      <a className="saltar" href="#contenido">
        Saltar al contenido
      </a>
      <header className="barra">
        <nav className="nav" aria-label="Módulos">
          <NavLink to="/flota">Flota</NavLink>
        </nav>
        <div className="sesion">
          <span>
            {sesion.email} · {etiquetaRol(sesion.rol)}
          </span>
          <button type="button" className="secundario" onClick={cerrar}>
            Cerrar sesión
          </button>
        </div>
      </header>
      <main id="contenido" className="contenido">
        <Outlet />
      </main>
    </div>
  );
}
