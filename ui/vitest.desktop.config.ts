import { defineConfig } from "vitest/config";

// The desktop smoke suite, `pnpm -C ui test:e2e:desktop` (PRD 34 §1, D-086): the debug app driven
// through tauri-driver, under `xvfb-run -a` on Linux. vite.config.ts runs the unit tests and
// playwright.config.ts the browser suite; neither picks up e2e-desktop/.
export default defineConfig({
  test: {
    dir: "e2e-desktop",
    include: ["**/*.test.ts"],
    environment: "node",
    globalSetup: ["e2e-desktop/driver.ts"],
    // One app, one driver: the files run one after another.
    fileParallelism: false,
    // PR-CI-009 allows one retry for e2e/smoke, and for no other check.
    retry: 1,
    // A session starts the app, which can take a while on a cold runner.
    hookTimeout: 60_000,
    testTimeout: 30_000,
  },
});
