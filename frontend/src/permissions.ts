export type Rol = "ADMIN" | "GERENTE" | "OPERADOR" | "CONDUCTOR" | "AUDITOR";

export type Modulo = "flota" | "conductores" | "pedidos" | "usuarios" | "modo";

const ETIQUETAS: Record<string, string> = {
  ADMIN: "Administrador",
  GERENTE: "Gerente",
  OPERADOR: "Operador",
  CONDUCTOR: "Conductor",
  AUDITOR: "Auditor",
  CAMIONETA: "Camioneta",
  FURGON: "Furgón",
  MOTO: "Moto",
  ACTIVO: "Activo",
  INACTIVO: "Inactivo",
  BLOQUEADO: "Bloqueado",
  MANTENIMIENTO: "Mantenimiento",
  VACACIONES: "Vacaciones",
  PENDIENTE: "Pendiente",
  EXPRESS: "Exprés",
  ESTANDAR: "Estándar",
  ECONOMICO: "Económico",
  PERECEDERO: "Perecedero",
  NO_PERECEDERO: "No perecedero",
};

export function etiquetaRol(rol: string): string {
  return ETIQUETAS[rol] ?? rol;
}

export function etiqueta(valor: string): string {
  return ETIQUETAS[valor] ?? valor;
}

export function puedeRegistrarFlota(rol: string): boolean {
  return rol === "ADMIN" || rol === "OPERADOR";
}

export function puedeEditarFlota(rol: string): boolean {
  return rol === "ADMIN" || rol === "GERENTE" || rol === "OPERADOR";
}

export function puedeRegistrarConductor(rol: string): boolean {
  return rol === "ADMIN" || rol === "OPERADOR";
}

export function puedeRegistrarPedido(rol: string): boolean {
  return rol === "ADMIN" || rol === "OPERADOR";
}

export function puedeGestionarUsuarios(rol: string): boolean {
  return rol === "ADMIN";
}

export function modulosVisibles(rol: string): Modulo[] {
  if (rol === "ADMIN") return ["flota", "conductores", "pedidos", "usuarios"];
  if (rol === "GERENTE") return ["flota", "conductores", "pedidos", "usuarios"];
  if (rol === "OPERADOR" || rol === "AUDITOR") return ["flota", "conductores", "pedidos"];
  if (rol === "CONDUCTOR") return ["flota", "modo"];
  return ["flota"];
}
