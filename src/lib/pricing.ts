import { offerConfig, type Book } from "@/config";

export interface ResolvedPrice {
  /** Whether the celebration offer is still active. */
  offerActive: boolean;
  /** The price the buyer pays right now. */
  currentPrice: number;
  /** The original (full) price. */
  originalPrice: number;
  /** Amount saved while the offer is live (0 once ended). */
  savings: number;
  /** Discount percentage while the offer is live (0 once ended). */
  discountPercent: number;
}

/**
 * Resolve the effective price for a book given "now".
 * Once the offer deadline passes, the discount disappears and the
 * original price is restored automatically — everywhere.
 */
export function resolvePrice(book: Book, now: Date = new Date()): ResolvedPrice {
  const deadline = new Date(offerConfig.offerEndsAt);
  const offerActive = now.getTime() < deadline.getTime();

  if (!offerActive) {
    return {
      offerActive: false,
      currentPrice: book.originalPrice,
      originalPrice: book.originalPrice,
      savings: 0,
      discountPercent: 0,
    };
  }

  const savings = Math.max(0, book.originalPrice - book.offerPrice);
  const pct =
    book.originalPrice > 0
      ? Math.round((savings / book.originalPrice) * 100)
      : 0;

  return {
    offerActive: true,
    currentPrice: book.offerPrice,
    originalPrice: book.originalPrice,
    savings,
    discountPercent: pct,
  };
}
