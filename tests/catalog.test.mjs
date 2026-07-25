import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, "..");

// The catalog is authored in TypeScript; validate its integrity by parsing the
// declared product ids and asserting each has a committed encrypted delivery
// blob. This catches "a course exists in the store but can't be delivered".
const catalogSrc = fs.readFileSync(path.join(ROOT, "src", "catalog.ts"), "utf8");

function idsFrom() {
  const ids = [];
  const re = /id:\s*"([a-z0-9-]+)",\s*category:/g;
  let m;
  while ((m = re.exec(catalogSrc))) ids.push(m[1]);
  return ids;
}

test("catalog declares the expected number of products", () => {
  const ids = idsFrom();
  assert.ok(ids.length >= 14, `expected >= 14 products, found ${ids.length}`);
  assert.equal(new Set(ids).size, ids.length, "product ids must be unique");
});

test("every catalog product has an encrypted delivery blob", () => {
  const ids = idsFrom();
  const dir = path.join(ROOT, "assets", "courses");
  for (const id of ids) {
    const enc = path.join(dir, `${id}.enc`);
    assert.ok(fs.existsSync(enc), `missing delivery blob for "${id}" (${enc})`);
    assert.ok(fs.statSync(enc).size > 0, `empty delivery blob for "${id}"`);
  }
});

test("legacy trading books still have encrypted assets", () => {
  const dir = path.join(ROOT, "assets", "books");
  for (const id of ["triple-analysis", "ai-trading"]) {
    assert.ok(fs.existsSync(path.join(dir, `${id}.enc`)), `missing ${id}.enc`);
  }
});
