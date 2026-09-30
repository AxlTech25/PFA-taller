/// <reference types="vitest/config" />
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const destino = process.env.VITE_PROXY_TARGET || "http://localhost:8000";

const proxy = {
  "/auth": destino,
  "/vehiculos": destino,
  "/health": destino,
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
