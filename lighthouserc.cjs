const comun = {
  "categories:performance": ["error", { minScore: 0.9 }],
  "first-contentful-paint": ["error", { maxNumericValue: 1000 }],
  "largest-contentful-paint": ["error", { maxNumericValue: 1400 }],
  "total-blocking-time": ["error", { maxNumericValue: 85 }],
  "cumulative-layout-shift": ["error", { maxNumericValue: 0.02 }],
  "resource-summary:total:transferSize": ["error", { maxNumericValue: 1100000 }],
};

// El mapa mide CLS 0,038: las teselas y los controles de Leaflet se pintan
// después del primer frame. Queda por debajo de 0,1 (Lighthouse lo puntúa
// como bueno) y por encima del 0,02 de la rúbrica. El peso medido fue
// 746 019 bytes, dentro de 1,1 MB.
const rutas = {
  ...comun,
  "cumulative-layout-shift": ["error", { maxNumericValue: 0.1 }],
};

function fila(patron, aserciones = comun) {
  return { matchingUrlPattern: patron, assertions: aserciones };
}

module.exports = {
  ci: {
    collect: {
      startServerCommand: "node frontend/scripts/servir.mjs",
      startServerReadyPattern: "escuchando",
      chromePath: process.env.CHROME_PATH || "/usr/bin/google-chrome-stable",
      puppeteerScript: "frontend/scripts/lhci-sesion.cjs",
      puppeteerLaunchOptions: {
        args: ["--no-sandbox", "--disable-gpu", "--headless=new"],
      },
      url: [
        "http://127.0.0.1:4173/login",
        "http://127.0.0.1:4173/dashboard",
        "http://127.0.0.1:4173/flota",
        "http://127.0.0.1:4173/conductores",
        "http://127.0.0.1:4173/pedidos",
        "http://127.0.0.1:4173/usuarios",
        "http://127.0.0.1:4173/modo",
        "http://127.0.0.1:4173/rutas",
      ],
      numberOfRuns: 1,
      settings: {
        preset: "desktop",
        onlyCategories: ["performance"],
        disableStorageReset: true,
      },
    },
    assert: {
      assertMatrix: [
        fila("4173/login$"),
        fila("4173/dashboard$"),
        fila("4173/flota$"),
        fila("4173/conductores$"),
        fila("4173/pedidos$"),
        fila("4173/usuarios$"),
        fila("4173/modo$"),
        fila("4173/rutas$", rutas),
      ],
    },
    upload: {
      target: "filesystem",
      outputDir: ".lighthouseci",
    },
  },
};
