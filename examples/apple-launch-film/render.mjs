#!/usr/bin/env node
/**
 * Renders examples/apple-launch-film/index.html → aura-launch.mp4
 * Uses system Chrome + ffmpeg. Requires: google-chrome, ffmpeg, puppeteer-core
 */
import { spawn } from "node:child_process";
import { createWriteStream, mkdirSync, rmSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import puppeteer from "puppeteer-core";

const __dirname = dirname(fileURLToPath(import.meta.url));
const htmlPath = join(__dirname, "index.html");
const outDir = join(__dirname, "frames");
const outMp4 = join(__dirname, "aura-launch.mp4");
const chromePath =
  process.env.CHROME_PATH ||
  ["/usr/local/bin/google-chrome", "/usr/bin/google-chrome", "/usr/bin/google-chrome-stable"].find(
    (p) => existsSync(p),
  );

if (!chromePath) {
  console.error("Chrome not found. Set CHROME_PATH.");
  process.exit(1);
}

mkdirSync(outDir, { recursive: true });
for (const f of await import("node:fs").then((fs) => fs.readdirSync(outDir))) {
  rmSync(join(outDir, f), { force: true });
}

const browser = await puppeteer.launch({
  executablePath: chromePath,
  headless: "new",
  args: [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--hide-scrollbars",
    `--window-size=1920,1080`,
  ],
  defaultViewport: { width: 1920, height: 1080, deviceScaleFactor: 1 },
});

const page = await browser.newPage();
await page.goto(pathToFileURL(htmlPath).href + "?still=1", {
  waitUntil: "networkidle0",
});
await page.evaluate(() => {
  document.body.classList.add("export");
});

const meta = await page.evaluate(() => window.__FILM__);
const { duration, fps, width, height } = meta;
const totalFrames = Math.round(duration * fps);
console.log(`Rendering ${totalFrames} frames @ ${fps}fps (${width}x${height}), ${duration}s`);

for (let i = 0; i < totalFrames; i++) {
  const t = i / fps;
  await page.evaluate((seconds) => window.seek(seconds), t);
  const file = join(outDir, `frame-${String(i).padStart(5, "0")}.png`);
  await page.screenshot({ path: file, type: "png", clip: { x: 0, y: 0, width, height } });
  if (i % 30 === 0 || i === totalFrames - 1) {
    console.log(`  frame ${i + 1}/${totalFrames} (t=${t.toFixed(2)}s)`);
  }
}

await browser.close();

console.log("Encoding MP4…");
await new Promise((resolve, reject) => {
  const ff = spawn(
    "ffmpeg",
    [
      "-y",
      "-framerate",
      String(fps),
      "-i",
      join(outDir, "frame-%05d.png"),
      "-c:v",
      "libx264",
      "-pix_fmt",
      "yuv420p",
      "-crf",
      "18",
      "-movflags",
      "+faststart",
      outMp4,
    ],
    { stdio: "inherit" },
  );
  ff.on("exit", (code) => (code === 0 ? resolve() : reject(new Error(`ffmpeg exit ${code}`))));
});

console.log(`Done → ${outMp4}`);
