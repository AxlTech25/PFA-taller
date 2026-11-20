import { expect, test } from "@playwright/test";

import { ADMIN, entrar } from "./helpers";

test("los documentos y la API responden los códigos esperados", async ({ request }) => {
  const login = await request.get("/login");
  expect(login.status()).toBe(200);

  for (const ruta of ["/flota", "/conductores", "/pedidos", "/rutas", "/dashboard"]) {
    const documento = await request.get(ruta, { headers: { Accept: "text/html" } });
    expect(documento.status(), ruta).toBe(200);
    expect(await documento.text()).toContain('id="root"');
  }

  const salud = await request.get("/health", { headers: { Accept: "application/json" } });
  expect(salud.status()).toBe(200);
  expect(await salud.json()).toMatchObject({ status: "ok" });

  const contrato = await request.get("/openapi.json", { headers: { Accept: "application/json" } });
  expect(contrato.status()).toBe(200);

  const anonimo = await request.get("/vehiculos?page=1&limite=12", {
    headers: { Accept: "application/json" },
  });
  expect(anonimo.status()).toBe(401);

  const credenciales = await request.post("/auth/login", {
    data: { email: "nadie@distrirapido.example.com", password: "clave-incorrecta" },
  });
  expect(credenciales.status()).toBe(401);

  const sesion = await request.post("/auth/login", {
    data: { email: ADMIN.email, password: ADMIN.password },
  });
  expect(sesion.status()).toBe(200);
  const token = (await sesion.json()).access_token as string;
  const flota = await request.get("/vehiculos?page=1&limite=12", {
    headers: { Accept: "application/json", Authorization: `Bearer ${token}` },
  });
  expect(flota.status()).toBe(200);

  const horario = await request.post("/conductores", {
    headers: { Authorization: `Bearer ${token}` },
    data: {
      nombre: "Integracion horario",
      dni: "87654321",
      licencia_categoria: "A-IIIb",
      anios_experiencia: 1,
      disponibilidad_inicio: "18:00",
      disponibilidad_fin: "08:00",
      lat_punto_partida: -12.01,
      lon_punto_partida: -76.98,
    },
  });
  expect(horario.status()).toBe(422);
});

test("un HTTP 500 de la flota se muestra sin romper la pantalla", async ({ page }) => {
  await entrar(page);
  await page.route("**/vehiculos**", (route) =>
    route.fulfill({
      status: 500,
      contentType: "application/json",
      body: JSON.stringify({ detail: "Fallo controlado de prueba" }),
    }),
  );
  await page.goto("/flota");
  await expect(page.getByRole("heading", { level: 1, name: "Flota" })).toBeVisible();
  await expect(page.locator("#alerta-flota")).toContainText("Fallo controlado de prueba");
});

test("si la red corta los conductores, la pantalla avisa y sigue en pie", async ({ page }) => {
  await entrar(page);
  await page.route("**/conductores**", async (route) => {
    if (route.request().resourceType() === "document") {
      await route.continue();
      return;
    }
    await route.abort("failed");
  });
  await page.goto("/conductores");
  await expect(page.getByRole("heading", { level: 1, name: "Conductores" })).toBeVisible();
  await expect(page.locator("#alerta-conductores")).toContainText("No se pudo cargar los conductores.");
});

test("un HTTP 422 simulado en el alta de flota queda en la alerta", async ({ page }, info) => {
  await entrar(page);
  await page.route("**/vehiculos", async (route) => {
    if (route.request().method() !== "POST") {
      await route.continue();
      return;
    }
    await route.fulfill({
      status: 422,
      contentType: "application/json",
      body: JSON.stringify({ detail: "El año de fabricación no es válido" }),
    });
  });
  await page.locator("#placa").fill(`Z${info.project.name.slice(0, 1).toUpperCase()}422`);
  await page.locator("#capacidad_kg").fill("100");
  await page.locator("#capacidad_m3").fill("1");
  await page.locator("#consumo_km_l").fill("10");
  await page.locator("#factor_emision_co2").fill("0.2");
  await page.getByRole("button", { name: "Registrar vehículo" }).click();
  await expect(page.locator("#alerta-flota")).toContainText("El año de fabricación no es válido");
  await expect(page.getByRole("heading", { level: 1, name: "Flota" })).toBeVisible();
});
