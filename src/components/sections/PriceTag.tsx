"use client";

import { useOfferActive } from "@/hooks/useOfferActive";
import { useBookPricing } from "@/components/providers/SiteConfigProvider";
import { useT } from "@/components/providers/I18nProvider";
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
  const t = useT();
  const { active, ready } = useOfferActive();
  const pricing = useBookPricing(book.id);
  const originalPrice = pricing.originalPrice;
  const offerPrice = pricing.offerPrice;
  const showOffer = (!ready || active) && offerPrice < originalPrice; // optimistic before hydration
  const pct = discountPercent(originalPrice, offerPrice);

  return (
    <div className={cn("flex flex-wrap items-end gap-x-4 gap-y-2", className)}>
      <div className="flex items-end gap-3">
        <span className="font-display text-4xl font-semibold text-soft sm:text-5xl">
          {formatUSD(showOffer ? offerPrice : originalPrice)}
        </span>
        {showOffer && (
          <span className="mb-1.5 font-mono text-lg text-soft/40 line-through">
            {formatUSD(originalPrice)}
          </span>
        )}
      </div>

      {showOffer && (
        <div className="mb-1 flex items-center gap-2">
          <Badge variant="emerald">{t.store.save} {formatUSD(originalPrice - offerPrice)}</Badge>
          <Badge variant="gold">-{pct}%</Badge>
        </div>
      )}
    </div>
  );
}
