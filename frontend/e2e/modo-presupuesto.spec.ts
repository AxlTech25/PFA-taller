import { type ChildProcess, spawn } from "node:child_process";
import { mkdirSync, writeFileSync } from "node:fs";
import { createServer, request as httpRequest, type IncomingMessage, type ServerResponse } from "node:http";
import { createServer as crearTcp } from "node:net";
import path from "node:path";

import { expect, test, type Page, type Response } from "@playwright/test";

import { PRESUPUESTO } from "./helpers";

const TOPE_BYTES = 150 * 1024;
const TOPE_3G_MS = 5_000;

// Bajada de Fast 3G (Chrome DevTools): 1,6 Mbit/s y 150 ms de latencia.
const RED_3G = { nombre: "3G rápida", bytesPorSegundo: (1.6 * 1000 * 1000) / 8, latenciaMs: 150 };

// 2G de referencia, el perfil Regular 2G que DevTools ya no muestra: 250 kbit/s y 300 ms.
const RED_2G = { nombre: "2G", bytesPorSegundo: (250 * 1000) / 8, latenciaMs: 300 };

const ritmo = { bytesPorSegundo: Number.POSITIVE_INFINITY, latenciaMs: 0 };

type Medicion = {
  red: string;
  bytes: number;
  milisegundos: number;
  paradas: number;
  peticionesMapa: string[];
};

let servidor: ChildProcess | null = null;
let origen = "";

function puertoLibre(): Promise<number> {
  return new Promise((resolve, reject) => {
    const escucha = crearTcp();
    escucha.listen(0, "127.0.0.1", () => {
      const direccion = escucha.address();
      const puerto = typeof direccion === "object" && direccion ? direccion.port : 0;
      escucha.close(() => resolve(puerto));
    });
    escucha.on("error", reject);
  });
}

function esperar(ms: number): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

async function escribirARitmo(respuesta: ServerResponse, cuerpo: Buffer): Promise<void> {
  if (!Number.isFinite(ritmo.bytesPorSegundo)) {
    respuesta.end(cuerpo);
    return;
  }
  const trozo = Math.max(1, Math.floor(ritmo.bytesPorSegundo / 10));
  for (let offset = 0; offset < cuerpo.length; offset += trozo) {
    respuesta.write(cuerpo.subarray(offset, offset + trozo));
    await esperar(100);
  }
  respuesta.end();
}

function proxyConRitmo(destino: number): Promise<string> {
  const servidorHttp = createServer((pedido, respuesta) => {
    const saliente = httpRequest(
      {
        hostname: "127.0.0.1",
        port: destino,
        path: pedido.url,
        method: pedido.method,
        headers: { ...pedido.headers, host: `127.0.0.1:${destino}` },
      },
      (entrante: IncomingMessage) => {
        const partes: Buffer[] = [];
        entrante.on("data", (parte: Buffer) => partes.push(parte));
        entrante.on("end", () => {
          void (async () => {
            await esperar(ritmo.latenciaMs);
            const encabezados = { ...entrante.headers };
            delete encabezados["transfer-encoding"];
            respuesta.writeHead(entrante.statusCode ?? 502, encabezados);
            await escribirARitmo(respuesta, Buffer.concat(partes));
          })();
        });
      },
    );
    saliente.on("error", () => {
      if (!respuesta.headersSent) respuesta.writeHead(502);
      respuesta.end();
    });
    pedido.pipe(saliente);
  });
  return new Promise((resolve) => {
    servidorHttp.listen(0, "127.0.0.1", () => {
      const direccion = servidorHttp.address();
      const puerto = typeof direccion === "object" && direccion ? direccion.port : 0;
      resolve(`http://127.0.0.1:${puerto}`);
    });
  });
}

async function asegurarServidor(): Promise<string> {
  if (origen) return origen;
  const puerto = await puertoLibre();
  servidor = spawn(process.execPath, ["scripts/servir.mjs"], {
    cwd: path.resolve("."),
    env: {
      ...process.env,
      PORT: String(puerto),
      DIST_DIR: path.resolve("dist"),
      API_UPSTREAM: "http://127.0.0.1:8000",
    },
    stdio: ["ignore", "pipe", "pipe"],
  });
  await new Promise<void>((resolve, reject) => {
    const limite = setTimeout(() => reject(new Error("El servidor de medición no arrancó")), 15_000);
    const oir = (dato: Buffer) => {
      if (!String(dato).includes("escuchando")) return;
      clearTimeout(limite);
      resolve();
    };
    servidor?.stdout?.on("data", oir);
    servidor?.stderr?.on("data", oir);
    servidor?.on("exit", (codigo) => {
      clearTimeout(limite);
      reject(new Error(`servir terminó con código ${codigo ?? "null"}`));
    });
  });
  origen = await proxyConRitmo(puerto);
  return origen;
}

function esMapa(url: string): boolean {
  return /leaflet|tile\.openstreetmap\.org|\/modo\/mapa/i.test(url);
}

async function entrar(page: Page, base: string): Promise<void> {
  await page.goto(`${base}/login`);
  await page.locator("#email").fill(PRESUPUESTO.email);
  await page.locator("#password").fill(PRESUPUESTO.password);
  await page.getByRole("button", { name: "Entrar" }).click();
  await expect(page).toHaveURL(/\/modo$/);
  await expect(page.getByRole("heading", { name: /Parada 12/ })).toBeVisible();
}

async function medir(page: Page, base: string, red: typeof RED_3G): Promise<Medicion> {
  // Chromium no aplica Network.emulateNetworkConditions a 127.0.0.1.
  // El ritmo lo pone el proxy que está delante de servir.mjs.
  ritmo.bytesPorSegundo = red.bytesPorSegundo;
  ritmo.latenciaMs = red.latenciaMs;
  const cliente = await page.context().newCDPSession(page);
  await cliente.send("Network.enable");
  await cliente.send("Network.setCacheDisabled", { cacheDisabled: true });
  const vistos: string[] = [];
  let bytes = 0;
  const sumar = async (respuesta: Response) => {
    vistos.push(respuesta.url());
    try {
      const tamanos = await respuesta.request().sizes();
      bytes += tamanos.responseBodySize + tamanos.responseHeadersSize;
    } catch {
      /* Alguna respuesta se cancela al cambiar de documento. */
    }
  };
  page.on("response", sumar);
  const inicio = Date.now();
  await page.goto(`${base}/modo`, { waitUntil: "load" });
  await expect(page.locator("ol.lista-paradas")).toBeVisible();
  const milisegundos = Date.now() - inicio;
  page.off("response", sumar);
  const paradas = await page.getByRole("heading", { name: /^Parada \d+\./ }).count();
  return {
    red: red.nombre,
    bytes,
    milisegundos,
    paradas,
    peticionesMapa: vistos.filter(esMapa),
  };
}

test.describe("presupuesto ENB-008", () => {
  test.beforeEach(({ }, info) => {
    test.skip(info.project.name !== "chromium", "La medición de red usa el CDP de Chromium");
  });

  test.afterAll(() => {
    servidor?.kill();
    servidor = null;
    origen = "";
  });

  test("doce paradas caben en 150 KB y la lista precede al mapa", async ({ browser }, info) => {
    const base = await asegurarServidor();
    const contexto = await browser.newContext();
    const pagina = await contexto.newPage();
    await entrar(pagina, base);

    const tresg = await medir(pagina, base, RED_3G);
    expect(tresg.paradas).toBe(12);
    expect(tresg.bytes).toBeLessThanOrEqual(TOPE_BYTES);
    expect(tresg.milisegundos).toBeLessThanOrEqual(TOPE_3G_MS);
    expect(tresg.peticionesMapa).toEqual([]);

    const dosg = await medir(pagina, base, RED_2G);
    expect(dosg.paradas).toBe(12);
    expect(dosg.peticionesMapa).toEqual([]);
    expect(dosg.bytes).toBeLessThanOrEqual(TOPE_BYTES);
    await expect(pagina.locator("ol.lista-paradas")).toBeVisible();

    const mapa: string[] = [];
    pagina.on("request", (pedido) => {
      if (esMapa(pedido.url())) mapa.push(pedido.url());
    });
    await pagina.getByRole("button", { name: "Ver mapa" }).click();
    await expect(pagina.getByRole("region", { name: "Mapa opcional de la ruta" })).toBeVisible();
    await expect.poll(() => mapa.length).toBeGreaterThan(0);
    await pagina.waitForTimeout(3_000);
    await expect(pagina.locator("ol.lista-paradas")).toBeVisible();

    const informe = { tresg, dosg, mapaDespues: mapa };
    const directorio = path.resolve("test-results");
    mkdirSync(directorio, { recursive: true });
    writeFileSync(path.join(directorio, "modo-presupuesto.json"), JSON.stringify(informe, null, 2));
    await info.attach("modo-presupuesto.json", {
      body: JSON.stringify(informe, null, 2),
      contentType: "application/json",
    });
    console.log(`PRESUPUESTO_JSON ${JSON.stringify(informe)}`);
    await contexto.close();
  });
});
