/**
 * Quick visual check: render single frames of `scene.html` at chosen
 * timestamps so a human (or an agent) can eyeball the composition.
 *
 *   node stills.mjs 3 9 20 36 50 72 92 110 132 147
 */
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..", "..");
const OUT = process.env.STILLS_DIR || path.join(HERE, ".stills");

const { fontCss, chromiumPath, loadPlaywright } = await import("./shared.mjs");
const times = process.argv.slice(2).map(Number);
const list = times.length ? times : [2, 4.8, 9, 13, 20, 26, 36, 43, 50, 60, 70, 78, 90, 100, 110, 122, 130, 140, 146];
const W = Number(process.env.SW || 1600), H = Number(process.env.SH || 900);

fs.mkdirSync(OUT, { recursive: true });
const html = fs.readFileSync(path.join(HERE, "scene.html"), "utf8").replace("/*FONTS*/", fontCss(ROOT));
const { chromium } = loadPlaywright(ROOT, HERE);
const browser = await chromium.launch({ executablePath: chromiumPath(), args: ["--force-color-profile=srgb", "--hide-scrollbars"] });
const page = await browser.newPage({ viewport: { width: W, height: H } });
await page.setContent(html, { waitUntil: "load" });
await page.evaluate(() => window.__ready);
for (const t of list) {
  await page.evaluate(([tt]) => window.__seek(tt, Math.round(tt * 30)), [t]);
  await page.screenshot({ path: path.join(OUT, `t${String(t).padStart(6, "0")}.png`) });
}
await page.evaluate(() => window.__thumb("en"));
await page.screenshot({ path: path.join(OUT, "thumb-en.png") });
await page.evaluate(() => window.__thumb("ar"));
await page.screenshot({ path: path.join(OUT, "thumb-ar.png") });
await browser.close();
console.log(`[stills] ${list.length + 2} frames → ${OUT}`);
