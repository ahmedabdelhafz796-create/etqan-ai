"use client";

import { motion } from "framer-motion";
import { ArrowRight, CircleCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Magnetic } from "@/components/ui/magnetic";
import { WorkflowCanvas } from "@/components/visuals/WorkflowCanvas";
import { useMarketplace } from "@/components/providers/I18nProvider";

/**
 * The homepage hero for the AI automation marketplace.
 *
 * What used to be here: a candlestick field, a parallax stack of 3D book
 * covers, a floating "+2.14%" chip and a "from $65" price tag. All of it
 * sold a trading library. The headline now sells automation, so the
 * visual is an automation — see WorkflowCanvas.
 *
 * The stat strip runs on measured numbers from the shipped bundles. The
 * fourth one is "0 known defects", which is a claim worth making only
 * because the test suite that backs it is published alongside.
 */
export function Hero() {
  const m = useMarketplace();

  return (
    <section
      id="top"
      className="relative overflow-hidden pt-32 pb-20 sm:pt-40 sm:pb-24"
    >
      {/* Ambient field. Iris, not gold — the AI line's colour. */}
      <div aria-hidden className="pointer-events-none absolute inset-0 -z-10">
        <div className="absolute inset-0 bg-iris-radial" />
        <div className="grid-bg absolute inset-0 opacity-[0.35]" />
        <div className="absolute left-1/2 top-0 h-[420px] w-[900px] -translate-x-1/2 rounded-full bg-[radial-gradient(ellipse,rgba(34,211,238,0.10),transparent_65%)] blur-3xl" />
      </div>
      <div
        aria-hidden
        className="pointer-events-none absolute inset-x-0 bottom-0 -z-10 h-40 bg-gradient-to-t from-night-900 to-transparent"
      />

      <div className="container-tight">
        <div className="mx-auto max-w-3xl text-center">
          <motion.div
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="flex justify-center"
          >
            <span className="inline-flex items-center gap-2 rounded-full border border-iris/30 bg-iris/[0.08] px-3.5 py-1.5 text-[12.5px] font-medium text-iris-light">
              <span className="relative flex h-1.5 w-1.5">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-aqua opacity-70" />
                <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-aqua" />
              </span>
              {m.hero.badge}
            </span>
          </motion.div>

          <h1 className="mt-7 font-display text-[2.5rem] font-semibold leading-[1.05] tracking-tight text-soft sm:text-[3.4rem] md:text-[4rem]">
            <span className="sr-only">{m.hero.headlinePlain}</span>
            <motion.span
              aria-hidden
              initial={{ opacity: 0, y: 20, filter: "blur(8px)" }}
              animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
              transition={{ duration: 0.7, delay: 0.12, ease: [0.22, 1, 0.36, 1] }}
              className="block"
            >
              {m.hero.headline1}{" "}
              <span className="text-gradient-iris">{m.hero.headlineAccent}</span>{" "}
              {m.hero.headline2}
            </motion.span>
          </h1>

          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.34 }}
            className="mx-auto mt-6 max-w-2xl text-[16.5px] leading-relaxed text-soft/60"
          >
            {m.hero.subtitle}
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.46 }}
            className="mt-9 flex flex-col items-center justify-center gap-3 sm:flex-row"
          >
            <Magnetic>
              <Button asChild variant="iris" size="xl" className="w-full sm:w-auto">
                <a href="#catalog">
                  {m.hero.ctaPrimary}
                  <ArrowRight className="h-5 w-5 rtl:rotate-180" />
                </a>
              </Button>
            </Magnetic>
            <Magnetic strength={10}>
              <Button asChild variant="glass" size="xl" className="w-full sm:w-auto">
                <a href="#catalog">{m.hero.ctaSecondary}</a>
              </Button>
            </Magnetic>
          </motion.div>

          <motion.ul
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.6 }}
            className="mt-7 flex flex-wrap items-center justify-center gap-x-6 gap-y-2.5 text-[12.5px] text-soft/45"
          >
            {m.hero.trust.map((tItem) => (
              <li key={tItem} className="flex items-center gap-1.5">
                <CircleCheck className="h-3.5 w-3.5 text-iris-mid" aria-hidden />
                {tItem}
              </li>
            ))}
          </motion.ul>
        </div>

        {/* The product itself, on screen within the first viewport. */}
        <motion.div
          initial={{ opacity: 0, y: 34 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.9, delay: 0.5, ease: [0.22, 1, 0.36, 1] }}
          className="mt-16"
        >
          <WorkflowCanvas className="shadow-card" />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.8 }}
          className="mt-10 grid grid-cols-2 gap-px overflow-hidden rounded-2xl border border-white/[0.08] bg-white/[0.05] sm:grid-cols-4"
        >
          {m.hero.stats.map((s) => (
            <div key={s.label} className="bg-night-900/70 px-5 py-6 text-center">
              <div className="font-display text-3xl font-semibold text-gradient-iris">
                {s.value}
              </div>
              <div className="mt-1 text-[11px] uppercase tracking-[0.12em] text-soft/40">
                {s.label}
              </div>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
