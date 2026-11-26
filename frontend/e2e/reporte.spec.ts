import { readFile } from "node:fs/promises";

import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

import { CONDUCTOR, entrar, fechaLima, ir } from "./helpers";

const ETIQUETAS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"];

test("el tablero descarga el reporte PDF del período con teclado (US-016)", async ({ page }) => {
  await entrar(page);
  await ir(page, "Tablero");
  await expect(page.getByRole("heading", { name: "Reporte PDF de sostenibilidad" })).toBeVisible();

  // Hoy siempre tiene las rutas de demostración que siembra la API.
  const hoy = fechaLima();
  await page.getByLabel("Desde").fill(hoy);
  await page.getByLabel("Hasta").fill(hoy);
  const boton = page.getByRole("button", { name: "Descargar reporte PDF" });
  await boton.focus();
  const descarga = page.waitForEvent("download");
  await page.keyboard.press("Enter");
  const archivo = await descarga;
  expect(archivo.suggestedFilename()).toBe(`reporte-sostenibilidad-${hoy}_${hoy}.pdf`);
  const ruta = await archivo.path();
  const contenido = await readFile(ruta);
  expect(contenido.subarray(0, 5).toString("latin1")).toBe("%PDF-");
  expect(contenido.length).toBeGreaterThan(1000);
  await expect(page.locator("output.exito")).toContainText("Reporte listo");

  const axe = await new AxeBuilder({ page }).withTags(ETIQUETAS).analyze();
  expect(axe.violations).toEqual([]);

  // Período sin rutas: se informa y no se genera archivo.
  let descargas = 0;
  page.on("download", () => {
    descargas += 1;
  });
  await page.getByLabel("Desde").fill("2099-01-01");
  await page.getByLabel("Hasta").fill("2099-01-31");
  await boton.click();
  await expect(page.locator("#alerta-reporte")).toContainText(
    "Sin datos de operación para el período seleccionado.",
  );
  expect(descargas).toBe(0);
  const axeVacio = await new AxeBuilder({ page }).withTags(ETIQUETAS).analyze();
  expect(axeVacio.violations).toEqual([]);
});

test("el conductor no puede descargar el reporte (403)", async ({ request }) => {
  const sesion = await request.post("/auth/login", {
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    data: { email: CONDUCTOR.email, password: CONDUCTOR.password },
  });
  expect(sesion.status()).toBe(200);
  const token = ((await sesion.json()) as { access_token: string }).access_token;
  const hoy = fechaLima();
  const respuesta = await request.get(`/indicadores/reporte.pdf?desde=${hoy}&hasta=${hoy}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  expect(respuesta.status()).toBe(403);
});
