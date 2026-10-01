import { NavLink, Navigate, Outlet } from "react-router-dom";

import { useAuth } from "../auth";
import { etiquetaRol, modulosVisibles, type Modulo } from "../permissions";

const ENLACES: { to: string; etiqueta: string; modulo: Modulo }[] = [
  { to: "/flota", etiqueta: "Flota", modulo: "flota" },
  { to: "/conductores", etiqueta: "Conductores", modulo: "conductores" },
  { to: "/pedidos", etiqueta: "Pedidos", modulo: "pedidos" },
  { to: "/usuarios", etiqueta: "Usuarios", modulo: "usuarios" },
  { to: "/modo", etiqueta: "Modo conductor", modulo: "modo" },
];

export function Shell() {
  const { sesion, cerrar } = useAuth();
  if (!sesion) return <Navigate to="/login" replace />;
  const visibles = modulosVisibles(sesion.rol);

  return (
    <div className="layout">
      <a className="saltar" href="#contenido">
        Saltar al contenido
      </a>
      <header className="barra">
        <nav className="nav" aria-label="Módulos">
          {ENLACES.filter((enlace) => visibles.includes(enlace.modulo)).map((enlace) => (
            <NavLink key={enlace.to} to={enlace.to}>
              {enlace.etiqueta}
            </NavLink>
          ))}
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
