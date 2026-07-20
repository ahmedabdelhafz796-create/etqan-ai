"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import type { Book } from "@/config";

const accentMap = {
  gold: {
    ring: "from-gold/40 via-gold/10 to-transparent",
    spine: "from-gold-deep to-gold-muted",
    glyph: "text-gold-light",
    grad: "from-night-600 via-night-700 to-night-900",
  },
  emerald: {
    ring: "from-emerald/40 via-emerald/10 to-transparent",
    spine: "from-emerald-deep to-emerald",
    glyph: "text-emerald-light",
    grad: "from-night-600 via-night-700 to-night-900",
  },
  royal: {
    ring: "from-royal/40 via-royal/10 to-transparent",
    spine: "from-royal-deep to-royal",
    glyph: "text-royal-light",
    grad: "from-night-600 via-night-700 to-night-900",
  },
} as const;

/**
 * Procedurally-rendered premium book cover (no external image needed).
 * Gives every book a distinct, on-brand jacket with a subtle chart motif.
 */
export function BookCover({ book }: { book: Book }) {
  const a = accentMap[book.cover.accent];

  return (
    <div className="relative aspect-[3/4] w-full [perspective:1200px]">
      {/* glow ring */}
      <div
        className={cn(
          "absolute -inset-6 rounded-[2rem] bg-gradient-to-br opacity-60 blur-2xl",
          a.ring
        )}
      />
      <motion.div
        whileHover={{ rotateY: -10, rotateX: 4, y: -6 }}
        transition={{ type: "spring", stiffness: 160, damping: 18 }}
        className="relative h-full w-full [transform-style:preserve-3d]"
      >
        <div
          className={cn(
            "relative flex h-full w-full flex-col overflow-hidden rounded-r-xl rounded-l-md border border-white/10 bg-gradient-to-br shadow-card",
            a.grad
          )}
        >
          {/* spine */}
          <div
            className={cn(
              "absolute inset-y-0 left-0 w-2.5 bg-gradient-to-b",
              a.spine
            )}
          />
          {/* sheen */}
          <div className="absolute inset-0 bg-gradient-to-tr from-white/[0.08] via-transparent to-transparent" />

          {/* faint chart motif */}
          <svg
            aria-hidden="true"
            viewBox="0 0 200 120"
            className="absolute bottom-8 left-6 right-4 opacity-[0.14]"
          >
            <polyline
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              className={a.glyph}
              points="0,90 25,70 50,80 75,45 100,60 125,30 150,42 175,18 200,26"
            />
          </svg>

          <div className="relative flex flex-1 flex-col p-6">
            <span
              className={cn(
                "font-mono text-[10px] uppercase tracking-[0.3em]",
                a.glyph
              )}
            >
              Etqan · Trading Library
            </span>

            <div className="mt-auto">
              <div className={cn("mb-3 h-px w-12 bg-current", a.glyph)} />
              <h3 className="font-display text-2xl font-semibold leading-tight text-soft">
                {book.cover.label}
              </h3>
              <p className="mt-2 text-xs text-soft/50">{book.subtitle}</p>
              <p
                className={cn(
                  "mt-4 font-mono text-[10px] uppercase tracking-[0.25em]",
                  a.glyph
                )}
              >
                {book.cover.edition}
              </p>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
