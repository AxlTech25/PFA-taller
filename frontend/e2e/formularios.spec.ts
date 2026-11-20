import { expect, test } from "@playwright/test";

import { dniNuevo, entrar, ir, placaNueva } from "./helpers";

test("flota no envía el alta si falta la placa", async ({ page }) => {
  await entrar(page);
  await page.getByRole("button", { name: "Registrar vehículo" }).click();
  const mensaje = await page.locator("#placa").evaluate((campo: HTMLInputElement) => campo.validationMessage);
  expect(mensaje.length).toBeGreaterThan(0);
  await expect(page.locator("#alerta-flota")).toHaveCount(0);
  await expect(page.locator("output.exito")).toHaveCount(0);
});

test("un año de fabricación inválido llega como HTTP 422", async ({ page }, info) => {
  await entrar(page);
  await page.locator("#placa").fill(placaNueva(info.project.name));
  await page.locator("#capacidad_kg").fill("100");
  await page.locator("#capacidad_m3").fill("1");
  await page.locator("#consumo_km_l").fill("10");
  await page.locator("#factor_emision_co2").fill("0.2");
  await page.locator("#anio_fabricacion").evaluate((campo: HTMLInputElement) => {
    campo.min = "";
    campo.max = "";
  });
  await page.locator("#anio_fabricacion").fill("1800");
  await page.getByRole("button", { name: "Registrar vehículo" }).click();
  await expect(page.locator("#alerta-flota")).toContainText("año");
});

test("un DNI incompleto lo detiene el navegador", async ({ page }) => {
  await entrar(page);
  await ir(page, "Conductores");
  await page.locator("#nombre").fill("Ana Prueba");
  await page.locator("#dni").fill("123");
  await page.getByRole("button", { name: "Registrar conductor" }).click();
  const mensaje = await page.locator("#dni").evaluate((campo: HTMLInputElement) => campo.validationMessage);
  expect(mensaje.length).toBeGreaterThan(0);
  await expect(page.locator("#alerta-conductores")).toHaveCount(0);
});

test("una latitud imposible de conductor responde HTTP 422", async ({ page }) => {
  await entrar(page);
  await ir(page, "Conductores");
  await page.locator("#nombre").fill("Ana Latitud");
  await page.locator("#dni").fill(dniNuevo());
  await page.locator("#lat_punto_partida").fill("999");
  await page.getByRole("button", { name: "Registrar conductor" }).click();
  await expect(page.locator("#alerta-conductores")).toContainText(/latitud/i);
});

test("un horario invertido de conductor responde HTTP 422", async ({ page }) => {
  await entrar(page);
  await ir(page, "Conductores");
  await page.locator("#nombre").fill("Ana Horario");
  await page.locator("#dni").fill(dniNuevo());
  await page.locator("#disponibilidad_inicio").fill("18:00");
  await page.locator("#disponibilidad_fin").fill("08:00");
  await page.getByRole("button", { name: "Registrar conductor" }).click();
  await expect(page.locator("#alerta-conductores")).toContainText(/hora/i);
});

test("pedidos exige el peso antes de enviar", async ({ page }) => {
  await entrar(page);
  await ir(page, "Pedidos");
  await expect(page.locator("#id_cliente option")).not.toHaveCount(0);
  await page.getByRole("button", { name: "Registrar pedido" }).click();
  const mensaje = await page.locator("#peso_kg").evaluate((campo: HTMLInputElement) => campo.validationMessage);
  expect(mensaje.length).toBeGreaterThan(0);
  await expect(page.locator("#alerta-pedidos")).toHaveCount(0);
});

test("una ventana de pedido invertida se explica sin salir de la pantalla", async ({ page }) => {
  await entrar(page);
  await ir(page, "Pedidos");
  await page.locator("#peso_kg").fill("4");
  await page.locator("#volumen_m3").fill("0.2");
  await page.locator("#ventana_inicio").fill("2026-11-20T18:00");
  await page.locator("#ventana_fin").fill("2026-11-20T08:00");
  await page.getByRole("button", { name: "Registrar pedido" }).click();
  await expect(page.locator("#alerta-pedidos")).toContainText(
    "La ventana de inicio debe ser anterior a la ventana de fin.",
  );
});

test("un pedido sin consentimiento responde HTTP 422", async ({ page }) => {
  await entrar(page);
  await ir(page, "Pedidos");
  await page.locator("#id_cliente").selectOption({ label: "Bodega Los Pinos — sin consentimiento" });
  await page.locator("#peso_kg").fill("4");
  await page.locator("#volumen_m3").fill("0.2");
  await page.getByRole("button", { name: "Registrar pedido" }).click();
  await expect(page.locator("#alerta-pedidos")).toContainText("consentimiento");
});

test("una latitud imposible de pedido responde HTTP 422", async ({ page }) => {
  await entrar(page);
  await ir(page, "Pedidos");
  await page.locator("#id_cliente").selectOption({ label: "Bodega El Ahorro — con consentimiento" });
  await page.locator("#peso_kg").fill("4");
  await page.locator("#volumen_m3").fill("0.2");
  await page.locator("#latitud").fill("999");
  await page.getByRole("button", { name: "Registrar pedido" }).click();
  await expect(page.locator("#alerta-pedidos")).toContainText(/latitud/i);
});
