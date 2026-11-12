const VIGENCIA_MS = 30_000;

type Guardado = { expira: number; datos: unknown };

const memoria = new Map<string, Guardado>();

export function vaciarConsultas(): void {
  memoria.clear();
}

export async function consultar<T>(
  pedir: (path: string) => Promise<T>,
  path: string,
  forzar = false,
): Promise<T> {
  const ahora = Date.now();
  const previo = memoria.get(path);
  if (!forzar && previo && previo.expira > ahora) {
    return previo.datos as T;
  }
  const datos = await pedir(path);
  memoria.set(path, { expira: ahora + VIGENCIA_MS, datos });
  return datos;
}
