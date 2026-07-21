import { books, offerConfig, links, siteConfig } from "@/config";
import { getAllSettings } from "@/lib/repositories";

/**
 * The single set of keys the admin may edit. Anything else posted to the
 * settings API is ignored. Prices/discounts are per-book.
 */
export const ALLOWED_SETTING_KEYS: string[] = [
  "offer_ends_at",
  "telegram_url",
  "payment_url",
  "seo_title",
  "seo_description",
  ...books.flatMap((b) => [
    `book_${b.id}_original`,
    `book_${b.id}_offer`,
    `book_${b.id}_active`,
  ]),
];

export interface EffectiveBook {
  id: string;
  originalPrice: number;
  offerPrice: number;
  active: boolean;
}

export interface EffectiveConfig {
  books: Record<string, EffectiveBook>;
  offerEndsAt: string;
  telegramUrl: string;
  paymentUrl: string;
  seoTitle: string;
  seoDescription: string;
}

function num(value: string | undefined, fallback: number): number {
  if (value == null || value === "") return fallback;
  const n = Number(value);
  return Number.isFinite(n) ? n : fallback;
}

/**
 * Merge admin overrides (DB) over the static config defaults. Safe to call
 * when no DB is configured — it simply returns the config defaults.
 */
export async function getEffectiveConfig(): Promise<EffectiveConfig> {
  let settings: Record<string, string> = {};
  try {
    settings = await getAllSettings();
  } catch {
    settings = {};
  }

  const effectiveBooks: Record<string, EffectiveBook> = {};
  for (const b of books) {
    effectiveBooks[b.id] = {
      id: b.id,
      originalPrice: num(settings[`book_${b.id}_original`], b.originalPrice),
      offerPrice: num(settings[`book_${b.id}_offer`], b.offerPrice),
      active: settings[`book_${b.id}_active`] !== "0",
    };
  }

  return {
    books: effectiveBooks,
    offerEndsAt: settings.offer_ends_at || offerConfig.offerEndsAt,
    telegramUrl: settings.telegram_url || links.telegramUrl,
    paymentUrl: settings.payment_url || links.paymentUrl,
    seoTitle: settings.seo_title || `${siteConfig.name} — Premium Trading Library`,
    seoDescription: settings.seo_description || siteConfig.description,
  };
}
