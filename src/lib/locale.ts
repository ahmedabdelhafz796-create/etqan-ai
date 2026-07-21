import { cookies, headers } from "next/headers";
import { LOCALE_COOKIE, defaultLocale, isLocale, type Locale } from "@/i18n/config";

/**
 * Resolve the active locale on the server: cookie first, then the
 * Accept-Language header, then the default. Reading these makes the page
 * dynamic, which is what we want for a per-visitor localized storefront.
 */
export async function getCurrentLocale(): Promise<Locale> {
  const cookieStore = await cookies();
  const fromCookie = cookieStore.get(LOCALE_COOKIE)?.value;
  if (isLocale(fromCookie)) return fromCookie;

  const hdrs = await headers();
  const accept = hdrs.get("accept-language") || "";
  const preferred = accept.split(",")[0]?.split("-")[0]?.trim().toLowerCase();
  if (isLocale(preferred)) return preferred;

  return defaultLocale;
}
