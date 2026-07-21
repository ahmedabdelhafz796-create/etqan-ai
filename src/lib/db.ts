import { createClient, type Client } from "@libsql/client";

/**
 * Database layer (libSQL / Turso).
 *
 * - Local dev: falls back to a file database (`file:local.db`) so everything
 *   works out of the box and can be verified without any cloud account.
 * - Production: set `TURSO_DATABASE_URL` + `TURSO_AUTH_TOKEN` (Turso / libSQL)
 *   for a serverless-friendly, globally-replicated SQLite.
 *
 * When no database is configured in production, `getDb()` returns null and
 * callers degrade gracefully (the marketing site + payments still work; the
 * admin/orders features simply report "database not configured").
 */

let client: Client | null = null;
let schemaReady: Promise<void> | null = null;

function resolveUrl(): string {
  if (process.env.TURSO_DATABASE_URL) return process.env.TURSO_DATABASE_URL;
  if (process.env.DATABASE_URL) return process.env.DATABASE_URL;
  // Convenient local default outside production.
  if (process.env.NODE_ENV !== "production") return "file:local.db";
  return "";
}

export function isDbConfigured(): boolean {
  return resolveUrl().length > 0;
}

export function getDb(): Client | null {
  const url = resolveUrl();
  if (!url) return null;
  if (!client) {
    client = createClient({
      url,
      authToken: process.env.TURSO_AUTH_TOKEN,
    });
  }
  return client;
}

const SCHEMA = [
  `CREATE TABLE IF NOT EXISTS settings (
     key TEXT PRIMARY KEY,
     value TEXT NOT NULL,
     updated_at INTEGER NOT NULL
   )`,
  `CREATE TABLE IF NOT EXISTS books (
     id TEXT PRIMARY KEY,
     original_price REAL NOT NULL,
     offer_price REAL NOT NULL,
     active INTEGER NOT NULL DEFAULT 1,
     file_key TEXT,
     updated_at INTEGER NOT NULL
   )`,
  `CREATE TABLE IF NOT EXISTS customers (
     email TEXT PRIMARY KEY,
     name TEXT,
     created_at INTEGER NOT NULL
   )`,
  `CREATE TABLE IF NOT EXISTS orders (
     id TEXT PRIMARY KEY,
     payment_id TEXT,
     book_id TEXT NOT NULL,
     customer_email TEXT,
     amount REAL NOT NULL,
     currency TEXT,
     status TEXT NOT NULL,
     created_at INTEGER NOT NULL,
     updated_at INTEGER NOT NULL
   )`,
  `CREATE TABLE IF NOT EXISTS download_grants (
     jti TEXT PRIMARY KEY,
     order_id TEXT,
     book_id TEXT NOT NULL,
     max_downloads INTEGER NOT NULL,
     used INTEGER NOT NULL DEFAULT 0,
     expires_at INTEGER NOT NULL,
     created_at INTEGER NOT NULL
   )`,
  `CREATE TABLE IF NOT EXISTS logs (
     id INTEGER PRIMARY KEY AUTOINCREMENT,
     level TEXT NOT NULL,
     event TEXT NOT NULL,
     detail TEXT,
     created_at INTEGER NOT NULL
   )`,
];

/** Create tables if they don't exist. Idempotent; runs at most once per process. */
export async function ensureSchema(): Promise<void> {
  const db = getDb();
  if (!db) return;
  if (!schemaReady) {
    schemaReady = (async () => {
      for (const stmt of SCHEMA) {
        await db.execute(stmt);
      }
    })();
  }
  return schemaReady;
}
