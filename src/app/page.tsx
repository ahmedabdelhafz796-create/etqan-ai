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

export default function HomePage() {
  return (
    <>
      <StructuredData />
      <ScrollProgress />
      <Navbar />

      <main>
        <Hero />
        <TickerTape />
        <CelebrationBanner />
        <BookStore />
        <WhyBuy />
        <TelegramSection />
        <WarningSection />
        <QuoteSection />
        <Testimonials />
        <FAQ />
        <Newsletter />
      </main>

      <Footer />
    </>
  );
}
