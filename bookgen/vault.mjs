import fs from "fs";
import path from "path";
import os from "os";
import { execFileSync } from "child_process";
import { fileURLToPath } from "url";
import { encrypt, decrypt } from "../scripts/lib/crypto.mjs";

/**
 * Book SOURCES vault.
 *
 * The authored book content (bookgen/books/*.mjs) is the paid product, so it
 * must never sit in plaintext in this public repo. This tool packs the whole
 * books/ directory into a single AES-256-GCM blob (bookgen/books.vault.enc)
 * committed to the repo, and restores it on a fresh checkout. Same key as the
 * download pipeline (NOWPAYMENTS_IPN_SECRET / DOWNLOAD_SIGNING_SECRET).
 *
 *   node vault.mjs pack     # books/  -> books.vault.enc
 *   node vault.mjs unpack   # books.vault.enc -> books/
 */
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const BOOKS = path.join(__dirname, "books");
const VAULT = path.join(__dirname, "books.vault.enc");
const secret = process.env.DOWNLOAD_SIGNING_SECRET || process.env.NOWPAYMENTS_IPN_SECRET || "";

if (!secret) { console.error("[vault] set NOWPAYMENTS_IPN_SECRET (or DOWNLOAD_SIGNING_SECRET)."); process.exit(1); }
const cmd = process.argv[2];

if (cmd === "pack") {
  if (!fs.existsSync(BOOKS)) { console.error("[vault] no books/ to pack."); process.exit(1); }
  const tar = path.join(os.tmpdir(), "books.tar");
  execFileSync("tar", ["-cf", tar, "-C", __dirname, "books"]);
  fs.writeFileSync(VAULT, encrypt(fs.readFileSync(tar), secret));
  fs.rmSync(tar, { force: true });
  const n = fs.readdirSync(BOOKS).filter((f) => f.endsWith(".mjs")).length;
  console.log(`[vault] packed ${n} book source(s) -> books.vault.enc (${(fs.statSync(VAULT).size / 1024).toFixed(0)} KB)`);
} else if (cmd === "unpack") {
  if (!fs.existsSync(VAULT)) { console.error("[vault] no books.vault.enc found."); process.exit(1); }
  const tar = path.join(os.tmpdir(), "books.tar");
  fs.writeFileSync(tar, decrypt(fs.readFileSync(VAULT), secret));
  execFileSync("tar", ["-xf", tar, "-C", __dirname]);
  fs.rmSync(tar, { force: true });
  console.log(`[vault] restored books/ from books.vault.enc`);
} else {
  console.error("usage: node vault.mjs pack|unpack");
  process.exit(1);
}
