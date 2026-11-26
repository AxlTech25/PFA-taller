import { fireEvent, screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { violacionesDe } from "../test/axe";
import { cuerpoDe, instalarFetch, montar } from "../test/pagina";
import type { Cliente, PreferenciaCliente as Ficha } from "../types";
import { MENSAJE_HORARIO, PreferenciasCliente, horarioContradictorio } from "./PreferenciasCliente";

const CLIENTES: Cliente[] = [
  { id_cliente: "cli-1", nombre: "Bodega El Ahorro", telefono: null, email: null, consentimiento_datos: true },
  { id_cliente: "cli-2", nombre: "Puesto sin ficha", telefono: null, email: null, consentimiento_datos: false },
];

function ficha(parcial: Partial<Ficha> = {}): Ficha {
  return {
    id_cliente: "cli-1",
    nombre_cliente: "Bodega El Ahorro",
    registrada: true,
    hora_inicio: "08:00:00",
    hora_fin: "12:00:00",
    punto_referencia: "frente a la bodega El Ahorro",
    restricciones_acceso: "Calle angosta",
    mensaje: null,
    ...parcial,
  };
}

function guardar() {
  const boton = screen.getByRole("button", { name: "Guardar preferencias" });
  boton.focus();
  fireEvent.submit(boton.closest("form") as HTMLFormElement);
}

describe("PreferenciasCliente (US-009)", () => {
  it("carga la ficha, guarda la preferencia válida y no tiene violaciones de axe", async () => {
    const { llamadas } = instalarFetch((_path, init) => {
      if (init?.method === "PUT") {
        return { body: ficha({ hora_inicio: "09:30:00", hora_fin: "13:00:00", mensaje: "Preferencia guardada." }) };
      }
      return { body: ficha({ registrada: false, hora_inicio: null, hora_fin: null, punto_referencia: null, restricciones_acceso: null }) };
    });
    const { container } = montar(<PreferenciasCliente clientes={CLIENTES} editable />, "OPERADOR");
    expect(await screen.findByText("Sin preferencias registradas.")).toBeInTheDocument();
    expect(llamadas[0].path).toBe("/clientes/cli-1/preferencia");
    expect(llamadas[0].init?.cache).toBe("no-cache");
    expect(await violacionesDe(container)).toBe("");

    fireEvent.change(screen.getByLabelText("Hora preferida desde"), { target: { value: "09:30" } });
    fireEvent.change(screen.getByLabelText("Hora preferida hasta"), { target: { value: "13:00" } });
    fireEvent.change(screen.getByLabelText("Referencia habitual"), { target: { value: "frente al mercado" } });
    fireEvent.change(screen.getByLabelText("Restricción de acceso"), { target: { value: "Solo moto" } });
    guardar();
    expect(await screen.findByText("Preferencia guardada.")).toBeInTheDocument();
    const put = llamadas.find((item) => item.init?.method === "PUT");
    expect(put?.path).toBe("/clientes/cli-1/preferencia");
    expect(cuerpoDe(put?.init)).toEqual({
      hora_inicio: "09:30",
      hora_fin: "13:00",
      punto_referencia: "frente al mercado",
      restricciones_acceso: "Solo moto",
    });
    expect(screen.getByLabelText("Hora preferida desde")).toHaveValue("09:30");
    expect(await violacionesDe(container)).toBe("");
  });

  it("rechaza horarios contradictorios sin llamar a la API", async () => {
    const { llamadas } = instalarFetch(() => ({ body: ficha() }));
    montar(<PreferenciasCliente clientes={CLIENTES} editable />);
    await waitFor(() => expect(screen.getByLabelText("Hora preferida desde")).toHaveValue("08:00"));
    fireEvent.change(screen.getByLabelText("Hora preferida desde"), { target: { value: "15:00" } });
    fireEvent.change(screen.getByLabelText("Hora preferida hasta"), { target: { value: "09:00" } });
    expect(screen.getByLabelText("Hora preferida hasta")).toHaveAttribute("aria-invalid", "true");
    guardar();
    expect(await screen.findByRole("alert")).toHaveTextContent(MENSAJE_HORARIO);
    expect(llamadas.some((item) => item.init?.method === "PUT")).toBe(false);

    fireEvent.change(screen.getByLabelText("Hora preferida hasta"), { target: { value: "" } });
    guardar();
    expect(await screen.findByRole("alert")).toHaveTextContent("Ingrese la hora de inicio y la hora de fin");
  });

  it("muestra el rechazo de la API y avisa del consentimiento", async () => {
    instalarFetch((_path, init) => {
      if (init?.method === "PUT") return { status: 422, body: { detail: "El cliente no ha otorgado el consentimiento" } };
      return { body: ficha({ id_cliente: "cli-2", registrada: false, hora_inicio: null, hora_fin: null }) };
    });
    montar(<PreferenciasCliente clientes={CLIENTES} editable />);
    fireEvent.change(screen.getByLabelText("Cliente de la ficha"), { target: { value: "cli-2" } });
    expect(await screen.findByText(/no guardará sus preferencias/)).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText("Hora preferida desde"), { target: { value: "07:00" } });
    fireEvent.change(screen.getByLabelText("Hora preferida hasta"), { target: { value: "10:00" } });
    guardar();
    expect(await screen.findByRole("alert")).toHaveTextContent("consentimiento");

    instalarFetch(() => {
      throw new Error("red");
    });
    guardar();
    expect(await screen.findByRole("alert")).toHaveTextContent("No se pudo guardar la preferencia.");
  });

  it("el gerente solo lee la ficha", async () => {
    const { llamadas } = instalarFetch(() => ({ body: ficha() }));
    const { container } = montar(<PreferenciasCliente clientes={CLIENTES} editable={false} />, "GERENTE");
    expect(await screen.findByText("08:00 – 12:00")).toBeInTheDocument();
    expect(screen.getByText("Calle angosta")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Guardar preferencias" })).not.toBeInTheDocument();
    expect(llamadas.every((item) => !item.init?.method)).toBe(true);
    expect(await violacionesDe(container)).toBe("");
  });

  it("informa si no puede cargar la ficha", async () => {
    instalarFetch(() => ({ status: 403, body: { detail: "Sin permiso" } }));
    montar(<PreferenciasCliente clientes={CLIENTES} editable />);
    expect(await screen.findByRole("alert")).toHaveTextContent("Sin permiso");
    expect(screen.getByText("Ficha no disponible.")).toBeInTheDocument();
    instalarFetch(() => {
      throw new Error("red");
    });
    fireEvent.change(screen.getByLabelText("Cliente de la ficha"), { target: { value: "cli-2" } });
    expect(await screen.findByRole("alert")).toHaveTextContent("No se pudo cargar la ficha del cliente.");
  });

  it("detecta horarios contradictorios", () => {
    expect(horarioContradictorio("08:00", "12:00")).toBe(false);
    expect(horarioContradictorio("12:00", "12:00")).toBe(true);
    expect(horarioContradictorio("", "12:00")).toBe(false);
  });
});
