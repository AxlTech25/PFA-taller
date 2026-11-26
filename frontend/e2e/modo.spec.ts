import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

import { ADMIN, CONDUCTOR, entrarConductor } from "./helpers";

test("el conductor ve su ruta del día y abre confirmar entrega sin guardar", async ({ page }) => {
  const posts: string[] = [];
  page.on("request", (request) => {
    if (request.method() === "POST" && request.url().includes("/modo/")) {
      posts.push(request.url());
    }
  });

  await entrarConductor(page);
  await expect(page.getByRole("navigation", { name: "Módulos" }).getByRole("link", { name: "Tablero" })).toHaveCount(0);
  await expect(page.getByRole("navigation", { name: "Módulos" }).getByRole("link", { name: "Rutas" })).toHaveCount(0);
  await expect(page.getByRole("heading", { name: /Parada 1/ })).toBeVisible();
  await expect(page.getByText("08:15")).toBeVisible();
  await expect(page.getByText("10:40")).toBeVisible();
  await expect(page.getByText("12:20")).toBeVisible();
  await expect(page.getByText("Parada 1: semáforo amarillo en la llegada estimada.")).toBeVisible();
  await expect(page.getByText(/fuera de la ventana/)).toBeVisible();
  await expect(page.getByText("Av. Próceres de la Independencia 2450")).toBeVisible();
  await expect(page.getByText(/Aviso de demostración/)).toBeVisible();
  await expect(page.getByText("Siguiente entrega")).toBeVisible();
  await expect(page.getByText(/CO₂/)).toHaveCount(0);

  const boton = page.getByRole("button", {
    name: "Confirmar entrega de la parada 1, Bodega El Ahorro",
  });
  await boton.focus();
  await expect(boton).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(boton).toHaveAttribute("aria-expanded", "true");
  const formulario = page.getByRole("form", { name: "Resultado de la parada 1" });
  await expect(formulario).toBeVisible();
  await expect(formulario.getByRole("radio", { name: "Entregado" })).toBeChecked();
  await page.keyboard.press("Escape");
  await expect(formulario).toHaveCount(0);
  await expect(boton).toBeFocused();
  await expect(page.getByText("Pendiente").first()).toBeVisible();
  expect(posts).toEqual([]);
});

test("la jornada solo la ve el conductor y pesa menos de 150 KB", async ({ request }) => {
  const anonimo = await request.get("/modo/jornada", { headers: { Accept: "application/json" } });
  expect(anonimo.status()).toBe(401);

  const admin = await request.post("/auth/login", {
    data: { email: ADMIN.email, password: ADMIN.password },
  });
  expect(admin.status()).toBe(200);
  const tokenAdmin = (await admin.json()).access_token as string;
  const ajena = await request.get("/modo/jornada", {
    headers: { Accept: "application/json", Authorization: `Bearer ${tokenAdmin}` },
  });
  expect(ajena.status()).toBe(403);

  const sesion = await request.post("/auth/login", {
    data: { email: CONDUCTOR.email, password: CONDUCTOR.password },
  });
  expect(sesion.status()).toBe(200);
  const token = (await sesion.json()).access_token as string;
  const jornada = await request.get("/modo/jornada", {
    headers: { Accept: "application/json", Authorization: `Bearer ${token}` },
  });
  expect(jornada.status()).toBe(200);
  expect((await jornada.body()).length).toBeLessThanOrEqual(150 * 1024);
  const cuerpo = await jornada.json();
  expect(cuerpo.hay_ruta).toBe(true);
  expect(cuerpo.paradas).toHaveLength(3);
  expect(cuerpo).not.toHaveProperty("co2_estimado_kg");
  expect(cuerpo).not.toHaveProperty("distancia_total_km");
  expect(cuerpo.paradas[0]).not.toHaveProperty("latitud");
});

test("el teclado llega a confirmar entrega antes que al mapa", async ({ page }) => {
  await entrarConductor(page);
  const vistos: string[] = [];
  for (let paso = 0; paso < 16; paso += 1) {
    await page.keyboard.press("Tab");
    const actual = await page.evaluate(() => {
      const nodo = document.activeElement;
      if (!nodo) return "";
      return (nodo.getAttribute("aria-label") || nodo.textContent || "").replace(/\s+/g, " ").trim();
    });
    vistos.push(actual);
    if (actual.includes("Confirmar entrega de la parada 1")) break;
  }
  expect(vistos.at(-1)).toContain("Confirmar entrega de la parada 1");
  expect(vistos.some((nombre) => nombre.startsWith("Ver mapa"))).toBe(false);
  const anillo = await page.evaluate(() => {
    const nodo = document.activeElement as HTMLElement | null;
    if (!nodo) return { estilo: "none", ancho: "0px" };
    const estilo = getComputedStyle(nodo);
    return { estilo: estilo.outlineStyle, ancho: estilo.outlineWidth };
  });
  expect(anillo.estilo).not.toBe("none");
  expect(Number.parseFloat(anillo.ancho)).toBeGreaterThanOrEqual(2);
  const caja = await page.evaluate(() => {
    const nodo = document.activeElement as HTMLElement | null;
    if (!nodo) return null;
    const rect = nodo.getBoundingClientRect();
    const estilo = getComputedStyle(nodo);
    return {
      ancho: Math.round(rect.width),
      alto: Math.round(rect.height),
      outlineWidth: estilo.outlineWidth,
      outlineStyle: estilo.outlineStyle,
      outlineColor: estilo.outlineColor,
    };
  });
  console.log(`FOCO_JSON ${JSON.stringify(caja)}`);
  await page.keyboard.press("Enter");
  await expect(page.getByRole("form", { name: "Resultado de la parada 1" })).toBeVisible();
  for (let paso = 0; paso < 14; paso += 1) {
    await page.keyboard.press("Tab");
    const actual = await page.evaluate(() => document.activeElement?.textContent?.replace(/\s+/g, " ").trim() ?? "");
    if (actual === "Ver mapa") break;
  }
  await expect(page.getByRole("button", { name: "Ver mapa" })).toBeFocused();
});

test("el modo conductor no tiene violaciones WCAG 2.2 AA", async ({ page }) => {
  await entrarConductor(page);
  await expect(page.getByRole("button", { name: /Confirmar entrega de la parada 1/ })).toBeVisible();
  const resultado = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"])
    .analyze();
  expect(resultado.violations).toEqual([]);

  await page.getByRole("button", { name: /Confirmar entrega de la parada 1/ }).click();
  await page.getByRole("radio", { name: "Fallido" }).check();
  await page.getByRole("button", { name: "Guardar resultado" }).click();
  await expect(page.getByText("Indique el motivo cuando la entrega es fallida.")).toBeVisible();
  const conFormulario = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"])
    .analyze();
  expect(conFormulario.violations).toEqual([]);
  for (const nombre of ["Entregado", "Fallido"]) {
    const caja = await page.locator("label.opcion-entrega", { hasText: nombre }).boundingBox();
    expect(caja?.height ?? 0).toBeGreaterThanOrEqual(44);
  }
  for (const nombre of ["Guardar resultado", "Cancelar"]) {
    const caja = await page.getByRole("button", { name: nombre }).boundingBox();
    expect(caja?.height ?? 0).toBeGreaterThanOrEqual(44);
  }
});
