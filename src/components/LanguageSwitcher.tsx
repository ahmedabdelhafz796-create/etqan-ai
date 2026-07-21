"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { Globe, Check } from "lucide-react";
import { locales, localeNames, LOCALE_COOKIE, type Locale } from "@/i18n/config";
import { useI18n } from "@/components/providers/I18nProvider";
import { cn } from "@/lib/utils";

function setLocaleCookie(next: Locale) {
  document.cookie = `${LOCALE_COOKIE}=${next}; path=/; max-age=31536000; samesite=lax`;
}

export function LanguageSwitcher({ className }: { className?: string }) {
  const { locale, t } = useI18n();
  const router = useRouter();
  const [open, setOpen] = React.useState(false);
  const ref = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    function onDoc(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, []);

  function choose(next: Locale) {
    setLocaleCookie(next);
    setOpen(false);
    router.refresh();
  }

  return (
    <div ref={ref} className={cn("relative", className)}>
      <button
        onClick={() => setOpen((v) => !v)}
        aria-label={t.nav.language}
        aria-haspopup="menu"
        aria-expanded={open}
        className="flex h-9 items-center gap-1.5 rounded-full border border-white/10 bg-white/5 px-3 text-xs text-soft/80 transition-colors hover:border-gold/30 hover:text-soft"
      >
        <Globe className="h-4 w-4" />
        <span className="uppercase">{locale}</span>
      </button>

      {open && (
        <div
          role="menu"
          className="absolute end-0 mt-2 w-40 overflow-hidden rounded-xl border border-white/10 bg-night-800/95 py-1 shadow-card backdrop-blur-xl"
        >
          {locales.map((l) => (
            <button
              key={l}
              role="menuitemradio"
              aria-checked={l === locale}
              onClick={() => choose(l)}
              className="flex w-full items-center justify-between px-3 py-2 text-sm text-soft/80 transition-colors hover:bg-white/5"
            >
              {localeNames[l]}
              {l === locale && <Check className="h-4 w-4 text-gold-light" />}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
