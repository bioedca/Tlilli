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
  // PRD 33 (`e2e/smoke`): one retry allowed in CI.
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [["github"], ["html", { open: "never" }]] : "list",
  use: {
    baseURL,
    trace: "on-first-retry",
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
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
