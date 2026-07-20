"use client";

import { useEffect, useState } from "react";

export interface CountdownState {
  days: number;
  hours: number;
  minutes: number;
  seconds: number;
  /** True once the target date has passed. */
  expired: boolean;
  /** True after the first client tick (avoids hydration mismatch). */
  ready: boolean;
}

const ZERO: Omit<CountdownState, "expired" | "ready"> = {
  days: 0,
  hours: 0,
  minutes: 0,
  seconds: 0,
};

function computeRemaining(target: number): CountdownState {
  const diff = target - Date.now();
  if (diff <= 0) {
    return { ...ZERO, expired: true, ready: true };
  }
  const totalSeconds = Math.floor(diff / 1000);
  return {
    days: Math.floor(totalSeconds / 86400),
    hours: Math.floor((totalSeconds % 86400) / 3600),
    minutes: Math.floor((totalSeconds % 3600) / 60),
    seconds: totalSeconds % 60,
    expired: false,
    ready: true,
  };
}

/**
 * Live countdown to an ISO date. Ticks every second on the client.
 * Server renders a neutral (not-ready) state to avoid hydration drift.
 */
export function useCountdown(targetIso: string): CountdownState {
  const target = new Date(targetIso).getTime();
  const [state, setState] = useState<CountdownState>({
    ...ZERO,
    expired: false,
    ready: false,
  });

  useEffect(() => {
    setState(computeRemaining(target));
    const interval = setInterval(() => {
      const next = computeRemaining(target);
      setState(next);
      if (next.expired) clearInterval(interval);
    }, 1000);
    return () => clearInterval(interval);
  }, [target]);

  return state;
}
