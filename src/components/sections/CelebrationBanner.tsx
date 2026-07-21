"use client";

import { motion } from "framer-motion";
import { PartyPopper, Tag } from "lucide-react";
import { Confetti } from "@/components/visuals/Confetti";
import { CountdownTimer } from "@/components/sections/CountdownTimer";
import { useOfferActive } from "@/hooks/useOfferActive";
import { useT } from "@/components/providers/I18nProvider";
import { offerConfig } from "@/config";

export function CelebrationBanner() {
  const t = useT();
  const { active, ready } = useOfferActive();

  // Once the offer ends, collapse to a gentle notice.
  if (ready && !active) {
    return (
      <section className="container-tight -mt-6">
        <div className="rounded-3xl border border-white/10 bg-white/[0.03] px-6 py-6 text-center">
          <p className="text-sm text-soft/60">{t.celebration.endedNotice}</p>
        </div>
      </section>
    );
  }

  return (
    <section className="container-tight -mt-6">
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
        className="relative overflow-hidden rounded-3xl border border-gold/25 bg-gradient-to-br from-night-700/80 via-night-800/80 to-night-900/80 px-6 py-8 shadow-glow backdrop-blur-xl sm:px-10 sm:py-10"
      >
        <Confetti active={active} />
        <div className="absolute -right-16 -top-16 h-56 w-56 rounded-full bg-gold/20 blur-3xl" />
        <div className="absolute -bottom-20 -left-10 h-56 w-56 rounded-full bg-emerald/15 blur-3xl" />

        <div className="relative flex flex-col items-center gap-8 lg:flex-row lg:items-center lg:justify-between">
          <div className="text-center lg:text-left">
            <motion.span
              animate={{ rotate: [0, -8, 8, 0] }}
              transition={{ duration: 2.5, repeat: Infinity, repeatDelay: 1 }}
              className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-2xl border border-gold/40 bg-gold/15 text-gold-light shadow-glow"
            >
              <PartyPopper className="h-6 w-6" />
            </motion.span>
            <h2 className="font-display text-2xl font-semibold text-soft sm:text-3xl">
              {t.celebration.title}
            </h2>
            <p className="mt-2 flex items-center justify-center gap-2 text-soft/65 lg:justify-start">
              <Tag className="h-4 w-4 text-gold-light" />
              {t.celebration.subtitle} · {t.celebration.ends}{" "}
              {offerConfig.offerDeadlineLabel}
            </p>
          </div>

          <div className="flex flex-col items-center gap-3">
            <span className="text-xs uppercase tracking-[0.3em] text-soft/45">
              {t.celebration.endsIn}
            </span>
            <CountdownTimer />
          </div>
        </div>
      </motion.div>
    </section>
  );
}
