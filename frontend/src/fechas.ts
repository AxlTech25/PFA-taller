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

/** DD/MM/AAAA a partir de un ISO de fecha, sin cargar datos de locale. */
export function fechaVisible(iso: string): string {
  const [anio, mes, dia] = iso.slice(0, 10).split("-");
  if (!anio || !mes || !dia || anio.length !== 4) return iso;
  return `${dia}/${mes}/${anio}`;
}

/** HH:MM de un ISO con marca de hora. El reloj es el que guardó la API. */
export function horaVisible(iso: string | null | undefined): string {
  if (!iso || iso.length < 16 || iso[10] !== "T") return "Sin hora";
  return iso.slice(11, 16);
}
