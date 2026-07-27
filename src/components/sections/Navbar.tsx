"use client";

import * as React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Menu, Workflow, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Magnetic } from "@/components/ui/magnetic";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { useT } from "@/components/providers/I18nProvider";
import { cn } from "@/lib/utils";
import { siteConfig } from "@/config";

export function Navbar() {
  const [scrolled, setScrolled] = React.useState(false);
  const [open, setOpen] = React.useState(false);
  const t = useT();

  // The AI marketplace owns the navigation. The trading library gets one
  // entry at the end, which is exactly its weight on the page.
  const NAV_LINKS = [
    { label: t.nav.links.automation, href: "#catalog" },
    { label: t.nav.links.how, href: "#how" },
    { label: t.nav.links.standard, href: "#standard" },
    { label: t.nav.links.faq, href: "#faq" },
    { label: t.nav.links.library, href: "#store" },
  ];

  React.useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 16);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <motion.header
      initial={{ y: -80, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      className={cn(
        "fixed inset-x-0 top-0 z-50 transition-all duration-300",
        scrolled
          ? "border-b border-white/10 bg-night-900/80 backdrop-blur-xl"
          : "border-b border-transparent bg-transparent"
      )}
    >
      <nav className="container-tight flex h-16 items-center justify-between md:h-18">
        <a href="#top" className="group flex items-center gap-2.5">
          {/* Was a candlestick chart. The mark now shows a workflow, which
              is what the site sells. */}
          <span className="flex h-9 w-9 items-center justify-center rounded-xl border border-iris/35 bg-iris/10 text-iris-light shadow-glow-iris">
            <Workflow className="h-5 w-5" />
          </span>
          <span className="font-display text-lg font-semibold tracking-tight text-soft">
            {siteConfig.name}
          </span>
        </a>

        <div className="hidden items-center gap-1 md:flex">
          {NAV_LINKS.map((l) => (
            <a
              key={l.label}
              href={l.href}
              className="rounded-full px-4 py-2 text-sm text-soft/70 transition-colors hover:text-soft"
            >
              {l.label}
            </a>
          ))}
        </div>

        <div className="hidden items-center gap-3 md:flex">
          <LanguageSwitcher />
          <Magnetic strength={8}>
            <Button asChild variant="iris" size="sm">
              <a href="#catalog">{t.nav.cta}</a>
            </Button>
          </Magnetic>
        </div>

        <div className="flex items-center gap-2 md:hidden">
          <LanguageSwitcher />
          <button
            className="flex h-10 w-10 items-center justify-center rounded-lg border border-white/10 text-soft"
            onClick={() => setOpen((v) => !v)}
            aria-label={t.nav.menu}
            aria-expanded={open}
          >
            {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </nav>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="overflow-hidden border-t border-white/10 bg-night-900/95 backdrop-blur-xl md:hidden"
          >
            <div className="container-tight flex flex-col gap-1 py-4">
              {NAV_LINKS.map((l) => (
                <a
                  key={l.label}
                  href={l.href}
                  onClick={() => setOpen(false)}
                  className="rounded-lg px-3 py-3 text-sm text-soft/80 hover:bg-white/5"
                >
                  {l.label}
                </a>
              ))}
              <Button
                asChild
                variant="iris"
                size="md"
                className="mt-2 w-full"
              >
                <a href="#catalog" onClick={() => setOpen(false)}>
                  {t.nav.cta}
                </a>
              </Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.header>
  );
}
