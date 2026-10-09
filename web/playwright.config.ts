import { defineConfig } from "@playwright/test";

// Smoke tests run against the static export, served the way it is deployed.
export default defineConfig({
  testDir: "./tests",
  use: { baseURL: "http://localhost:4173" },
  webServer: {
    command: "node scripts/serve-out.mjs 4173",
    url: "http://localhost:4173",
    reuseExistingServer: !process.env.CI,
  },
});
