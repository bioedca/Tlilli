import { AxeBuilder } from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

test.describe("shell", () => {
  test("loads with the editor and review landmarks", async ({ page }) => {
    await page.goto("/");

    await expect(page).toHaveTitle("Tlilli");
    await expect(page.getByRole("main", { name: "Editor" })).toBeVisible();
    await expect(
      page.getByRole("complementary", { name: "Review" }),
    ).toBeVisible();
  });

  // PR-TST-020: every page is audited with axe-core and fails on WCAG 2 A/AA violations.
  test("has no WCAG 2 A/AA violations", async ({ page }) => {
    await page.goto("/");

    const results = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
      .analyze();

    expect(results.violations).toEqual([]);
  });
});
