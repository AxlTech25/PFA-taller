type Props = Readonly<{
  tono?: "oscuro" | "claro";
}>;

export function Marca({ tono = "oscuro" }: Props) {
  const fondo = tono === "claro" ? "#ffffff" : "#08553d";
  const trazo = tono === "claro" ? "#08553d" : "#ffffff";
  return (
    <svg
      className="marca-logo"
      viewBox="0 0 32 32"
      width="32"
      height="32"
      aria-hidden="true"
      focusable="false"
    >
      <rect width="32" height="32" rx="6" fill={fondo} />
      <path
        d="M7 23h18M9 23c2-7 4-7 6-2s3-8 5-8 3 6 5 10"
        fill="none"
        stroke={trazo}
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  );
}
