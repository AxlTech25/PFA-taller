import type { ReactNode } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import { useAuth } from "./auth";
import { ConductoresPage } from "./pages/ConductoresPage";
import { FlotaPage } from "./pages/FlotaPage";
import { LoginPage } from "./pages/LoginPage";
import { ModoConductorPage } from "./pages/ModoConductorPage";
import { PedidosPage } from "./pages/PedidosPage";
import { Shell } from "./pages/Shell";
import { UsuariosPage } from "./pages/UsuariosPage";
import { modulosVisibles, type Modulo } from "./permissions";

function Inicio() {
  const { sesion } = useAuth();
  if (sesion?.rol === "CONDUCTOR") return <Navigate to="/modo" replace />;
  return <Navigate to="/flota" replace />;
}

function Modulo({ modulo, children }: { modulo: Modulo; children: ReactNode }) {
  const { sesion } = useAuth();
  if (!sesion || !modulosVisibles(sesion.rol).includes(modulo)) {
    return (
      <p className="alerta" role="alert">
        No tiene permiso para acceder a este módulo.
      </p>
    );
  }
  return children;
}

export function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<Shell />}>
        <Route path="/" element={<Inicio />} />
        <Route
          path="/flota"
          element={
            <Modulo modulo="flota">
              <FlotaPage />
            </Modulo>
          }
        />
        <Route
          path="/conductores"
          element={
            <Modulo modulo="conductores">
              <ConductoresPage />
            </Modulo>
          }
        />
        <Route
          path="/pedidos"
          element={
            <Modulo modulo="pedidos">
              <PedidosPage />
            </Modulo>
          }
        />
        <Route
          path="/usuarios"
          element={
            <Modulo modulo="usuarios">
              <UsuariosPage />
            </Modulo>
          }
        />
        <Route
          path="/modo"
          element={
            <Modulo modulo="modo">
              <ModoConductorPage />
            </Modulo>
          }
        />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
