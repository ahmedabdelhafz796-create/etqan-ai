# E-tqan — Premium Digital Course Library

A production-ready, dark-luxury educational marketplace selling **premium,
trilingual (English · العربية · Türkçe) courses** in programming, AI, web,
design, productivity and trading. Built with **Next.js 16 (App Router) ·
TypeScript · TailwindCSS · Framer Motion · Radix UI · Lucide**, with
server-side crypto/card checkout and encrypted, automatic delivery.

Design language: Apple × Stripe × Linear — glass, glow, gold & emerald accents
on deep night black. Books are rendered by a bespoke engine into premium PDFs
(covers, clickable ToC, diagrams, code, exercises, quizzes, projects).

## Documentation

- **[FINAL_COMPLETION_REPORT.md](./FINAL_COMPLETION_REPORT.md)** — requirement-by-requirement audit
- **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** — env vars + deploy
- **[PAYMENT_SETUP.md](./PAYMENT_SETUP.md)** — NOWPayments + Lemon Squeezy
- **[ADMIN_GUIDE.md](./ADMIN_GUIDE.md)** — the admin dashboard
- **[SECURITY_REPORT.md](./SECURITY_REPORT.md)** — security posture
- **[CONTENT_REPORT.md](./CONTENT_REPORT.md)** — the book library + engine
- **[marketing/PROMO_PACKAGE.md](./marketing/PROMO_PACKAGE.md)** — promo video brief
- **[bookgen/README.md](./bookgen/README.md)** — the book-generation engine

## Quick start

```bash
npm install
npm run dev            # http://localhost:3000
```

Quality gates:

```bash
npm run lint
npm run typecheck
npm test
NOWPAYMENTS_IPN_SECRET=dev-secret npm run build
```

## Configuration

- **Catalog** (courses, bundles, prices, categories): `src/catalog.ts`.
- **Legacy trading books + site strings**: `src/config.ts`.
- **Environment**: copy `.env.example` and set values in your host. The only
  required-for-live values are payment keys and (optionally) the database;
  see DEPLOYMENT_GUIDE.md. No placeholders remain in code.

## Architecture

```
src/
  catalog.ts                 # courses & bundles (single source of truth)
  config.ts                  # trading books, brand, offer, links
  app/
    layout.tsx               # fonts + SEO metadata
    page.tsx                 # landing composition (Marketplace centerpiece)
    sitemap.ts / robots / manifest / opengraph-image
    thank-you/               # post-payment auto-delivery page
    admin/                   # dashboard, orders, customers, courses, coupons, settings, logs
    api/
      payment/route.ts       # NOWPayments + Lemon Squeezy checkout (+ coupons, rate-limited)
      download/[bookId]/      # signed, expiring, count-limited downloads → CDN
      webhooks/{nowpayments,lemonsqueezy}/
      newsletter/ · admin/{settings,coupons,upload,login,logout}/
  components/                # ui, visuals, sections, admin, providers
  lib/                       # payment, lemonsqueezy, download-token, rate-limit, repositories, db, …
  i18n/                      # EN/AR/TR dictionaries + localized book text
bookgen/                     # premium book engine (encrypted sources vault)
assets/{books,courses}/*.enc # AES-256-GCM encrypted deliverables
scripts/                     # prepare-downloads, pack-courses, pack-premium
tests/                       # node:test (crypto round-trip, catalog integrity)
```

## Features

- 🎓 Trilingual premium course marketplace with category filter & bundles
- 💳 Server-side checkout: NOWPayments crypto + optional Lemon Squeezy card/PayPal
- 🔐 Encrypted delivery, signed & expiring download links (max-2), auto-delivery
- 🎟️ Server-authoritative coupons
- 🛡️ CSP + secure headers, rate limiting, HMAC-verified webhooks
- 🧑‍💼 Admin: orders, customers, courses, books, coupons, settings, logs
- 🔍 SEO: metadata, Open Graph, Course/Book JSON-LD, sitemap, robots, manifest
- ♿ Accessible, responsive, reduced-motion aware, RTL for Arabic

---

_All content is original educational material produced by E-tqan._
