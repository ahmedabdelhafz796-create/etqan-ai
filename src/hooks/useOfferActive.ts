"use client";

import { useNow } from "@/hooks/useClock";
import { offerConfig } from "@/config";

/**
 * Client-side source of truth for whether the celebration offer is still
 * live. Server components use `resolvePrice` directly; this hook keeps
 * interactive UI (prices, badges) in sync as the clock ticks past the
 * deadline — without a page reload and without any hydration mismatch.
 */
export function useOfferActive(): { active: boolean; ready: boolean } {
  const now = useNow();
  const ready = now !== 0;
  const deadline = new Date(offerConfig.offerEndsAt).getTime();
  // Optimistic (active) until the client clock confirms otherwise.
  const active = !ready || now < deadline;
  return { active, ready };
}
