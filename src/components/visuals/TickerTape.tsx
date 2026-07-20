"use client";

import * as React from "react";
import { TrendingUp, TrendingDown, Radio } from "lucide-react";
import { cn } from "@/lib/utils";

interface Tick {
  symbol: string;
  price: string;
  change: string;
  up: boolean;
}

const TICKS: Tick[] = [
  { symbol: "BTC/USD", price: "68,420.10", change: "+2.14%", up: true },
  { symbol: "XAU/USD", price: "2,338.50", change: "+0.64%", up: true },
  { symbol: "EUR/USD", price: "1.0842", change: "-0.18%", up: false },
  { symbol: "NAS100", price: "19,210.7", change: "+0.72%", up: true },
  { symbol: "ETH/USD", price: "3,512.88", change: "+1.02%", up: true },
  { symbol: "SPX500", price: "5,431.20", change: "+0.42%", up: true },
  { symbol: "GBP/USD", price: "1.2718", change: "+0.09%", up: true },
  { symbol: "USOIL", price: "81.44", change: "-0.87%", up: false },
  { symbol: "SOL/USD", price: "168.22", change: "+3.51%", up: true },
];

function Item({ t, live }: { t: Tick; live: number }) {
  // Subtle live-price flicker on the last decimal for realism.
  const jittered = React.useMemo(() => {
    if (!t.price.includes(".")) return t.price;
    const digit = (parseInt(t.price.slice(-1), 10) + live) % 10;
    return t.price.slice(0, -1) + digit;
  }, [t.price, live]);

  return (
    <span className="flex items-center gap-2 whitespace-nowrap font-mono text-xs text-soft/70">
      <span className="font-medium text-soft/90">{t.symbol}</span>
      <span className="tabular-nums">{jittered}</span>
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
  );
}

export function TickerTape({ className }: { className?: string }) {
  const [live, setLive] = React.useState(0);
  React.useEffect(() => {
    const id = setInterval(() => setLive((v) => v + 1), 1400);
    return () => clearInterval(id);
  }, []);

  const doubled = [...TICKS, ...TICKS];

  return (
    <div
      className={cn(
        "relative flex items-center border-y border-white/5 bg-night-800/40 backdrop-blur-sm",
        className
      )}
    >
      {/* LIVE label */}
      <div className="z-10 flex shrink-0 items-center gap-1.5 border-r border-white/10 bg-night-900/70 px-4 py-2.5">
        <span className="relative flex h-2 w-2">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-loss opacity-75" />
          <span className="relative inline-flex h-2 w-2 rounded-full bg-loss" />
        </span>
        <span className="flex items-center gap-1 font-mono text-[10px] font-semibold uppercase tracking-widest text-soft/80">
          <Radio className="h-3 w-3" /> Live Markets
        </span>
      </div>

      {/* marquee */}
      <div className="group relative flex flex-1 overflow-hidden py-2.5" aria-hidden="true">
        <div className="pointer-events-none absolute inset-y-0 left-0 z-10 w-16 bg-gradient-to-r from-night-900 to-transparent" />
        <div className="pointer-events-none absolute inset-y-0 right-0 z-10 w-16 bg-gradient-to-l from-night-900 to-transparent" />
        <div className="flex shrink-0 animate-marquee items-center gap-8 pl-8 pr-8 group-hover:[animation-play-state:paused]">
          {doubled.map((t, i) => (
            <Item key={i} t={t} live={live} />
          ))}
        </div>
      </div>
    </div>
  );
}
