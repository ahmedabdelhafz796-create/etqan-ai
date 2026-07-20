"use client";

import { motion, useTransform } from "framer-motion";
import { ArrowRight, ShieldCheck, Star, TrendingUp } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Magnetic } from "@/components/ui/magnetic";
import { CandlestickField } from "@/components/visuals/CandlestickField";
import { Particles } from "@/components/visuals/Particles";
import { BookCover } from "@/components/visuals/BookCover";
import { useMouseParallax } from "@/hooks/useMouseParallax";
import { books, offerConfig } from "@/config";

const stats = [
  { value: "26", label: "Core Modules" },
  { value: "100+", label: "Chapters" },
  { value: "240+", label: "Chart Examples" },
  { value: "2", label: "Flagship Books" },
];

const headline = ["Trade", "the", "way"];
const headlineGold = ["institutions"];
const headlineRest = ["actually", "do."];

export function Hero() {
  const { x, y, bind } = useMouseParallax(90, 16);

  // Layer depths driven by pointer.
  const bgX = useTransform(x, [-0.5, 0.5], [24, -24]);
  const bgY = useTransform(y, [-0.5, 0.5], [18, -18]);
  const midX = useTransform(x, [-0.5, 0.5], [40, -40]);
  const midY = useTransform(y, [-0.5, 0.5], [30, -30]);
  const bookX = useTransform(x, [-0.5, 0.5], [-38, 38]);
  const bookY = useTransform(y, [-0.5, 0.5], [-26, 26]);
  const bookRotY = useTransform(x, [-0.5, 0.5], [16, -16]);
  const bookRotX = useTransform(y, [-0.5, 0.5], [-10, 10]);

  return (
    <section
      id="top"
      onMouseMove={bind.onMouseMove}
      onMouseLeave={bind.onMouseLeave}
      className="perspective relative flex min-h-[100svh] items-center overflow-hidden pt-28 pb-16 sm:pt-32"
    >
      {/* ── background layers ── */}
      <motion.div
        style={{ x: bgX, y: bgY }}
        className="pointer-events-none absolute inset-0 -z-10 scale-110"
      >
        <div className="absolute inset-0 opacity-[0.4]">
          <CandlestickField />
        </div>
        <div className="absolute inset-0 grid-bg opacity-30" />
      </motion.div>

      <motion.div
        style={{ x: midX, y: midY }}
        className="pointer-events-none absolute inset-0 -z-10"
      >
        <div className="absolute left-1/2 top-[12%] h-[460px] w-[860px] -translate-x-1/2 bg-gold-radial blur-2xl" />
        <div className="absolute right-[8%] top-[38%] h-[320px] w-[320px] rounded-full bg-[radial-gradient(circle,rgba(18,185,129,0.18),transparent_60%)] blur-2xl" />
      </motion.div>

      <Particles count={22} className="-z-10" />
      <div className="pointer-events-none absolute inset-x-0 bottom-0 -z-10 h-40 bg-gradient-to-t from-night-900 to-transparent" />

      {/* ── content ── */}
      <div className="container-tight relative">
        <div className="grid items-center gap-12 lg:grid-cols-[1.05fr_0.95fr]">
          {/* Left copy */}
          <div className="text-center lg:text-left">
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="flex justify-center lg:justify-start"
            >
              <Badge variant="gold" className="gap-2 px-4 py-1.5">
                <span className="relative flex h-2 w-2">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-gold-light opacity-75" />
                  <span className="relative inline-flex h-2 w-2 rounded-full bg-gold-light" />
                </span>
                {offerConfig.celebrationTitle} · until{" "}
                {offerConfig.offerDeadlineLabel.split(" ·")[0]}
              </Badge>
            </motion.div>

            <h1 className="mt-6 font-display text-[2.6rem] font-semibold leading-[1.04] tracking-tight text-soft sm:text-6xl md:text-[4.4rem]">
              <span className="sr-only">
                Trade the way institutions actually do.
              </span>
              <span aria-hidden className="flex flex-wrap justify-center gap-x-3 lg:justify-start">
                {[...headline, ...headlineGold, ...headlineRest].map((w, i) => {
                  const isGold = headlineGold.includes(w) && i === headline.length;
                  return (
                    <motion.span
                      key={i}
                      initial={{ opacity: 0, y: 26, filter: "blur(8px)" }}
                      animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
                      transition={{
                        duration: 0.6,
                        delay: 0.15 + i * 0.08,
                        ease: [0.22, 1, 0.36, 1],
                      }}
                      className={isGold ? "text-gradient-gold" : undefined}
                    >
                      {w}
                    </motion.span>
                  );
                })}
              </span>
            </h1>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.5 }}
              className="mx-auto mt-6 max-w-xl text-base leading-relaxed text-soft/65 sm:text-lg lg:mx-0"
            >
              A premium library of professional trading books — market
              structure, liquidity, order flow, SMC, ICT, Wyckoff and AI-driven
              institutional analysis. No hype. No indicators. Just the real
              logic that moves price.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.62 }}
              className="mt-9 flex flex-col items-center gap-4 sm:flex-row sm:justify-center lg:justify-start"
            >
              <Magnetic>
                <Button asChild variant="gold" size="xl" className="w-full sm:w-auto">
                  <a href="#store">
                    Explore the Library
                    <ArrowRight className="h-5 w-5" />
                  </a>
                </Button>
              </Magnetic>
              <Magnetic strength={10}>
                <Button asChild variant="glass" size="xl" className="w-full sm:w-auto">
                  <a href="#telegram">See the Signals</a>
                </Button>
              </Magnetic>
            </motion.div>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.7, delay: 0.8 }}
              className="mt-7 flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-xs text-soft/50 lg:justify-start"
            >
              <span className="flex items-center gap-1.5">
                <ShieldCheck className="h-4 w-4 text-emerald-light" />
                Lifetime access &amp; updates
              </span>
              <span className="flex items-center gap-1.5">
                <Star className="h-4 w-4 text-gold-light" />
                Institutional-grade curriculum
              </span>
              <span className="flex items-center gap-1.5">Secure crypto checkout</span>
            </motion.div>
          </div>

          {/* Right — 3D floating book mockups */}
          <motion.div
            initial={{ opacity: 0, scale: 0.94 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.9, delay: 0.35, ease: [0.22, 1, 0.36, 1] }}
            className="preserve-3d relative mx-auto h-[360px] w-full max-w-sm sm:max-w-md lg:h-[440px]"
          >
            <motion.div
              style={{ x: bookX, y: bookY, rotateX: bookRotX, rotateY: bookRotY }}
              className="preserve-3d absolute inset-0"
            >
              {/* Book 2 — behind */}
              <motion.div
                animate={{ y: [0, -16, 0] }}
                transition={{ duration: 7, repeat: Infinity, ease: "easeInOut" }}
                className="absolute right-2 top-6 w-48"
                style={{ transform: "translateZ(20px) rotateZ(6deg)" }}
              >
                <BookCover book={books[1]} />
              </motion.div>

              {/* Book 1 — front */}
              <motion.div
                animate={{ y: [0, 18, 0] }}
                transition={{
                  duration: 6,
                  repeat: Infinity,
                  ease: "easeInOut",
                  delay: 0.6,
                }}
                className="absolute left-0 top-16 w-56"
                style={{ transform: "translateZ(70px) rotateZ(-5deg)" }}
              >
                <BookCover book={books[0]} />
              </motion.div>

              {/* floating price chip */}
              <motion.div
                animate={{ y: [0, -12, 0] }}
                transition={{ duration: 5, repeat: Infinity, ease: "easeInOut" }}
                style={{ transform: "translateZ(120px)" }}
                className="absolute -right-2 bottom-6 rounded-2xl border border-gold/25 bg-night-800/70 px-4 py-3 backdrop-blur-xl shadow-glow"
              >
                <p className="text-[10px] uppercase tracking-widest text-soft/50">
                  From
                </p>
                <p className="font-display text-2xl font-semibold text-gradient-gold">
                  $65
                </p>
              </motion.div>

              {/* floating live chip */}
              <motion.div
                animate={{ y: [0, 10, 0] }}
                transition={{
                  duration: 5.5,
                  repeat: Infinity,
                  ease: "easeInOut",
                  delay: 1,
                }}
                style={{ transform: "translateZ(100px)" }}
                className="absolute -left-4 top-2 flex items-center gap-2 rounded-full border border-emerald/25 bg-night-800/70 px-3 py-2 backdrop-blur-xl"
              >
                <TrendingUp className="h-4 w-4 text-emerald-light" />
                <span className="font-mono text-xs text-emerald-light">
                  +2.14%
                </span>
              </motion.div>
            </motion.div>
          </motion.div>
        </div>

        {/* stat row */}
        <motion.div
          initial={{ opacity: 0, y: 28 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.9 }}
          className="mx-auto mt-14 grid max-w-3xl grid-cols-2 gap-px overflow-hidden rounded-2xl border border-white/10 bg-white/[0.04] backdrop-blur-xl sm:grid-cols-4"
        >
          {stats.map((s, i) => (
            <motion.div
              key={s.label}
              whileHover={{ y: -3 }}
              className="bg-night-900/40 px-6 py-6 text-center transition-colors hover:bg-white/[0.03]"
              style={{ transitionDelay: `${i * 20}ms` }}
            >
              <div className="font-display text-3xl font-semibold text-gradient-gold">
                {s.value}
              </div>
              <div className="mt-1 text-xs uppercase tracking-wide text-soft/50">
                {s.label}
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* scroll cue */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.3 }}
          className="mt-12 flex justify-center"
        >
          <div className="flex h-9 w-6 items-start justify-center rounded-full border border-white/15 p-1">
            <motion.span
              animate={{ y: [0, 10, 0], opacity: [1, 0.3, 1] }}
              transition={{ duration: 1.8, repeat: Infinity }}
              className="h-1.5 w-1.5 rounded-full bg-gold-light"
            />
          </div>
        </motion.div>
      </div>
    </section>
  );
}
