"use client";

import { motion } from "framer-motion";
import { useCountdown } from "@/hooks/useCountdown";
import { useSiteConfig } from "@/components/providers/SiteConfigProvider";
import { useT } from "@/components/providers/I18nProvider";
import { cn } from "@/lib/utils";

interface Props {
  className?: string;
  compact?: boolean;
}

function pad(n: number) {
  return n.toString().padStart(2, "0");
}

export function CountdownTimer({ className, compact = false }: Props) {
  const t = useT();
  const { offerEndsAt } = useSiteConfig();
  const { days, hours, minutes, seconds, expired, ready } =
    useCountdown(offerEndsAt);

  const units = [
    { label: t.countdown.days, value: days },
    { label: t.countdown.hours, value: hours },
    { label: t.countdown.minutes, value: minutes },
    { label: t.countdown.seconds, value: seconds },
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
          {t.countdown.ended}
          <span className="ms-2 text-soft/50">{t.countdown.endedRestored}</span>
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
              "gradient-border relative flex flex-col items-center justify-center overflow-hidden rounded-xl border border-white/10 bg-white/[0.05] backdrop-blur-xl",
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
