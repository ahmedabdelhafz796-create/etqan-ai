import crypto from "crypto";
import { cookies } from "next/headers";

/**
 * Minimal, dependency-free admin authentication.
 *
 * A single admin password (`ADMIN_PASSWORD`) grants a signed, expiring
 * session cookie (HMAC-SHA256 with `ADMIN_SESSION_SECRET`). No database row
 * or user table needed. Admin is fully disabled until both env vars are set.
 */

const COOKIE_NAME = "etqan_admin";
const SESSION_TTL_MS = 12 * 60 * 60 * 1000; // 12 hours

function sessionSecret(): string {
  return (
    process.env.ADMIN_SESSION_SECRET ||
    process.env.ADMIN_PASSWORD || // fallback so a set password alone works
    ""
  );
}

export function isAdminConfigured(): boolean {
  return Boolean(process.env.ADMIN_PASSWORD && sessionSecret());
}

/** Constant-time password check. */
export function checkPassword(input: string): boolean {
  const expected = process.env.ADMIN_PASSWORD || "";
  if (!expected) return false;
  const a = Buffer.from(input);
  const b = Buffer.from(expected);
  if (a.length !== b.length) return false;
  return crypto.timingSafeEqual(a, b);
}

function sign(value: string): string {
  return crypto
    .createHmac("sha256", sessionSecret())
    .update(value)
    .digest("hex");
}

export function createSessionValue(): string {
  const exp = String(Date.now() + SESSION_TTL_MS);
  return `${exp}.${sign(exp)}`;
}

export function verifySessionValue(value: string | undefined): boolean {
  if (!value) return false;
  const [exp, sig] = value.split(".");
  if (!exp || !sig) return false;
  const expected = sign(exp);
  const a = Buffer.from(sig);
  const b = Buffer.from(expected);
  if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) return false;
  return Date.now() < Number(exp);
}

export const ADMIN_COOKIE = COOKIE_NAME;
export const ADMIN_SESSION_TTL_MS = SESSION_TTL_MS;

/** Server-side helper: is the current request authenticated? */
export async function isAuthenticated(): Promise<boolean> {
  const store = await cookies();
  return verifySessionValue(store.get(COOKIE_NAME)?.value);
}
