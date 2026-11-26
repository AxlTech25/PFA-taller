import { ApiError, mensajeError } from "./api";

export const MAX_DIAS_REPORTE = 31;

export function nombreReporte(desde: string, hasta: string): string {
  return `reporte-sostenibilidad-${desde}_${hasta}.pdf`;
}

/** Valida el período antes de pedir el PDF (la API repite la misma regla). */
export function errorPeriodo(desde: string, hasta: string): string | null {
  if (!desde || !hasta) return "Indique la fecha inicial y la final.";
  const inicio = Date.parse(`${desde}T00:00:00Z`);
  const fin = Date.parse(`${hasta}T00:00:00Z`);
  if (Number.isNaN(inicio) || Number.isNaN(fin)) return "Indique fechas válidas.";
  if (fin < inicio) return "La fecha final no puede ser anterior a la inicial.";
  if ((fin - inicio) / 86_400_000 + 1 > MAX_DIAS_REPORTE) {
    return `El período del reporte no puede superar ${MAX_DIAS_REPORTE} días.`;
  }
  return null;
}

/** Pide el PDF con el token de la sesión. Sin datos, la API responde 404 y no hay archivo. */
export async function pedirReporte(
  desde: string,
  hasta: string,
  token: string | null | undefined,
): Promise<Blob> {
  const headers = new Headers({ Accept: "application/pdf" });
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const respuesta = await fetch(
    `/indicadores/reporte.pdf?desde=${encodeURIComponent(desde)}&hasta=${encodeURIComponent(hasta)}`,
    { headers, cache: "no-store" },
  );
  if (!respuesta.ok) {
    const cuerpo = await respuesta.json().catch(() => ({}));
    throw new ApiError(respuesta.status, mensajeError(cuerpo));
  }
  return respuesta.blob();
}

/** Ofrece la descarga sin abrir otra pestaña. */
export function guardarArchivo(blob: Blob, nombre: string): void {
  const url = URL.createObjectURL(blob);
  const enlace = document.createElement("a");
  enlace.href = url;
  enlace.download = nombre;
  enlace.hidden = true;
  document.body.append(enlace);
  enlace.click();
  enlace.remove();
  globalThis.setTimeout(() => URL.revokeObjectURL(url), 1000);
}
