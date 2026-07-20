import { books, siteConfig } from "@/config";

/** JSON-LD structured data for SEO (Organization + Products). */
export function StructuredData() {
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
      dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }}
    />
  );
}
