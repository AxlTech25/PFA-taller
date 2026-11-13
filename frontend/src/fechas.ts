/** Fecha local YYYY-MM-DD con la API nativa Intl, sin librería de fechas. */

export function fechaHoy(ahora: Date = new Date()): string {
  const partes = new Intl.DateTimeFormat("en-CA", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).formatToParts(ahora);
  const valor = (tipo: Intl.DateTimeFormatPartTypes) =>
    partes.find((parte) => parte.type === tipo)?.value ?? "";
  return `${valor("year")}-${valor("month")}-${valor("day")}`;
}

export function fechaHoraLocal(hora: string, ahora: Date = new Date()): string {
  return `${fechaHoy(ahora)}T${hora}`;
}
