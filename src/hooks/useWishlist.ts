"use client";

import * as React from "react";

const KEY = "etqan:wishlist";

function read(): string[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(KEY);
    const parsed = raw ? (JSON.parse(raw) as unknown) : [];
    return Array.isArray(parsed) ? parsed.filter((v): v is string => typeof v === "string") : [];
  } catch {
    return [];
  }
}

function write(ids: string[]) {
  try {
    window.localStorage.setItem(KEY, JSON.stringify(ids));
  } catch {
    /* storage unavailable (private mode) — wishlist is best-effort */
  }
  window.dispatchEvent(new Event("etqan:wishlist-change"));
}

/**
 * Client-side wishlist persisted in localStorage. No account required, so it
 * works for anonymous buyers; syncs across components via a window event.
 */
export function useWishlist() {
  const [ids, setIds] = React.useState<string[]>([]);

  React.useEffect(() => {
    const sync = () => setIds(read());
    sync();
    window.addEventListener("etqan:wishlist-change", sync);
    window.addEventListener("storage", sync);
    return () => {
      window.removeEventListener("etqan:wishlist-change", sync);
      window.removeEventListener("storage", sync);
    };
  }, []);

  const toggle = React.useCallback((id: string) => {
    const current = read();
    write(current.includes(id) ? current.filter((v) => v !== id) : [...current, id]);
  }, []);

  const has = React.useCallback((id: string) => ids.includes(id), [ids]);

  return { ids, toggle, has, count: ids.length };
}
