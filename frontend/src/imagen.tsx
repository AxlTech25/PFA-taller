import type { ImgHTMLAttributes } from "react";

type Props = Readonly<{
  avif?: string;
  webp?: string;
  src: string;
  alt: string;
  width: number;
  height: number;
  loading?: ImgHTMLAttributes<HTMLImageElement>["loading"];
}>;

/**
 * Entrega AVIF, luego WebP y, al final, el archivo de respaldo.
 * El producto no tiene fotografías propias: el mapa usa teselas PNG de
 * OpenStreetMap y esta pieza queda para un activo fotográfico futuro.
 */
export function ImagenAdaptativa({
  avif,
  webp,
  src,
  alt,
  width,
  height,
  loading = "lazy",
}: Props) {
  return (
    <picture>
      {avif ? <source srcSet={avif} type="image/avif" /> : null}
      {webp ? <source srcSet={webp} type="image/webp" /> : null}
      <img src={src} alt={alt} width={width} height={height} loading={loading} decoding="async" />
    </picture>
  );
}

export function opcionesTesela(attribution: string) {
  return {
    attribution,
    maxZoom: 18,
    detectRetina: false as const,
    updateWhenIdle: true,
  };
}
