import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { Paginador } from "./Paginador";

describe("Paginador", () => {
  it("oculta los controles cuando cabe en una página", () => {
    const { container } = render(<Paginador page={1} totalPages={1} onPage={() => undefined} />);
    expect(container).toBeEmptyDOMElement();
  });

  it("cambia de página de a 12 registros", () => {
    const onPage = vi.fn();
    render(<Paginador page={2} totalPages={3} onPage={onPage} />);
    fireEvent.click(screen.getByRole("button", { name: "Siguiente" }));
    fireEvent.click(screen.getByRole("button", { name: "Anterior" }));
    expect(onPage).toHaveBeenNthCalledWith(1, 3);
    expect(onPage).toHaveBeenNthCalledWith(2, 1);
    expect(screen.getByText("Página 2 de 3")).toBeInTheDocument();
  });
});
