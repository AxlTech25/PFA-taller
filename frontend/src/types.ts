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
