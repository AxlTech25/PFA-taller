import { expect, test } from "@playwright/test";

import { ADMIN, CONDUCTOR, entrarConductor } from "./helpers";

test("el conductor ve su ruta del día y confirma sin guardar", async ({ page }) => {
  const posts: string[] = [];
  page.on("request", (request) => {
    if (request.method() === "POST" && request.url().includes("/modo/jornada")) {
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
  await expect(
    page.getByText(
      "Parada 1, Bodega El Ahorro: la confirmación quedó en esta pantalla y todavía no se guarda.",
    ),
  ).toBeVisible();
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
