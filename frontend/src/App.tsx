import { Navigate, Route, Routes } from "react-router-dom";

import { LoginPage } from "./pages/LoginPage";
import { FlotaPage } from "./pages/FlotaPage";
import { Shell } from "./pages/Shell";

export function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<Shell />}>
        <Route path="/" element={<Navigate to="/flota" replace />} />
        <Route path="/flota" element={<FlotaPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/flota" replace />} />
    </Routes>
  );
}
