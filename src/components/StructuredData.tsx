import { automationBundles, books, siteConfig } from "@/config";
import { getMarketplaceCopy } from "@/i18n/marketplace";

/**
 * JSON-LD structured data for SEO.
 *
 * The bundles were missing entirely — the graph described two books and
 * nothing else, on a site whose primary product line is 23 automation
 * workflows. Search engines were being told the same thing the old
 * homepage said. They are emitted first, matching the page order.
 *
 * Descriptions come from the English marketplace copy rather than being
 * written twice: a second copy would drift from what the page says.
 */
export function StructuredData() {
  const m = getMarketplaceCopy("en");
  // Only advertise real, configured profiles (skip generic placeholders).
  const sameAs = [
    process.env.NEXT_PUBLIC_TWITTER_URL,
    process.env.NEXT_PUBLIC_YOUTUBE_URL,
    process.env.NEXT_PUBLIC_INSTAGRAM_URL,
    process.env.NEXT_PUBLIC_TELEGRAM_URL,
  ].filter((u): u is string => Boolean(u));

  const data = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "Organization",
        name: siteConfig.name,
        url: siteConfig.url,
        description: siteConfig.description,
        ...(sameAs.length ? { sameAs } : {}),
      },
      {
        "@type": "WebSite",
        name: siteConfig.name,
        url: siteConfig.url,
      },
      ...automationBundles.map((b) => ({
        "@type": "SoftwareApplication",
        name: b.name,
        applicationCategory: "BusinessApplication",
        operatingSystem: "n8n (Cloud or self-hosted)",
        description: m.bundles[b.id as keyof typeof m.bundles].summary,
        offers: {
          "@type": "Offer",
          price: b.price ?? 0,
          priceCurrency: "USD",
          availability: "https://schema.org/InStock",
          url: b.checkoutUrl,
        },
      })),
      ...books.map((book) => ({
        "@type": "Book",
        name: book.title,
        bookFormat: "https://schema.org/EBook",
        description: book.description,
        inLanguage: "en",
        offers: {
          "@type": "Offer",
          price: book.offerPrice,
          priceCurrency: "USD",
          availability: "https://schema.org/InStock",
          url: `${siteConfig.url}/#store`,
        },
      })),
    ],
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{
        // Escape `<` so a stray "</script>" in data can never break out.
        __html: JSON.stringify(data).replace(/</g, "\\u003c"),
      }}
    />
  );
}
