import { fireEvent, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import * as reporte from "../reporte";
import { violacionesDe } from "../test/axe";
import { montar } from "../test/pagina";
import { ReportePdf } from "./ReportePdf";

afterEach(() => {
  vi.restoreAllMocks();
});

function cambiar(etiqueta: string, valor: string) {
  fireEvent.change(screen.getByLabelText(etiqueta), { target: { value: valor } });
}

describe("ReportePdf (US-016)", () => {
  it("descarga el PDF del período con teclado y sin violaciones de axe", async () => {
    const blob = new Blob(["%PDF"], { type: "application/pdf" });
    const pedir = vi.spyOn(reporte, "pedirReporte").mockResolvedValue(blob);
    const guardar = vi.spyOn(reporte, "guardarArchivo").mockImplementation(() => {});
    const { container } = montar(<ReportePdf />, "GERENTE");
    expect(await violacionesDe(container)).toBe("");
    cambiar("Desde", "2026-11-01");
    cambiar("Hasta", "2026-11-07");
    const boton = screen.getByRole("button", { name: "Descargar reporte PDF" });
    boton.focus();
    expect(boton).toHaveFocus();
    fireEvent.submit(boton.closest("form") as HTMLFormElement);
    expect(await screen.findByText("Reporte listo: reporte-sostenibilidad-2026-11-01_2026-11-07.pdf.")).toBeInTheDocument();
    expect(pedir).toHaveBeenCalledWith("2026-11-01", "2026-11-07", "token-prueba");
    expect(guardar).toHaveBeenCalledWith(blob, "reporte-sostenibilidad-2026-11-01_2026-11-07.pdf");
    expect(await violacionesDe(container)).toBe("");
  });

  it("valida el período sin llamar a la API", async () => {
    const pedir = vi.spyOn(reporte, "pedirReporte");
    montar(<ReportePdf />);
    cambiar("Desde", "2026-11-08");
    cambiar("Hasta", "2026-11-01");
    fireEvent.click(screen.getByRole("button", { name: "Descargar reporte PDF" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("anterior a la inicial");
    expect(pedir).not.toHaveBeenCalled();
  });

  it("informa el período vacío, la sesión vencida y el fallo de red", async () => {
    const pedir = vi
      .spyOn(reporte, "pedirReporte")
      .mockRejectedValueOnce(new (await import("../api")).ApiError(404, "Sin datos de operación para el período seleccionado."));
    const guardar = vi.spyOn(reporte, "guardarArchivo");
    const { container } = montar(<ReportePdf />);
    fireEvent.click(screen.getByRole("button", { name: "Descargar reporte PDF" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Sin datos de operación");
    expect(guardar).not.toHaveBeenCalled();
    expect(await violacionesDe(container)).toBe("");

    pedir.mockRejectedValueOnce(new Error("red"));
    fireEvent.click(screen.getByRole("button", { name: "Descargar reporte PDF" }));
    expect(await screen.findByText("No se pudo generar el reporte PDF.")).toBeInTheDocument();

    pedir.mockRejectedValueOnce(new (await import("../api")).ApiError(401, "Sesión vencida"));
    fireEvent.click(screen.getByRole("button", { name: "Descargar reporte PDF" }));
    expect(await screen.findByText("Sesión vencida")).toBeInTheDocument();
    expect(sessionStorage.getItem("ecologistica.sesion")).toBeNull();
  });
});
