"use client";

import { motion } from "framer-motion";
import { Star } from "lucide-react";
import { SectionHeading } from "@/components/ui/section-heading";
import { useT } from "@/components/providers/I18nProvider";

interface Testimonial {
  name: string;
  role: string;
  initials: string;
  accent: string;
  quote: string;
}

const testimonials: Testimonial[] = [
  {
    name: "A. Rahman",
    role: "Swing Trader · 3 yrs",
    initials: "AR",
    accent: "from-gold to-gold-deep",
    quote:
      "Triple Analysis finally connected the dots for me. I stopped chasing indicators and started reading liquidity. My win-rate didn't just improve — my whole mindset did.",
  },
  {
    name: "M. Chen",
    role: "Prop Firm Funded",
    initials: "MC",
    accent: "from-emerald to-emerald-deep",
    quote:
      "The risk management chapter alone paid for the book ten times over. This is the first material that reads like it was written by someone who actually trades size.",
  },
  {
    name: "S. Okafor",
    role: "Quant-curious Trader",
    initials: "SO",
    accent: "from-royal to-royal-deep",
    quote:
      "Advanced AI Trading is in a different league. The system blueprints and the AI workflow library changed how I research markets entirely. Worth every dollar.",
  },
  {
    name: "L. Moretti",
    role: "Full-time FX",
    initials: "LM",
    accent: "from-gold to-gold-deep",
    quote:
      "I've bought a lot of courses. Most are noise. This is the first library that respects your intelligence and your time. Clean, deep, and genuinely institutional.",
  },
  {
    name: "K. Yılmaz",
    role: "Crypto & Indices",
    initials: "KY",
    accent: "from-emerald to-emerald-deep",
    quote:
      "The case studies are gold. Watching a full trade broken down from HTF bias to the exact exit taught me more than a year of YouTube ever did.",
  },
  {
    name: "D. Novak",
    role: "Part-time, Growing",
    initials: "DN",
    accent: "from-royal to-royal-deep",
    quote:
      "What sold me was the honesty — the warning about AI, the psychology focus. It's clear these authors care about you actually making it, not just buying.",
  },
];

export function Testimonials() {
  const dict = useT();
  return (
    <section className="py-24 sm:py-28">
      <div className="container-tight">
        <SectionHeading
          eyebrow={dict.testimonials.eyebrow}
          title={
            <>
              {dict.testimonials.title1}{" "}
              <span className="text-gradient-gold">
                {dict.testimonials.titleGold}
              </span>
            </>
          }
          description={dict.testimonials.description}
        />

        <div className="mt-14 columns-1 gap-4 sm:columns-2 lg:columns-3 [&>*]:mb-4 [&>*]:break-inside-avoid">
          {testimonials.map((t, i) => (
            <motion.figure
              key={t.name}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.5, delay: (i % 3) * 0.08 }}
              onMouseMove={(e) => {
                const r = e.currentTarget.getBoundingClientRect();
                e.currentTarget.style.setProperty("--mx", `${e.clientX - r.left}px`);
                e.currentTarget.style.setProperty("--my", `${e.clientY - r.top}px`);
              }}
              className="spotlight gradient-border rounded-2xl border border-white/10 bg-white/[0.03] p-6 transition-colors hover:border-gold/20"
            >
              <div className="flex gap-0.5 text-gold-light">
                {Array.from({ length: 5 }).map((_, s) => (
                  <Star key={s} className="h-4 w-4 fill-current" />
                ))}
              </div>
              <blockquote className="mt-4 text-sm leading-relaxed text-soft/75">
                &ldquo;{dict.testimonials.items[i]?.quote ?? t.quote}&rdquo;
              </blockquote>
              <figcaption className="mt-5 flex items-center gap-3">
                <span
                  className={`flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br ${t.accent} font-display text-sm font-semibold text-night-900`}
                >
                  {t.initials}
                </span>
                <span>
                  <span className="block text-sm font-medium text-soft">
                    {t.name}
                  </span>
                  <span className="block text-xs text-soft/45">
                    {dict.testimonials.items[i]?.role ?? t.role}
                  </span>
                </span>
              </figcaption>
            </motion.figure>
          ))}
        </div>
      </div>
    </section>
  );
}
