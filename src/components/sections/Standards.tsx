"use client";

import {
  AlertOctagon,
  KeyRound,
  RefreshCw,
  Repeat2,
  Server,
  Split,
  type LucideIcon,
} from "lucide-react";
import { SectionHeading } from "@/components/ui/section-heading";
import { Reveal } from "@/components/ui/reveal";
import { useMarketplace } from "@/components/providers/I18nProvider";

const ICONS: LucideIcon[] = [
  KeyRound,
  RefreshCw,
  Split,
  Repeat2,
  AlertOctagon,
  Server,
];

/**
 * The six build rules, stated as rules rather than as benefits.
 *
 * This replaced a "why buy these books" section written for traders. It
 * is the strongest thing the product line has: competitors claim their
 * templates are production-ready, and none publish what that means or
 * what enforces it.
 */
export function Standards() {
  const m = useMarketplace();

  return (
    <section id="standard" className="relative scroll-mt-24 py-24 sm:py-28">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(ellipse_60%_50%_at_50%_100%,rgba(34,211,238,0.06),transparent_70%)]"
      />
      <div className="container-tight">
        <SectionHeading
          eyebrow={m.standards.eyebrow}
          title={
            <>
              {m.standards.title1}{" "}
              <span className="text-gradient-iris">
                {m.standards.titleAccent}
              </span>
            </>
          }
          description={m.standards.description}
        />

        <div className="mt-14 grid gap-px overflow-hidden rounded-3xl border border-white/[0.08] bg-white/[0.06] sm:grid-cols-2 lg:grid-cols-3">
          {m.standards.items.map((item, i) => {
            const Icon = ICONS[i];
            return (
              <Reveal key={item.title} delay={Math.min(i * 0.05, 0.2)}>
                <div className="h-full bg-night-900 p-7 transition-colors duration-300 hover:bg-night-800">
                  <span className="flex h-11 w-11 items-center justify-center rounded-xl border border-iris/20 bg-iris/[0.08] text-iris-light">
                    <Icon className="h-5 w-5" aria-hidden />
                  </span>
                  <h3 className="mt-5 text-[15.5px] font-bold tracking-tight">
                    {item.title}
                  </h3>
                  <p className="mt-2 text-[14px] leading-relaxed text-white/50">
                    {item.body}
                  </p>
                </div>
              </Reveal>
            );
          })}
        </div>
      </div>
    </section>
  );
}
