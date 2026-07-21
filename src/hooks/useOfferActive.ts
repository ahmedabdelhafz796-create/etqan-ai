"use client";

import { useNow } from "@/hooks/useClock";
import { useSiteConfig } from "@/components/providers/SiteConfigProvider";

/**
 * Client-side source of truth for whether the celebration offer is still
 * live. Reads the (admin-editable) deadline from site config and keeps
 * interactive UI in sync as the clock ticks past it — without a page reload
 * and without any hydration mismatch.
 */
export function useOfferActive(): { active: boolean; ready: boolean } {
  const now = useNow();
  const { offerEndsAt } = useSiteConfig();
  const ready = now !== 0;
  const deadline = new Date(offerEndsAt).getTime();
  // Optimistic (active) until the client clock confirms otherwise.
  const active = !ready || now < deadline;
  return { active, ready };
}
