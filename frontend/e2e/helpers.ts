import { expect, type Page } from "@playwright/test";

export const ADMIN = {
  email: process.env.E2E_ADMIN_EMAIL ?? "admin@distrirapido.example.com",
  password: process.env.E2E_ADMIN_PASSWORD ?? "AdminDemo1",
};

let consecutivo = 0;

export function placaNueva(proyecto: string): string {
  consecutivo += 1;
  const marca = proyecto.replace(/[^a-z]/gi, "").slice(0, 1).toUpperCase() || "E";
  const cola = `${Date.now() % 1_000_000}${consecutivo}`.slice(-8);
  return `${marca}${cola}`.slice(0, 10);
}

export function dniNuevo(): string {
  consecutivo += 1;
  return String((Date.now() + consecutivo) % 100_000_000).padStart(8, "0");
}

export function fechaLima(ahora = new Date()): string {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: "America/Lima",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(ahora);
}

export async function entrar(page: Page): Promise<void> {
  await page.goto("/login");
  await page.locator("#email").fill(ADMIN.email);
  await page.locator("#password").fill(ADMIN.password);
  await page.getByRole("button", { name: "Entrar" }).click();
  await expect(page).toHaveURL(/\/flota$/);
  await expect(page.getByRole("heading", { level: 1, name: "Flota" })).toBeVisible();
}

export async function ir(page: Page, nombre: string): Promise<void> {
  await page
    .getByRole("navigation", { name: "Módulos" })
    .getByRole("link", { name: nombre, exact: true })
    .click();
}
