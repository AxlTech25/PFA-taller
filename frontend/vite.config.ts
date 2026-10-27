/// <reference types="vitest/config" />
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

import { respuestaSpa } from "./src/proxy";

const destino = process.env.VITE_PROXY_TARGET || "http://localhost:8000";
const raizFrontend = dirname(fileURLToPath(import.meta.url));
const raizRepo = resolve(raizFrontend, "..");

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
  "/optimizaciones": api(),
  "/rutas": api(),
  "/indicadores": api(),
  "/health": api(),
  "/docs": destino,
  "/openapi.json": destino,
};

function normalizarSf(valor: string): string {
  let archivo = valor.trim().replaceAll("\\", "/");
  if (/^[A-Za-z]:\//.test(archivo) || archivo.startsWith("/")) {
    const relativo = relative(raizRepo, archivo).replaceAll("\\", "/");
    if (!relativo.startsWith("..")) return relativo;
  }
  if (archivo.startsWith("./")) archivo = archivo.slice(2);
  if (archivo.startsWith("frontend/")) return archivo;
  if (archivo.startsWith("src/")) return `frontend/${archivo}`;
  return relative(raizRepo, resolve(raizFrontend, archivo)).replaceAll("\\", "/");
}

function normalizarLcov() {
  const ruta = resolve(raizFrontend, "coverage", "lcov.info");
  if (!existsSync(ruta)) return;
  const texto = readFileSync(ruta, "utf8");
  const lineas = texto.split(/\r?\n/).map((linea) => {
    if (!linea.startsWith("SF:")) return linea;
    return `SF:${normalizarSf(linea.slice(3))}`;
  });
  writeFileSync(ruta, lineas.join("\n"));
}

const globalConHook = globalThis as { __ecologisticaLcov?: boolean };
if (!globalConHook.__ecologisticaLcov) {
  globalConHook.__ecologisticaLcov = true;
  process.on("exit", normalizarLcov);
}

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    proxy,
  },
  test: {
    environment: "jsdom",
    include: ["src/**/*.test.ts", "src/**/*.test.tsx"],
    setupFiles: ["./src/test/setup.ts"],
    coverage: {
      provider: "v8",
      reporter: ["text", "lcov"],
      reportsDirectory: "coverage",
      all: true,
      include: ["src/**/*.{ts,tsx}"],
      exclude: [
        "src/**/*.test.ts",
        "src/**/*.test.tsx",
        "src/test/**",
        "src/vite-env.d.ts",
      ],
    },
  },
});
