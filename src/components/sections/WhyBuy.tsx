"use client";

import {
  Brain,
  CandlestickChart,
  Dumbbell,
  GraduationCap,
  Infinity as InfinityIcon,
  LineChart,
  ScrollText,
  ShieldCheck,
  Sparkles,
  type LucideIcon,
} from "lucide-react";
import { SectionHeading } from "@/components/ui/section-heading";
import { RevealGroup, RevealItem } from "@/components/ui/reveal";
import { SpotlightCard } from "@/components/ui/spotlight-card";
import { useT } from "@/components/providers/I18nProvider";

const icons: LucideIcon[] = [
  GraduationCap,
  CandlestickChart,
  ScrollText,
  Dumbbell,
  LineChart,
  ShieldCheck,
  Brain,
  Sparkles,
  InfinityIcon,
];

export function WhyBuy() {
  const t = useT();
  return (
    <section id="why" className="scroll-mt-24 py-24 sm:py-28">
      <div className="container-tight">
        <SectionHeading
          eyebrow={t.why.eyebrow}
          title={
            <>
              {t.why.title1}{" "}
              <span className="text-gradient-gold">{t.why.titleGold}</span>
            </>
          }
          description={t.why.description}
        />

        <RevealGroup className="mt-14 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {t.why.perks.map((p, i) => {
            const Icon = icons[i] ?? GraduationCap;
            return (
              <RevealItem key={p.title}>
                <SpotlightCard className="h-full p-6 transition-transform duration-300 hover:-translate-y-1.5 hover:shadow-glow">
                  <span className="flex h-11 w-11 items-center justify-center rounded-xl border border-gold/25 bg-gold/10 text-gold-light transition-transform duration-300 group-hover:scale-110 group-hover:rotate-3">
                    <Icon className="h-5 w-5" />
                  </span>
                  <h3 className="mt-4 font-display text-lg font-semibold text-soft">
                    {p.title}
                  </h3>
                  <p className="mt-2 text-sm leading-relaxed text-soft/55">
                    {p.desc}
                  </p>
                </SpotlightCard>
              </RevealItem>
            );
          })}
        </RevealGroup>
      </div>
    </section>
  );
}
