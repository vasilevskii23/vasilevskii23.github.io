import puppeteer from "/tmp/node_modules/puppeteer-core/lib/esm/puppeteer/puppeteer-core.js";
import { createServer } from "node:http";
import {
  readFileSync,
  writeFileSync,
  existsSync,
  mkdirSync,
  unlinkSync,
} from "node:fs";
import { join, extname, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = __dirname;
const outDir = join(root, "slides");
const tmpDir = join(root, ".export-tmp");
mkdirSync(outDir, { recursive: true });
mkdirSync(tmpDir, { recursive: true });

const mime = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css",
  ".js": "text/javascript",
  ".mjs": "text/javascript",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".png": "image/png",
  ".svg": "image/svg+xml",
  ".woff2": "font/woff2",
};

const baseHtml = readFileSync(join(root, "slide.html"), "utf8");

function htmlForSlide(n) {
  let html = baseHtml.replace(
    /<section class="slide([^"]*)" data-n="(\d+)">/g,
    (_, cls, num) => {
      const on = Number(num) === n ? " on" : "";
      return `<section class="slide${cls}${on}" data-n="${num}">`;
    }
  );
  // Absolute asset paths so tmp HTML under .export-tmp still loads images.
  html = html.replaceAll('src="assets/', 'src="/assets/');
  html = html.replace(
    /<script>[\s\S]*?<\/script>\s*<\/body>/,
    `<script>document.title=${JSON.stringify(
      `Кино России — слайд ${String(n).padStart(2, "0")}`
    )};</script></body>`
  );
  return html;
}

const server = createServer((req, res) => {
  const urlPath = decodeURIComponent((req.url || "/").split("?")[0]);
  const rel = urlPath === "/" ? "/slide.html" : urlPath;
  const filePath = join(root, rel);
  if (!filePath.startsWith(root) || !existsSync(filePath)) {
    res.writeHead(404);
    res.end("not found");
    return;
  }
  const type = mime[extname(filePath).toLowerCase()] || "application/octet-stream";
  res.writeHead(200, { "Content-Type": type, "Cache-Control": "no-store" });
  res.end(readFileSync(filePath));
});

await new Promise((resolve) => server.listen(8765, "127.0.0.1", resolve));

const chrome = existsSync("/usr/bin/google-chrome-stable")
  ? "/usr/bin/google-chrome-stable"
  : "google-chrome";

const browser = await puppeteer.launch({
  executablePath: chrome,
  headless: true,
  args: ["--no-sandbox", "--disable-gpu", "--hide-scrollbars"],
  defaultViewport: { width: 1080, height: 1350, deviceScaleFactor: 1 },
});

const page = await browser.newPage();

for (let n = 1; n <= 18; n++) {
  const name = `slide_${String(n).padStart(2, "0")}.jpg`;
  const tmpHtml = join(tmpDir, `slide-${n}.html`);
  writeFileSync(tmpHtml, htmlForSlide(n));
  const outFile = join(outDir, name);
  process.stdout.write(`export ${name}...\n`);
  await page.goto(`http://127.0.0.1:8765/.export-tmp/slide-${n}.html`, {
    waitUntil: "networkidle0",
    timeout: 60000,
  });
  await page.evaluate(async () => {
    if (document.fonts?.ready) await document.fonts.ready;
    const imgs = [...document.images];
    await Promise.all(
      imgs.map((img) =>
        img.complete
          ? Promise.resolve()
          : new Promise((res) => {
              img.onload = img.onerror = () => res();
            })
      )
    );
  });
  await page.waitForSelector(".slide.on", { timeout: 10000 });
  await page.screenshot({
    path: outFile,
    type: "jpeg",
    quality: 92,
    clip: { x: 0, y: 0, width: 1080, height: 1350 },
  });
}

await browser.close();
server.close();
for (let n = 1; n <= 18; n++) {
  try {
    unlinkSync(join(tmpDir, `slide-${n}.html`));
  } catch {}
}
console.log("done:", outDir);
