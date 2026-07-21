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
import { Magnetic } from "@/components/ui/magnetic";
import { Reveal } from "@/components/ui/reveal";
import { useSiteConfig } from "@/components/providers/SiteConfigProvider";
import { useT, fill } from "@/components/providers/I18nProvider";
import { offerConfig } from "@/config";

const featureIcons = [BarChart2, Target, Shield, TrendingUp, Bell, Crown];

export function TelegramSection() {
  const { telegramUrl } = useSiteConfig();
  const t = useT();
  const date = offerConfig.telegramLaunchLabel;
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
                  {t.telegram.goingLive} · {date}
                </Badge>
              </Reveal>

              <Reveal delay={0.05}>
                <h2 className="font-display text-3xl font-semibold leading-tight text-soft sm:text-4xl">
                  {t.telegram.title1}{" "}
                  <span className="text-gradient-gold">{t.telegram.titleGold}</span>
                </h2>
              </Reveal>

              <Reveal delay={0.1}>
                <p className="mt-4 max-w-xl text-base leading-relaxed text-soft/60 sm:text-lg">
                  {fill(t.telegram.body, { date })}
                </p>
              </Reveal>

              <Reveal delay={0.15}>
                <div className="mt-8">
                  <Magnetic className="inline-block">
                    <Button
                      asChild
                      variant="gold"
                      size="xl"
                      className="w-full sm:w-auto"
                    >
                      <a
                        href={telegramUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        <Send className="h-5 w-5" />
                        {t.telegram.cta}
                      </a>
                    </Button>
                  </Magnetic>
                  <p className="mt-3 text-xs text-soft/45">
                    {fill(t.telegram.note, { date })}
                  </p>
                </div>
              </Reveal>
            </div>

            <div className="grid gap-3 sm:grid-cols-2">
              {t.telegram.features.map((f, i) => {
                const Icon = featureIcons[i] ?? BarChart2;
                return (
                <motion.div
                  key={f.title}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: i * 0.06 }}
                  whileHover={{ y: -4 }}
                  onMouseMove={(e) => {
                    const r = e.currentTarget.getBoundingClientRect();
                    e.currentTarget.style.setProperty("--mx", `${e.clientX - r.left}px`);
                    e.currentTarget.style.setProperty("--my", `${e.clientY - r.top}px`);
                  }}
                  className="spotlight gradient-border group rounded-2xl border border-white/10 bg-white/[0.04] p-4 transition-colors hover:border-gold/25 hover:bg-white/[0.06]"
                >
                  <Icon className="h-5 w-5 text-gold-light transition-transform duration-300 group-hover:scale-110" />
                  <p className="mt-3 text-sm font-medium text-soft">
                    {f.title}
                  </p>
                  <p className="mt-1 text-xs leading-relaxed text-soft/50">
                    {f.desc}
                  </p>
                </motion.div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
