export function numero(valor: number, decimales: number): string {
  // Sin Intl: mismo criterio del tablero para no cargar datos ICU.
  const [entero, fraccion] = valor.toFixed(decimales).split(".");
  const grupos = entero.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  return fraccion ? `${grupos}.${fraccion}` : grupos;
}

export function soles(valor: number | null | undefined): string {
  if (valor == null) return "Pendiente";
  return valor < 0 ? `-S/ ${numero(-valor, 2)}` : `S/ ${numero(valor, 2)}`;
}

export function porcentaje(valor: number | null | undefined): string {
  return valor == null ? "Pendiente" : `${numero(valor, 1)} %`;
}
