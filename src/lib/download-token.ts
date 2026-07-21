import crypto from "crypto";

/**
 * Stateless, tamper-proof download tokens.
 *
 * A token encodes the book id, a unique id (jti) and an expiry timestamp,
 * signed with HMAC-SHA256. It is used to build one-time-ish secure download
 * links that expire after `DOWNLOAD_TTL_MS` (10 minutes by default). The
 * per-token download *count* limit (max 2) is enforced separately by the
 * download store, keyed on the jti.
 */

const TEN_MINUTES = 10 * 60 * 1000;
export const DOWNLOAD_TTL_MS = Number(
  process.env.DOWNLOAD_TTL_MS || TEN_MINUTES
);
export const DOWNLOAD_MAX = Number(process.env.DOWNLOAD_MAX || 2);

function signingSecret(): string {
  const secret =
    process.env.DOWNLOAD_SIGNING_SECRET ||
    process.env.NOWPAYMENTS_IPN_SECRET ||
    "";
  return secret;
}

interface TokenPayload {
  b: string; // bookId
  j: string; // jti
  e: number; // expiry (ms epoch)
}

function b64url(input: Buffer | string): string {
  return Buffer.from(input)
    .toString("base64")
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "");
}

function b64urlDecode(input: string): Buffer {
  const pad = input.length % 4 ? 4 - (input.length % 4) : 0;
  const normalized = input.replace(/-/g, "+").replace(/_/g, "/") + "=".repeat(pad);
  return Buffer.from(normalized, "base64");
}

function sign(payloadB64: string, secret: string): string {
  return b64url(
    crypto.createHmac("sha256", secret).update(payloadB64).digest()
  );
}

export interface IssuedToken {
  token: string;
  jti: string;
  expiresAt: number;
}

/** Create a signed download token plus its metadata (jti, expiry). */
export function issueDownloadToken(
  bookId: string,
  ttlMs: number = DOWNLOAD_TTL_MS
): IssuedToken {
  const secret = signingSecret();
  if (!secret) {
    throw new Error(
      "DOWNLOAD_SIGNING_SECRET (or NOWPAYMENTS_IPN_SECRET) must be set to issue download tokens."
    );
  }
  const jti = crypto.randomUUID();
  const expiresAt = Date.now() + ttlMs;
  const payload: TokenPayload = { b: bookId, j: jti, e: expiresAt };
  const payloadB64 = b64url(JSON.stringify(payload));
  const token = `${payloadB64}.${sign(payloadB64, secret)}`;
  return { token, jti, expiresAt };
}

/** Create a signed download token for a book. */
export function createDownloadToken(
  bookId: string,
  ttlMs: number = DOWNLOAD_TTL_MS
): string {
  return issueDownloadToken(bookId, ttlMs).token;
}

export interface VerifiedToken {
  valid: boolean;
  bookId?: string;
  jti?: string;
  reason?: "malformed" | "bad_signature" | "expired" | "no_secret";
}

/** Verify a download token's signature and expiry. */
export function verifyDownloadToken(token: string): VerifiedToken {
  const secret = signingSecret();
  if (!secret) return { valid: false, reason: "no_secret" };

  const parts = token.split(".");
  if (parts.length !== 2) return { valid: false, reason: "malformed" };
  const [payloadB64, sig] = parts;

  const expected = sign(payloadB64, secret);
  const a = Buffer.from(sig);
  const b = Buffer.from(expected);
  if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) {
    return { valid: false, reason: "bad_signature" };
  }

  let payload: TokenPayload;
  try {
    payload = JSON.parse(b64urlDecode(payloadB64).toString("utf8"));
  } catch {
    return { valid: false, reason: "malformed" };
  }

  if (Date.now() > payload.e) {
    return { valid: false, bookId: payload.b, jti: payload.j, reason: "expired" };
  }
  return { valid: true, bookId: payload.b, jti: payload.j };
}
