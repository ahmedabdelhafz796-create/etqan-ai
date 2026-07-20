import { SectionHeading } from "@/components/ui/section-heading";
import { Reveal } from "@/components/ui/reveal";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

const faqs = [
  {
    q: "Are these books for beginners or advanced traders?",
    a: "Triple Analysis is built to take a motivated beginner to a professional level, step by step. Advanced AI Trading is for traders who already understand the fundamentals and want to industrialize their edge with systems and AI. Read the warning section — order matters.",
  },
  {
    q: "What format are the books delivered in?",
    a: "High-resolution digital PDFs, optimized for both desktop and tablet. You get instant access after checkout, plus every future update to your edition at no extra cost.",
  },
  {
    q: "How do I pay?",
    a: "Checkout is handled securely through crypto payments. Prices are shown in USD and converted at checkout. The moment payment confirms, your download is delivered — no waiting, no middlemen.",
  },
  {
    q: "Is the First Edition price really going away?",
    a: "Yes. The founding-price offer is locked until July 30, 2026 at 23:59. When the countdown hits zero, discounts are removed automatically and the books return to their standard prices.",
  },
  {
    q: "Do I need indicators or paid software to apply this?",
    a: "No. Everything is taught using pure price action and market structure on any standard charting platform. If it costs money to run, we tell you exactly why it's worth it — and most of the time, it isn't.",
  },
  {
    q: "When do the Telegram signals start?",
    a: "Professional signals and trade ideas begin publishing August 1st, 2026 — built on the exact framework taught in the books, with full entries, stop loss, take profit and risk notes.",
  },
  {
    q: "Is this financial advice?",
    a: "No. These are educational materials. Trading involves substantial risk, and nothing here is a guarantee of profit. You are always responsible for your own decisions and risk.",
  },
];

export function FAQ() {
  return (
    <section id="faq" className="scroll-mt-24 py-24 sm:py-28">
      <div className="container-tight">
        <SectionHeading
          eyebrow="FAQ"
          title="Answers, before you ask."
          description="Everything you need to know about the books, delivery, pricing and the signals."
        />

        <Reveal className="mx-auto mt-12 max-w-3xl">
          <Accordion type="single" collapsible className="space-y-3">
            {faqs.map((f, i) => (
              <AccordionItem key={i} value={`faq-${i}`}>
                <AccordionTrigger>{f.q}</AccordionTrigger>
                <AccordionContent>
                  <p className="leading-relaxed">{f.a}</p>
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </Reveal>
      </div>
    </section>
  );
}
