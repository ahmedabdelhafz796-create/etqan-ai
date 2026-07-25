/**
 * Shared plumbing for the video tools: font embedding and binary lookup.
 */
import fs from "fs";
import path from "path";
import { createRequire } from "module";

/* Font subsets → the code points each face is allowed to serve. */
const RANGE = {
  latin:
    "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329," +
    "U+2000-206F,U+2070-209F,U+20AC,U+2122,U+2190-21BB,U+2212,U+2215,U+2500-257F,U+2580-259F," +
    "U+25A0-25FF,U+2713-2717,U+FEFF,U+FFFD",
  "latin-ext":
    "U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+1D00-1DBF,U+1E00-1E9F," +
    "U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF",
  arabic:
    "U+0600-06FF,U+0750-077F,U+0870-088E,U+0890-0891,U+0898-08E1,U+08E3-08FF,U+200C-200E," +
    "U+2010-2011,U+204F,U+2E41,U+FB50-FDFF,U+FE70-FEFF",
};
const FAMILY = {
  Sora: "Sora", Inter: "Inter", Cairo: "Cairo",
  JetBrainsMono: "JetBrains Mono", SourceSerif4: "Source Serif 4", Amiri: "Amiri",
};

/** Build self-contained @font-face rules from `bookgen/fonts`. */
export function fontCss(root) {
  const dir = path.join(root, "bookgen", "fonts");
  const out = [];
  for (const f of fs.readdirSync(dir)) {
    const m = /^([A-Za-z0-9]+)-(\d+)-(normal|italic)-(latin|latin-ext|arabic)\.woff2$/.exec(f);
    if (!m || !FAMILY[m[1]]) continue;
    const [, fam, weight, style, subset] = m;
    const b64 = fs.readFileSync(path.join(dir, f)).toString("base64");
    out.push(
      `@font-face{font-family:"${FAMILY[fam]}";font-style:${style};font-weight:${weight};` +
        `font-display:block;src:url(data:font/woff2;base64,${b64}) format("woff2");` +
        `unicode-range:${RANGE[subset]};}`
    );
  }
  if (!out.length) throw new Error(`no fonts found in ${dir}`);
  return out.join("\n");
}

/** Playwright pins an exact Chromium build; use whatever this image ships. */
export function chromiumPath() {
  if (process.env.CHROMIUM_PATH) return process.env.CHROMIUM_PATH;
  for (const p of [
    "/opt/pw-browsers/chromium/chrome-linux/chrome",
    "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    "/opt/pw-browsers/chromium",
  ]) if (fs.existsSync(p)) return p;
  return undefined;
}

function requireFrom(dirs, name) {
  for (const dir of dirs) {
    if (!dir) continue;
    try { return createRequire(path.join(dir, "index.js"))(name); } catch { /* keep looking */ }
  }
  return null;
}

export function loadPlaywright(root, here) {
  const pw = requireFrom([here, root, path.join(root, "bookgen")], "playwright");
  if (!pw) throw new Error("playwright not found — install it in bookgen/ (npm i playwright)");
  return pw;
}

export function ffmpegPath(here, root) {
  if (process.env.FFMPEG && fs.existsSync(process.env.FFMPEG)) return process.env.FFMPEG;
  const bin = requireFrom([here, root, process.env.VIDEO_TOOLS], "ffmpeg-static");
  if (!bin) {
    throw new Error(
      "ffmpeg not found — run `npm i ffmpeg-static` inside marketing/video, " +
      "or set FFMPEG=/path/to/ffmpeg (a build with libx264 + aac)."
    );
  }
  return bin;
}
