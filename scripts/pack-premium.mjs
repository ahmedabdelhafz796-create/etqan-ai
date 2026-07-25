import fs from "fs";
import path from "path";
import os from "os";
import { execFileSync } from "child_process";
import { encrypt } from "./lib/crypto.mjs";

/**
 * Packs the rendered PREMIUM E-tqan books for a product into its encrypted
 * delivery blob (assets/courses/<id>.enc), replacing any repackaged originals.
 *
 * It collects bookgen/out/<id>.<lang>.pdf for a product id and any bundle
 * members, names them nicely, zips, encrypts and writes the course blob.
 *
 *   NOWPAYMENTS_IPN_SECRET=… node scripts/pack-premium.mjs python
 *   NOWPAYMENTS_IPN_SECRET=… node scripts/pack-premium.mjs python javascript …
 */
const secret = process.env.DOWNLOAD_SIGNING_SECRET || process.env.NOWPAYMENTS_IPN_SECRET || "";
if (!secret) { console.error("[pack-premium] set NOWPAYMENTS_IPN_SECRET."); process.exit(1); }

const ROOT = process.cwd();
const OUT_BOOKS = path.join(ROOT, "bookgen", "out");
const COURSES = path.join(ROOT, "assets", "courses");
fs.mkdirSync(COURSES, { recursive: true });

const LANG = { en: "English", ar: "Arabic", tr: "Turkish" };
// product id -> human title used in the zipped filenames
const TITLES = {
  python: "Python", javascript: "JavaScript", java: "Java", html: "HTML", css: "CSS", sql: "SQL",
  "ai-app-building": "AI App Building", "building-websites": "Building Any Website",
  "excel-ai": "Excel + AI", "design-graphics": "Design & Graphics", "ai-arsenal": "AI Arsenal 2026",
};
// bundle id -> member product ids
const BUNDLES = {
  "bundle-languages": ["html", "css", "javascript", "python", "java", "sql"],
  "bundle-future-skills": ["ai-app-building", "building-websites", "design-graphics", "excel-ai"],
  "bundle-gold": ["python", "javascript", "java", "html", "css", "sql", "ai-arsenal", "ai-app-building", "building-websites", "excel-ai", "design-graphics"],
};

function premiumFiles(pid) {
  // returns [{src, name}] for every rendered language edition of a product
  const out = [];
  for (const [lang, label] of Object.entries(LANG)) {
    const src = path.join(OUT_BOOKS, `${pid}.${lang}.pdf`);
    if (fs.existsSync(src)) out.push({ src, name: `${TITLES[pid] || pid} — E-tqan Premium (${label}).pdf` });
  }
  return out;
}

function packProduct(id) {
  let files;
  if (BUNDLES[id]) {
    files = [];
    for (const m of BUNDLES[id]) files.push(...premiumFiles(m));
  } else {
    files = premiumFiles(id);
  }
  if (!files.length) { console.warn(`  ! no rendered premium PDFs for ${id} — skipped`); return; }
  const staging = fs.mkdtempSync(path.join(os.tmpdir(), `prem-${id}-`));
  for (const f of files) fs.copyFileSync(f.src, path.join(staging, f.name));
  const zip = path.join(os.tmpdir(), `${id}.premium.zip`);
  fs.rmSync(zip, { force: true });
  execFileSync("zip", ["-j", "-q", zip, ...fs.readdirSync(staging).map((f) => path.join(staging, f))]);
  const blob = encrypt(fs.readFileSync(zip), secret);
  fs.writeFileSync(path.join(COURSES, `${id}.enc`), blob);
  fs.rmSync(staging, { recursive: true, force: true });
  fs.rmSync(zip, { force: true });
  console.log(`  ✓ ${id}: ${files.length} premium PDF(s) → assets/courses/${id}.enc (${(blob.length / 1048576).toFixed(2)}MB)`);
}

const ids = process.argv.slice(2);
if (!ids.length) { console.error("usage: node scripts/pack-premium.mjs <productId...>"); process.exit(1); }
console.log("[pack-premium] packing premium editions…");
for (const id of ids) packProduct(id);
console.log("[pack-premium] done.");
