import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ImagenAdaptativa, opcionesTesela } from "./imagen";

describe("imágenes", () => {
  it("ofrece AVIF y WebP antes del respaldo", () => {
    const { container } = render(
      <ImagenAdaptativa
        avif="/marca.avif"
        webp="/marca.webp"
        src="/marca.png"
        alt="Marca de EcoLogística"
        width={32}
        height={32}
      />,
    );
    const fuentes = container.querySelectorAll("source");
    expect(fuentes[0]).toHaveAttribute("type", "image/avif");
    expect(fuentes[1]).toHaveAttribute("type", "image/webp");
    const imagen = screen.getByRole("img", { name: "Marca de EcoLogística" });
    expect(imagen).toHaveAttribute("width", "32");
    expect(imagen).toHaveAttribute("decoding", "async");
  });

  it("pide teselas PNG sin duplicar la resolución retina", () => {
    expect(opcionesTesela("© OpenStreetMap")).toMatchObject({
      detectRetina: false,
      maxZoom: 18,
      updateWhenIdle: true,
    });
  });
});
