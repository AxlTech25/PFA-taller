module.exports = {
  ci: {
    collect: {
      startServerCommand: "node frontend/scripts/servir.mjs",
      startServerReadyPattern: "escuchando",
      url: ["http://127.0.0.1:4173/login"],
      numberOfRuns: 1,
      settings: {
        preset: "desktop",
        onlyCategories: ["performance"],
        chromeFlags: "--no-sandbox --disable-gpu --headless=new",
      },
    },
    assert: {
      assertions: {
        "categories:performance": ["error", { minScore: 0.9 }],
        "first-contentful-paint": ["error", { maxNumericValue: 1000 }],
        "largest-contentful-paint": ["error", { maxNumericValue: 1400 }],
        "total-blocking-time": ["error", { maxNumericValue: 85 }],
        "cumulative-layout-shift": ["error", { maxNumericValue: 0.02 }],
        "resource-summary:total:transferSize": ["error", { maxNumericValue: 1100000 }],
      },
    },
    upload: {
      target: "filesystem",
      outputDir: ".lighthouseci",
    },
  },
};
