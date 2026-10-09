import { expect, test, type Page } from "@playwright/test";

/** Collect console errors and failed requests so a page that "loads" with errors still fails. */
function watch(page: Page): string[] {
  const problems: string[] = [];
  page.on("console", (message) => {
    if (message.type() === "error") problems.push(message.text());
  });
  page.on("pageerror", (error) => problems.push(error.message));
  page.on("response", (response) => {
    if (response.status() >= 400) problems.push(`${response.status()} ${response.url()}`);
  });
  return problems;
}

test("home shows the headline numbers and both charts", async ({ page }) => {
  const problems = watch(page);
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toContainText("H-1B");
  await expect(page.locator("figure svg").first()).toBeVisible();
  await expect(page.locator("figure svg")).toHaveCount(2);
  expect(problems).toEqual([]);
});

test("explore filters the table", async ({ page }) => {
  const problems = watch(page);
  await page.goto("/explore");
  const counter = page.getByTestId("result-count");
  const before = await counter.textContent();
  await page.getByLabel("Filed for H-1B before").selectOption("yes");
  await expect(counter).not.toHaveText(before!);
  await page.getByLabel("Size of latest raise").selectOption("$50M+");
  const rows = page.locator("tbody tr");
  expect(await rows.count()).toBeGreaterThan(0);
  expect(problems).toEqual([]);
});

test("a company page opens from explore", async ({ page }) => {
  const problems = watch(page);
  await page.goto("/explore");
  await page.getByLabel("Filed for H-1B before").selectOption("yes");
  await page.locator("tbody tr a").first().click();
  await expect(page).toHaveURL(/\/company\//);
  await expect(page.getByRole("heading", { name: "Raises" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Form D" }).first()).toBeVisible();
  expect(problems).toEqual([]);
});

test("radar and method load", async ({ page }) => {
  const problems = watch(page);
  await page.goto("/radar");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Radar");
  await page.goto("/method");
  await expect(page.getByRole("heading", { name: "Match quality" })).toBeVisible();
  expect(problems).toEqual([]);
});

test("no sideways scrolling on a phone", async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 800 });
  for (const path of ["/", "/explore", "/radar", "/method"]) {
    await page.goto(path);
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - window.innerWidth,
    );
    expect(overflow, path).toBeLessThanOrEqual(0);
  }
});
