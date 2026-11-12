import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach, vi } from "vitest";

import { vaciarConsultas } from "../consulta";

document.documentElement.lang = "es";

afterEach(() => {
  cleanup();
  vaciarConsultas();
  sessionStorage.clear();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});
