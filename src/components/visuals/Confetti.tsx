"use client";

import * as React from "react";
import { motion, useReducedMotion } from "framer-motion";

const COLORS = ["#E9C46A", "#F4D98B", "#34D399", "#3B82F6", "#F7F4EE"];

function seeded(i: number) {
  const x = Math.sin(i * 91.7) * 9137.13;
  return x - Math.floor(x);
}

interface Props {
  count?: number;
  active?: boolean;
}

/**
 * Lightweight looping confetti for the celebration banner.
 * Respects prefers-reduced-motion.
 */
export function Confetti({ count = 26, active = true }: Props) {
  const reduce = useReducedMotion();
  const [mounted, setMounted] = React.useState(false);
  React.useEffect(() => setMounted(true), []);

  if (!active || reduce || !mounted) return null;

  return (
    <div
      aria-hidden="true"
      className="pointer-events-none absolute inset-0 overflow-hidden"
    >
      {Array.from({ length: count }).map((_, i) => {
        const left = seeded(i) * 100;
        const size = 5 + seeded(i + 3) * 6;
        const duration = 4 + seeded(i + 5) * 4;
        const delay = seeded(i + 9) * 5;
        const color = COLORS[i % COLORS.length];
        const rounded = seeded(i + 1) > 0.5;
        return (
          <motion.span
            key={i}
            className="absolute top-[-24px]"
            style={{
              left: `${left}%`,
              width: size,
              height: size * (rounded ? 1 : 1.6),
              backgroundColor: color,
              borderRadius: rounded ? "9999px" : "2px",
            }}
            initial={{ y: -24, opacity: 0, rotate: 0 }}
            animate={{
              y: ["-24px", "120%"],
              opacity: [0, 1, 1, 0],
              rotate: [0, 220, 380],
              x: [0, seeded(i + 7) > 0.5 ? 18 : -18, 0],
            }}
            transition={{
              duration,
              delay,
              repeat: Infinity,
              ease: "easeIn",
            }}
          />
        );
      })}
    </div>
  );
}
