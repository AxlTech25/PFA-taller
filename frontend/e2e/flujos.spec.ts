import { expect, test, type APIRequestContext, type Page } from "@playwright/test";

import { dniNuevo, entrar, ir, placaNueva } from "./helpers";

async function tokenDe(page: Page): Promise<string> {
  const token = await page.evaluate(() => {
    const crudo = sessionStorage.getItem("ecologistica.sesion");
    if (!crudo) return "";
    return (JSON.parse(crudo) as { access_token?: string }).access_token ?? "";
  });
  expect(token.length).toBeGreaterThan(10);
  return token;
}

async function flotaIncluye(request: APIRequestContext, token: string, placa: string): Promise<boolean> {
  for (let pagina = 1; pagina <= 8; pagina += 1) {
    const respuesta = await request.get(`/vehiculos?page=${pagina}&limite=50`, {
      headers: { Accept: "application/json", Authorization: `Bearer ${token}` },
    });
    expect(respuesta.status()).toBe(200);
    const cuerpo = (await respuesta.json()) as {
      items: { placa: string }[];
      total_pages: number;
    };
    if (cuerpo.items.some((item) => item.placa === placa)) return true;
    if (pagina >= cuerpo.total_pages) break;
  }
  return false;
}

test("la flota lista las unidades de demostración y registra otra", async ({ page, request }, info) => {
  await entrar(page);
  await expect(page.getByRole("heading", { name: "Unidades registradas" })).toBeVisible();
  await expect(page.locator("table tbody tr").first()).toBeVisible();
  expect(await flotaIncluye(request, await tokenDe(page), "DMO-101")).toBe(true);
  await expect(page.getByRole("heading", { name: "Registrar vehículo" })).toBeVisible();

  const placa = placaNueva(info.project.name);
  await page.locator("#placa").fill(placa);
  await page.locator("#capacidad_kg").fill("800");
  await page.locator("#capacidad_m3").fill("4");
  await page.locator("#consumo_km_l").fill("11");
  await page.locator("#factor_emision_co2").fill("0.25");
  await page.getByRole("button", { name: "Registrar vehículo" }).click();
  await expect(page.locator("output.exito")).toContainText("Vehículo registrado correctamente");
  await expect(page.getByRole("cell", { name: placa, exact: true })).toBeVisible();

  await page.getByLabel(`Factor de emisión de ${placa}`).fill("0.26");
  await page.getByRole("button", { name: `Guardar ${placa}` }).click();
  await expect(page.locator("output.exito")).toContainText("Vehículo actualizado correctamente");
});

test("conductores muestra el alta y deja registrado un conductor", async ({ page }) => {
  await entrar(page);
  await ir(page, "Conductores");
  await expect(page).toHaveURL(/\/conductores$/);
  await expect(page.getByRole("heading", { level: 1, name: "Conductores" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Registrar conductor" })).toBeVisible();

  const dni = dniNuevo();
  await page.locator("#nombre").fill(`Conductor E2E ${dni}`);
  await page.locator("#dni").fill(dni);
  await page.getByRole("button", { name: "Registrar conductor" }).click();
  await expect(page.locator("output.exito")).toContainText("Conductor registrado correctamente");
  await expect(page.getByRole("cell", { name: dni, exact: true })).toBeVisible();
});

test("pedidos ofrece los clientes de demostración y registra una entrega", async ({ page }) => {
  await entrar(page);
  await ir(page, "Pedidos");
  await expect(page).toHaveURL(/\/pedidos$/);
  await expect(page.getByRole("heading", { level: 1, name: "Pedidos" })).toBeVisible();
  await expect(page.locator("#id_cliente")).toBeVisible();
  await page.locator("#id_cliente").selectOption({ label: "Bodega El Ahorro — con consentimiento" });
  await page.locator("#peso_kg").fill("12.5");
  await page.locator("#volumen_m3").fill("0.4");
  const referencia = `E2E ${Date.now().toString().slice(-6)}`;
  await page.locator("#direccion").fill("Jr. Los Pinos 123");
  await page.locator("#punto_referencia").fill(referencia);
  await page.getByRole("button", { name: "Registrar pedido" }).click();
  await expect(page.locator("output.exito")).toContainText("Pedido registrado correctamente");
  const fila = page.getByRole("row", { name: new RegExp(referencia) });
  await expect(fila).toContainText("Bodega El Ahorro");
  await expect(fila).toContainText("San Juan de Lurigancho");
  await expect(fila).toContainText(`${referencia} (aproximada)`);
  await expect(fila).toContainText("Pendiente");
});

test("rutas encola la optimización del día y muestra el resultado", async ({ page }) => {
  await entrar(page);
  await ir(page, "Rutas");
  await expect(page).toHaveURL(/\/rutas$/);
  await expect(page.getByRole("heading", { level: 1, name: "Rutas" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Generar plan del día" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Mapa del plan" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Plan generado" })).toBeVisible();

  await page.locator("#fecha").fill("2099-01-01");
  await expect(page.locator("#fecha")).toHaveValue("2099-01-01");
  await page.getByRole("button", { name: "Generar rutas" }).click();
  await expect(page.locator("#alerta-rutas")).toContainText("No hay pedidos pendientes", {
    timeout: 20_000,
  });
});

test("el tablero consulta el período y responde sin datos de operación", async ({ page }) => {
  await entrar(page);
  await ir(page, "Tablero");
  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(page.getByRole("heading", { level: 1, name: "Tablero" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Período" })).toBeVisible();
  // Hoy puede tener la ruta de demostración del conductor. El período vacío es otro día.
  await page.locator("#fecha-tablero").fill("2099-01-01");
  await expect(page.locator("#fecha-tablero")).toHaveValue("2099-01-01");
  await expect(page.locator("output.aviso")).toContainText("Sin datos de operación para el período seleccionado.");
  await page.getByRole("button", { name: "Consultar" }).click();
  await expect(page.locator("output.aviso")).toContainText("Sin datos de operación para el período seleccionado.");
});
