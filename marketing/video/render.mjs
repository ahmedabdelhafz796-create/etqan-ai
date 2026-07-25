/**
 * ============================================================
 *  E-tqan — promo video renderer
 * ============================================================
 *  Drives `scene.html` frame by frame with headless Chromium and
 *  pipes the frames straight into ffmpeg (nothing touches disk but
 *  the final file). Because the stage is a pure function of time,
 *  every render is bit-for-bit reproducible.
 *
 *    node render.mjs                 # every deliverable
 *    node render.mjs master reels    # only these presets
 *    node render.mjs --list
 *
 *  Requires: playwright (bookgen/node_modules), ffmpeg (ffmpeg-static
 *  or the FFMPEG env var). Fonts come from bookgen/fonts.
 * ============================================================
 */
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { spawn } from "child_process";
import { renderMusic } from "./music.mjs";
import { fontCss, chromiumPath, loadPlaywright, ffmpegPath } from "./shared.mjs";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..", "..");
const OUT = path.join(ROOT, "marketing", "renders");
const FFMPEG = ffmpegPath(HERE, ROOT);

/* ── presets (mirrors marketing/ASSET_SPECS.md) ──────── */
/** `cut` = list of [from, to] windows on the 150 s master timeline. */
const PRESETS = {
  master:  { w: 1920, h: 1080, fps: 30, cut: [[0, 150]],  file: "etqan-master-16x9-1080p.mp4",  label: "YouTube master 16:9 · 2:30" },
  trailer: { w: 1920, h: 1080, fps: 30, cut: [[0, 6], [6, 13], [45, 52], [85, 93], [142, 150]], file: "etqan-trailer-16x9-30s.mp4", label: "Short trailer 16:9 · 0:30" },
  social:  { w: 1920, h: 1080, fps: 30, cut: [[0, 45]],   file: "etqan-linkedin-16x9-45s.mp4",  label: "X / LinkedIn 16:9 · 0:45" },
  reels:   { w: 1080, h: 1920, fps: 30, cut: [[6, 13], [16, 24], [45, 52], [85, 93], [142, 150]], file: "etqan-reels-9x16-30s.mp4", label: "TikTok / Reels 9:16 · 0:30" },
  shorts:  { w: 1080, h: 1920, fps: 30, cut: [[0, 30], [45, 52], [125, 132], [142, 150]], file: "etqan-shorts-9x16-45s.mp4", label: "YouTube Shorts 9:16 · 0:45" },
  story:   { w: 1080, h: 1920, fps: 30, cut: [[0, 6], [143, 147]], file: "etqan-story-9x16-10s.mp4", label: "Story teaser 9:16 · 0:10" },
  feed:    { w: 1080, h: 1080, fps: 30, cut: [[6, 13], [45, 52], [143, 150]], file: "etqan-feed-1x1-20s.mp4", label: "Instagram feed 1:1 · 0:20" },
};
const durationOf = (p) => p.cut.reduce((n, [a, b]) => n + (b - a), 0);
/** output second → master-timeline second */
function mapTime(t, cut) {
  let acc = 0;
  for (const [a, b] of cut) {
    const len = b - a;
    if (t < acc + len) return a + (t - acc);
    acc += len;
  }
  const last = cut[cut.length - 1];
  return last[1] - 0.001;
}

/* ── render one preset ───────────────────────────────── */
async function renderPreset(browser, html, name) {
  const p = PRESETS[name];
  const dur = durationOf(p);
  const frames = Math.round(dur * p.fps);
  const outFile = path.join(OUT, p.file);
  const wav = path.join(OUT, `.${name}.wav`);

  fs.writeFileSync(wav, renderMusic(dur));

  const page = await browser.newPage({
    viewport: { width: p.w, height: p.h },
    deviceScaleFactor: 1,
    reducedMotion: "reduce",
  });
  await page.setContent(html, { waitUntil: "load" });
  await page.evaluate(() => window.__ready);

  const ff = spawn(FFMPEG, [
    "-y", "-hide_banner", "-loglevel", "error",
    "-f", "image2pipe", "-vcodec", "mjpeg", "-framerate", String(p.fps), "-i", "pipe:0",
    "-i", wav,
    "-c:v", "libx264", "-preset", "medium", "-crf", "20",
    "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.2",
    "-x264-params", "keyint=60:min-keyint=30",
    "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
    "-movflags", "+faststart", "-shortest",
    outFile,
  ]);
  let ffErr = "";
  ff.stderr.on("data", (d) => { ffErr += d.toString(); });
  const done = new Promise((res, rej) => {
    ff.on("close", (code) => (code === 0 ? res() : rej(new Error(`ffmpeg exited ${code}\n${ffErr}`))));
    ff.on("error", rej);
  });

  const t0 = Date.now();
  for (let f = 0; f < frames; f++) {
    const mt = mapTime(f / p.fps, p.cut);
    await page.evaluate(([t, i]) => window.__seek(t, i), [mt, f]);
    const buf = await page.screenshot({ type: "jpeg", quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once("drain", r));
    if (f % 150 === 0 || f === frames - 1) {
      const pct = ((f + 1) / frames) * 100;
      process.stdout.write(`\r  ${name}: ${pct.toFixed(0)}% (${f + 1}/${frames})   `);
    }
  }
  ff.stdin.end();
  await done;
  await page.close();
  fs.unlinkSync(wav);

  const mb = (fs.statSync(outFile).size / 1048576).toFixed(1);
  process.stdout.write(`\r  ✓ ${p.file} · ${dur.toFixed(0)}s · ${p.w}×${p.h} · ${mb}MB · ${((Date.now() - t0) / 1000).toFixed(0)}s\n`);
}

/* ── thumbnails ──────────────────────────────────────── */
async function renderThumbs(browser, html) {
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
  await page.setContent(html, { waitUntil: "load" });
  await page.evaluate(() => window.__ready);
  for (const lang of ["en", "ar"]) {
    await page.evaluate((l) => window.__thumb(l), lang);
    const file = path.join(OUT, `etqan-thumbnail-${lang}.png`);
    await page.screenshot({ path: file });
    console.log(`  ✓ ${path.basename(file)} · 1280×720`);
  }
  await page.close();
}

/* ── main ────────────────────────────────────────────── */
const args = process.argv.slice(2);
if (args.includes("--list")) {
  for (const [k, v] of Object.entries(PRESETS)) console.log(`${k.padEnd(9)} ${v.label} → ${v.file}`);
  process.exit(0);
}
const wanted = args.filter((a) => !a.startsWith("--"));
const todo = wanted.length ? wanted : Object.keys(PRESETS);
for (const n of todo) if (!PRESETS[n]) throw new Error(`unknown preset "${n}" (see --list)`);

fs.mkdirSync(OUT, { recursive: true });
const html = fs.readFileSync(path.join(HERE, "scene.html"), "utf8").replace("/*FONTS*/", fontCss(ROOT));

const { chromium } = loadPlaywright(ROOT, HERE);
const browser = await chromium.launch({
  executablePath: chromiumPath(),
  args: ["--force-color-profile=srgb", "--font-render-hinting=none", "--disable-lcd-text", "--hide-scrollbars"],
});
console.log(`[video] rendering ${todo.length} preset(s) → marketing/renders/`);
for (const name of todo) await renderPreset(browser, html, name);
if (!wanted.length || args.includes("--thumbs")) await renderThumbs(browser, html);
await browser.close();
console.log("[video] done.");
