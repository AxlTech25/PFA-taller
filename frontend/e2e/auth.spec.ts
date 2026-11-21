import { expect, test } from "@playwright/test";

import { ADMIN, entrar } from "./helpers";

const PRIVADAS = ["/flota", "/conductores", "/pedidos", "/rutas", "/dashboard", "/modo"];

test("el inicio de sesión válido abre la flota", async ({ page }) => {
  await entrar(page);
  await expect(page.getByText(ADMIN.email)).toBeVisible();
  await expect(page.getByText("Administrador")).toBeVisible();
  await expect(page.getByRole("navigation", { name: "Módulos" }).getByRole("link", { name: "Flota" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Cerrar sesión" })).toBeVisible();
});

test("las credenciales inválidas muestran el error y no abren la sesión", async ({ page }) => {
  await page.goto("/login");
  await page.locator("#email").fill("nadie@distrirapido.example.com");
  await page.locator("#password").fill("clave-incorrecta");
  await page.getByRole("button", { name: "Entrar" }).click();
  await expect(page.locator("#alerta-login")).toContainText("Credenciales inválidas");
  await expect(page).toHaveURL(/\/login$/);
  await expect(page.getByRole("heading", { name: "EcoLogística Lima" })).toBeVisible();
});

test("una ruta protegida sin sesión vuelve al login", async ({ page }) => {
  for (const ruta of PRIVADAS) {
    await page.goto(ruta);
    await expect(page).toHaveURL(/\/login$/);
    await expect(page.getByRole("heading", { name: "EcoLogística Lima" })).toBeVisible();
  }
});

test("el login exige correo y contraseña antes de llamar a la API", async ({ page }) => {
  await page.goto("/login");
  await page.getByRole("button", { name: "Entrar" }).click();
  const mensaje = await page.locator("#email").evaluate((campo: HTMLInputElement) => campo.validationMessage);
  expect(mensaje.length).toBeGreaterThan(0);
  await expect(page.locator("#alerta-login")).toHaveCount(0);
  await expect(page).toHaveURL(/\/login$/);
});
