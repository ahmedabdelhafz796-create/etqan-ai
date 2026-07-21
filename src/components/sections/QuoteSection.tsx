"use client";

import { motion } from "framer-motion";
import { Quote } from "lucide-react";
import { useT } from "@/components/providers/I18nProvider";

export function QuoteSection() {
  const t = useT();
  return (
    <section className="relative overflow-hidden py-24 sm:py-28">
      <div className="pointer-events-none absolute inset-0 -z-10">
        <div className="absolute left-1/2 top-1/2 h-[400px] w-[900px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-gold-radial blur-2xl" />
        <div className="absolute inset-0 grid-bg opacity-20" />
      </div>

      <div className="container-tight">
        <motion.figure
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="relative mx-auto max-w-4xl rounded-3xl border border-gold/20 bg-gradient-to-br from-white/[0.04] to-transparent p-10 text-center backdrop-blur-xl sm:p-16"
        >
          <Quote className="mx-auto h-12 w-12 text-gold/40" />

          <blockquote className="mt-8">
            <p className="font-display text-2xl font-medium leading-snug text-soft sm:text-4xl sm:leading-tight">
              &ldquo;{t.quote.lead}{" "}
              <span className="text-gradient-gold">{t.quote.leadGold}</span>{" "}
              {t.quote.leadTail}&rdquo;
            </p>
            <p className="mx-auto mt-6 max-w-2xl text-base leading-relaxed text-soft/60 sm:text-lg">
              {t.quote.body}
            </p>
          </blockquote>

          <figcaption className="mt-8 flex items-center justify-center gap-3">
            <span className="h-px w-8 bg-gold/40" />
            <span className="font-mono text-xs uppercase tracking-[0.3em] text-gold-light">
              {t.quote.attribution}
            </span>
            <span className="h-px w-8 bg-gold/40" />
          </figcaption>
        </motion.figure>
      </div>
    </section>
  );
}
