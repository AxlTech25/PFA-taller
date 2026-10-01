/** Sirve el SPA solo en navegaciones de documento. Un POST de login no debe caer aquí. */
export function respuestaSpa(
  method: string | undefined,
  accept: string | string[] | undefined,
): "/index.html" | undefined {
  const verbo = (method ?? "GET").toUpperCase();
  if (verbo !== "GET" && verbo !== "HEAD") return undefined;
  const encabezado = Array.isArray(accept) ? accept.join(",") : accept;
  if (encabezado?.includes("text/html")) return "/index.html";
  return undefined;
}
