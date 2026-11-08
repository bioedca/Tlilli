// SPDX-FileCopyrightText: 2026 bioedca
// SPDX-License-Identifier: Apache-2.0

import { defineConfig, devices } from "@playwright/test";

// The cloud sandbox ships a Chromium build that Playwright cannot download itself.
// Point TLILLI_PW_CHROMIUM at it there; CI and laptops use Playwright's own browsers.
const chromiumPath = process.env.TLILLI_PW_CHROMIUM;
const port = 4173;
const baseURL = `http://127.0.0.1:${port}`;

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  // No retries: PR-CI-009 allows one only for the desktop `e2e/smoke` job, which is a separate
  // (tauri-driver) suite; a browser test that passes only on retry must fail the `ui` check.
  retries: 0,
  reporter: process.env.CI ? [["github"], ["html", { open: "never" }]] : "list",
  use: {
    baseURL,
    trace: "retain-on-failure",
  },
  projects: [
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
        ...(chromiumPath
          ? { launchOptions: { executablePath: chromiumPath } }
          : {}),
      },
    },
  ],
  webServer: {
    command: `pnpm exec vite build && pnpm exec vite preview --host 127.0.0.1 --port ${port} --strictPort`,
    url: baseURL,
    // Always build and serve the current source; a reused preview could be an older build.
    reuseExistingServer: false,
    timeout: 120_000,
  },
});
