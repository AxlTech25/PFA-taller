import { expect, test } from "@playwright/test";

const produccion = process.env.E2E_PRODUCCION === "1";

test.describe("producción, solo lectura", () => {
  test.skip(!produccion, "Se omite salvo E2E_PRODUCCION=1 contra la URL pública.");

  test("el login público responde y muestra la marca", async ({ page }) => {
    const respuesta = await page.goto("/login");
    expect(respuesta?.status()).toBe(200);
    await expect(page.getByRole("heading", { name: "EcoLogística Lima" })).toBeVisible();
  });

  test("la salud y el contrato responden, y una página compartida distingue HTML de JSON", async ({ request }) => {
    const salud = await request.get("/health", { headers: { Accept: "application/json" } });
    expect(salud.status()).toBe(200);
    expect(await salud.json()).toMatchObject({ status: "ok" });

    const contrato = await request.get("/openapi.json", { headers: { Accept: "application/json" } });
    expect(contrato.status()).toBe(200);

    const documento = await request.get("/usuarios", { headers: { Accept: "text/html" } });
    expect(documento.status()).toBe(200);
    expect(documento.headers()["content-type"] ?? "").toContain("text/html");
    expect(await documento.text()).toContain('id="root"');

    const anonimo = await request.get("/usuarios", { headers: { Accept: "application/json" } });
    expect(anonimo.status()).toBe(401);
  });
});
