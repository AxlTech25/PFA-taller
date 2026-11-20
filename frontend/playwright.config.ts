import { defineConfig, devices } from "@playwright/test";

// PLAYWRIGHT_BASE_URL apunta a un servidor ya levantado (Docker Compose en
// el puerto 5173 o un vite preview local). Sin esa variable, webServer
// compila el frontend y lo sirve en http://127.0.0.1:4173, con el proxy
// hacia la API en VITE_PROXY_TARGET (por defecto http://127.0.0.1:8000).
const baseURL = process.env.PLAYWRIGHT_BASE_URL ?? "http://127.0.0.1:4173";
const servidorExterno = Boolean(process.env.PLAYWRIGHT_BASE_URL);

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  timeout: 60_000,
  expect: { timeout: 10_000 },
  outputDir: "test-results",
  reporter: [
    ["list"],
    ["html", { outputFolder: "playwright-report", open: "never" }],
  ],
  use: {
    baseURL,
    locale: "es-PE",
    timezoneId: "America/Lima",
    trace: process.env.CI ? "retain-on-failure" : "on",
    screenshot: "only-on-failure",
    video: "off",
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "firefox", use: { ...devices["Desktop Firefox"] } },
    { name: "webkit", use: { ...devices["Desktop Safari"] } },
  ],
  webServer: servidorExterno
    ? undefined
    : {
        command: "npm run build && npm run preview -- --host 127.0.0.1 --port 4173 --strictPort",
        url: baseURL,
        reuseExistingServer: !process.env.CI,
        timeout: 180_000,
        env: {
          VITE_PROXY_TARGET: process.env.VITE_PROXY_TARGET ?? "http://127.0.0.1:8000",
        },
      },
});
