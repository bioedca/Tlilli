// SPDX-FileCopyrightText: 2026 bioedca
// SPDX-License-Identifier: Apache-2.0

import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { App } from "./App";

describe("App", () => {
  it("renders the editor and review landmarks with accessible names", () => {
    render(<App />);

    expect(screen.getByRole("main", { name: "Editor" })).toBeInTheDocument();
    expect(
      screen.getByRole("complementary", { name: "Review" }),
    ).toBeInTheDocument();
  });
});
