"use client";

import { motion } from "framer-motion";
import { useCountdown } from "@/hooks/useCountdown";
import { offerConfig } from "@/config";
import { cn } from "@/lib/utils";

interface Props {
  className?: string;
  compact?: boolean;
}

function pad(n: number) {
  return n.toString().padStart(2, "0");
}

export function CountdownTimer({ className, compact = false }: Props) {
  const { days, hours, minutes, seconds, expired, ready } = useCountdown(
    offerConfig.offerEndsAt
  );

  const units = [
    { label: "Days", value: days },
    { label: "Hours", value: hours },
    { label: "Minutes", value: minutes },
    { label: "Seconds", value: seconds },
  ];

  if (ready && expired) {
    return (
      <div
        className={cn(
          "flex items-center justify-center rounded-2xl border border-white/10 bg-white/[0.04] px-6 py-4 text-center",
          className
        )}
      >
        <p className="font-display text-lg font-medium text-soft/80">
          Offer has ended.
          <span className="ml-2 text-soft/50">
            Original prices have been restored.
          </span>
        </p>
      </div>
    );
  }

  return (
    <div
      className={cn(
        "flex items-stretch justify-center gap-2 sm:gap-3",
        className
      )}
    >
      {units.map((u, i) => (
        <div key={u.label} className="flex items-stretch gap-2 sm:gap-3">
          <div
            className={cn(
              "flex flex-col items-center justify-center rounded-xl border border-white/10 bg-white/[0.05] backdrop-blur-xl",
              compact ? "min-w-[58px] px-2.5 py-2" : "min-w-[72px] px-3 py-3 sm:min-w-[88px]"
            )}
          >
            <motion.span
              key={u.value}
              initial={{ y: -8, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.3 }}
              className={cn(
                "font-mono font-semibold tabular-nums text-soft",
                compact ? "text-xl" : "text-3xl sm:text-4xl"
              )}
            >
              {ready ? pad(u.value) : "--"}
            </motion.span>
            <span
              className={cn(
                "mt-1 uppercase tracking-widest text-soft/45",
                compact ? "text-[9px]" : "text-[10px]"
              )}
            >
              {u.label}
            </span>
          </div>
          {i < units.length - 1 && (
            <span
              className={cn(
                "self-center font-mono text-gold/40",
                compact ? "text-lg" : "text-2xl"
              )}
            >
              :
            </span>
          )}
        </div>
      ))}
    </div>
  );
}
