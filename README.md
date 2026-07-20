# ETQAN AI — Premium Trading Bookstore

A production-ready, dark-luxury digital bookstore for selling professional
trading books. Built with **Next.js (App Router) · TypeScript · TailwindCSS ·
Framer Motion · Radix UI · Lucide** and a NOWPayments-ready checkout
architecture.

Design language: TradingView × Binance × Bloomberg × Apple × Stripe — glass,
glow, animated candlesticks, gold & emerald accents on deep night black.

---

## Quick start

```bash
npm install
npm run dev
```

Open <http://localhost:3000>.

Build for production:

```bash
npm run build && npm start
```

---

## One-file configuration

Everything you'll want to edit lives in **`src/config.ts`**:

- Book titles, subtitles, descriptions & curricula
- **Prices & discounts** (`originalPrice`, `offerPrice`)
- **Countdown / offer end date** (`offerConfig.offerEndsAt`)
- **Telegram link placeholder** → `TELEGRAM_URL_PLACEHOLDER`
- **Payment URL placeholder** → `PAYMENT_URL_PLACEHOLDER`
- Brand, social links, SEO strings

When the countdown expires, discounts hide automatically and original
prices are restored across the whole site — no code changes needed.

## Go-live checklist (replace ONE variable each)

| What | Where |
| --- | --- |
| Direct checkout link | `NEXT_PUBLIC_PAYMENT_URL` (replaces `PAYMENT_URL_PLACEHOLDER`) |
| Telegram invite | `NEXT_PUBLIC_TELEGRAM_URL` (replaces `TELEGRAM_URL_PLACEHOLDER`) |
| NOWPayments API | `NOWPAYMENTS_API_KEY` in `.env.local` |

Copy `.env.example` → `.env.local` and fill in values.

---

## NOWPayments integration

The project ships a **real, typed** integration surface — no fake success:

- `src/lib/payment.ts` — service that calls the NOWPayments REST API.
- `src/app/api/payment/route.ts` — server route that creates an offer-aware
  invoice and returns the hosted checkout URL.
- The **Buy Now** button (`src/components/sections/BuyButton.tsx`) calls the
  route; if no API key is configured yet it gracefully falls back to the
  payment URL placeholder — nothing is faked.

Set `NOWPAYMENTS_API_KEY` (and optionally `NOWPAYMENTS_IPN_SECRET`) to go live.

---

## Project structure

```
src/
  config.ts                  # single source of truth (prices, dates, links, books)
  app/
    layout.tsx               # fonts + SEO metadata
    page.tsx                 # landing page composition
    globals.css
    sitemap.ts / robots.ts / manifest.ts
    icon.svg
    thank-you/               # post-payment page
    api/
      payment/route.ts       # NOWPayments invoice endpoint
      newsletter/route.ts    # newsletter opt-in endpoint
  components/
    ui/                      # button, accordion, badge, reveal, section-heading
    visuals/                 # candlesticks, ticker tape, confetti, book cover
    sections/                # hero, banner, countdown, store, telegram, warning…
  hooks/                     # useCountdown, useOfferActive
  lib/                       # utils, pricing, payment service
```

## Features

- 🕯️ Animated candlestick hero background & live market ticker tape
- 🎉 First-Edition celebration banner with confetti
- ⏳ Live countdown timer (auto-restores prices on expiry)
- 📚 Premium book cards with expandable institutional curricula
- 💳 NOWPayments-ready **Buy Now** flow
- 📡 Telegram signals section (launches Aug 1, 2026)
- ⚠️ Beginner warning + luxury psychology quote
- ⭐ Why-buy grid, FAQ accordion, testimonials, newsletter
- 🔍 SEO: metadata, Open Graph, JSON-LD, sitemap, robots, manifest
- ♿ Accessible, responsive, reduced-motion aware

---

_Educational content only. Trading involves substantial risk._
