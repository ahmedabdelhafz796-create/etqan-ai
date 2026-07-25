import { test } from "node:test";
import assert from "node:assert/strict";
import { encrypt, decrypt, fileHash, deriveKey } from "../scripts/lib/crypto.mjs";

const SECRET = "test-secret-value-1234567890";

test("encrypt → decrypt round-trips exactly", () => {
  const data = Buffer.from("The quick brown fox — مرحبا — Merhaba 🎓", "utf8");
  const blob = encrypt(data, SECRET);
  assert.ok(blob.length > data.length, "ciphertext carries iv+tag overhead");
  const back = decrypt(blob, SECRET);
  assert.deepEqual(back, data);
});

test("decrypt with the wrong key fails (auth tag)", () => {
  const blob = encrypt(Buffer.from("secret"), SECRET);
  assert.throws(() => decrypt(blob, "wrong-secret"));
});

test("ciphertext is non-deterministic (random IV)", () => {
  const a = encrypt(Buffer.from("same"), SECRET);
  const b = encrypt(Buffer.from("same"), SECRET);
  assert.notDeepEqual(a, b);
});

test("fileHash is deterministic and key-dependent", () => {
  const h1 = fileHash("python", SECRET);
  const h2 = fileHash("python", SECRET);
  const h3 = fileHash("python", "other-secret");
  assert.equal(h1, h2);
  assert.notEqual(h1, h3);
  assert.match(h1, /^[0-9a-f]{64}$/);
});

test("deriveKey yields a 32-byte AES-256 key", () => {
  assert.equal(deriveKey(SECRET).length, 32);
});
