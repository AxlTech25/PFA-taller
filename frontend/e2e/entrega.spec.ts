import AxeBuilder from "@axe-core/playwright";
import { expect, test, type APIRequestContext, type Page } from "@playwright/test";

import { CONDUCTOR, PRESUPUESTO } from "./helpers";

// US-018. Usa la ruta de 12 paradas del conductor de presupuesto: cada navegador
// (y cada reintento) confirma las dos siguientes paradas pendientes, así la ruta
// de tres paradas del conductor de demostración queda intacta para modo.spec.ts.

type Parada = { secuencia: number; id_detalle: string; estado_entrega: string };

async function entrarPresupuesto(page: Page): Promise<void> {
  await page.goto("/login");
  await page.locator("#email").fill(PRESUPUESTO.email);
  await page.locator("#password").fill(PRESUPUESTO.password);
  await page.getByRole("button", { name: "Entrar" }).click();
  await expect(page).toHaveURL(/\/modo$/);
  await expect(page.locator("ol.lista-paradas")).toBeVisible();
}

async function token(request: APIRequestContext, cuenta: { email: string; password: string }) {
  const sesion = await request.post("/auth/login", {
    data: { email: cuenta.email, password: cuenta.password },
  });
  expect(sesion.status()).toBe(200);
  return (await sesion.json()).access_token as string;
}

async function paradas(request: APIRequestContext, clave: string): Promise<Parada[]> {
  const jornada = await request.get("/modo/jornada", {
    headers: { Accept: "application/json", Authorization: `Bearer ${clave}` },
  });
  expect(jornada.status()).toBe(200);
  return (await jornada.json()).paradas as Parada[];
}

async function siguientePendiente(page: Page): Promise<{ numero: number; etiqueta: string }> {
  const boton = page.getByRole("button", { name: /^Confirmar entrega de la parada \d+,/ }).first();
  await expect(boton).toBeVisible();
  const etiqueta = (await boton.getAttribute("aria-label")) ?? "";
  const numero = Number(/parada (\d+),/.exec(etiqueta)?.[1]);
  expect(numero).toBeGreaterThan(0);
  return { numero, etiqueta };
}

test("el conductor registra una entrega y un fallo con motivo", async ({ page, request }) => {
  await entrarPresupuesto(page);

  const entregada = await siguientePendiente(page);
  const botonEntregada = page.getByRole("button", { name: entregada.etiqueta, exact: true });
  await botonEntregada.focus();
  await page.keyboard.press("Enter");
  const formulario = page.getByRole("form", { name: `Resultado de la parada ${entregada.numero}` });
  await expect(formulario.getByRole("radio", { name: "Entregado" })).toBeChecked();
  await formulario.getByRole("button", { name: "Guardar resultado" }).click();
  const avisoEntregada = page.getByText(
    new RegExp(`^Parada ${entregada.numero}, .*: registrada como entregada\\.$`),
  );
  await expect(avisoEntregada).toBeVisible();
  await expect(avisoEntregada).toBeFocused();
  await expect(botonEntregada).toHaveCount(0);
  const tarjeta = page.locator("article.parada-conductor", {
    has: page.getByRole("heading", { name: new RegExp(`^Parada ${entregada.numero}\\.`) }),
  });
  await expect(tarjeta.locator(".insignia.ENTREGADO")).toHaveText("Entregado");

  const fallida = await siguientePendiente(page);
  expect(fallida.numero).toBeGreaterThan(entregada.numero);
  await page.getByRole("button", { name: fallida.etiqueta, exact: true }).click();
  await page.getByRole("radio", { name: "Fallido" }).check();
  await page.getByRole("button", { name: "Guardar resultado" }).click();
  const motivo = page.getByRole("textbox", { name: "Motivo del fallo (obligatorio)" });
  await expect(page.getByText("Indique el motivo cuando la entrega es fallida.")).toBeVisible();
  await expect(motivo).toBeFocused();
  await motivo.fill("Cliente ausente (prueba e2e)");
  const resultado = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"])
    .analyze();
  expect(resultado.violations).toEqual([]);
  await page.getByRole("button", { name: "Guardar resultado" }).click();
  await expect(
    page.getByText(new RegExp(`^Parada ${fallida.numero}, .*: registrada como fallida\\.$`)),
  ).toBeVisible();
  await expect(page.getByText("Motivo: Cliente ausente (prueba e2e)").first()).toBeVisible();

  // Tras recargar, la lista sale de la base de datos con los dos resultados.
  await page.reload();
  await expect(page.locator("ol.lista-paradas")).toBeVisible();
  await expect(page.getByRole("button", { name: entregada.etiqueta, exact: true })).toHaveCount(0);
  await expect(page.getByRole("button", { name: fallida.etiqueta, exact: true })).toHaveCount(0);

  const clave = await token(request, PRESUPUESTO);
  const lista = await paradas(request, clave);
  const porNumero = new Map(lista.map((parada) => [parada.secuencia, parada]));
  expect(porNumero.get(entregada.numero)?.estado_entrega).toBe("ENTREGADO");
  expect(porNumero.get(fallida.numero)?.estado_entrega).toBe("FALLIDO");

  const repetida = await request.post(
    `/modo/paradas/${porNumero.get(entregada.numero)?.id_detalle}/confirmacion`,
    { headers: { Authorization: `Bearer ${clave}` }, data: { resultado: "ENTREGADO" } },
  );
  expect(repetida.status()).toBe(409);
});

test("otro conductor recibe 403 y una parada inexistente 404", async ({ request }) => {
  const propia = await token(request, PRESUPUESTO);
  const ajena = await token(request, CONDUCTOR);
  const lista = await paradas(request, propia);
  const pendiente = lista.find((parada) => parada.estado_entrega === "PENDIENTE") ?? lista[0];

  const intruso = await request.post(`/modo/paradas/${pendiente.id_detalle}/confirmacion`, {
    headers: { Authorization: `Bearer ${ajena}` },
    data: { resultado: "ENTREGADO" },
  });
  expect(intruso.status()).toBe(403);

  const inexistente = await request.post(
    "/modo/paradas/00000000-0000-4000-8000-000000000000/confirmacion",
    { headers: { Authorization: `Bearer ${propia}` }, data: { resultado: "ENTREGADO" } },
  );
  expect(inexistente.status()).toBe(404);

  const despues = await paradas(request, propia);
  expect(despues.find((parada) => parada.id_detalle === pendiente.id_detalle)?.estado_entrega).toBe(
    pendiente.estado_entrega,
  );
});
