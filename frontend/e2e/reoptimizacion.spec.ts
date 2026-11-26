import AxeBuilder from "@axe-core/playwright";
import { expect, test, type APIRequestContext, type Page } from "@playwright/test";

import { CONDUCTOR, dniNuevo, entrar, ir } from "./helpers";

type Cabeceras = Record<string, string>;

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
  // Martes (como las fechas de flujos.spec) para que la restricción de placa deje flota.
  // Un tramo de semanas por navegador y otra semana por intento: un reintento no reutiliza la ruta.
  const tramo: Record<string, number> = { chromium: 0, firefox: 15, webkit: 30 };
  const semana = (tramo[proyecto] ?? 0) + (Math.floor(Date.now() / 1000) % 15);
  const fecha = new Date(Date.UTC(2098, 0, 7 + semana * 7));
  return fecha.toISOString().slice(0, 10);
}

async function crearPedido(
  request: APIRequestContext,
  headers: Cabeceras,
  idCliente: string,
  fecha: string,
  referencia: string,
  latitud: number,
  longitud: number,
): Promise<void> {
  const respuesta = await request.post("/pedidos", {
    headers,
    data: {
      id_cliente: idCliente,
      direccion: `Calle ${referencia}`,
      punto_referencia: referencia,
      latitud,
      longitud,
      peso_kg: 5,
      volumen_m3: 0.1,
      ventana_inicio: `${fecha}T06:00:00Z`,
      ventana_fin: `${fecha}T19:00:00Z`,
      prioridad: "ESTANDAR",
      tipo_producto: "NO_PERECEDERO",
    },
  });
  expect(respuesta.status(), await respuesta.text()).toBe(201);
}

test("el operador re-optimiza una ruta confirmada con un pedido nuevo en 30 s o menos", async ({
  page,
  request,
}, info) => {
  await entrar(page);
  const token = await tokenDe(page);
  const headers = {
    Accept: "application/json",
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };
  const fecha = fechaDe(info.project.name);
  const sufijo = `${info.project.name.slice(0, 3)}-${Date.now() % 100000}`;

  const clientes = await request.get("/clientes?page=1&limite=50", { headers });
  expect(clientes.status()).toBe(200);
  const cliente = ((await clientes.json()) as {
    items: { id_cliente: string; consentimiento_datos: boolean }[];
  }).items.find((item) => item.consentimiento_datos);
  expect(cliente).toBeTruthy();
  const idCliente = cliente?.id_cliente ?? "";

  const conductor = await request.post("/conductores", {
    headers,
    data: {
      nombre: `Conductor reopt ${info.project.name}`,
      dni: dniNuevo(),
      licencia_categoria: "A-IIIb",
      anios_experiencia: 3,
      disponibilidad_inicio: "06:00:00",
      disponibilidad_fin: "20:00:00",
      lat_punto_partida: -12.01,
      lon_punto_partida: -76.98,
    },
  });
  expect(conductor.status(), await conductor.text()).toBe(201);

  // Pedidos en San Juan de Lurigancho, lejos de la reserva demo de Ate sur.
  await crearPedido(request, headers, idCliente, fecha, `reopt-a-${sufijo}`, -12.005, -76.985);
  await crearPedido(request, headers, idCliente, fecha, `reopt-b-${sufijo}`, -12.015, -76.975);
  const alta = await request.post("/optimizaciones", { headers, data: { fecha } });
  expect(alta.status(), await alta.text()).toBe(202);
  const idJob = ((await alta.json()) as { id_job: string }).id_job;
  let estado = "ENCOLADO";
  let mensaje = "";
  for (let intento = 0; intento < 40 && (estado === "ENCOLADO" || estado === "EN_PROCESO"); intento += 1) {
    await page.waitForTimeout(500);
    const consulta = await request.get(`/optimizaciones/${idJob}`, { headers });
    const cuerpo = (await consulta.json()) as { estado: string; mensaje?: string };
    estado = cuerpo.estado;
    mensaje = cuerpo.mensaje ?? "";
  }
  expect(estado, mensaje).toBe("COMPLETADO");

  const listado = await request.get(`/rutas?fecha=${fecha}&page=1&limite=50`, { headers });
  expect(listado.status()).toBe(200);
  const rutas = ((await listado.json()) as { items: { id_ruta: string; estado: string }[] }).items;
  expect(rutas.length).toBeGreaterThan(0);
  const idRuta = rutas[0].id_ruta;
  const confirmada = await request.post(`/rutas/${idRuta}/confirmar`, { headers });
  expect(confirmada.status(), await confirmada.text()).toBe(200);

  // Llega un pedido nuevo durante la jornada.
  const nuevo = `reopt-c-${sufijo}`;
  await crearPedido(request, headers, idCliente, fecha, nuevo, -12.01, -76.99);

  // RBAC: el conductor no puede re-optimizar (403).
  const sesionConductor = await request.post("/auth/login", {
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    data: { email: CONDUCTOR.email, password: CONDUCTOR.password },
  });
  expect(sesionConductor.status()).toBe(200);
  const tokenConductor = ((await sesionConductor.json()) as { access_token: string }).access_token;
  const prohibido = await request.post(`/rutas/${idRuta}/reoptimizar`, {
    headers: { ...headers, Authorization: `Bearer ${tokenConductor}` },
    data: { motivo: "CONGESTION" },
  });
  expect(prohibido.status()).toBe(403);

  await ir(page, "Rutas");
  const cargada = page.waitForResponse(
    (respuesta) =>
      respuesta.url().includes("/rutas?") &&
      respuesta.url().includes(`fecha=${fecha}`) &&
      respuesta.status() === 200,
  );
  await page.locator("#fecha").evaluate((campo, valor) => {
    const input = campo as HTMLInputElement;
    const definir = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value")?.set;
    definir?.call(input, valor);
    input.dispatchEvent(new Event("input", { bubbles: true }));
    input.dispatchEvent(new Event("change", { bubbles: true }));
  }, fecha);
  await cargada;

  // Todo el flujo con teclado.
  const abrir = page.getByRole("button", { name: /^Re-optimizar paradas pendientes de / }).first();
  await expect(abrir).toBeVisible();
  await abrir.focus();
  await page.keyboard.press("Enter");
  await expect(abrir).toHaveAttribute("aria-expanded", "true");
  const motivo = page.getByRole("combobox", { name: "Motivo del cambio" });
  await expect(motivo).toBeFocused();
  await motivo.selectOption("NUEVO_PEDIDO");
  const casilla = page.getByRole("checkbox", { name: new RegExp(nuevo) });
  await expect(casilla).toBeVisible();
  await casilla.focus();
  await page.keyboard.press("Space");
  await expect(casilla).toBeChecked();

  const axeFormulario = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"])
    .analyze();
  expect(axeFormulario.violations).toEqual([]);

  const detalle = page.getByLabel("Detalle (opcional)");
  await detalle.focus();
  await page.keyboard.type("Pedido urgente de último minuto");
  const respuesta = page.waitForResponse(
    (r) => r.url().endsWith(`/rutas/${idRuta}/reoptimizar`) && r.request().method() === "POST",
  );
  await page.keyboard.press("Enter");
  const cuerpo = (await (await respuesta).json()) as {
    segundos: number;
    presupuesto_s: number;
    agregadas: number;
  };
  expect(cuerpo.agregadas).toBe(1);
  expect(cuerpo.presupuesto_s).toBeLessThanOrEqual(30);
  expect(cuerpo.segundos).toBeLessThanOrEqual(30);
  console.log(`REOPT_E2E proyecto=${info.project.name} segundos=${cuerpo.segundos}`);

  await expect(page.locator("output.exito").filter({ hasText: "Tiempo medido" })).toContainText("(tope 30 s)");
  await expect(abrir).toBeFocused();
  await expect(page.getByRole("cell", { name: nuevo, exact: true })).toBeVisible();

  const axeResultado = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"])
    .analyze();
  expect(axeResultado.violations).toEqual([]);
});
