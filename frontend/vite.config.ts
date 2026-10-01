/// <reference types="vitest/config" />
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

import { respuestaSpa } from "./src/proxy";

const destino = process.env.VITE_PROXY_TARGET || "http://localhost:8000";

function api() {
  return {
    target: destino,
    bypass(req: { method?: string; headers: { accept?: string | string[] } }) {
      return respuestaSpa(req.method, req.headers.accept);
    },
  };
}

const proxy = {
  "/auth": api(),
  "/usuarios": api(),
  "/vehiculos": api(),
  "/conductores": api(),
  "/pedidos": api(),
  "/clientes": api(),
  "/health": api(),
  "/docs": destino,
  "/openapi.json": destino,
};

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    proxy,
  },
  test: {
    environment: "node",
    include: ["src/**/*.test.ts"],
  },
});
