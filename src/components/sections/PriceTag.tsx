"use client";

import { useOfferActive } from "@/hooks/useOfferActive";
import { formatUSD, discountPercent, cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import type { Book } from "@/config";

/**
 * Live price display. While the celebration offer is active it shows the
 * discounted price, the struck original, and the savings. The moment the
 * countdown expires (client clock) it restores the original price.
 */
export function PriceTag({
  book,
  className,
}: {
  book: Book;
  className?: string;
}) {
  const { active, ready } = useOfferActive();
  const showOffer = !ready || active; // optimistic before hydration
  const pct = discountPercent(book.originalPrice, book.offerPrice);

  return (
    <div className={cn("flex flex-wrap items-end gap-x-4 gap-y-2", className)}>
      <div className="flex items-end gap-3">
        <span className="font-display text-4xl font-semibold text-soft sm:text-5xl">
          {formatUSD(showOffer ? book.offerPrice : book.originalPrice)}
        </span>
        {showOffer && (
          <span className="mb-1.5 font-mono text-lg text-soft/40 line-through">
            {formatUSD(book.originalPrice)}
          </span>
        )}
      </div>

      {showOffer && (
        <div className="mb-1 flex items-center gap-2">
          <Badge variant="emerald">Save {formatUSD(book.originalPrice - book.offerPrice)}</Badge>
          <Badge variant="gold">-{pct}%</Badge>
        </div>
      )}
    </div>
  );
}
