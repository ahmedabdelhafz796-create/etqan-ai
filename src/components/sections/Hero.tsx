"use client";

import { motion } from "framer-motion";
import { ArrowRight, ShieldCheck, Sparkles, Star } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { CandlestickField } from "@/components/visuals/CandlestickField";
import { offerConfig } from "@/config";

const stats = [
  { value: "26", label: "Core Modules" },
  { value: "100+", label: "Chapters" },
  { value: "240+", label: "Chart Examples" },
  { value: "2", label: "Flagship Books" },
];

export function Hero() {
  return (
    <section
      id="top"
      className="relative overflow-hidden pt-28 pb-20 sm:pt-36 sm:pb-28"
    >
      {/* animated chart background */}
      <div className="pointer-events-none absolute inset-0 -z-10">
        <div className="absolute inset-0 opacity-[0.35]">
          <CandlestickField />
        </div>
        <div className="absolute inset-0 grid-bg opacity-40" />
        <div className="absolute inset-0 bg-gradient-to-b from-night-900/40 via-night-900/70 to-night-900" />
        <div className="absolute left-1/2 top-0 h-[420px] w-[820px] -translate-x-1/2 bg-gold-radial blur-2xl" />
      </div>

      <div className="container-tight relative">
        <div className="mx-auto max-w-3xl text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <Badge variant="gold" className="mb-6 px-4 py-1.5">
              <Sparkles className="h-3.5 w-3.5" />
              {offerConfig.celebrationTitle} · until {offerConfig.offerDeadlineLabel.split(" ·")[0]}
            </Badge>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.05 }}
            className="font-display text-4xl font-semibold leading-[1.08] tracking-tight text-soft sm:text-6xl md:text-7xl"
          >
            Trade the way{" "}
            <span className="text-gradient-gold">institutions</span> actually
            do.
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.12 }}
            className="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-soft/65 sm:text-xl"
          >
            A premium library of professional trading books — market structure,
            liquidity, order flow, SMC, ICT, Wyckoff and AI-driven institutional
            analysis. No hype. No indicators. Just the real logic that moves
            price.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.18 }}
            className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row"
          >
            <Button asChild variant="gold" size="xl" className="w-full sm:w-auto">
              <a href="#store">
                Explore the Library
                <ArrowRight className="h-5 w-5" />
              </a>
            </Button>
            <Button
              asChild
              variant="glass"
              size="xl"
              className="w-full sm:w-auto"
            >
              <a href="#telegram">See the Signals</a>
            </Button>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.7, delay: 0.28 }}
            className="mt-6 flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-xs text-soft/50"
          >
            <span className="flex items-center gap-1.5">
              <ShieldCheck className="h-4 w-4 text-emerald-light" />
              Lifetime access & updates
            </span>
            <span className="flex items-center gap-1.5">
              <Star className="h-4 w-4 text-gold-light" />
              Institutional-grade curriculum
            </span>
            <span className="flex items-center gap-1.5">
              Secure crypto checkout
            </span>
          </motion.div>
        </div>

        {/* stat row */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.35 }}
          className="mx-auto mt-16 grid max-w-3xl grid-cols-2 gap-px overflow-hidden rounded-2xl border border-white/10 bg-white/[0.04] backdrop-blur-xl sm:grid-cols-4"
        >
          {stats.map((s) => (
            <div key={s.label} className="bg-night-900/40 px-6 py-6 text-center">
              <div className="font-display text-3xl font-semibold text-gradient-gold">
                {s.value}
              </div>
              <div className="mt-1 text-xs uppercase tracking-wide text-soft/50">
                {s.label}
              </div>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
