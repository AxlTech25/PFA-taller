export type Rol = "ADMIN" | "GERENTE" | "OPERADOR" | "CONDUCTOR" | "AUDITOR";

export function puedeRegistrarFlota(rol: string): boolean {
  return rol === "ADMIN" || rol === "OPERADOR";
}

export function etiquetaRol(rol: string): string {
  const etiquetas: Record<string, string> = {
    ADMIN: "Administrador",
    GERENTE: "Gerente",
    OPERADOR: "Operador",
    CONDUCTOR: "Conductor",
    AUDITOR: "Auditor",
  };
  return etiquetas[rol] ?? rol;
}
