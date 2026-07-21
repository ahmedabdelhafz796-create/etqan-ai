import { NextResponse } from "next/server";
import { promises as fs } from "fs";
import path from "path";
import { isAuthenticated } from "@/lib/admin-auth";
import { getBook } from "@/config";
import { uploadPathFor, UPLOADS_DIR } from "@/lib/book-files";
import { log } from "@/lib/repositories";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const MAX_BYTES = 60 * 1024 * 1024; // 60 MB

/**
 * POST /api/admin/upload  (multipart/form-data: bookId, file)
 * Stores the product PDF for a book in the private uploads directory.
 *
 * Note: on serverless hosting the local filesystem is ephemeral. For durable
 * storage, mount a volume at PRIVATE_FILES_DIR or swap this for object
 * storage (S3 / R2 / Vercel Blob) — the download route resolves through
 * book-files.ts, which is the single place to change.
 */
export async function POST(request: Request) {
  if (!(await isAuthenticated())) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }

  let form: FormData;
  try {
    form = await request.formData();
  } catch {
    return NextResponse.json({ error: "bad_form" }, { status: 400 });
  }

  const bookId = String(form.get("bookId") || "");
  const file = form.get("file");

  if (!getBook(bookId)) {
    return NextResponse.json({ error: "unknown_book" }, { status: 404 });
  }
  if (!(file instanceof File)) {
    return NextResponse.json({ error: "no_file" }, { status: 400 });
  }
  if (file.type && file.type !== "application/pdf") {
    return NextResponse.json(
      { error: "not_pdf", message: "Only PDF files are accepted." },
      { status: 415 }
    );
  }
  if (file.size > MAX_BYTES) {
    return NextResponse.json(
      { error: "too_large", message: "File exceeds 60 MB." },
      { status: 413 }
    );
  }

  const bytes = Buffer.from(await file.arrayBuffer());
  await fs.mkdir(UPLOADS_DIR, { recursive: true });
  const dest = uploadPathFor(bookId);
  await fs.writeFile(dest, bytes);
  await log("info", "book_uploaded", { bookId, size: bytes.length, name: path.basename(dest) });

  return NextResponse.json({ ok: true, size: bytes.length });
}
