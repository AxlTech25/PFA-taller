/**
 * Deja la sesión de prueba en una cookie antes de cada URL.
 * Lighthouse abre otra pestaña, así que sessionStorage no llega.
 * También vacía la caché HTTP para que cada pantalla se mida en frío.
 */

const ADMIN = {
  email: process.env.LHCI_ADMIN_EMAIL || "admin.lhci@distrirapido.example.com",
  password: process.env.AUDITORIA_PASSWORD || process.env.LHCI_PASSWORD || "clave-segura",
};
const CONDUCTOR = {
  email: process.env.LHCI_CONDUCTOR_EMAIL || "conductor.lhci@distrirapido.example.com",
  password: ADMIN.password,
};

const tokens = new Map();

async function entrar(page, credencial) {
  const guardado = tokens.get(credencial.email);
  if (guardado) return guardado;
  const sesion = await page.evaluate(async (cuerpo) => {
    const respuesta = await fetch("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json", "Accept-Encoding": "identity" },
      body: JSON.stringify(cuerpo),
    });
    if (!respuesta.ok) throw new Error(await respuesta.text());
    return respuesta.json();
  }, credencial);
  tokens.set(credencial.email, sesion);
  return sesion;
}

function desactivarCache(browser) {
  if (browser.__auditoriaSinCache) return;
  browser.__auditoriaSinCache = true;
  browser.on("targetcreated", async (target) => {
    if (target.type() !== "page") return;
    const pagina = await target.page();
    if (!pagina) return;
    const cliente = await pagina.createCDPSession();
    await cliente.send("Network.enable");
    await cliente.send("Network.setCacheDisabled", { cacheDisabled: true });
  });
}

module.exports = async (browser, contexto) => {
  desactivarCache(browser);
  const url = new URL(contexto.url);
  const page = await browser.newPage();
  const cliente = await page.createCDPSession();
  await cliente.send("Network.clearBrowserCache");
  await page.goto(`${url.origin}/login`, { waitUntil: "domcontentloaded" });
  const cookies = await page.cookies(url.origin);
  const previa = cookies.filter((cookie) => cookie.name === "ecologistica_sesion");
  if (previa.length > 0) await page.deleteCookie(...previa);

  const esLogin = url.pathname === "/login";
  if (!esLogin) {
    const credencial = url.pathname === "/modo" ? CONDUCTOR : ADMIN;
    const sesion = await entrar(page, credencial);
    await page.setCookie({
      name: "ecologistica_sesion",
      value: encodeURIComponent(JSON.stringify(sesion)),
      url: url.origin,
    });
  }
  await page.close();
};
