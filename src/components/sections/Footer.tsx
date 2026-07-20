import {
  CandlestickChart,
  Instagram,
  Send,
  Youtube,
} from "lucide-react";
import { siteConfig, links } from "@/config";

const nav = {
  Library: [
    { label: "Triple Analysis", href: "#store" },
    { label: "Advanced AI Trading", href: "#store" },
    { label: "Why Buy", href: "#why" },
    { label: "FAQ", href: "#faq" },
  ],
  Community: [
    { label: "Telegram Signals", href: "#telegram" },
    { label: "Newsletter", href: "#top" },
    { label: "Testimonials", href: "#top" },
  ],
};

// Simple X (Twitter) glyph — lucide has no brand mark.
function XIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" className={className} aria-hidden>
      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24h-6.66l-5.214-6.817-5.966 6.817H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
    </svg>
  );
}

const socials = [
  { icon: Send, href: links.telegramUrl, label: "Telegram" },
  { icon: XIcon, href: siteConfig.social.twitter, label: "X" },
  { icon: Youtube, href: siteConfig.social.youtube, label: "YouTube" },
  { icon: Instagram, href: siteConfig.social.instagram, label: "Instagram" },
];

export function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="relative border-t border-white/10 bg-night-900/60">
      <div className="container-tight py-16">
        <div className="grid gap-10 lg:grid-cols-[1.4fr_1fr_1fr]">
          <div>
            <a href="#top" className="flex items-center gap-2.5">
              <span className="flex h-9 w-9 items-center justify-center rounded-xl border border-gold/30 bg-gold/10 text-gold-light">
                <CandlestickChart className="h-5 w-5" />
              </span>
              <span className="font-display text-lg font-semibold text-soft">
                {siteConfig.name}
              </span>
            </a>
            <p className="mt-4 max-w-sm text-sm leading-relaxed text-soft/55">
              {siteConfig.tagline} Institutional-grade trading books and signals
              for traders who are serious about mastering the markets — and
              themselves.
            </p>
            <div className="mt-6 flex gap-3">
              {socials.map((s) => (
                <a
                  key={s.label}
                  href={s.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label={s.label}
                  className="flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-white/5 text-soft/70 transition-all hover:-translate-y-0.5 hover:border-gold/30 hover:text-gold-light"
                >
                  <s.icon className="h-4 w-4" />
                </a>
              ))}
            </div>
          </div>

          {Object.entries(nav).map(([title, items]) => (
            <div key={title}>
              <h3 className="text-xs font-semibold uppercase tracking-widest text-soft/45">
                {title}
              </h3>
              <ul className="mt-4 space-y-3">
                {items.map((item) => (
                  <li key={item.label}>
                    <a
                      href={item.href}
                      className="text-sm text-soft/65 transition-colors hover:text-gold-light"
                    >
                      {item.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="my-10 hairline" />

        {/* Disclaimer */}
        <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-5">
          <p className="text-xs leading-relaxed text-soft/45">
            <span className="font-medium text-soft/70">Risk disclaimer:</span>{" "}
            Trading financial markets carries substantial risk and is not
            suitable for every investor. The content sold and published by{" "}
            {siteConfig.name} is educational in nature and does not constitute
            financial, investment or trading advice. Past performance and
            examples are not indicative of future results. You are solely
            responsible for your own trading decisions and any resulting profit
            or loss. Never risk capital you cannot afford to lose.
          </p>
        </div>

        <div className="mt-8 flex flex-col items-center justify-between gap-4 text-xs text-soft/40 sm:flex-row">
          <p>
            © {year} {siteConfig.name}. All rights reserved.
          </p>
          <div className="flex items-center gap-5">
            <a href="#" className="transition-colors hover:text-soft/70">
              Terms
            </a>
            <a href="#" className="transition-colors hover:text-soft/70">
              Privacy
            </a>
            <a href="#" className="transition-colors hover:text-soft/70">
              Refund Policy
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
