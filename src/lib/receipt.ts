import crypto from "crypto";

/**
 * Receipt links — the durable half of delivery.
 *
 * A download link is deliberately short-lived (10 minutes, 2 uses), which is
 * right for a click straight after payment but wrong for an email that may be
 * opened days later. A *receipt* token is the long-lived counterpart: it names
 * the order, is signed with the same secret, and lasts `RECEIPT_TTL_DAYS`.
 * Opening `/thank-you?receipt=…` exchanges it for a fresh download link, so the
 * buyer can come back at any point in the window without contacting support —
 * and the file itself is never reachable from the email alone.
 */

const DAY = 24 * 60 * 60 * 1000;
export const RECEIPT_TTL_DAYS = Number(process.env.RECEIPT_TTL_DAYS || 30);
/** How many download links one receipt may mint before it stops working. */
export const RECEIPT_MAX_ISSUES = Number(process.env.RECEIPT_MAX_ISSUES || 12);

function signingSecret(): string {
  return (
    process.env.DOWNLOAD_SIGNING_SECRET ||
    process.env.NOWPAYMENTS_IPN_SECRET ||
    ""
  );
}

interface ReceiptPayload {
  o: string; // order id
  b: string; // product id
  e: number; // expiry (ms epoch)
}

const b64url = (input: Buffer | string) =>
  Buffer.from(input).toString("base64").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");

function b64urlDecode(input: string): Buffer {
  const pad = input.length % 4 ? 4 - (input.length % 4) : 0;
  return Buffer.from(input.replace(/-/g, "+").replace(/_/g, "/") + "=".repeat(pad), "base64");
}

const sign = (payload: string, secret: string) =>
  b64url(crypto.createHmac("sha256", secret).update(`receipt:${payload}`).digest());

/** Create a signed receipt token for an order. Returns "" when unconfigured. */
export function issueReceiptToken(
  orderId: string,
  productId: string,
  ttlMs: number = RECEIPT_TTL_DAYS * DAY
): string {
  const secret = signingSecret();
  if (!secret) return "";
  const payload: ReceiptPayload = { o: orderId, b: productId, e: Date.now() + ttlMs };
  const body = b64url(JSON.stringify(payload));
  return `${body}.${sign(body, secret)}`;
}

export interface VerifiedReceipt {
  valid: boolean;
  orderId?: string;
  productId?: string;
  reason?: "malformed" | "bad_signature" | "expired" | "no_secret";
}

/** Verify a receipt token's signature and expiry. */
export function verifyReceiptToken(token: string): VerifiedReceipt {
  const secret = signingSecret();
  if (!secret) return { valid: false, reason: "no_secret" };

  const parts = token.split(".");
  if (parts.length !== 2) return { valid: false, reason: "malformed" };
  const [body, sig] = parts;

  const expected = sign(body, secret);
  const a = Buffer.from(sig);
  const b = Buffer.from(expected);
  if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) {
    return { valid: false, reason: "bad_signature" };
  }

  let payload: ReceiptPayload;
  try {
    payload = JSON.parse(b64urlDecode(body).toString("utf8"));
  } catch {
    return { valid: false, reason: "malformed" };
  }
  if (Date.now() > payload.e) {
    return { valid: false, orderId: payload.o, productId: payload.b, reason: "expired" };
  }
  return { valid: true, orderId: payload.o, productId: payload.b };
}

/** Absolute URL a buyer can return to for a fresh download link. */
export function receiptUrl(baseUrl: string, token: string): string {
  return `${baseUrl.replace(/\/$/, "")}/thank-you?receipt=${encodeURIComponent(token)}`;
}
