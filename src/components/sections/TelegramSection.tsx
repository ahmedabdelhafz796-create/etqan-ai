"use client";

import { motion } from "framer-motion";
import {
  BarChart2,
  Bell,
  CalendarClock,
  Crown,
  Send,
  Shield,
  Target,
  TrendingUp,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Reveal } from "@/components/ui/reveal";
import { links, offerConfig } from "@/config";

const features = [
  { icon: BarChart2, title: "Daily Analysis", desc: "Structured market breakdowns before every session." },
  { icon: Target, title: "Entry Levels", desc: "Precise, pre-planned entries with clear invalidation." },
  { icon: Shield, title: "Stop Loss (SL)", desc: "Defined risk on every idea — no exceptions." },
  { icon: TrendingUp, title: "Take Profit (TP)", desc: "Layered targets mapped to real liquidity." },
  { icon: Bell, title: "Market Reviews", desc: "End-of-day recaps and what to watch next." },
  { icon: Crown, title: "VIP Community", desc: "A focused room of serious, like-minded traders." },
];

export function TelegramSection() {
  return (
    <section
      id="telegram"
      className="relative scroll-mt-24 overflow-hidden py-24 sm:py-28"
    >
      <div className="pointer-events-none absolute inset-0 -z-10">
        <div className="absolute left-1/2 top-1/3 h-[380px] w-[760px] -translate-x-1/2 rounded-full bg-royal/10 blur-3xl" />
      </div>

      <div className="container-tight">
        <div className="relative overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-night-700/70 to-night-900/80 p-8 backdrop-blur-xl sm:p-12">
          <div className="grid items-center gap-10 lg:grid-cols-[1.1fr_0.9fr]">
            <div>
              <Reveal>
                <Badge variant="royal" className="mb-5">
                  <CalendarClock className="h-3.5 w-3.5" />
                  Going live · {offerConfig.telegramLaunchLabel}
                </Badge>
              </Reveal>

              <Reveal delay={0.05}>
                <h2 className="font-display text-3xl font-semibold leading-tight text-soft sm:text-4xl">
                  Exclusive{" "}
                  <span className="text-gradient-gold">Telegram Signals</span>
                </h2>
              </Reveal>

              <Reveal delay={0.1}>
                <p className="mt-4 max-w-xl text-base leading-relaxed text-soft/60 sm:text-lg">
                  Beginning{" "}
                  <span className="font-medium text-soft/90">
                    {offerConfig.telegramLaunchLabel}
                  </span>
                  , we publish professional trading signals and trade ideas
                  built on the exact framework taught in the books — full
                  transparency, real risk management, zero noise.
                </p>
              </Reveal>

              <Reveal delay={0.15}>
                <div className="mt-8">
                  <Button
                    asChild
                    variant="gold"
                    size="xl"
                    className="w-full sm:w-auto"
                  >
                    <a
                      href={links.telegramUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      <Send className="h-5 w-5" />
                      Join Telegram
                    </a>
                  </Button>
                  <p className="mt-3 text-xs text-soft/45">
                    Free preview channel now · VIP room opens{" "}
                    {offerConfig.telegramLaunchLabel}.
                  </p>
                </div>
              </Reveal>
            </div>

            <div className="grid gap-3 sm:grid-cols-2">
              {features.map((f, i) => (
                <motion.div
                  key={f.title}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: i * 0.06 }}
                  className="rounded-2xl border border-white/10 bg-white/[0.04] p-4 transition-colors hover:border-gold/25 hover:bg-white/[0.06]"
                >
                  <f.icon className="h-5 w-5 text-gold-light" />
                  <p className="mt-3 text-sm font-medium text-soft">
                    {f.title}
                  </p>
                  <p className="mt-1 text-xs leading-relaxed text-soft/50">
                    {f.desc}
                  </p>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
