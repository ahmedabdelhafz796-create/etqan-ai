"use client";

import { createContext, useContext } from "react";
import { books as staticBooks, offerConfig, links } from "@/config";

export interface BookPricing {
  originalPrice: number;
  offerPrice: number;
  active: boolean;
}

export interface SiteConfigValue {
  books: Record<string, BookPricing>;
  offerEndsAt: string;
  telegramUrl: string;
  paymentUrl: string;
}

/** Fallback built from static config, so consumers work even without a provider. */
const fallback: SiteConfigValue = {
  books: Object.fromEntries(
    staticBooks.map((b) => [
      b.id,
      { originalPrice: b.originalPrice, offerPrice: b.offerPrice, active: true },
    ])
  ),
  offerEndsAt: offerConfig.offerEndsAt,
  telegramUrl: links.telegramUrl,
  paymentUrl: links.paymentUrl,
};

const Ctx = createContext<SiteConfigValue>(fallback);

export function SiteConfigProvider({
  value,
  children,
}: {
  value: SiteConfigValue;
  children: React.ReactNode;
}) {
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useSiteConfig(): SiteConfigValue {
  return useContext(Ctx);
}

export function useBookPricing(id: string): BookPricing {
  const cfg = useContext(Ctx);
  return cfg.books[id] ?? fallback.books[id];
}
