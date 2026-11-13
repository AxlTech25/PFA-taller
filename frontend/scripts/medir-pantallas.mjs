/**
 * Mide cada pantalla en frío con Lighthouse (preset escritorio) y, al final,
 * una sesión que las recorre en orden para el SWDM. El servidor estático y
 * la API tienen que estar ya en marcha.
 *
 *   node frontend/scripts/medir-pantallas.mjs despues
 *
 * Requiere lighthouse y puppeteer-core resolubles (LHCI_NODE_PATH o NODE_PATH).
 */

import { mkdirSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { dirname, join } from "node:path";

const require = createRequire(import.meta.url);
const etiqueta = process.argv[2] || "despues";
const origen = process.env.LHCI_ORIGIN || "http://127.0.0.1:4173";
const salida = process.env.MEDICION_SALIDA || join(
  "docs/03 Implementación/reduccion del impacto ambiental/evidencias",
);
const chrome = process.env.CHROME_PATH || "/usr/bin/google-chrome-stable";
const admin = {
  email: process.env.LHCI_ADMIN_EMAIL || "admin.lhci@distrirapido.example.com",
  password: process.env.AUDITORIA_PASSWORD || "clave-segura",
};
const conductor = {
  email: process.env.LHCI_CONDUCTOR_EMAIL || "conductor.lhci@distrirapido.example.com",
  password: admin.password,
};

const pantallas = [
  ["login", "/login", null],
  ["tablero", "/dashboard", "admin"],
  ["flota", "/flota", "admin"],
  ["conductores", "/conductores", "admin"],
  ["pedidos", "/pedidos", "admin"],
  ["usuarios", "/usuarios", "admin"],
  ["modo", "/modo", "conductor"],
  ["rutas", "/rutas", "admin"],
];

const moduloLighthouse = require("lighthouse");
const lighthouse = moduloLighthouse.default || moduloLighthouse;
const escritorio = require("lighthouse/core/config/desktop-config.js").default;
const puppeteer = require("puppeteer-core");

async function token(pagina, credencial) {
  return pagina.evaluate(async (cuerpo) => {
    const respuesta = await fetch("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(cuerpo),
    });
    if (!respuesta.ok) throw new Error(await respuesta.text());
    return respuesta.json();
  }, credencial);
}

function resumen(lhr) {
  const detalles = lhr.audits["resource-summary"] && lhr.audits["resource-summary"].details;
  const total = (detalles && detalles.items || []).find((item) => item.resourceType === "total") || {
    transferSize: null,
    requestCount: null,
  };
  return {
    url: lhr.finalDisplayedUrl || lhr.finalUrl,
    requestedUrl: lhr.requestedUrl,
    lighthouseVersion: lhr.lighthouseVersion,
    fetchTime: lhr.fetchTime,
    score: lhr.categories.performance.score,
    fcp: lhr.audits["first-contentful-paint"].numericValue,
    lcp: lhr.audits["largest-contentful-paint"].numericValue,
    tbt: lhr.audits["total-blocking-time"].numericValue,
    cls: lhr.audits["cumulative-layout-shift"].numericValue,
    transferSize: total.transferSize,
    requests: total.requestCount,
  };
}

async function preparar(page, sesion) {
  await page.goto(`${origen}/login`, { waitUntil: "domcontentloaded" });
  await page.evaluate((datos) => {
    sessionStorage.removeItem("ecologistica.sesion");
    if (datos) sessionStorage.setItem("ecologistica.sesion", JSON.stringify(datos));
  }, sesion);
  const cliente = await page.createCDPSession();
  await cliente.send("Network.clearBrowserCache");
}

const browser = await puppeteer.launch({
  executablePath: chrome,
  args: ["--no-sandbox", "--disable-gpu", "--headless=new"],
});
mkdirSync(salida, { recursive: true });
const paginaLogin = await browser.newPage();
await paginaLogin.goto(`${origen}/login`, { waitUntil: "domcontentloaded" });
const sesionAdmin = await token(paginaLogin, admin);
const sesionConductor = await token(paginaLogin, conductor);
await paginaLogin.close();

const filas = [];
for (const [id, camino, rol] of pantallas) {
  const page = await browser.newPage();
  const sesion = rol === "admin" ? sesionAdmin : rol === "conductor" ? sesionConductor : null;
  await preparar(page, sesion);
  const resultado = await lighthouse(`${origen}${camino}`, {
    logLevel: "error",
    output: ["json", "html"],
    disableStorageReset: true,
    onlyCategories: ["performance"],
  }, escritorio, page);
  const json = resultado.report[0];
  const html = resultado.report[1];
  writeFileSync(join(salida, `lighthouse-${etiqueta}-${id}.json`), json);
  writeFileSync(join(salida, `lighthouse-${etiqueta}-${id}.html`), html);
  const fila = { id, camino, ...resumen(JSON.parse(json)) };
  filas.push(fila);
  console.log(id, fila.score, Math.round(fila.fcp), Math.round(fila.lcp), fila.tbt, fila.cls, fila.transferSize, fila.requests, fila.url);
  await page.close();
}

const recorrido = await browser.newPage();
const cdp = await recorrido.createCDPSession();
await cdp.send("Network.enable");
let transferido = 0;
const porTipo = [];
cdp.on("Network.loadingFinished", (evento) => {
  transferido += evento.encodedDataLength || 0;
});
cdp.on("Network.responseReceived", (evento) => {
  porTipo.push({
    url: evento.response.url,
    type: evento.type,
    encoded: evento.response.encodedDataLength,
    status: evento.response.status,
  });
});
await preparar(recorrido, null);
for (const [id, camino, rol] of pantallas) {
  const sesion = rol === "admin" ? sesionAdmin : rol === "conductor" ? sesionConductor : null;
  if (id !== "login") {
    await recorrido.evaluate((datos) => {
      sessionStorage.setItem("ecologistica.sesion", JSON.stringify(datos));
    }, sesion);
  }
  const antes = transferido;
  await recorrido.goto(`${origen}${camino}`, { waitUntil: "load", timeout: 60000 });
  await new Promise((resolver) => setTimeout(resolver, 2500));
  console.log("sesion", id, transferido - antes);
}
const informe = { etiqueta, origen, pantallas: filas, sesionBytes: transferido, respuestas: porTipo.length };
writeFileSync(join(salida, `lighthouse-${etiqueta}-resumen.json`), JSON.stringify(informe, null, 2));
console.log("SESION", transferido);
await browser.close();
