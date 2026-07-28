import { Navbar } from "@/components/sections/Navbar";
import { ScrollProgress } from "@/components/sections/ScrollProgress";
import { Hero } from "@/components/sections/Hero";
import { Integrations } from "@/components/sections/Integrations";
import { Catalog } from "@/components/sections/Catalog";
import { HowItWorks } from "@/components/sections/HowItWorks";
import { Standards } from "@/components/sections/Standards";
import { Proof } from "@/components/sections/Proof";
import { FinalCta } from "@/components/sections/FinalCta";
import { FAQ } from "@/components/sections/FAQ";
import { BooksDivider } from "@/components/sections/BooksDivider";
import { BookStore } from "@/components/sections/BookStore";
import { Newsletter } from "@/components/sections/Newsletter";
import { Footer } from "@/components/sections/Footer";
import { StructuredData } from "@/components/StructuredData";
import { SiteConfigProvider } from "@/components/providers/SiteConfigProvider";
import { I18nProvider } from "@/components/providers/I18nProvider";
import { getEffectiveConfig } from "@/lib/site-settings";
import { getCurrentLocale } from "@/lib/locale";
import { getDictionary } from "@/i18n/dictionaries";
import { getLocalizedBooks } from "@/i18n/books";
import { dirFor } from "@/i18n/config";

/**
 * Homepage: an AI automation marketplace.
 *
 * The running order is the argument a sceptical buyer makes, in the
 * order they make it:
 *
 *   Hero          — here is a working workflow, not a promise
 *   Integrations  — it runs on the tools you already have
 *   Catalog       — every product, with what is actually inside each
 *   HowItWorks    — installing it will not eat your weekend
 *   Standards     — this is what "production-ready" means here
 *   Proof         — and here is the evidence, shipped with the files
 *   FinalCta      — start free
 *   FAQ           — the remaining objections
 *   BooksDivider  — a different, secondary product starts below
 *   BookStore     — the trading library, on its own crypto checkout
 *
 * Everything above BooksDivider is the AI line and never mentions
 * trading. Everything below is the book line and never mentions Lemon
 * Squeezy. The two share this file and nothing else — separate
 * components, separate copy, separate payment paths.
 *
 * Removed with the trading storefront: the live ticker tape, the
 * first-edition countdown banner, the Telegram signals section, the
 * risk-warning band, the trading quote, and a testimonials wall whose
 * quotes were written rather than collected.
 */
export default async function HomePage() {
  const [eff, locale] = await Promise.all([
    getEffectiveConfig(),
    getCurrentLocale(),
  ]);
  const dict = getDictionary(locale);
  const localizedBooks = getLocalizedBooks(locale);
  const activeIds = Object.values(eff.books)
    .filter((b) => b.active)
    .map((b) => b.id);

  return (
    <I18nProvider value={{ t: dict, locale, dir: dirFor(locale) }}>
      <SiteConfigProvider
        value={{
          books: eff.books,
          offerEndsAt: eff.offerEndsAt,
          telegramUrl: eff.telegramUrl,
          paymentUrl: eff.paymentUrl,
        }}
      >
        <StructuredData />
        <ScrollProgress />
        <Navbar />

        <main>
          <Hero />
          <Integrations />
          <Catalog />
          <HowItWorks />
          <Standards />
          <Proof />
          <FinalCta />
          <FAQ />

          <BooksDivider />
          <BookStore books={localizedBooks} activeIds={activeIds} />

          <Newsletter />
        </main>

        <Footer />
      </SiteConfigProvider>
    </I18nProvider>
  );
}
