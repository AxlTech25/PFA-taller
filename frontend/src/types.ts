export type Sesion = {
  access_token: string;
  id_usuario: string;
  email: string;
  rol: string;
};

export type Vehiculo = {
  id_vehiculo: string;
  placa: string;
  tipo: "CAMIONETA" | "FURGON" | "MOTO";
  capacidad_kg: number;
  capacidad_m3: number;
  consumo_km_l: number;
  factor_emision_co2: number;
  anio_fabricacion: number;
  estado: "ACTIVO" | "MANTENIMIENTO" | "INACTIVO";
  mensaje?: string;
};

export type Usuario = {
  id_usuario: string;
  email: string;
  rol: string;
  estado: "ACTIVO" | "INACTIVO" | "BLOQUEADO";
  intentos_fallidos: number;
  bloqueado_hasta?: string | null;
  mensaje?: string;
};

export type Conductor = {
  id_conductor: string;
  nombre: string;
  dni: string | null;
  licencia_categoria: string;
  anios_experiencia: number;
  disponibilidad_inicio: string;
  disponibilidad_fin: string;
  lat_punto_partida: number | null;
  lon_punto_partida: number | null;
  estado: string;
  mensaje?: string;
};

export type Cliente = {
  id_cliente: string;
  nombre: string;
  telefono: string | null;
  email: string | null;
  consentimiento_datos: boolean;
};

export type Pedido = {
  id_pedido: string;
  id_cliente: string;
  nombre_cliente?: string | null;
  direccion?: string | null;
  punto_referencia?: string | null;
  latitud: number | null;
  longitud: number | null;
  peso_kg: number;
  volumen_m3: number;
  ventana_inicio: string;
  ventana_fin: string;
  prioridad: string;
  tipo_producto: string;
  estado: string;
  mensaje?: string;
};
