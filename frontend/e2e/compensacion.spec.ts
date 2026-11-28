import AxeBuilder from "@axe-core/playwright";
import { expect, test, type APIRequestContext, type Page } from "@playwright/test";

import { CONDUCTOR, dniNuevo, entrar, fechaLima, ir } from "./helpers";

const ETIQUETAS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"];

async function tokenDe(page: Page): Promise<string> {
  const token = await page.evaluate(() => {
    const crudo = sessionStorage.getItem("ecologistica.sesion");
    if (!crudo) return "";
    return (JSON.parse(crudo) as { access_token?: string }).access_token ?? "";
  });
  expect(token.length).toBeGreaterThan(10);
  return token;
}

function fechaDe(proyecto: string): string {
  // Martes de 2097 (la restricción de placa deja flota). Semanas propias por navegador e intento.
  const tramo: Record<string, number> = { chromium: 0, firefox: 15, webkit: 30 };
  const semana = (tramo[proyecto] ?? 0) + (Math.floor(Date.now() / 1000) % 15);
  return new Date(Date.UTC(2097, 0, 1 + semana * 7)).toISOString().slice(0, 10);
}

async function planificar(page: Page, request: APIRequestContext, fecha: string, nombre: string) {
  const headers = {
    Accept: "application/json",
    Authorization: `Bearer ${await tokenDe(page)}`,
    "Content-Type": "application/json",
  };
  const clientes = await request.get("/clientes?page=1&limite=50", { headers });
  const cliente = ((await clientes.json()) as {
    items: { id_cliente: string; consentimiento_datos: boolean }[];
  }).items.find((item) => item.consentimiento_datos);
  expect(cliente).toBeTruthy();
  const conductor = await request.post("/conductores", {
    headers,
    data: {
      nombre: `Conductor compensación ${nombre}`,
      dni: dniNuevo(),
      licencia_categoria: "A-IIIb",
      anios_experiencia: 2,
      disponibilidad_inicio: "06:00:00",
      disponibilidad_fin: "20:00:00",
      lat_punto_partida: -12.01,
      lon_punto_partida: -76.98,
    },
  });
  expect(conductor.status(), await conductor.text()).toBe(201);
  const pedido = await request.post("/pedidos", {
    headers,
    data: {
      id_cliente: cliente?.id_cliente,
      direccion: "Calle compensación",
      latitud: -12.005,
      longitud: -76.985,
      peso_kg: 5,
      volumen_m3: 0.1,
      ventana_inicio: `${fecha}T06:00:00Z`,
      ventana_fin: `${fecha}T19:00:00Z`,
      prioridad: "ESTANDAR",
      tipo_producto: "NO_PERECEDERO",
    },
  });
  expect(pedido.status(), await pedido.text()).toBe(201);
  const alta = await request.post("/optimizaciones", { headers, data: { fecha } });
  expect(alta.status(), await alta.text()).toBe(202);
  const idJob = ((await alta.json()) as { id_job: string }).id_job;
  let estado = "ENCOLADO";
  let mensaje = "";
  for (let intento = 0; intento < 40 && (estado === "ENCOLADO" || estado === "EN_PROCESO"); intento += 1) {
    await page.waitForTimeout(500);
    const cuerpo = (await (await request.get(`/optimizaciones/${idJob}`, { headers })).json()) as {
      estado: string;
      mensaje?: string;
    };
    estado = cuerpo.estado;
    mensaje = cuerpo.mensaje ?? "";
  }
  expect(estado, mensaje).toBe("COMPLETADO");
}

test("el tablero calcula el plan de compensación con teclado (US-017)", async ({ page, request }, info) => {
  await entrar(page);
  const fecha = fechaDe(info.project.name);
  await planificar(page, request, fecha, info.project.name);
  await ir(page, "Tablero");
  await expect(page.getByRole("heading", { name: "Plan de compensación de carbono" })).toBeVisible();

  await page.getByLabel("Inicio del período").fill(fecha);
  await page.getByLabel("Fin del período").fill(fecha);
  const boton = page.getByRole("button", { name: "Calcular plan de compensación" });
  await boton.focus();
  const respuesta = page.waitForResponse(
    (r) => r.url().includes("/indicadores/compensacion?") && r.status() === 200,
  );
  await page.keyboard.press("Enter");
  const plan = (await (await respuesta).json()) as {
    calculable: boolean;
    co2_emitido_kg: number;
    factor_captura_arbol_kg: number | null;
    costo_por_arbol_soles: number | null;
    arboles_necesarios: number | null;
    costo_estimado_soles: number | null;
    estado_factor: string;
    estado_costo: string;
  };
  expect(plan.calculable).toBe(true);
  expect(plan.co2_emitido_kg).toBeGreaterThan(0);
  const resultado = page.getByRole("list", { name: "Proyectos locales sugeridos" });
  await expect(resultado).toContainText("Lomas de Lima");
  await expect(resultado).toContainText("Parque Zonal Huáscar");
  await expect(resultado).toContainText("Árboles para Lima");
  // Migración 008: factor EPA 60 kg y costo SERPAR S/ 94.
  expect(plan.estado_factor).toBe("CONFIGURADO");
  expect(plan.estado_costo).toBe("CONFIGURADO");
  expect(plan.factor_captura_arbol_kg).toBe(60);
  expect(plan.costo_por_arbol_soles).toBe(94);
  expect(plan.arboles_necesarios).toBe(Math.ceil(plan.co2_emitido_kg / 60));
  expect(plan.costo_estimado_soles).toBe(
    Math.round((plan.arboles_necesarios ?? 0) * 94 * 100) / 100,
  );
  await expect(page.getByText("Árboles necesarios").locator("xpath=following-sibling::dd")).toHaveText(
    String(plan.arboles_necesarios),
  );
  const costo = (plan.costo_estimado_soles ?? 0).toFixed(2);
  await expect(page.getByText("Costo estimado").locator("xpath=following-sibling::dd")).toHaveText(
    `S/ ${costo}`,
  );
  const axe = await new AxeBuilder({ page }).withTags(ETIQUETAS).analyze();
  expect(axe.violations).toEqual([]);

  await page.getByLabel("Inicio del período").fill("2099-01-01");
  await page.getByLabel("Fin del período").fill("2099-01-31");
  await boton.click();
  await expect(page.getByText(/No es posible calcular la compensación/)).toBeVisible();
  const axeVacio = await new AxeBuilder({ page }).withTags(ETIQUETAS).analyze();
  expect(axeVacio.violations).toEqual([]);
});

test("el conductor no puede ver el plan de compensación (403)", async ({ request }) => {
  const sesion = await request.post("/auth/login", {
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    data: { email: CONDUCTOR.email, password: CONDUCTOR.password },
  });
  expect(sesion.status()).toBe(200);
  const token = ((await sesion.json()) as { access_token: string }).access_token;
  const hoy = fechaLima();
  const respuesta = await request.get(`/indicadores/compensacion?desde=${hoy}&hasta=${hoy}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  expect(respuesta.status()).toBe(403);
});
