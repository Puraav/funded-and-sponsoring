// Serve the static export in out/ the way Vercel does (clean URLs), for tests and Lighthouse.
// Usage: node scripts/serve-out.mjs [port]
import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { gzipSync } from "node:zlib";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../out");
const port = Number(process.argv[2] ?? 4173);
const types = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript",
  ".css": "text/css",
  ".json": "application/json",
  ".png": "image/png",
  ".ico": "image/x-icon",
  ".woff2": "font/woff2",
  ".txt": "text/plain",
};

createServer(async (request, response) => {
  let file = decodeURIComponent(request.url.split("?")[0]);
  if (file.endsWith("/")) file += "index.html";
  if (!path.extname(file)) file += ".html";
  try {
    const body = await readFile(path.join(root, file));
    const type = types[path.extname(file)] ?? "application/octet-stream";
    // compress text like a real host does, so Lighthouse measures realistic transfer sizes
    const zip = /text|javascript|json/.test(type) && /gzip/.test(request.headers["accept-encoding"] ?? "");
    response.writeHead(200, { "Content-Type": type, ...(zip ? { "Content-Encoding": "gzip" } : {}) });
    response.end(zip ? gzipSync(body) : body);
  } catch {
    response.writeHead(404, { "Content-Type": "text/plain" }).end("not found");
  }
}).listen(port, () => console.log(`serving out/ on http://localhost:${port}`));
