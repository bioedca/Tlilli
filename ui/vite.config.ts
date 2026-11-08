// SPDX-FileCopyrightText: 2026 bioedca
// SPDX-License-Identifier: Apache-2.0

import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"],
    // Playwright owns `e2e/`; Vitest only runs the unit and integration tests under `src/`.
    include: ["src/**/*.test.{ts,tsx}"],
    coverage: {
      provider: "v8",
      include: ["src/**"],
      exclude: ["src/test/**", "src/main.tsx"],
      reporter: ["text", "lcov"],
    },
  },
});
