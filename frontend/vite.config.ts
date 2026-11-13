/// <reference types="vitest/config" />
import { existsSync, readFileSync, readdirSync, statSync, writeFileSync } from "node:fs";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { brotliCompressSync, constants, gzipSync } from "node:zlib";

import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

import { respuestaSpa } from "./src/proxy.ts";

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

function cssEnLinea(html: string, dist: string) {
  return html.replace(/<link rel="stylesheet"[^>]*href="([^"]+)"[^>]*>/, (_etiqueta, href: string) => {
    const archivo = resolve(dist, String(href).replace(/^\//, ""));
    if (!existsSync(archivo)) return _etiqueta;
    const css = readFileSync(archivo, "utf8").replace(/<\/style/gi, "<\\/style");
    return `<style>${css}</style>`;
  });
}

function comprimirDist() {
  const recorrer = (directorio: string) => {
    for (const nombre of readdirSync(directorio)) {
      const ruta = join(directorio, nombre);
      if (statSync(ruta).isDirectory()) {
        recorrer(ruta);
        continue;
      }
      const precomprimido = nombre.endsWith(".gz") || nombre.endsWith(".br");
      if (precomprimido || !/\.(js|css|html|svg|json)$/.test(nombre)) continue;
      const datos = readFileSync(ruta);
      if (datos.length < 1024) continue;
      writeFileSync(`${ruta}.gz`, gzipSync(datos, { level: 6 }));
      writeFileSync(
        `${ruta}.br`,
        brotliCompressSync(datos, { params: { [constants.BROTLI_PARAM_QUALITY]: 5 } }),
      );
    }
  };
  return {
    name: "comprimir-dist",
    apply: "build" as const,
    closeBundle() {
      const dist = resolve(raizFrontend, "dist");
      const html = join(dist, "index.html");
      if (existsSync(html)) {
        writeFileSync(html, cssEnLinea(readFileSync(html, "utf8"), dist));
      }
      if (existsSync(dist)) recorrer(dist);
    },
  };
}

export default defineConfig({
  plugins: [react(), comprimirDist()],
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
