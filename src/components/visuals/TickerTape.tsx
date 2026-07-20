"use client";

import { TrendingUp, TrendingDown } from "lucide-react";
import { cn } from "@/lib/utils";

interface Tick {
  symbol: string;
  price: string;
  change: string;
  up: boolean;
}

const TICKS: Tick[] = [
  { symbol: "BTC/USD", price: "68,420.10", change: "+2.14%", up: true },
  { symbol: "ETH/USD", price: "3,512.88", change: "+1.02%", up: true },
  { symbol: "EUR/USD", price: "1.0842", change: "-0.18%", up: false },
  { symbol: "XAU/USD", price: "2,338.50", change: "+0.64%", up: true },
  { symbol: "SPX500", price: "5,431.20", change: "+0.42%", up: true },
  { symbol: "NAS100", price: "19,210.7", change: "-0.31%", up: false },
  { symbol: "GBP/USD", price: "1.2718", change: "+0.09%", up: true },
  { symbol: "USOIL", price: "81.44", change: "-0.87%", up: false },
  { symbol: "SOL/USD", price: "168.22", change: "+3.51%", up: true },
];

export function TickerTape({ className }: { className?: string }) {
  const doubled = [...TICKS, ...TICKS];
  return (
    <div
      className={cn(
        "group relative flex overflow-hidden border-y border-white/5 bg-white/[0.02] py-2.5",
        className
      )}
      aria-hidden="true"
    >
      <div className="flex shrink-0 animate-marquee items-center gap-8 pr-8 group-hover:[animation-play-state:paused]">
        {doubled.map((t, i) => (
          <span
            key={i}
            className="flex items-center gap-2 whitespace-nowrap font-mono text-xs text-soft/70"
          >
            <span className="font-medium text-soft/90">{t.symbol}</span>
            <span>{t.price}</span>
            <span
              className={cn(
                "flex items-center gap-0.5 font-medium",
                t.up ? "text-emerald-light" : "text-loss"
              )}
            >
              {t.up ? (
                <TrendingUp className="h-3 w-3" />
              ) : (
                <TrendingDown className="h-3 w-3" />
              )}
              {t.change}
            </span>
            <span className="text-white/10">•</span>
          </span>
        ))}
      </div>
    </div>
  );
}
