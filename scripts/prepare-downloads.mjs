import fs from "fs";
import path from "path";
import { decrypt, fileHash } from "./lib/crypto.mjs";

/**
 * Runs BEFORE `next build` (npm "prebuild").
 *
 * Decrypts the committed, encrypted product PDFs into the deployment's
 * `public/dl/<hash>.pdf`, where <hash> is an unguessable HMAC of the book id
 * keyed by NOWPAYMENTS_IPN_SECRET. These decrypted files are served directly
 * by the CDN (no serverless size/time limits) and are never committed to git
 * (public/dl is gitignored). The download route redirects to them only after
 * verifying a valid, short-lived purchase token.
 *
 * If the secret isn't available (e.g. a local build without env), it simply
 * skips — nothing breaks.
 */

const BOOKS = ["triple-analysis", "ai-trading"];
const ASSETS_DIR = path.join(process.cwd(), "assets", "books");
const COURSES_DIR = path.join(process.cwd(), "assets", "courses");
const OUT_DIR = path.join(process.cwd(), "public", "dl");

const secret =
  process.env.DOWNLOAD_SIGNING_SECRET || process.env.NOWPAYMENTS_IPN_SECRET || "";

if (!secret) {
  console.log("[prepare-downloads] no secret set — skipping (downloads inactive).");
  process.exit(0);
}

fs.mkdirSync(OUT_DIR, { recursive: true });

let ok = 0;
for (const id of BOOKS) {
  const encPath = path.join(ASSETS_DIR, `${id}.enc`);
  if (!fs.existsSync(encPath)) {
    console.warn(`[prepare-downloads] missing ${encPath} — skipping ${id}`);
    continue;
  }
  try {
    const plain = decrypt(fs.readFileSync(encPath), secret);
    const outPath = path.join(OUT_DIR, `${fileHash(id, secret)}.pdf`);
    fs.writeFileSync(outPath, plain);
    ok++;
    console.log(`[prepare-downloads] ${id} → public/dl/${path.basename(outPath)} (${(plain.length / 1048576).toFixed(1)}MB)`);
  } catch (err) {
    console.error(`[prepare-downloads] failed for ${id}:`, err.message);
  }
}
console.log(`[prepare-downloads] prepared ${ok}/${BOOKS.length} book file(s).`);

// Courses & bundles: each assets/courses/<id>.enc is an encrypted ZIP of that
// product's trilingual PDFs. The product id is derived from the filename, so
// this stays in sync with the catalog automatically — no hardcoded list.
let cok = 0;
let ctotal = 0;
if (fs.existsSync(COURSES_DIR)) {
  const encs = fs.readdirSync(COURSES_DIR).filter((f) => f.endsWith(".enc"));
  ctotal = encs.length;
  for (const file of encs) {
    const id = file.replace(/\.enc$/, "");
    try {
      const plain = decrypt(fs.readFileSync(path.join(COURSES_DIR, file)), secret);
      const outPath = path.join(OUT_DIR, `${fileHash(id, secret)}.zip`);
      fs.writeFileSync(outPath, plain);
      cok++;
      console.log(`[prepare-downloads] ${id} → public/dl/${path.basename(outPath)} (${(plain.length / 1048576).toFixed(1)}MB)`);
    } catch (err) {
      console.error(`[prepare-downloads] failed for ${id}:`, err.message);
    }
  }
}
console.log(`[prepare-downloads] prepared ${cok}/${ctotal} course file(s).`);
