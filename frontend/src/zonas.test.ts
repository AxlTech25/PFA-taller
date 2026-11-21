import { describe, expect, it } from "vitest";

import { anilloZona, comoZonas, etiquetaZona } from "./zonas";

describe("zonas de restricción", () => {
  it("traduce el tipo y lee el anillo en latitud, longitud", () => {
    expect(etiquetaZona("RESERVA_ECOLOGICA")).toBe("Reserva ecológica");
    expect(etiquetaZona("RIESGO_SEGURIDAD")).toBe("Zona de riesgo");
    expect(etiquetaZona("RESTRICCION_HORARIA")).toBe("Restricción horaria");
    expect(etiquetaZona("CENTRO_HISTORICO")).toBe("Centro histórico");
    expect(etiquetaZona("VIA_NO_PAVIMENTADA")).toBe("Vía no pavimentada");
    expect(etiquetaZona("BAJA_VISIBILIDAD")).toBe("Baja visibilidad");
    expect(etiquetaZona("OTRO")).toBe("OTRO");
    const anillo = anilloZona({
      id_zona: "z1",
      nombre: "DEMO · caja",
      tipo: "RIESGO_SEGURIDAD",
      severidad: "ALTA",
      es_demostracion: true,
      geometria: {
        type: "Polygon",
        coordinates: [
          [
            [-76.98, -12.02],
            [-76.97, -12.02],
            [-76.97, -12.01],
          ],
        ],
      },
    });
    expect(anillo).toEqual([
      [-12.02, -76.98],
      [-12.02, -76.97],
      [-12.01, -76.97],
    ]);
  });

  it("ignora una respuesta que no es el listado de zonas", () => {
    expect(comoZonas(null)).toEqual({ advertencia: "", zonas: [] });
    expect(comoZonas([{ id_ruta: "r1" }])).toEqual({ advertencia: "", zonas: [] });
    expect(comoZonas({ advertencia: 1, zonas: [{ nombre: "sin geometría" }] })).toEqual({
      advertencia: "",
      zonas: [],
    });
    const lista = comoZonas({
      advertencia: "Dato demo",
      zonas: [
        {
          id_zona: "z1",
          nombre: "DEMO · caja",
          tipo: "RESERVA_ECOLOGICA",
          severidad: "ALTA",
          es_demostracion: true,
          geometria: { type: "Polygon", coordinates: [[[-76.9, -12.1]]] },
        },
      ],
    });
    expect(lista.advertencia).toBe("Dato demo");
    expect(lista.zonas).toHaveLength(1);
  });
});
