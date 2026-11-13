import { createServer, request as httpRequest } from "node:http";
import { createHash } from "node:crypto";
import { existsSync, readFileSync, statSync } from "node:fs";
import { extname, join, normalize } from "node:path";
import { fileURLToPath } from "node:url";
import { brotliCompressSync, constants, gzipSync } from "node:zlib";

const dist = process.env.DIST_DIR
  ? `${process.env.DIST_DIR.replace(/[/\\]+$/, "")}/`
  : fileURLToPath(new URL("../dist/", import.meta.url));
const puerto = Number(process.env.PORT || 4173);
// Solo se reenvía a la API de esta máquina. Un valor distinto no activa el proxy:
// el host no puede salir de una variable ni de la petición.
const proxyLocal = process.env.API_UPSTREAM === "http://127.0.0.1:8000";
const rutasApi = [
  "/auth/login",
  "/usuarios",
  "/vehiculos",
  "/conductores",
  "/pedidos",
  "/clientes",
  "/optimizaciones",
  "/rutas",
  "/indicadores",
  "/health",
  "/openapi.json",
  "/docs",
];

const tipos = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".svg": "image/svg+xml",
  ".json": "application/json; charset=utf-8",
  ".png": "image/png",
  ".webp": "image/webp",
  ".avif": "image/avif",
  ".woff2": "font/woff2",
};

function resolver(urlPath) {
  const limpio = decodeURIComponent(urlPath.split("?")[0]);
  const relativo = normalize(limpio).replace(/^(\.\.(\/|\\|$))+/, "").replace(/^[/\\]+/, "");
  const candidato = join(dist, relativo);
  if (candidato.startsWith(dist) && existsSync(candidato) && statSync(candidato).isFile()) {
    return candidato;
  }
  if (!extname(limpio)) return join(dist, "index.html");
  return null;
}

function etag(datos) {
  return `W/"${createHash("sha256").update(datos).digest("hex").slice(0, 32)}"`;
}

function negociar(accept, datos, ruta) {
  const pedidos = String(accept || "")
    .split(",")
    .map((parte) => parte.split(";")[0].trim().toLowerCase());
  if (pedidos.includes("br") && existsSync(`${ruta}.br`)) {
    return { cuerpo: readFileSync(`${ruta}.br`), algoritmo: "br" };
  }
  if (pedidos.includes("gzip") && existsSync(`${ruta}.gz`)) {
    return { cuerpo: readFileSync(`${ruta}.gz`), algoritmo: "gzip" };
  }
  if (datos.length >= 1024 && pedidos.includes("br")) {
    return {
      cuerpo: brotliCompressSync(datos, { params: { [constants.BROTLI_PARAM_QUALITY]: 5 } }),
      algoritmo: "br",
    };
  }
  if (datos.length >= 1024 && pedidos.includes("gzip")) {
    return { cuerpo: gzipSync(datos, { level: 6 }), algoritmo: "gzip" };
  }
  return { cuerpo: datos, algoritmo: null };
}

function esApi(req) {
  if (!proxyLocal) return false;
  // La navegación del documento pide text/html. Esas rutas (/rutas, /pedidos…)
  // coinciden con la API y tienen que devolver la aplicación, no el JSON.
  const accept = String(req.headers.accept || "");
  if (accept.includes("text/html")) return false;
  return rutaLocal(req.url) !== null;
}

function rutaLocal(urlRecibida) {
  let relativa;
  try {
    relativa = new URL(urlRecibida || "/", "http://auditoria.local");
  } catch {
    return null;
  }
  if (relativa.hostname !== "auditoria.local" || relativa.username || relativa.password) return null;
  const canonica = rutasApi.find((ruta) => ruta === relativa.pathname);
  if (!canonica) return null;
  const pares = [];
  for (const clave of ["page", "limite", "fecha"]) {
    const valor = relativa.searchParams.get(clave);
    if (valor === null) continue;
    if (!/^[0-9A-Za-z_+.-]{1,40}$/.test(valor)) return null;
    pares.push(`${clave}=${encodeURIComponent(valor)}`);
  }
  if (pares.length === 0) return canonica;
  return `${canonica}?${pares.join("&")}`;
}

function proxy(req, res) {
  const ruta = rutaLocal(req.url);
  if (!ruta) {
    res.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
    res.end("Ruta no permitida");
    return;
  }
  const saliente = httpRequest(
    {
      protocol: "http:",
      hostname: "127.0.0.1",
      port: 8000,
      method: req.method,
      path: ruta,
      headers: { ...req.headers, host: "127.0.0.1:8000" },
    },
    (respuesta) => {
      res.writeHead(respuesta.statusCode || 502, respuesta.headers);
      respuesta.pipe(res);
    },
  );
  saliente.on("error", () => {
    if (!res.headersSent) res.writeHead(502, { "Content-Type": "text/plain; charset=utf-8" });
    res.end("API no disponible");
  });
  req.pipe(saliente);
}

const server = createServer((req, res) => {
  if (esApi(req)) {
    proxy(req, res);
    return;
  }
  const ruta = resolver(req.url || "/");
  if (!ruta) {
    res.writeHead(404, { "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "no-store" });
    res.end("No encontrado");
    return;
  }
  const datos = readFileSync(ruta);
  const marca = etag(datos);
  const hashed = ruta.includes(`${join(dist, "assets")}`);
  const cache = hashed ? "public, max-age=31536000, immutable" : "no-cache";
  if (req.headers["if-none-match"] === marca) {
    res.writeHead(304, { ETag: marca, "Cache-Control": cache, Vary: "Accept-Encoding" });
    res.end();
    return;
  }
  const { cuerpo, algoritmo } = negociar(req.headers["accept-encoding"], datos, ruta);
  const headers = {
    "Content-Type": tipos[extname(ruta)] || "application/octet-stream",
    "Content-Length": cuerpo.length,
    ETag: marca,
    "Cache-Control": cache,
    Vary: "Accept-Encoding",
  };
  if (algoritmo) headers["Content-Encoding"] = algoritmo;
  res.writeHead(200, headers);
  res.end(cuerpo);
});

server.listen(puerto, "127.0.0.1", () => {
  console.log(`escuchando en http://127.0.0.1:${puerto}`);
});
