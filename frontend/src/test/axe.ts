import axe from "axe-core";

const OPCIONES: axe.RunOptions = {
  runOnly: {
    type: "tag",
    values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"],
  },
  rules: {
    "color-contrast": { enabled: false },
  },
};

export async function violacionesDe(nodo: Element): Promise<string> {
  const resultados = await axe.run(nodo, OPCIONES);
  return resultados.violations
    .map((violacion) => {
      const destinos = violacion.nodes.map((nodoRegla) => nodoRegla.target.join(" ")).join("; ");
      return `${violacion.id} (${violacion.impact}): ${violacion.help}. ${destinos}`;
    })
    .join("\n");
}
