import crypto from "crypto";

/**
 * Must match `fileHash` in scripts/lib/crypto.mjs exactly. Produces the
 * unguessable public filename of a book's decrypted PDF so the download route
 * can redirect the buyer to it after verifying their purchase token.
 */
export function fileHash(bookId: string): string | null {
  const secret =
    process.env.NOWPAYMENTS_IPN_SECRET ||
    process.env.DOWNLOAD_SIGNING_SECRET ||
    "";
  if (!secret) return null;
  return crypto.createHmac("sha256", secret).update(`dl:${bookId}`).digest("hex");
}
