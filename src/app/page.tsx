import { Navbar } from "@/components/sections/Navbar";
import { ScrollProgress } from "@/components/sections/ScrollProgress";
import { Hero } from "@/components/sections/Hero";
import { TickerTape } from "@/components/visuals/TickerTape";
import { CelebrationBanner } from "@/components/sections/CelebrationBanner";
import { BookStore } from "@/components/sections/BookStore";
import { WhyBuy } from "@/components/sections/WhyBuy";
import { TelegramSection } from "@/components/sections/TelegramSection";
import { WarningSection } from "@/components/sections/WarningSection";
import { QuoteSection } from "@/components/sections/QuoteSection";
import { Testimonials } from "@/components/sections/Testimonials";
import { FAQ } from "@/components/sections/FAQ";
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
          <TickerTape />
          <CelebrationBanner />
          <BookStore books={localizedBooks} activeIds={activeIds} />
          <WhyBuy />
          <TelegramSection />
          <WarningSection />
          <QuoteSection />
          <Testimonials />
          <FAQ />
          <Newsletter />
        </main>

        <Footer />
      </SiteConfigProvider>
    </I18nProvider>
  );
}
