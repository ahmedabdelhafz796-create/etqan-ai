"use client";

import * as React from "react";
import { motion, useReducedMotion } from "framer-motion";
import { cn } from "@/lib/utils";

function seeded(i: number, s = 1) {
  const x = Math.sin(i * 127.1 + s * 311.7) * 43758.5453;
  return x - Math.floor(x);
}

interface Props {
  count?: number;
  className?: string;
  color?: string;
}

/**
 * Floating luminous particles — a subtle "dust of gold" layer that adds
 * depth and life without stealing focus. Deterministic (SSR-safe) and
 * disabled under prefers-reduced-motion.
 */
export function Particles({
  count = 26,
  className,
  color = "rgba(233,196,106,0.7)",
}: Props) {
  const reduce = useReducedMotion();
  const [mounted, setMounted] = React.useState(false);
  React.useEffect(() => setMounted(true), []);
  if (reduce || !mounted) return null;

  return (
    <div
      aria-hidden="true"
      className={cn("pointer-events-none absolute inset-0 overflow-hidden", className)}
    >
      {Array.from({ length: count }).map((_, i) => {
        const left = seeded(i, 1) * 100;
        const top = seeded(i, 2) * 100;
        const size = 1.5 + seeded(i, 3) * 3;
        const dur = 9 + seeded(i, 4) * 12;
        const delay = seeded(i, 5) * -18;
        const drift = 24 + seeded(i, 6) * 40;
        return (
          <motion.span
            key={i}
            className="absolute rounded-full"
            style={{
              left: `${left}%`,
              top: `${top}%`,
              width: size,
              height: size,
              background: color,
              boxShadow: `0 0 ${size * 3}px ${color}`,
            }}
            animate={{
              y: [0, -drift, 0],
              x: [0, seeded(i, 7) > 0.5 ? drift * 0.4 : -drift * 0.4, 0],
              opacity: [0, 0.9, 0],
            }}
            transition={{
              duration: dur,
              delay,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />
        );
      })}
    </div>
  );
}
