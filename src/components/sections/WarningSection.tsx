"use client";

import { motion } from "framer-motion";
import { AlertTriangle } from "lucide-react";
import { Reveal } from "@/components/ui/reveal";
import { useT } from "@/components/providers/I18nProvider";

export function WarningSection() {
  const t = useT();
  return (
    <section className="relative py-16 sm:py-20">
      <div className="container-tight">
        <Reveal>
          <div className="relative overflow-hidden rounded-3xl border border-loss/30 bg-gradient-to-br from-loss/[0.08] via-night-800/60 to-night-900/70 p-8 backdrop-blur-xl sm:p-10">
            <div className="absolute -right-10 -top-10 h-40 w-40 rounded-full bg-loss/15 blur-3xl" />
            <div className="absolute left-0 top-0 h-full w-1 bg-gradient-to-b from-loss to-loss/20" />

            <div className="relative flex flex-col gap-6 sm:flex-row sm:items-start">
              <motion.span
                animate={{ scale: [1, 1.06, 1] }}
                transition={{ duration: 2.5, repeat: Infinity }}
                className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl border border-loss/40 bg-loss/15 text-loss"
              >
                <AlertTriangle className="h-7 w-7" />
              </motion.span>

              <div>
                <h2 className="font-display text-2xl font-semibold text-soft sm:text-3xl">
                  {t.warning.title}
                </h2>
                <p className="mt-4 max-w-2xl text-base leading-relaxed text-soft/65">
                  {t.warning.body1}
                </p>

                <ul className="mt-5 grid gap-2.5 sm:grid-cols-2">
                  {t.warning.fundamentals.map((f, i) => (
                    <motion.li
                      key={f}
                      initial={{ opacity: 0, x: -12 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      viewport={{ once: true }}
                      transition={{ duration: 0.4, delay: i * 0.05 }}
                      className="flex items-center gap-2.5 text-sm text-soft/80"
                    >
                      <span className="h-1.5 w-1.5 rounded-full bg-loss" />
                      {f}
                    </motion.li>
                  ))}
                </ul>

                <p className="mt-6 max-w-2xl rounded-xl border border-white/10 bg-white/[0.03] p-4 text-sm leading-relaxed text-soft/70">
                  {t.warning.body2}
                </p>
              </div>
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
