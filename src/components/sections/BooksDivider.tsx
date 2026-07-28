"use client";

import { BookOpen } from "lucide-react";
import { Reveal } from "@/components/ui/reveal";
import { useMarketplace } from "@/components/providers/I18nProvider";

/**
 * The hand-off from the AI marketplace to the trading library.
 *
 * The homepage sells automation. The books are a real second product
 * line, but a visitor who scrolls into two trading book covers with no
 * warning assumes they took a wrong turn. This band says plainly that a
 * different, secondary product starts here — and it is where the gold
 * accent is allowed to reappear, so the colour shift is explained rather
 * than jarring.
 */
export function BooksDivider() {
  const m = useMarketplace();

  return (
    <section className="relative py-16 sm:py-20">
      <div aria-hidden className="hairline" />
      <div className="container-tight">
        <Reveal>
          <div className="mt-14 flex flex-col items-center gap-5 text-center">
            <span className="flex h-12 w-12 items-center justify-center rounded-2xl border border-gold/25 bg-gold/[0.07] text-gold-light">
              <BookOpen className="h-5 w-5" aria-hidden />
            </span>
            <p className="text-[11px] font-bold uppercase tracking-[0.18em] text-white/30">
              {m.books.eyebrow}
            </p>
            <h2 className="font-display text-3xl font-bold tracking-tight sm:text-[2.25rem]">
              {m.books.title1}{" "}
              <span className="text-gradient-gold">{m.books.titleAccent}</span>
            </h2>
            <p className="max-w-xl text-[15px] leading-relaxed text-white/50">
              {m.books.description}
            </p>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
