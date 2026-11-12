export const TAMANO_PAGINA = 12;

export type Pagina<T> = {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
};

export function comoPagina<T>(data: unknown): Pagina<T> {
  if (Array.isArray(data)) {
    return {
      items: data as T[],
      total: data.length,
      page: 1,
      page_size: Math.max(data.length, TAMANO_PAGINA),
      total_pages: data.length > 0 ? 1 : 0,
    };
  }
  return data as Pagina<T>;
}

export function rutaPagina(base: string, page: number): string {
  const union = base.includes("?") ? "&" : "?";
  return `${base}${union}page=${page}&limite=${TAMANO_PAGINA}`;
}
