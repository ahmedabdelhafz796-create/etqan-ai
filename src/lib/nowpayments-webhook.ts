import crypto from "crypto";

/**
 * NOWPayments IPN signature verification.
 *
 * NOWPayments signs each IPN callback with HMAC-SHA512 over the JSON body
 * whose keys are sorted alphabetically (recursively), using your IPN secret.
 * The signature arrives in the `x-nowpayments-sig` header.
 *
 * Docs: https://documenter.getpostman.com/view/7907941/S1a32n38#ipn-callbacks
 */

/** Recursively sort object keys so the serialization is deterministic. */
export function sortObject(obj: unknown): unknown {
  if (Array.isArray(obj)) return obj.map(sortObject);
  if (obj && typeof obj === "object") {
    return Object.keys(obj as Record<string, unknown>)
      .sort()
      .reduce<Record<string, unknown>>((acc, key) => {
        acc[key] = sortObject((obj as Record<string, unknown>)[key]);
        return acc;
      }, {});
  }
  return obj;
}

/**
 * Verify an IPN signature. Returns true only if the HMAC matches.
 * Uses a constant-time comparison to avoid timing attacks.
 */
export function verifyIpnSignature(
  payload: unknown,
  signature: string | null,
  secret: string
): boolean {
  if (!signature || !secret) return false;

  const sorted = sortObject(payload);
  const hmac = crypto.createHmac("sha512", secret);
  hmac.update(JSON.stringify(sorted));
  const digest = hmac.digest("hex");

  const a = Buffer.from(digest, "utf8");
  const b = Buffer.from(signature, "utf8");
  if (a.length !== b.length) return false;
  return crypto.timingSafeEqual(a, b);
}

/** Payment statuses NOWPayments can report. */
export type NowPaymentsStatus =
  | "waiting"
  | "confirming"
  | "confirmed"
  | "sending"
  | "partially_paid"
  | "finished"
  | "failed"
  | "refunded"
  | "expired";

/** A payment is fully settled and the product can be delivered. */
export function isPaidStatus(status: string): boolean {
  return status === "finished" || status === "confirmed";
}
