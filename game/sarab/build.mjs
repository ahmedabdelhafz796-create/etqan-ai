/**
 * Bundles the game into ONE self-contained HTML file.
 * No CDN, no external fonts, no network at runtime — which is what
 * the web game portals (and the artifact sandbox) require.
 *
 *   node build.mjs
 */
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import * as esbuild from "esbuild";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..", "..");
const OUT = path.join(HERE, "dist");

const RANGE = {
  latin: "U+0000-00FF,U+0131,U+0152-0153,U+2000-206F,U+20AC,U+2122,U+2212,U+FEFF,U+FFFD",
  arabic: "U+0600-06FF,U+0750-077F,U+08A0-08FF,U+200C-200E,U+2010-2011,U+204F,U+2E41,U+FB50-FDFF,U+FE70-FEFF",
};

function fontCss() {
  const dir = path.join(ROOT, "bookgen", "fonts");
  const want = [
    ["Cairo", 400, "Cairo-400-normal-arabic.woff2", "arabic"],
    ["Cairo", 400, "Cairo-400-normal-latin.woff2", "latin"],
    ["Cairo", 700, "Cairo-700-normal-arabic.woff2", "arabic"],
    ["Cairo", 700, "Cairo-700-normal-latin.woff2", "latin"],
  ];
  return want
    .filter(([, , f]) => fs.existsSync(path.join(dir, f)))
    .map(([fam, w, f, sub]) => {
      const b64 = fs.readFileSync(path.join(dir, f)).toString("base64");
      return `@font-face{font-family:"${fam}";font-style:normal;font-weight:${w};font-display:swap;` +
        `src:url(data:font/woff2;base64,${b64}) format("woff2");unicode-range:${RANGE[sub]};}`;
    })
    .join("\n");
}

const bundle = await esbuild.build({
  entryPoints: [path.join(HERE, "src", "main.js")],
  bundle: true,
  minify: true,
  format: "iife",
  target: ["es2020"],
  write: false,
  legalComments: "none",
});
const js = bundle.outputFiles[0].text;

const html = fs
  .readFileSync(path.join(HERE, "src", "index.template.html"), "utf8")
  .replace("/*FONTS*/", fontCss())
  .replace("/*GAME*/", () => js);

fs.mkdirSync(OUT, { recursive: true });
const file = path.join(OUT, "index.html");
fs.writeFileSync(file, html);
console.log(`[sarab] ${path.relative(ROOT, file)} · ${(html.length / 1024).toFixed(0)} KB (js ${(js.length / 1024).toFixed(0)} KB)`);
