// Screenshot the dbt docs lineage graph into docs/lineage.png.
// Usage (after `dbt docs generate`): node scripts/lineage-screenshot.mjs
import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "@playwright/test";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const target = path.join(root, "dbt", "target");
const types = { ".html": "text/html", ".json": "application/json" };

const server = createServer(async (request, response) => {
  const name = request.url === "/" ? "index.html" : request.url.split("?")[0].slice(1);
  try {
    const body = await readFile(path.join(target, path.basename(name)));
    response.writeHead(200, { "Content-Type": types[path.extname(name)] ?? "text/plain" });
    response.end(body);
  } catch {
    response.writeHead(404).end();
  }
});
await new Promise((resolve) => server.listen(0, resolve));
const { port } = server.address();

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 2000, height: 1200 }, deviceScaleFactor: 2 });
// g_v=1 opens the full-screen graph; the selector shows this project's models, not dbt_utils
await page.goto(`http://localhost:${port}/#!/overview?g_v=1&g_i=fundsponsor&g_e=dbt_utils`);
await page.waitForSelector("canvas", { timeout: 30000 });
await page.waitForTimeout(4000);
await page.screenshot({ path: path.join(root, "docs", "lineage.png") });
await browser.close();
server.close();
console.log("wrote docs/lineage.png");
