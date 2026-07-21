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
import { getEffectiveConfig } from "@/lib/site-settings";

// Revalidate periodically so admin price/offer/link changes go live without a
// deploy, while keeping the page fast (statically cached between refreshes).
export const revalidate = 30;

export default async function HomePage() {
  const eff = await getEffectiveConfig();
  const activeIds = Object.values(eff.books)
    .filter((b) => b.active)
    .map((b) => b.id);

  return (
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
        <BookStore activeIds={activeIds} />
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
  );
}
