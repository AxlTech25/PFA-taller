import { Suspense } from "react";
import { NavLink, Navigate, Outlet } from "react-router-dom";

import { useAuth } from "../auth";
import { Marca } from "../marca";
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
        <div className="marca-nav">
          <Marca tono="claro" />
          <nav className="nav" aria-label="Módulos">
            {enlaces.map((enlace) => (
              <NavLink key={enlace.to} to={enlace.to}>
                {enlace.etiqueta}
              </NavLink>
            ))}
          </nav>
        </div>
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
        <Suspense fallback={<p role="status">Cargando módulo…</p>}>
          <Outlet />
        </Suspense>
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
