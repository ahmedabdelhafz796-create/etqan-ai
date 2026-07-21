"use client";

import { motion } from "framer-motion";
import { Check } from "lucide-react";
import { useT } from "@/components/providers/I18nProvider";
import { Badge } from "@/components/ui/badge";
import { BookCover } from "@/components/visuals/BookCover";
import { PriceTag } from "@/components/sections/PriceTag";
import { BuyButton } from "@/components/sections/BuyButton";
import { Curriculum } from "@/components/sections/Curriculum";
import type { Book } from "@/config";
import { cn } from "@/lib/utils";

export function BookCard({ book, index }: { book: Book; index: number }) {
  const t = useT();
  const flipped = index % 2 === 1;

  return (
    <motion.article
      initial={{ opacity: 0, y: 40 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-100px" }}
      transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
      onMouseMove={(e) => {
        const r = e.currentTarget.getBoundingClientRect();
        e.currentTarget.style.setProperty("--mx", `${e.clientX - r.left}px`);
        e.currentTarget.style.setProperty("--my", `${e.clientY - r.top}px`);
      }}
      className="spotlight gradient-border group relative overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-white/[0.06] to-white/[0.01] p-6 shadow-card backdrop-blur-xl transition-colors hover:border-gold/25 sm:p-8"
    >
      {/* hover glow */}
      <div className="pointer-events-none absolute -inset-px rounded-3xl opacity-0 transition-opacity duration-500 group-hover:opacity-100">
        <div className="absolute inset-0 rounded-3xl bg-gradient-to-br from-gold/[0.08] via-transparent to-emerald/[0.05]" />
      </div>

      <div
        className={cn(
          "relative grid items-center gap-8 lg:grid-cols-[minmax(0,0.85fr)_minmax(0,1.15fr)]",
          flipped && "lg:[&>*:first-child]:order-2"
        )}
      >
        {/* Cover */}
        <div className="mx-auto w-full max-w-[280px] lg:max-w-none">
          <BookCover book={book} />
        </div>

        {/* Details */}
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant={book.cover.accent === "emerald" ? "emerald" : "gold"}>
              {t.store.book} {book.order}
            </Badge>
            <Badge variant="muted">{book.badge}</Badge>
          </div>

          <h3 className="mt-4 font-display text-3xl font-semibold leading-tight text-soft sm:text-4xl">
            {book.title}
          </h3>
          <p className="mt-2 text-lg text-gradient-gold">{book.subtitle}</p>

          <p className="mt-4 text-sm leading-relaxed text-soft/60 sm:text-base">
            {book.description}
          </p>

          {/* highlights */}
          <ul className="mt-5 grid gap-2 sm:grid-cols-2">
            {book.highlights.map((h, i) => (
              <li
                key={i}
                className="flex items-start gap-2 text-sm text-soft/75"
              >
                <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-emerald/15 text-emerald-light">
                  <Check className="h-3 w-3" />
                </span>
                {h}
              </li>
            ))}
          </ul>

          {/* stats */}
          <div className="mt-6 flex gap-6">
            {book.stats.map((s) => (
              <div key={s.label}>
                <div className="font-display text-xl font-semibold text-soft">
                  {s.value}
                </div>
                <div className="text-xs uppercase tracking-wide text-soft/45">
                  {s.label}
                </div>
              </div>
            ))}
          </div>

          <div className="mt-7 hairline" />

          {/* price + buy */}
          <div className="mt-6 flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
            <PriceTag book={book} />
            <div className="w-full sm:max-w-[260px]">
              <BuyButton book={book} />
            </div>
          </div>
        </div>
      </div>

      {/* Inside the book */}
      <Curriculum book={book} />
    </motion.article>
  );
}
