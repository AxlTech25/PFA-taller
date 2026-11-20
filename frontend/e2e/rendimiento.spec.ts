import { mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";

import { expect, test, type Page } from "@playwright/test";

import { ADMIN, fechaLima, placaNueva } from "./helpers";

const TOPE_API_MS = 500;
const TOPE_TTFB_MS = 500;
const TOPE_FCP_MS = 2_500;
const TOPE_LCP_MS = 4_000;

type MuestraApi = {
  metodo: string;
  ruta: string;
  estado: number;
  mediana_ms: number;
  max_ms: number;
};

type Vital = {
  nombre: string;
  ruta: string;
  ttfb_ms: number;
  fcp_ms: number;
  lcp_ms: number;
};

const PANTALLAS: { nombre: string; ruta: string; titulo: string }[] = [
  { nombre: "Login", ruta: "/login", titulo: "EcoLogística Lima" },
  { nombre: "Flota", ruta: "/flota", titulo: "Flota" },
  { nombre: "Conductores", ruta: "/conductores", titulo: "Conductores" },
  { nombre: "Pedidos", ruta: "/pedidos", titulo: "Pedidos" },
  { nombre: "Rutas", ruta: "/rutas", titulo: "Rutas" },
  { nombre: "Tablero", ruta: "/dashboard", titulo: "Tablero" },
];

function redondear(valor: number): number {
  return Number(valor.toFixed(2));
}

function mediana(muestras: number[]): number {
  const orden = [...muestras].sort((a, b) => a - b);
  return orden[Math.floor(orden.length / 2)] ?? 0;
}

async function instalarLcp(page: Page): Promise<void> {
  await page.addInitScript(() => {
    const marca = window as Window & { __lcp?: number };
    const guardar = (entrada: PerformanceEntry) => {
      if (entrada.startTime >= (marca.__lcp ?? 0)) marca.__lcp = entrada.startTime;
    };
    try {
      new PerformanceObserver((lista) => {
        for (const entrada of lista.getEntries()) guardar(entrada);
      }).observe({ type: "largest-contentful-paint", buffered: true });
    } catch {
      /* El navegador no expone LCP. La lectura posterior lo deja en cero y el test falla. */
    }
  });
}

async function medirPantalla(page: Page, pantalla: (typeof PANTALLAS)[number]): Promise<Vital> {
  await page.goto(pantalla.ruta, { waitUntil: "load" });
  await expect(page.getByRole("heading", { level: 1, name: pantalla.titulo })).toBeVisible();
  await page.waitForFunction(
    () => {
      const marca = window as Window & { __lcp?: number };
      return typeof marca.__lcp === "number" && marca.__lcp > 0;
    },
    null,
    { timeout: 5_000 },
  );
  const cifras = await page.evaluate(() => {
    const navegacion = performance.getEntriesByType("navigation")[0] as PerformanceNavigationTiming | undefined;
    const pinturas = performance.getEntriesByType("paint");
    const fcp = pinturas.find((entrada) => entrada.name === "first-contentful-paint")?.startTime ?? 0;
    const lcp = (window as Window & { __lcp?: number }).__lcp ?? 0;
    return { ttfb: navegacion?.responseStart ?? 0, fcp, lcp };
  });
  return {
    nombre: pantalla.nombre,
    ruta: pantalla.ruta,
    ttfb_ms: redondear(cifras.ttfb),
    fcp_ms: redondear(cifras.fcp),
    lcp_ms: redondear(cifras.lcp),
  };
}

async function cronometrar(
  page: Page,
  metodo: string,
  ruta: string,
  token: string,
  body?: string,
): Promise<MuestraApi> {
  const muestras: number[] = [];
  let estado = 0;
  for (let i = 0; i < 6; i += 1) {
    const resultado = await page.evaluate(
      async ({ metodo, ruta, token, body }) => {
        const encabezados: Record<string, string> = { Accept: "application/json" };
        if (token) encabezados.Authorization = `Bearer ${token}`;
        if (body) encabezados["Content-Type"] = "application/json";
        const inicio = performance.now();
        const respuesta = await fetch(ruta, { method: metodo, headers: encabezados, body, cache: "no-store" });
        await respuesta.arrayBuffer();
        return { status: respuesta.status, ms: performance.now() - inicio };
      },
      { metodo, ruta, token, body },
    );
    estado = resultado.status;
    if (i > 0) muestras.push(resultado.ms);
  }
  return {
    metodo,
    ruta,
    estado,
    mediana_ms: redondear(mediana(muestras)),
    max_ms: redondear(Math.max(...muestras)),
  };
}

test("web vitals por pantalla y tiempos de API bajo 500 ms", async ({ page }, info) => {
  await instalarLcp(page);
  const login = await medirPantalla(page, PANTALLAS[0]);

  await page.locator("#email").fill(ADMIN.email);
  await page.locator("#password").fill(ADMIN.password);
  await page.getByRole("button", { name: "Entrar" }).click();
  await expect(page).toHaveURL(/\/flota$/);

  const token = await page.evaluate(() => {
    const crudo = sessionStorage.getItem("ecologistica.sesion");
    if (!crudo) return "";
    return (JSON.parse(crudo) as { access_token?: string }).access_token ?? "";
  });
  expect(token.length).toBeGreaterThan(10);

  const pantallas = [login];
  for (const pantalla of PANTALLAS.slice(1)) {
    pantallas.push(await medirPantalla(page, pantalla));
  }

  const fecha = fechaLima();
  const api: MuestraApi[] = [];
  api.push(
    await cronometrar(
      page,
      "POST",
      "/auth/login",
      "",
      JSON.stringify({ email: ADMIN.email, password: ADMIN.password }),
    ),
  );
  for (const ruta of [
    "/health",
    "/auth/me",
    "/vehiculos?page=1&limite=12",
    "/conductores?page=1&limite=12",
    "/pedidos?page=1&limite=12",
    "/clientes?page=1&limite=12",
    `/rutas?fecha=${fecha}&page=1&limite=12`,
    `/indicadores?fecha=${fecha}`,
    "/usuarios?page=1&limite=12",
  ]) {
    api.push(await cronometrar(page, "GET", ruta, ruta === "/health" ? "" : token));
  }

  const altas: number[] = [];
  let altaEstado = 0;
  let idVehiculo = "";
  for (let i = 0; i < 4; i += 1) {
    const resultado = await page.evaluate(
      async ({ token, cuerpo }) => {
        const inicio = performance.now();
        const respuesta = await fetch("/vehiculos", {
          method: "POST",
          cache: "no-store",
          headers: {
            Accept: "application/json",
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify(cuerpo),
        });
        const datos = (await respuesta.json()) as { id_vehiculo?: string };
        return { status: respuesta.status, ms: performance.now() - inicio, id: datos.id_vehiculo ?? "" };
      },
      {
        token,
        cuerpo: {
          placa: placaNueva(`${info.project.name}${i}`),
          tipo: "MOTO",
          capacidad_kg: 40,
          capacidad_m3: 0.2,
          consumo_km_l: 30,
          factor_emision_co2: 0.08,
          anio_fabricacion: 2022,
        },
      },
    );
    altaEstado = resultado.status;
    if (resultado.id) idVehiculo = resultado.id;
    if (i > 0) altas.push(resultado.ms);
  }
  api.push({
    metodo: "POST",
    ruta: "/vehiculos",
    estado: altaEstado,
    mediana_ms: redondear(mediana(altas)),
    max_ms: redondear(Math.max(...altas)),
  });

  const cambios: number[] = [];
  let cambioEstado = 0;
  for (let i = 0; i < 4; i += 1) {
    const resultado = await page.evaluate(
      async ({ token, idVehiculo, factor }) => {
        const inicio = performance.now();
        const respuesta = await fetch(`/vehiculos/${idVehiculo}`, {
          method: "PUT",
          cache: "no-store",
          headers: {
            Accept: "application/json",
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ factor_emision_co2: factor }),
        });
        await respuesta.arrayBuffer();
        return { status: respuesta.status, ms: performance.now() - inicio };
      },
      { token, idVehiculo, factor: 0.09 + i * 0.01 },
    );
    cambioEstado = resultado.status;
    if (i > 0) cambios.push(resultado.ms);
  }
  api.push({
    metodo: "PUT",
    ruta: "/vehiculos/{id}",
    estado: cambioEstado,
    mediana_ms: redondear(mediana(cambios)),
    max_ms: redondear(Math.max(...cambios)),
  });

  const informe = {
    navegador: info.project.name,
    medido_en: new Date().toISOString(),
    pantallas,
    api,
  };
  const directorio = path.resolve("test-results");
  mkdirSync(directorio, { recursive: true });
  writeFileSync(path.join(directorio, `mediciones-${info.project.name}.json`), JSON.stringify(informe, null, 2));
  await info.attach(`mediciones-${info.project.name}.json`, {
    body: JSON.stringify(informe, null, 2),
    contentType: "application/json",
  });

  for (const pantalla of pantallas) {
    expect(pantalla.ttfb_ms, `TTFB ${pantalla.nombre}`).toBeGreaterThan(0);
    expect(pantalla.ttfb_ms, `TTFB ${pantalla.nombre}`).toBeLessThan(TOPE_TTFB_MS);
    expect(pantalla.fcp_ms, `FCP ${pantalla.nombre}`).toBeGreaterThan(0);
    expect(pantalla.fcp_ms, `FCP ${pantalla.nombre}`).toBeLessThan(TOPE_FCP_MS);
    expect(pantalla.lcp_ms, `LCP ${pantalla.nombre}`).toBeGreaterThan(0);
    expect(pantalla.lcp_ms, `LCP ${pantalla.nombre}`).toBeLessThan(TOPE_LCP_MS);
  }
  for (const llamada of api) {
    expect(llamada.estado, `${llamada.metodo} ${llamada.ruta}`).toBeGreaterThanOrEqual(200);
    expect(llamada.estado, `${llamada.metodo} ${llamada.ruta}`).toBeLessThan(300);
    expect(llamada.mediana_ms, `${llamada.metodo} ${llamada.ruta}`).toBeGreaterThan(0);
    expect(llamada.mediana_ms, `${llamada.metodo} ${llamada.ruta}`).toBeLessThan(TOPE_API_MS);
  }
});
