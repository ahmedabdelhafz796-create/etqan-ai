import path from "path";

/**
 * Maps a book id to its private product file. The files live outside the web
 * root (default `private/books/`, gitignored) and are only ever streamed
 * through the authenticated /api/download route — never served statically.
 *
 * On serverless hosting, point PRIVATE_FILES_DIR at a mounted volume, or
 * replace the resolver with signed object-storage URLs (S3/R2/Vercel Blob).
 */
const FILES_DIR =
  process.env.PRIVATE_FILES_DIR || path.join(process.cwd(), "private", "books");

const BOOK_FILES: Record<string, { file: string; downloadName: string }> = {
  "triple-analysis": {
    file: "Abu omran-2.pdf",
    downloadName: "Triple-Analysis-Etqan-AI.pdf",
  },
  "ai-trading": {
    file: "AI-Trading-Guide-1.pdf",
    downloadName: "Advanced-AI-Trading-Etqan-AI.pdf",
  },
};

export interface ResolvedBookFile {
  absolutePath: string;
  downloadName: string;
}

export function resolveBookFile(bookId: string): ResolvedBookFile | null {
  const entry = BOOK_FILES[bookId];
  if (!entry) return null;
  // Guard against path traversal — only known basenames are used.
  const absolutePath = path.join(FILES_DIR, path.basename(entry.file));
  return { absolutePath, downloadName: entry.downloadName };
}
