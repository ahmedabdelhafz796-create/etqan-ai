import fs from "fs";
import path from "path";
import { decrypt, encrypt } from "./lib/crypto.mjs";

/**
 * ============================================================
 *  RE-KEY every encrypted asset in the repository
 * ============================================================
 *  Rotates the file-encryption key without re-rendering anything:
 *  each blob is decrypted with the OLD key and re-encrypted with
 *  the NEW one, in place.
 *
 *  Covers:
 *    assets/books/*.enc        (trading book PDFs)
 *    assets/courses/*.enc      (course & bundle deliverables)
 *    bookgen/books.vault.enc   (private book sources)
 *
 *  Run this LOCALLY so the new key never leaves your machine:
 *
 *    OLD_SECRET='current-value' NEW_SECRET='your-new-value' \
 *      node scripts/rekey-assets.mjs
 *
 *  Then set DOWNLOAD_SIGNING_SECRET=<your-new-value> in your host's
 *  environment and redeploy. Because the public download filenames are
 *  an HMAC of this key, they rotate automatically on the next build —
 *  old links stop resolving, which is exactly what you want.
 *
 *  Use --dry-run to verify before writing anything.
 * ============================================================
 */

const OLD = process.env.OLD_SECRET || "";
const NEW = process.env.NEW_SECRET || "";
const DRY = process.argv.includes("--dry-run");

if (!OLD || !NEW) {
  console.error("Usage: OLD_SECRET=… NEW_SECRET=… node scripts/rekey-assets.mjs [--dry-run]");
  process.exit(1);
}
if (OLD === NEW) {
  console.error("[rekey] OLD_SECRET and NEW_SECRET are identical — nothing to do.");
  process.exit(1);
}
if (NEW.length < 16) {
  console.error("[rekey] NEW_SECRET is too short. Use at least 16 characters (32+ recommended).");
  process.exit(1);
}

const ROOT = process.cwd();
const TARGETS = [
  ...listEnc(path.join(ROOT, "assets", "books")),
  ...listEnc(path.join(ROOT, "assets", "courses")),
  path.join(ROOT, "bookgen", "books.vault.enc"),
].filter((f) => fs.existsSync(f));

function listEnc(dir) {
  try {
    return fs.readdirSync(dir).filter((f) => f.endsWith(".enc")).map((f) => path.join(dir, f));
  } catch {
    return [];
  }
}

if (TARGETS.length === 0) {
  console.error("[rekey] no .enc assets found — run from the repository root.");
  process.exit(1);
}

console.log(`[rekey] ${DRY ? "DRY RUN — " : ""}re-keying ${TARGETS.length} asset(s)…`);

let ok = 0;
const failures = [];

for (const file of TARGETS) {
  const rel = path.relative(ROOT, file);
  try {
    const plain = decrypt(fs.readFileSync(file), OLD);
    const reEncrypted = encrypt(plain, NEW);
    // Verify the new blob decrypts before touching the original.
    const check = decrypt(reEncrypted, NEW);
    if (!check.equals(plain)) throw new Error("verification mismatch");
    if (!DRY) fs.writeFileSync(file, reEncrypted);
    ok++;
    console.log(`  ✓ ${rel} (${(plain.length / 1048576).toFixed(2)}MB)`);
  } catch (err) {
    failures.push(rel);
    console.error(`  ✗ ${rel}: ${err.message}`);
  }
}

console.log(`[rekey] ${DRY ? "would re-key" : "re-keyed"} ${ok}/${TARGETS.length} asset(s).`);

if (failures.length) {
  console.error("\n[rekey] FAILED for: " + failures.join(", "));
  console.error("Nothing was written for those files. Check that OLD_SECRET is correct.");
  process.exit(1);
}

if (!DRY) {
  console.log(
    "\nNext steps:\n" +
    "  1. Set DOWNLOAD_SIGNING_SECRET=<NEW_SECRET> in your hosting environment.\n" +
    "  2. Commit the re-encrypted assets and redeploy.\n" +
    "  3. Verify a download works, then rotate your NOWPayments keys freely —\n" +
    "     payments and file encryption are now independent."
  );
}
