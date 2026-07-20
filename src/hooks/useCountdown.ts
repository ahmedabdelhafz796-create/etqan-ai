"use client";

import { useNow } from "@/hooks/useClock";

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

function computeRemaining(target: number, now: number): CountdownState {
  const diff = target - now;
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
 * Live countdown to an ISO date, driven by the shared client clock.
 * Server (and the first paint) render a neutral not-ready state, so there is
 * never a hydration mismatch.
 */
export function useCountdown(targetIso: string): CountdownState {
  const target = new Date(targetIso).getTime();
  const now = useNow();

  if (now === 0) {
    return { ...ZERO, expired: false, ready: false };
  }
  return computeRemaining(target, now);
}
