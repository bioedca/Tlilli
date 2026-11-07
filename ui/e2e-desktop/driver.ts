/**
 * Global setup of the desktop smoke suite: starts tauri-driver before the tests and stops it
 * after them (PRD 34 §1, D-086). tauri-driver starts the platform's WebDriver itself
 * (WebKitWebDriver on Linux) and starts the app for each session. The app is the debug build
 * with the UI embedded: `pnpm -C ui tauri build --debug --no-bundle`, or set TLILLI_APP.
 */
import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import { resolve } from "node:path";
import type { TestProject } from "vitest/node";

declare module "vitest" {
  export interface ProvidedContext {
    webdriver: { server: string; application: string };
  }
}

// tauri-driver's default port; it gives the native driver the next one, 4445.
const PORT = 4444;
const READY_MS = 30_000;

export default async function setup(project: TestProject) {
  const application =
    process.env.TLILLI_APP ??
    resolve(import.meta.dirname, "../../target/debug/tlilli-app");
  if (!existsSync(application)) {
    throw new Error(
      `${application} does not exist: build it with \`pnpm -C ui tauri build --debug --no-bundle\`, or set TLILLI_APP`,
    );
  }
  // Without a display the app's window never opens and the first session waits out its timeout.
  if (
    process.platform === "linux" &&
    !process.env.DISPLAY &&
    !process.env.WAYLAND_DISPLAY
  ) {
    throw new Error(
      "no display: run the suite under a virtual one, `xvfb-run -a pnpm -C ui test:e2e:desktop`",
    );
  }

  const driver = spawn(
    process.env.TAURI_DRIVER ?? "tauri-driver",
    ["--port", String(PORT)],
    {
      stdio: ["ignore", "inherit", "inherit"],
    },
  );
  let exit: string | undefined;
  driver.on("error", (error) => {
    exit = `could not start tauri-driver (cargo install tauri-driver --locked): ${error.message}`;
  });
  driver.on("exit", (code, signal) => {
    exit = `tauri-driver exited (${signal ?? `status ${code}`})`;
  });

  const server = `http://127.0.0.1:${PORT}`;
  const deadline = Date.now() + READY_MS;
  for (;;) {
    if (exit !== undefined) {
      throw new Error(exit);
    }
    const ready = await fetch(`${server}/status`).then(
      (response) => response.ok,
      () => false,
    );
    if (ready) {
      break;
    }
    if (Date.now() > deadline) {
      driver.kill();
      throw new Error(
        `tauri-driver did not answer on ${server} within ${READY_MS} ms`,
      );
    }
    await new Promise((resolve) => setTimeout(resolve, 100));
  }

  project.provide("webdriver", { server, application });
  return async () => {
    if (exit === undefined) {
      const exited = new Promise((resolve) => driver.once("exit", resolve));
      driver.kill();
      await exited;
    }
  };
}
