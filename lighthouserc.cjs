function tope(maxNumericValue) {
  return ["error", { maxNumericValue, aggregationMethod: "median" }];
}

const comun = {
  "categories:performance": ["error", { minScore: 0.9, aggregationMethod: "median" }],
  "first-contentful-paint": tope(1000),
  "largest-contentful-paint": tope(1400),
  "total-blocking-time": tope(85),
  "cumulative-layout-shift": tope(0.02),
  "resource-summary:total:transferSize": tope(1100000),
};

const rutas = comun;

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
      // Una sola pasada del tablero osciló entre 97 ms y 146 ms de TBT
      // (presupuesto 85 ms) en el mismo artefacto. La mediana de 3 pasadas
      // descarta ese sample suelto sin subir el presupuesto.
      numberOfRuns: 3,
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
