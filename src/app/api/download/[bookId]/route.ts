import { NextResponse } from "next/server";
import { promises as fs } from "fs";
import {
  verifyDownloadToken,
  DOWNLOAD_MAX,
  DOWNLOAD_TTL_MS,
} from "@/lib/download-token";
import { downloadStore } from "@/lib/download-store";
import { consumeGrant } from "@/lib/repositories";
import { resolveBookFile } from "@/lib/book-files";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/**
 * GET /api/download/:bookId?token=...
 *
 * Streams a purchased book PDF only when presented with a valid, unexpired
 * download token whose per-link download count is still under the limit
 * (10-minute expiry, max 2 downloads by default).
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
        ? "This download link has expired. Please request a new one."
        : "Invalid or missing download token.";
    return NextResponse.json({ error: verified.reason, message }, { status });
  }

  if (verified.bookId !== bookId) {
    return NextResponse.json(
      { error: "mismatch", message: "Token does not match this book." },
      { status: 403 }
    );
  }

  // Enforce the download-count limit for this specific link.
  // Prefer the persistent DB grant; fall back to the in-memory store.
  let count: number;
  const grant = await consumeGrant(verified.jti!);
  if (grant === null) {
    // No database configured — use the per-instance in-memory counter.
    count = await downloadStore.increment(verified.jti!, DOWNLOAD_TTL_MS);
    if (count > DOWNLOAD_MAX) {
      return NextResponse.json(
        {
          error: "limit_reached",
          message: `This link has reached its ${DOWNLOAD_MAX}-download limit.`,
        },
        { status: 429 }
      );
    }
  } else if (!grant.ok) {
    const status = grant.reason === "expired" ? 410 : grant.reason === "not_found" ? 403 : 429;
    return NextResponse.json(
      {
        error: grant.reason,
        message:
          grant.reason === "limit_reached"
            ? `This link has reached its ${DOWNLOAD_MAX}-download limit.`
            : grant.reason === "expired"
              ? "This download link has expired."
              : "Download grant not found.",
      },
      { status }
    );
  } else {
    count = grant.used;
  }

  const resolved = resolveBookFile(bookId);
  if (!resolved) {
    return NextResponse.json(
      { error: "unknown_book", message: "Unknown book." },
      { status: 404 }
    );
  }

  let data: Buffer;
  try {
    data = await fs.readFile(resolved.absolutePath);
  } catch {
    return NextResponse.json(
      {
        error: "file_unavailable",
        message:
          "The product file is not available on this server. Upload it to the private files directory or configure object storage.",
      },
      { status: 404 }
    );
  }

  return new NextResponse(new Uint8Array(data), {
    status: 200,
    headers: {
      "Content-Type": "application/pdf",
      "Content-Disposition": `attachment; filename="${resolved.downloadName}"`,
      "Content-Length": String(data.length),
      "Cache-Control": "private, no-store",
      "X-Download-Count": String(count),
    },
  });
}
