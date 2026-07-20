"use client";

import * as React from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface Candle {
  x: number;
  bodyTop: number;
  bodyH: number;
  wickTop: number;
  wickH: number;
  bull: boolean;
  delay: number;
}

/** Deterministic pseudo-random so SSR & client agree. */
function seeded(i: number) {
  const x = Math.sin(i * 12.9898) * 43758.5453;
  return x - Math.floor(x);
}

function buildCandles(count: number, width: number, height: number): Candle[] {
  const gap = width / count;
  const bodyW = gap * 0.42;
  let mid = height * 0.55;
  const candles: Candle[] = [];
  for (let i = 0; i < count; i++) {
    const drift = (seeded(i) - 0.48) * height * 0.14;
    mid = Math.min(height * 0.85, Math.max(height * 0.15, mid + drift));
    const bull = seeded(i + 100) > 0.45;
    const bodyH = 8 + seeded(i + 3) * (height * 0.16);
    const wickH = bodyH + 10 + seeded(i + 7) * (height * 0.1);
    candles.push({
      x: i * gap + gap / 2 - bodyW / 2,
      bodyTop: mid - bodyH / 2,
      bodyH,
      wickTop: mid - wickH / 2,
      wickH,
      bull,
      delay: i * 0.04,
    });
  }
  return candles;
}

interface Props {
  className?: string;
  count?: number;
  width?: number;
  height?: number;
}

/**
 * Subtle animated candlestick chart used as a section background.
 * Purely decorative — hidden from assistive tech.
 */
export function CandlestickField({
  className,
  count = 34,
  width = 1200,
  height = 420,
}: Props) {
  const candles = React.useMemo(
    () => buildCandles(count, width, height),
    [count, width, height]
  );
  const bodyW = (width / count) * 0.42;
  const wickW = 1.6;

  return (
    <svg
      aria-hidden="true"
      viewBox={`0 0 ${width} ${height}`}
      preserveAspectRatio="xMidYMid slice"
      className={cn("h-full w-full", className)}
    >
      <defs>
        <linearGradient id="bull-grad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#34D399" />
          <stop offset="100%" stopColor="#0B7A56" />
        </linearGradient>
        <linearGradient id="bear-grad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#EF4444" />
          <stop offset="100%" stopColor="#B91C1C" />
        </linearGradient>
      </defs>
      {candles.map((c, i) => {
        const color = c.bull ? "url(#bull-grad)" : "url(#bear-grad)";
        const stroke = c.bull ? "#34D399" : "#EF4444";
        return (
          <motion.g
            key={i}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: [0, 0.9, 0.75], y: 0 }}
            transition={{
              duration: 0.8,
              delay: c.delay,
              repeat: Infinity,
              repeatType: "reverse",
              repeatDelay: 2.4,
            }}
          >
            <rect
              x={c.x + bodyW / 2 - wickW / 2}
              y={c.wickTop}
              width={wickW}
              height={c.wickH}
              fill={stroke}
              opacity={0.5}
            />
            <rect
              x={c.x}
              y={c.bodyTop}
              width={bodyW}
              height={c.bodyH}
              rx={1.5}
              fill={color}
            />
          </motion.g>
        );
      })}
    </svg>
  );
}
