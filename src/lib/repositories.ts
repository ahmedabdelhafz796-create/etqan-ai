import { getDb, ensureSchema } from "@/lib/db";

/**
 * Thin, typed data-access helpers. Every function is a no-op (or returns an
 * empty result) when no database is configured, so the rest of the app never
 * has to branch on DB availability.
 */

export interface OrderRecord {
  id: string;
  paymentId: string | null;
  bookId: string;
  customerEmail: string | null;
  amount: number;
  currency: string | null;
  status: string;
  createdAt: number;
  updatedAt: number;
}

export interface GrantRecord {
  jti: string;
  orderId: string | null;
  bookId: string;
  maxDownloads: number;
  used: number;
  expiresAt: number;
}

// ── Logs ──────────────────────────────────────────────────────────────
export async function log(
  level: "info" | "warn" | "error",
  event: string,
  detail?: unknown
): Promise<void> {
  const db = getDb();
  if (!db) return;
  await ensureSchema();
  await db.execute({
    sql: "INSERT INTO logs (level, event, detail, created_at) VALUES (?, ?, ?, ?)",
    args: [level, event, detail ? JSON.stringify(detail) : null, Date.now()],
  });
}

export async function listLogs(limit = 100) {
  const db = getDb();
  if (!db) return [];
  await ensureSchema();
  const r = await db.execute({
    sql: "SELECT level, event, detail, created_at FROM logs ORDER BY id DESC LIMIT ?",
    args: [limit],
  });
  return r.rows;
}

// ── Customers ─────────────────────────────────────────────────────────
export async function upsertCustomer(email: string, name?: string): Promise<void> {
  const db = getDb();
  if (!db || !email) return;
  await ensureSchema();
  await db.execute({
    sql: `INSERT INTO customers (email, name, created_at) VALUES (?, ?, ?)
          ON CONFLICT(email) DO UPDATE SET name = COALESCE(excluded.name, name)`,
    args: [email.toLowerCase(), name ?? null, Date.now()],
  });
}

export async function listCustomers(limit = 200) {
  const db = getDb();
  if (!db) return [];
  await ensureSchema();
  const r = await db.execute({
    sql: "SELECT email, name, created_at FROM customers ORDER BY created_at DESC LIMIT ?",
    args: [limit],
  });
  return r.rows;
}

// ── Orders ────────────────────────────────────────────────────────────
export async function recordOrder(o: {
  id: string;
  paymentId?: string | null;
  bookId: string;
  customerEmail?: string | null;
  amount: number;
  currency?: string | null;
  status: string;
}): Promise<void> {
  const db = getDb();
  if (!db) return;
  await ensureSchema();
  const now = Date.now();
  await db.execute({
    sql: `INSERT INTO orders (id, payment_id, book_id, customer_email, amount, currency, status, created_at, updated_at)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
          ON CONFLICT(id) DO UPDATE SET
            payment_id = excluded.payment_id,
            status = excluded.status,
            customer_email = COALESCE(excluded.customer_email, orders.customer_email),
            updated_at = excluded.updated_at`,
    args: [
      o.id,
      o.paymentId ?? null,
      o.bookId,
      o.customerEmail?.toLowerCase() ?? null,
      o.amount,
      o.currency ?? null,
      o.status,
      now,
      now,
    ],
  });
}

export async function listOrders(limit = 200) {
  const db = getDb();
  if (!db) return [];
  await ensureSchema();
  const r = await db.execute({
    sql: `SELECT id, payment_id, book_id, customer_email, amount, currency, status, created_at, updated_at
          FROM orders ORDER BY created_at DESC LIMIT ?`,
    args: [limit],
  });
  return r.rows;
}

export async function orderStats() {
  const db = getDb();
  if (!db) return { total: 0, paid: 0, revenue: 0 };
  await ensureSchema();
  const r = await db.execute(
    `SELECT
       COUNT(*) AS total,
       SUM(CASE WHEN status IN ('finished','confirmed') THEN 1 ELSE 0 END) AS paid,
       SUM(CASE WHEN status IN ('finished','confirmed') THEN amount ELSE 0 END) AS revenue
     FROM orders`
  );
  const row = r.rows[0] || {};
  return {
    total: Number(row.total ?? 0),
    paid: Number(row.paid ?? 0),
    revenue: Number(row.revenue ?? 0),
  };
}

// ── Download grants (persistent max-N enforcement) ────────────────────
export async function createGrant(g: {
  jti: string;
  orderId?: string | null;
  bookId: string;
  maxDownloads: number;
  expiresAt: number;
}): Promise<void> {
  const db = getDb();
  if (!db) return;
  await ensureSchema();
  await db.execute({
    sql: `INSERT INTO download_grants (jti, order_id, book_id, max_downloads, used, expires_at, created_at)
          VALUES (?, ?, ?, ?, 0, ?, ?)`,
    args: [g.jti, g.orderId ?? null, g.bookId, g.maxDownloads, g.expiresAt, Date.now()],
  });
}

/**
 * Atomically consume one download from a grant.
 * Returns:
 *  - { ok: true, used } when a download is allowed
 *  - { ok: false, reason } otherwise
 * Falls back to `null` when no DB is configured (caller uses in-memory store).
 */
export async function consumeGrant(
  jti: string
): Promise<
  | { ok: true; used: number }
  | { ok: false; reason: "not_found" | "limit_reached" | "expired" }
  | null
> {
  const db = getDb();
  if (!db) return null;
  await ensureSchema();

  const found = await db.execute({
    sql: "SELECT max_downloads, used, expires_at FROM download_grants WHERE jti = ?",
    args: [jti],
  });
  if (found.rows.length === 0) return { ok: false, reason: "not_found" };
  const row = found.rows[0];
  const used = Number(row.used);
  const expires = Number(row.expires_at);
  if (Date.now() > expires) return { ok: false, reason: "expired" };

  // Conditional update guards against races (used < max).
  const upd = await db.execute({
    sql: "UPDATE download_grants SET used = used + 1 WHERE jti = ? AND used < max_downloads",
    args: [jti],
  });
  if (upd.rowsAffected === 0) return { ok: false, reason: "limit_reached" };
  return { ok: true, used: used + 1 };
}

// ── Settings (key/value overrides for prices, countdown, links, SEO) ──
export async function getSetting(key: string): Promise<string | null> {
  const db = getDb();
  if (!db) return null;
  await ensureSchema();
  const r = await db.execute({
    sql: "SELECT value FROM settings WHERE key = ?",
    args: [key],
  });
  return r.rows.length ? String(r.rows[0].value) : null;
}

export async function getAllSettings(): Promise<Record<string, string>> {
  const db = getDb();
  if (!db) return {};
  await ensureSchema();
  const r = await db.execute("SELECT key, value FROM settings");
  return Object.fromEntries(r.rows.map((row) => [String(row.key), String(row.value)]));
}

export async function setSetting(key: string, value: string): Promise<void> {
  const db = getDb();
  if (!db) return;
  await ensureSchema();
  await db.execute({
    sql: `INSERT INTO settings (key, value, updated_at) VALUES (?, ?, ?)
          ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at`,
    args: [key, value, Date.now()],
  });
}
