import { books, siteConfig } from "@/config";

/** JSON-LD structured data for SEO (Organization + Products). */
export function StructuredData() {
  const data = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "Organization",
        name: siteConfig.name,
        url: siteConfig.url,
        description: siteConfig.description,
        sameAs: [
          siteConfig.social.twitter,
          siteConfig.social.youtube,
          siteConfig.social.instagram,
        ],
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
      // eslint-disable-next-line react/no-danger
      dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }}
    />
  );
}
