import crypto from "crypto";

/**
 * ============================================================
 *  Lemon Squeezy — Payment Service (architecture)
 * ============================================================
 *  A clean, typed integration surface for Lemon Squeezy hosted
 *  checkout (cards / PayPal), offered ALONGSIDE NOWPayments crypto.
 *
 *  Real implementation: every function talks to the Lemon Squeezy
 *  REST API using the credentials in your environment. It is inert
 *  (isLemonConfigured() === false) until you set the env vars —
 *  no secrets are ever hardcoded.
 *
 *  Required env (see .env.example):
 *    LEMONSQUEEZY_API_KEY       — server API key
 *    LEMONSQUEEZY_STORE_ID      — numeric store id
 *    LEMONSQUEEZY_WEBHOOK_SECRET — signing secret for webhooks
 *    LEMONSQUEEZY_VARIANT_MAP   — optional JSON { "<productId>": "<variantId>" }
 *
 *  Docs: https://docs.lemonsqueezy.com/api
 * ============================================================
 */

const API = "https://api.lemonsqueezy.com/v1";
const API_KEY = process.env.LEMONSQUEEZY_API_KEY || "";
const STORE_ID = process.env.LEMONSQUEEZY_STORE_ID || "";
const WEBHOOK_SECRET = process.env.LEMONSQUEEZY_WEBHOOK_SECRET || "";

export function isLemonConfigured(): boolean {
  return API_KEY.trim().length > 0 && STORE_ID.trim().length > 0;
}

/** Optional map of catalog product id → Lemon Squeezy variant id. */
export function variantFor(productId: string): string | null {
  try {
    const map = JSON.parse(process.env.LEMONSQUEEZY_VARIANT_MAP || "{}") as Record<string, string>;
    return map[productId] ?? null;
  } catch {
    return null;
  }
}

export interface LemonCheckoutParams {
  productId: string;
  title: string;
  priceAmount: number; // USD
  redirectUrl?: string;
  email?: string;
}

/**
 * Create a hosted Lemon Squeezy checkout and return its URL.
 *
 * If a variant id is mapped for the product (LEMONSQUEEZY_VARIANT_MAP), the
 * checkout uses that product's configured price. Otherwise it creates a
 * custom-priced checkout for the exact amount (custom price in cents).
 * Server-side only — the API key never reaches the browser.
 */
export async function createLemonCheckout(
  params: LemonCheckoutParams
): Promise<{ url: string } | null> {
  if (!isLemonConfigured()) return null;
  const variantId = variantFor(params.productId);

  const attributes: Record<string, unknown> = {
    checkout_data: {
      ...(params.email ? { email: params.email } : {}),
      custom: { product_id: params.productId },
    },
    product_options: {
      redirect_url: params.redirectUrl,
      name: `${params.title} — E-tqan`,
    },
  };
  // Custom price (in cents) when no fixed variant price is used.
  if (!variantId) {
    attributes.custom_price = Math.round(params.priceAmount * 100);
  }

  const body = {
    data: {
      type: "checkouts",
      attributes,
      relationships: {
        store: { data: { type: "stores", id: String(STORE_ID) } },
        variant: {
          data: { type: "variants", id: String(variantId ?? process.env.LEMONSQUEEZY_DEFAULT_VARIANT_ID ?? "") },
        },
      },
    },
  };

  const res = await fetch(`${API}/checkouts`, {
    method: "POST",
    headers: {
      Accept: "application/vnd.api+json",
      "Content-Type": "application/vnd.api+json",
      Authorization: `Bearer ${API_KEY}`,
    },
    body: JSON.stringify(body),
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Lemon Squeezy checkout failed (${res.status})`);
  }
  const json = (await res.json()) as { data?: { attributes?: { url?: string } } };
  const url = json.data?.attributes?.url;
  return url ? { url } : null;
}

/**
 * Verify a Lemon Squeezy webhook signature (HMAC-SHA256 of the raw body,
 * compared in constant time). Returns false if not configured or invalid.
 */
export function verifyLemonSignature(rawBody: string, signature: string | null): boolean {
  if (!WEBHOOK_SECRET || !signature) return false;
  const expected = crypto.createHmac("sha256", WEBHOOK_SECRET).update(rawBody, "utf8").digest("hex");
  const a = Buffer.from(expected, "utf8");
  const b = Buffer.from(signature, "utf8");
  if (a.length !== b.length) return false;
  return crypto.timingSafeEqual(a, b);
}
