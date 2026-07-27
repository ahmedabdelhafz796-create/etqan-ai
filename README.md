# ETQAN AI

A marketplace for **production-hardened AI automation systems, tools and
templates**, with a professional trading library as a secondary collection.

Built with **Next.js (App Router) · TypeScript · TailwindCSS · Framer Motion ·
Radix UI · Lucide**.

## Two product lines, two checkout paths

| Line | Sold through | Where |
| --- | --- | --- |
| AI systems, tools, templates | **Lemon Squeezy** (external) | `#catalog` |
| Trading library | **NOWPayments** (in-house crypto) | `#store` |

These never mix. The catalogue cards link out to Lemon Squeezy; the book
cards use the site's own payment route. They share no component and no code
path — see `src/components/sections/Catalog.tsx` for the first and
`src/components/sections/BuyButton.tsx` for the second.

The homepage is the AI marketplace end to end: hero, catalogue, how it
installs, the six build rules, the test report, then the FAQ. The trading
library is one section below a labelled divider, and it is the only place
gold appears — the AI line runs on iris/aqua so the two are never confused.

## The automation catalogue

The workflows themselves are built and tested in [`suite/`](./suite), which
contains a template factory, a validator that gates releases, and a minimal
n8n execution engine used for behavioural testing.

**23 workflows · 285 nodes · 151 behavioural tests · 14 gate probes.**

```bash
cd suite/factory
python3 build.py        # generate + validate; writes only what passes
python3 test_gate.py    # prove the validator rejects bad input
node harness/run.mjs    # execute the workflows against adversarial input
python3 package.py      # produce the sellable bundles
```

## 🚀 Deploy in one click

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/git/external?repository-url=https://github.com/ahmedabdelhafz796-create/etqan-ai)
&nbsp;
[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start/deploy?repository=https://github.com/ahmedabdelhafz796-create/etqan-ai)

No environment variables required to launch — see **[DEPLOYMENT.md](./DEPLOYMENT.md)**
for the step-by-step guide and the optional config table.

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
