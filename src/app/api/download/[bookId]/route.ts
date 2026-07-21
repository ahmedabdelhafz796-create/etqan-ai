import { NextResponse } from "next/server";
import {
  verifyDownloadToken,
  DOWNLOAD_MAX,
  DOWNLOAD_TTL_MS,
} from "@/lib/download-token";
import { downloadStore } from "@/lib/download-store";
import { consumeGrant } from "@/lib/repositories";
import { fileHash } from "@/lib/download-hash";
import { getBook } from "@/config";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/**
 * GET /api/download/:bookId?token=...
 *
 * Verifies a valid, unexpired purchase token whose per-link download count is
 * still under the limit, then redirects to the book's decrypted PDF on the CDN
 * (prepared at build time at /dl/<hash>.pdf). Redirecting means large files are
 * served by the CDN directly, without any serverless size/time limits.
 */
export async function GET(
  request: Request,
  { params }: { params: Promise<{ bookId: string }> }
) {
  const { bookId } = await params;
  const token = new URL(request.url).searchParams.get("token") || "";

  const verified = verifyDownloadToken(token);
  if (!verified.valid) {
    const status = verified.reason === "expired" ? 410 : 403;
    const message =
      verified.reason === "expired"
        ? "This download link has expired. Please return to the thank-you page to get a fresh one."
        : "Invalid or missing download token.";
    return NextResponse.json({ error: verified.reason, message }, { status });
  }

  if (verified.bookId !== bookId || !getBook(bookId)) {
    return NextResponse.json(
      { error: "mismatch", message: "Token does not match this book." },
      { status: 403 }
    );
  }

  // Enforce the per-link download limit (DB grant, else in-memory fallback).
  const grant = await consumeGrant(verified.jti!);
  if (grant === null) {
    const count = await downloadStore.increment(verified.jti!, DOWNLOAD_TTL_MS);
    if (count > DOWNLOAD_MAX) {
      return NextResponse.json(
        { error: "limit_reached", message: `This link reached its ${DOWNLOAD_MAX}-download limit.` },
        { status: 429 }
      );
    }
  } else if (!grant.ok) {
    const status = grant.reason === "expired" ? 410 : grant.reason === "not_found" ? 403 : 429;
    return NextResponse.json({ error: grant.reason, message: "Download not available." }, { status });
  }

  const hash = fileHash(bookId);
  if (!hash) {
    return NextResponse.json(
      { error: "unconfigured", message: "Downloads are not configured on this server." },
      { status: 503 }
    );
  }

  // Redirect to the CDN-served decrypted PDF.
  const origin = new URL(request.url).origin;
  return NextResponse.redirect(`${origin}/dl/${hash}.pdf`, { status: 302 });
}
