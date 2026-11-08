// SPDX-FileCopyrightText: 2026 bioedca
// SPDX-License-Identifier: Apache-2.0

import { afterAll, beforeAll, expect, inject, test } from "vitest";
import { Session } from "./webdriver";

// The desktop smoke suite (PRD 34 §1): the real app, started by tauri-driver, wires up. Phase 0
// has a window with two empty landmarks; later phases add opening a workspace, typing, a run
// with a fake agent and accepting a suggestion.
let session: Session;

beforeAll(async () => {
  const { server, application } = inject("webdriver");
  session = await Session.start(server, application);
});

afterAll(async () => {
  await session?.end();
});

test("the window shows the UI built into the app", async () => {
  expect(await session.title()).toBe("Tlilli");
  // tauri://localhost serves the files embedded in the binary (on Windows the app's own protocol
  // takes the form http://tauri.localhost), so the page did not come from a dev server.
  expect(await session.location()).toMatch(/^tauri:\/\/localhost\/?$/);
});

test("the editor and the review pane are named landmarks", async () => {
  const editor = await session.waitFor("main");
  expect(await session.role(editor)).toBe("main");
  expect(await session.label(editor)).toBe("Editor");

  const review = await session.waitFor("aside");
  expect(await session.role(review)).toBe("complementary");
  expect(await session.label(review)).toBe("Review");
});
