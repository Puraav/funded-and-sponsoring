import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Fully static site: `next build` writes plain files to out/.
  output: "export",
  images: { unoptimized: true },
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
