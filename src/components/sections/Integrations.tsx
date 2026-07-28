"use client";

import { useMarketplace } from "@/components/providers/I18nProvider";

/**
 * The "works with what you already run" strip, directly under the hero.
 *
 * Wordmarks rather than logos, deliberately: shipping third-party brand
 * logos means shipping their trademarks, and a marquee of borrowed logos
 * on a new store reads as borrowed credibility. The line underneath is
 * the substantive claim — plain n8n JSON, no runtime of ours in the way.
 */
export function Integrations() {
  const m = useMarketplace();

  return (
    <section className="relative border-y border-white/[0.06] bg-white/[0.012] py-12">
      <div className="container-tight">
        <p className="text-center text-[11px] font-bold uppercase tracking-[0.18em] text-white/30">
          {m.integrations.title}
        </p>

        <ul className="mt-7 flex flex-wrap items-center justify-center gap-x-9 gap-y-4">
          {m.integrations.items.map((name) => (
            <li
              key={name}
              className="font-display text-[15px] font-semibold tracking-tight text-white/35 transition-colors duration-300 hover:text-white/70"
            >
              {name}
            </li>
          ))}
        </ul>

        <p className="mx-auto mt-7 max-w-2xl text-center text-[13px] leading-relaxed text-white/35">
          {m.integrations.note}
        </p>
      </div>
    </section>
  );
}
