import { createServer } from "node:http";
import { createHash } from "node:crypto";
import { existsSync, readFileSync, statSync } from "node:fs";
import { extname, join, normalize } from "node:path";
import { fileURLToPath } from "node:url";
import { brotliCompressSync, constants, gzipSync } from "node:zlib";

const dist = fileURLToPath(new URL("../dist/", import.meta.url));
const puerto = Number(process.env.PORT || 4173);

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

const server = createServer((req, res) => {
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
