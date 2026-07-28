"use client";

import { createContext, useContext } from "react";
import type { Dictionary } from "@/i18n/dictionaries";
import type { Locale } from "@/i18n/config";
import {
  getMarketplaceCopy,
  type MarketplaceCopy,
} from "@/i18n/marketplace";

interface I18nValue {
  t: Dictionary;
  locale: Locale;
  dir: "ltr" | "rtl";
}

const I18nContext = createContext<I18nValue | null>(null);

export function I18nProvider({
  value,
  children,
}: {
  value: I18nValue;
  children: React.ReactNode;
}) {
  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n(): I18nValue {
  const ctx = useContext(I18nContext);
  if (!ctx) {
    throw new Error("useI18n must be used within an I18nProvider");
  }
  return ctx;
}

/** Shortcut to the dictionary. */
export function useT(): Dictionary {
  return useI18n().t;
}

/**
 * Copy for the AI marketplace, resolved from the active locale.
 *
 * It is derived here rather than threaded through the provider value so a
 * server component never has to pass it down — the locale already is in
 * context, and the copy is a pure lookup on it.
 */
export function useMarketplace(): MarketplaceCopy {
  return getMarketplaceCopy(useI18n().locale);
}

/** Simple {placeholder} interpolation. */
export function fill(template: string, vars: Record<string, string | number>): string {
  return template.replace(/\{(\w+)\}/g, (_, k) =>
    k in vars ? String(vars[k]) : `{${k}}`
  );
}
