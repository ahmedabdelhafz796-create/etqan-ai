/**
 * Download-count store — enforces the "max N downloads per link" rule.
 *
 * The default implementation is an in-memory Map, which is correct for a
 * single long-lived server but resets on redeploy and is not shared across
 * serverless instances. For production on serverless (Vercel), set
 * `KV_REST_API_URL` + `KV_REST_API_TOKEN` (Vercel KV / Upstash Redis) and
 * swap in a KV-backed implementation — the interface below is the seam.
 *
 * Because tokens already expire after 10 minutes, the in-memory store is a
 * reasonable default: a buyer's link and its counter share the same short
 * lifetime.
 */

export interface DownloadStore {
  /**
   * Atomically increment the counter for `jti` and return the new count.
   * Returns the count AFTER incrementing.
   */
  increment(jti: string, ttlMs: number): Promise<number>;
}

class InMemoryDownloadStore implements DownloadStore {
  private counts = new Map<string, { n: number; expires: number }>();

  async increment(jti: string, ttlMs: number): Promise<number> {
    this.gc();
    const now = Date.now();
    const existing = this.counts.get(jti);
    if (!existing || existing.expires < now) {
      this.counts.set(jti, { n: 1, expires: now + ttlMs });
      return 1;
    }
    existing.n += 1;
    return existing.n;
  }

  private gc() {
    const now = Date.now();
    for (const [k, v] of this.counts) {
      if (v.expires < now) this.counts.delete(k);
    }
  }
}

// Reuse a single instance across hot reloads in dev.
const globalForStore = globalThis as unknown as {
  __downloadStore?: DownloadStore;
};

export const downloadStore: DownloadStore =
  globalForStore.__downloadStore ?? new InMemoryDownloadStore();

if (process.env.NODE_ENV !== "production") {
  globalForStore.__downloadStore = downloadStore;
}
