"use client";

import { useSyncExternalStore } from "react";

/**
 * A single shared 1-second clock exposed through `useSyncExternalStore`.
 *
 * Why this pattern:
 *  - It is SSR-safe. The server snapshot is a fixed `0`, so server output is
 *    deterministic and every consumer renders a neutral state during
 *    hydration — no mismatch.
 *  - It avoids `setState`-inside-`useEffect` (the cascading-render smell),
 *    because React reads the cached snapshot and only re-renders on a real
 *    tick notification.
 *  - One interval powers the whole app (countdown, offer state, etc.).
 */
const store = {
  now: 0,
  started: false,
  listeners: new Set<() => void>(),
  start() {
    if (this.started) return;
    this.started = true;
    this.now = Date.now();
    setInterval(() => {
      this.now = Date.now();
      this.listeners.forEach((l) => l());
    }, 1000);
  },
};

function subscribe(cb: () => void) {
  store.listeners.add(cb);
  store.start();
  return () => {
    store.listeners.delete(cb);
  };
}

/** Current time in ms, ticking each second. `0` during SSR / first paint. */
export function useNow(): number {
  return useSyncExternalStore(
    subscribe,
    () => store.now,
    () => 0
  );
}

/** True only after the component has mounted on the client. */
export function useIsClient(): boolean {
  return useNow() !== 0;
}
