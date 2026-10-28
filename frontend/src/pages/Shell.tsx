import { NavLink, Navigate, Outlet } from "react-router-dom";

import { useAuth } from "../auth";
import { etiquetaRol, modulosVisibles, type Modulo } from "../permissions";

const ENLACES: { to: string; etiqueta: string; modulo: Modulo }[] = [
  { to: "/flota", etiqueta: "Flota", modulo: "flota" },
  { to: "/conductores", etiqueta: "Conductores", modulo: "conductores" },
  { to: "/pedidos", etiqueta: "Pedidos", modulo: "pedidos" },
  { to: "/rutas", etiqueta: "Rutas", modulo: "rutas" },
  { to: "/dashboard", etiqueta: "Tablero", modulo: "dashboard" },
  { to: "/usuarios", etiqueta: "Usuarios", modulo: "usuarios" },
  { to: "/modo", etiqueta: "Modo conductor", modulo: "modo" },
];

export function Shell() {
  const { sesion, cerrar } = useAuth();
  if (!sesion) return <Navigate to="/login" replace />;
  const visibles = modulosVisibles(sesion.rol);
  const enlaces = ENLACES.filter((enlace) => visibles.includes(enlace.modulo));

  return (
    <div className="layout">
      <a className="saltar" href="#contenido">
        Saltar al contenido
      </a>
      <header className="barra">
        <nav className="nav" aria-label="Módulos">
          {enlaces.map((enlace) => (
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
      <main className="contenido">
        <a id="contenido" className="ancla-contenido" href="#contenido">
          Contenido principal
        </a>
        <Outlet />
      </main>
      <footer className="pie">
        <nav aria-label="Accesos directos">
          <p className="pie-titulo">Accesos directos</p>
          <div className="pie-enlaces">
            {enlaces.map((enlace) => (
              <NavLink key={enlace.to} to={enlace.to}>
                {enlace.etiqueta}
              </NavLink>
            ))}
          </div>
        </nav>
      </footer>
    </div>
  );
}
