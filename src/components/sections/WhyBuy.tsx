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
} from "lucide-react";
import { SectionHeading } from "@/components/ui/section-heading";
import { RevealGroup, RevealItem } from "@/components/ui/reveal";
import { SpotlightCard } from "@/components/ui/spotlight-card";

const perks = [
  { icon: GraduationCap, title: "Institutional Concepts", desc: "Learn the framework desks and funds trade — structure, liquidity, order flow." },
  { icon: CandlestickChart, title: "Professional Charts", desc: "Hundreds of clean, annotated charts that show, not just tell." },
  { icon: ScrollText, title: "Case Studies", desc: "Full trade breakdowns from bias to entry to exit." },
  { icon: Dumbbell, title: "Exercises", desc: "Practice sets with worked solutions to build real skill." },
  { icon: LineChart, title: "Real Examples", desc: "Live-market examples across FX, crypto, indices and metals." },
  { icon: ShieldCheck, title: "Risk Management", desc: "A complete system for sizing, R-multiples and drawdown control." },
  { icon: Brain, title: "Psychology", desc: "Master fear, greed and impatience — the real edge." },
  { icon: Sparkles, title: "AI Integration", desc: "Use AI as a co-analyst — the right way, at the right time." },
  { icon: InfinityIcon, title: "Lifetime Knowledge", desc: "Timeless principles plus lifetime updates to every edition." },
];

export function WhyBuy() {
  return (
    <section id="why" className="scroll-mt-24 py-24 sm:py-28">
      <div className="container-tight">
        <SectionHeading
          eyebrow="Why these books"
          title={
            <>
              Everything a serious trader needs —{" "}
              <span className="text-gradient-gold">nothing they don&apos;t.</span>
            </>
          }
          description="No signals-only shortcuts, no recycled indicator hype. Just a complete, professional education engineered to compound over a lifetime."
        />

        <RevealGroup className="mt-14 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {perks.map((p) => (
            <RevealItem key={p.title}>
              <SpotlightCard className="h-full p-6 transition-transform duration-300 hover:-translate-y-1.5 hover:shadow-glow">
                <span className="flex h-11 w-11 items-center justify-center rounded-xl border border-gold/25 bg-gold/10 text-gold-light transition-transform duration-300 group-hover:scale-110 group-hover:rotate-3">
                  <p.icon className="h-5 w-5" />
                </span>
                <h3 className="mt-4 font-display text-lg font-semibold text-soft">
                  {p.title}
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-soft/55">
                  {p.desc}
                </p>
              </SpotlightCard>
            </RevealItem>
          ))}
        </RevealGroup>
      </div>
    </section>
  );
}
