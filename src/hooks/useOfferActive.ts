"use client";

import { useEffect, useState } from "react";
import { offerConfig } from "@/config";

/**
 * Client-side source of truth for whether the celebration offer is
 * still live. Server components use `resolvePrice` directly; this hook
 * keeps interactive UI (prices, badges) in sync as the clock ticks
 * past the deadline without a page reload.
 */
export function useOfferActive(): { active: boolean; ready: boolean } {
  const [active, setActive] = useState(true);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const deadline = new Date(offerConfig.offerEndsAt).getTime();
    const check = () => {
      setActive(Date.now() < deadline);
      setReady(true);
    };
    check();
    const id = setInterval(check, 1000);
    return () => clearInterval(id);
  }, []);

  return { active, ready };
}
