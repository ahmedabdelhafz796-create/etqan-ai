import crypto from "crypto";

/**
 * Shared file-crypto used by the encrypt tool and the build-time
 * prepare-downloads script. Product PDFs are stored ENCRYPTED in the (public)
 * repo and only decrypted into the deployment's CDN output at build time,
 * using a key derived from NOWPAYMENTS_IPN_SECRET (which lives only in the
 * server environment, never in the repo).
 */

const SALT = "etqan-files-v1";

export function deriveKey(secret) {
  return crypto.scryptSync(secret, SALT, 32);
}

export function encrypt(buffer, secret) {
  const key = deriveKey(secret);
  const iv = crypto.randomBytes(12);
  const cipher = crypto.createCipheriv("aes-256-gcm", key, iv);
  const enc = Buffer.concat([cipher.update(buffer), cipher.final()]);
  const tag = cipher.getAuthTag();
  return Buffer.concat([iv, tag, enc]);
}

export function decrypt(blob, secret) {
  const key = deriveKey(secret);
  const iv = blob.subarray(0, 12);
  const tag = blob.subarray(12, 28);
  const data = blob.subarray(28);
  const decipher = crypto.createDecipheriv("aes-256-gcm", key, iv);
  decipher.setAuthTag(tag);
  return Buffer.concat([decipher.update(data), decipher.final()]);
}

/**
 * Deterministic, unguessable public filename for a book's decrypted PDF.
 * Same value must be computable by the app at runtime to build the redirect.
 */
export function fileHash(bookId, secret) {
  return crypto.createHmac("sha256", secret).update(`dl:${bookId}`).digest("hex");
}
