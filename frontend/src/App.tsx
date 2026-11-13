import { lazy, useEffect, type ReactNode } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import { Alerta } from "./avisos";
import { useAuth } from "./auth";
import { LoginPage } from "./pages/LoginPage";
import { Shell } from "./pages/Shell";
import { modulosVisibles, type Modulo } from "./permissions";

const FlotaPage = lazy(() => import("./pages/FlotaPage").then((m) => ({ default: m.FlotaPage })));
const ConductoresPage = lazy(() =>
  import("./pages/ConductoresPage").then((m) => ({ default: m.ConductoresPage })),
);
const PedidosPage = lazy(() =>
  import("./pages/PedidosPage").then((m) => ({ default: m.PedidosPage })),
);
const RutasPage = lazy(() => import("./pages/RutasPage").then((m) => ({ default: m.RutasPage })));
const DashboardPage = lazy(() =>
  import("./pages/DashboardPage").then((m) => ({ default: m.DashboardPage })),
);
const UsuariosPage = lazy(() =>
  import("./pages/UsuariosPage").then((m) => ({ default: m.UsuariosPage })),
);
const ModoConductorPage = lazy(() =>
  import("./pages/ModoConductorPage").then((m) => ({ default: m.ModoConductorPage })),
);

function Inicio() {
  const { sesion } = useAuth();
  if (sesion?.rol === "CONDUCTOR") return <Navigate to="/modo" replace />;
  return <Navigate to="/flota" replace />;
}

function Modulo({ modulo, children }: Readonly<{ modulo: Modulo; children: ReactNode }>) {
  const { sesion } = useAuth();
  const permitido = Boolean(sesion && modulosVisibles(sesion.rol).includes(modulo));

  useEffect(() => {
    if (!permitido) document.title = "Acceso denegado · EcoLogística Lima";
  }, [permitido]);

  if (!permitido) {
    return (
      <>
        <h1>Acceso denegado</h1>
        <Alerta id="alerta-permiso">No tiene permiso para acceder a este módulo.</Alerta>
      </>
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
          path="/rutas"
          element={
            <Modulo modulo="rutas">
              <RutasPage />
            </Modulo>
          }
        />
        <Route
          path="/dashboard"
          element={
            <Modulo modulo="dashboard">
              <DashboardPage />
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
