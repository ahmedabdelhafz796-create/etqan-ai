import fs from "fs";
import path from "path";
import os from "os";
import { execFileSync } from "child_process";
import { encrypt } from "./lib/crypto.mjs";

/**
 * DEV TOOL (run manually, not in CI).
 *
 * Packs each catalog product's trilingual course PDFs into a single ZIP,
 * encrypts it with the store secret and writes assets/courses/<id>.enc.
 * These encrypted blobs are the only course files committed to the (public)
 * repo; prepare-downloads.mjs decrypts them into public/dl/<hash>.zip at
 * build time, and the download route serves them after verifying a purchase.
 *
 * Usage:
 *   NOWPAYMENTS_IPN_SECRET=... EDU_DIR=/path/to/source node scripts/pack-courses.mjs
 */

const secret =
  process.env.DOWNLOAD_SIGNING_SECRET || process.env.NOWPAYMENTS_IPN_SECRET || "";
if (!secret) {
  console.error("[pack-courses] set NOWPAYMENTS_IPN_SECRET to pack.");
  process.exit(1);
}

const EDU_DIR = process.env.EDU_DIR;
if (!EDU_DIR || !fs.existsSync(EDU_DIR)) {
  console.error("[pack-courses] set EDU_DIR to the source PDFs directory.");
  process.exit(1);
}

const OUT_DIR = path.join(process.cwd(), "assets", "courses");
fs.mkdirSync(OUT_DIR, { recursive: true });

// product id -> list of source PDF paths (relative to EDU_DIR).
const P = {
  python: ["01_python/Python - English.pdf", "01_python/Python - Arabic.pdf", "01_python/Python - Turkish.pdf"],
  javascript: ["02_javascript/JavaScript - English.pdf", "02_javascript/JavaScript - Arabic.pdf", "02_javascript/JavaScript - Turkish.pdf"],
  java: ["03_java/Java - English.pdf", "03_java/Java - Arabic.pdf", "03_java/Java - Turkish.pdf"],
  html: ["04_html/HTML - English.pdf", "04_html/HTML - Arabic.pdf", "04_html/HTML - Turkish.pdf"],
  css: ["05_css/CSS - English.pdf", "05_css/CSS - Arabic.pdf", "05_css/CSS - Turkish.pdf"],
  sql: ["06_sql/SQL - English.pdf", "06_sql/SQL - Arabic.pdf"],
  "ai-app-building": ["07_ai_app_building/AI App Building - English.pdf", "07_ai_app_building/AI App Building - Arabic.pdf", "07_ai_app_building/AI App Building - Turkish.pdf"],
  "building-websites": ["08_building_any_website/Building Any Website - English.pdf", "08_building_any_website/Building Any Website - Arabic.pdf", "08_building_any_website/Building Any Website - Turkish.pdf"],
  "excel-ai": ["09_excel_ai/Excel and AI - English.pdf", "09_excel_ai/Excel and AI - Arabic.pdf", "09_excel_ai/Excel and AI - Turkish.pdf"],
  "design-graphics": ["10_design_graphics/Design and Graphics - English.pdf", "10_design_graphics/Design and Graphics - Arabic.pdf", "10_design_graphics/Design and Graphics - Turkish.pdf"],
  "ai-arsenal": fs.readdirSync(path.join(EDU_DIR, "11_ai_arsenal_2026")).filter((f) => f.endsWith(".pdf")).map((f) => `11_ai_arsenal_2026/${f}`),
};

// Bundles = union of member products' files (+ any bonus files).
const BUNDLES = {
  "bundle-languages": ["html", "css", "javascript", "python", "java", "sql"],
  "bundle-future-skills": ["ai-app-building", "building-websites", "design-graphics", "excel-ai"],
  "bundle-gold": ["python", "javascript", "java", "html", "css", "sql", "ai-arsenal", "ai-app-building", "building-websites", "excel-ai", "design-graphics"],
};
const bonus = { "bundle-languages": ["12_bundle_languages/Roadmap Bonus - Arabic.pdf"] };
for (const [id, members] of Object.entries(BUNDLES)) {
  const files = new Set();
  for (const m of members) for (const f of P[m]) files.add(f);
  for (const f of bonus[id] || []) files.add(f);
  P[id] = [...files];
}

function packOne(id, rels) {
  const staging = fs.mkdtempSync(path.join(os.tmpdir(), `pack-${id}-`));
  for (const rel of rels) {
    const src = path.join(EDU_DIR, rel);
    if (!fs.existsSync(src)) { console.warn(`  ! missing ${rel}`); continue; }
    fs.copyFileSync(src, path.join(staging, path.basename(rel)));
  }
  const zipPath = path.join(os.tmpdir(), `${id}.zip`);
  fs.rmSync(zipPath, { force: true });
  execFileSync("zip", ["-j", "-q", zipPath, ...fs.readdirSync(staging).map((f) => path.join(staging, f))]);
  const blob = encrypt(fs.readFileSync(zipPath), secret);
  fs.writeFileSync(path.join(OUT_DIR, `${id}.enc`), blob);
  fs.rmSync(staging, { recursive: true, force: true });
  fs.rmSync(zipPath, { force: true });
  console.log(`  ✓ ${id}: ${rels.length} file(s) → assets/courses/${id}.enc (${(blob.length / 1048576).toFixed(2)}MB)`);
}

console.log("[pack-courses] packing…");
for (const [id, rels] of Object.entries(P)) packOne(id, rels);
console.log("[pack-courses] done.");
