import AxeBuilder from "@axe-core/playwright";
import { expect, test, type APIRequestContext, type Page } from "@playwright/test";

import { CONDUCTOR, dniNuevo, entrar, ir } from "./helpers";

const ETIQUETAS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"];
const CLIENTE = "Bodega El Ahorro (con consentimiento)";
// Horario amplio (RES-CS5): con la jornada de 06:00–20:00 no altera los planes de otras pruebas.
const AMPLIO = { hora_inicio: "06:00", hora_fin: "21:00" };

async function cabeceras(page: Page) {
  const token = await page.evaluate(() => {
    const crudo = sessionStorage.getItem("ecologistica.sesion");
    return crudo ? ((JSON.parse(crudo) as { access_token?: string }).access_token ?? "") : "";
  });
  expect(token.length).toBeGreaterThan(10);
  return {
    Accept: "application/json",
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };
}

async function idCliente(request: APIRequestContext, headers: Record<string, string>): Promise<string> {
  const respuesta = await request.get("/clientes?page=1&limite=50", { headers });
  const cliente = ((await respuesta.json()) as {
    items: { id_cliente: string; nombre: string; consentimiento_datos: boolean }[];
  }).items.find((item) => item.consentimiento_datos && item.nombre === "Bodega El Ahorro");
  expect(cliente).toBeTruthy();
  return cliente?.id_cliente ?? "";
}

function fechaDe(proyecto: string): string {
  // Martes de 2096 (la restricción de placa deja flota). Semanas propias por navegador e intento.
  const tramo: Record<string, number> = { chromium: 0, firefox: 15, webkit: 30 };
  const semana = (tramo[proyecto] ?? 0) + (Math.floor(Date.now() / 1000) % 15);
  return new Date(Date.UTC(2096, 0, 3 + semana * 7)).toISOString().slice(0, 10);
}

test("el operador registra la preferencia de horario con teclado y la corrige (US-009)", async ({
  page,
  request,
}) => {
  await entrar(page);
  const headers = await cabeceras(page);
  const id = await idCliente(request, headers);
  try {
    await ir(page, "Pedidos");
    const seccion = page.getByRole("region", { name: "Preferencias de entrega del cliente" });
    await expect(seccion).toBeVisible();
    await seccion.getByLabel("Cliente de la ficha").selectOption({ label: CLIENTE });

    // Horarios contradictorios: se rechaza y se pide corrección, sin guardar.
    await seccion.getByLabel("Hora preferida desde").fill("15:00");
    await seccion.getByLabel("Hora preferida hasta").fill("09:00");
    await seccion.getByRole("button", { name: "Guardar preferencias" }).click();
    await expect(page.locator("#alerta-preferencias")).toContainText(
      "La hora de inicio debe ser anterior a la hora de fin",
    );

    // La API también lo rechaza aunque se salte el formulario.
    const directa = await request.put(`/clientes/${id}/preferencia`, {
      headers,
      data: { hora_inicio: "12:00", hora_fin: "12:00" },
    });
    expect(directa.status()).toBe(422);

    await seccion.getByLabel("Hora preferida desde").fill("08:00");
    await seccion.getByLabel("Hora preferida hasta").fill("12:00");
    await seccion.getByLabel("Referencia habitual").fill("frente a la bodega El Ahorro");
    await seccion.getByLabel("Restricción de acceso").fill("Calle angosta: solo camioneta pequeña");
    await seccion.getByRole("button", { name: "Guardar preferencias" }).focus();
    const guardado = page.waitForResponse(
      (r) => r.url().includes("/preferencia") && r.request().method() === "PUT",
    );
    await page.keyboard.press("Enter");
    expect((await guardado).status()).toBe(200);
    await expect(page.locator("#exito-preferencias")).toContainText("Preferencia guardada");

    const axe = await new AxeBuilder({ page }).withTags(ETIQUETAS).analyze();
    expect(axe.violations).toEqual([]);

    // Persiste: al volver a la página la ficha trae lo guardado.
    await page.reload();
    const otra = page.getByRole("region", { name: "Preferencias de entrega del cliente" });
    await otra.getByLabel("Cliente de la ficha").selectOption({ label: CLIENTE });
    await expect(otra.getByLabel("Hora preferida desde")).toHaveValue("08:00");
    await expect(otra.getByLabel("Hora preferida hasta")).toHaveValue("12:00");
    await expect(otra.getByLabel("Restricción de acceso")).toHaveValue("Calle angosta: solo camioneta pequeña");
  } finally {
    const restaurar = await request.put(`/clientes/${id}/preferencia`, { headers, data: AMPLIO });
    expect(restaurar.status()).toBe(200);
  }
});

test("la optimización lee la preferencia como restricción suave (US-009)", async ({ page, request }, info) => {
  await entrar(page);
  const headers = await cabeceras(page);
  const id = await idCliente(request, headers);
  const fecha = fechaDe(info.project.name);
  const ficha = await request.put(`/clientes/${id}/preferencia`, { headers, data: AMPLIO });
  expect(ficha.status(), await ficha.text()).toBe(200);
  const conductor = await request.post("/conductores", {
    headers,
    data: {
      nombre: `Conductor preferencias ${info.project.name}`,
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
      id_cliente: id,
      direccion: "Calle preferencias",
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
  let cuerpo: { estado: string; mensaje?: string; comparacion?: Record<string, number> | null } = {
    estado: "ENCOLADO",
  };
  for (let intento = 0; intento < 40 && ["ENCOLADO", "EN_PROCESO"].includes(cuerpo.estado); intento += 1) {
    await page.waitForTimeout(500);
    cuerpo = await (await request.get(`/optimizaciones/${idJob}`, { headers })).json();
  }
  expect(cuerpo.estado, cuerpo.mensaje).toBe("COMPLETADO");
  // El motor midió la atención frente al horario preferido (06:00–21:00: dentro, 0 min).
  expect(cuerpo.comparacion?.minutos_fuera_preferencia).toBe(0);
});

test("el conductor no accede a las preferencias de clientes (403)", async ({ request }) => {
  const sesion = await request.post("/auth/login", {
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    data: { email: CONDUCTOR.email, password: CONDUCTOR.password },
  });
  expect(sesion.status()).toBe(200);
  const token = ((await sesion.json()) as { access_token: string }).access_token;
  const respuesta = await request.get("/clientes/00000000-0000-4000-8000-000000000000/preferencia", {
    headers: { Authorization: `Bearer ${token}`, Accept: "application/json" },
  });
  expect(respuesta.status()).toBe(403);
});
