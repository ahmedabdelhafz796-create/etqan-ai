"use client";

import * as React from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  Activity,
  BarChart3,
  Building2,
  ChevronDown,
  Cpu,
  Crosshair,
  Database,
  LayoutGrid,
  LineChart,
  ListChecks,
  Shield,
  ShieldCheck,
  Waves,
  Zap,
  type LucideIcon,
} from "lucide-react";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { cn } from "@/lib/utils";
import type { Book } from "@/config";

const ICONS: Record<string, LucideIcon> = {
  layout: LayoutGrid,
  waves: Waves,
  activity: Activity,
  "bar-chart-3": BarChart3,
  crosshair: Crosshair,
  shield: Shield,
  "building-2": Building2,
  database: Database,
  cpu: Cpu,
  zap: Zap,
  "line-chart": LineChart,
  "shield-check": ShieldCheck,
};

export function Curriculum({ book }: { book: Book }) {
  const [open, setOpen] = React.useState(false);

  const totalChapters = book.curriculum.reduce(
    (n, m) => n + m.chapters.length,
    0
  );

  return (
    <div className="mt-8 overflow-hidden rounded-2xl border border-white/10 bg-white/[0.02]">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between gap-4 px-5 py-4 text-left transition-colors hover:bg-white/[0.03]"
        aria-expanded={open}
      >
        <div className="flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl border border-gold/25 bg-gold/10 text-gold-light">
            <ListChecks className="h-5 w-5" />
          </span>
          <div>
            <p className="font-display text-base font-semibold text-soft">
              Inside the Book
            </p>
            <p className="text-xs text-soft/50">
              {book.curriculum.length} modules · {totalChapters} chapters ·
              full curriculum
            </p>
          </div>
        </div>
        <ChevronDown
          className={cn(
            "h-5 w-5 shrink-0 text-gold/70 transition-transform duration-300",
            open && "rotate-180"
          )}
        />
      </button>

      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
            className="overflow-hidden"
          >
            <div className="border-t border-white/10 p-4 sm:p-5">
              <Accordion
                type="single"
                collapsible
                defaultValue="module-0"
                className="space-y-3"
              >
                {book.curriculum.map((mod, mi) => {
                  const Icon = ICONS[mod.icon] ?? BarChart3;
                  return (
                    <AccordionItem key={mi} value={`module-${mi}`}>
                      <AccordionTrigger>
                        <span className="flex items-center gap-3">
                          <span className="flex h-8 w-8 items-center justify-center rounded-lg border border-white/10 bg-white/5 text-gold-light">
                            <Icon className="h-4 w-4" />
                          </span>
                          <span>
                            <span className="mr-2 font-mono text-xs text-gold/60">
                              {(mi + 1).toString().padStart(2, "0")}
                            </span>
                            {mod.title}
                          </span>
                        </span>
                      </AccordionTrigger>
                      <AccordionContent>
                        <div className="space-y-4 pl-11">
                          {mod.chapters.map((ch, ci) => (
                            <div key={ci}>
                              <p className="text-sm font-medium text-soft/90">
                                {ch.title}
                              </p>
                              <ul className="mt-2 space-y-1.5">
                                {ch.lessons.map((lesson, li) => (
                                  <li
                                    key={li}
                                    className="flex items-start gap-2 text-sm text-soft/55"
                                  >
                                    <span className="mt-2 h-1 w-1 shrink-0 rounded-full bg-gold/60" />
                                    {lesson}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          ))}
                        </div>
                      </AccordionContent>
                    </AccordionItem>
                  );
                })}
              </Accordion>

              {/* What's included */}
              <div className="mt-5 rounded-xl border border-emerald/20 bg-emerald/[0.06] p-4">
                <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-emerald-light">
                  Every copy includes
                </p>
                <ul className="grid gap-2 sm:grid-cols-2">
                  {book.includes.map((inc, i) => (
                    <li
                      key={i}
                      className="flex items-center gap-2 text-sm text-soft/70"
                    >
                      <ShieldCheck className="h-4 w-4 shrink-0 text-emerald-light" />
                      {inc}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
