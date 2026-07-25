# Project Structure — E-tqan

A map of every directory and the role it plays. Only production files remain in
the repository; build artifacts and secrets are gitignored.

```
etqan-ai/
├── src/
│   ├── catalog.ts               ★ Courses & bundles — single source of truth
│   │                              (ids, categories, prices, tags, related,
│   │                              bundle membership, per-language files)
│   ├── config.ts                  Brand, SEO strings, offer window, links,
│   │                              analytics IDs, legacy trading books
│   ├── middleware.ts?             (none — headers set in next.config.mjs)
│   ├── app/
│   │   ├── layout.tsx             Fonts, metadata, providers, ambient bg
│   │   ├── page.tsx               Landing composition (Marketplace centerpiece)
│   │   ├── globals.css            Tailwind layers + design tokens
│   │   ├── sitemap.ts             Sitemap (courses + section anchors)
│   │   ├── robots.txt / manifest.ts / icon.svg / opengraph-image.tsx
│   │   ├── thank-you/page.tsx     Post-payment auto-delivery page
│   │   ├── admin/
│   │   │   ├── login/page.tsx     Password gate (rate-limited)
│   │   │   └── (dash)/            Authenticated dashboard group
│   │   │       ├── layout.tsx     Sidebar nav + auth guard
│   │   │       ├── page.tsx       Dashboard: orders, revenue, customers
│   │   │       ├── orders/        All orders
│   │   │       ├── customers/     Buyers
│   │   │       ├── courses/       Catalog + delivery-readiness overview
│   │   │       ├── books/         Trading book pricing + PDF upload
│   │   │       ├── coupons/       Discount code management
│   │   │       ├── settings/      Live setting overrides (allow-listed)
│   │   │       └── logs/          Structured audit log
│   │   └── api/
│   │       ├── payment/route.ts            Checkout: NOWPayments + Lemon Squeezy,
│   │       │                               coupons, rate-limited
│   │       ├── download/[bookId]/route.ts  Signed, expiring, count-limited → CDN
│   │       ├── newsletter/route.ts         Validated opt-in (+ persistence)
│   │       ├── webhooks/
│   │       │   ├── nowpayments/route.ts    HMAC-SHA512 verified IPN → grant
│   │       │   └── lemonsqueezy/route.ts   HMAC-SHA256 verified webhook → grant
│   │       └── admin/{login,logout,settings,coupons,upload}/
│   ├── components/
│   │   ├── ui/                    button, badge, accordion, reveal, spotlight,
│   │   │                          magnetic, section-heading
│   │   ├── visuals/               AmbientBackground, Particles, BookCover, Confetti
│   │   ├── sections/              Navbar, Hero, CelebrationBanner, Marketplace★,
│   │   │                          BookStore, WhyBuy, TelegramSection (support),
│   │   │                          WarningSection, QuoteSection, Testimonials,
│   │   │                          FAQ, Newsletter, Footer, BuyButton, ScrollProgress
│   │   ├── admin/                 ui helpers, BookAdmin, CouponAdmin, LogoutButton
│   │   ├── providers/             I18nProvider, SiteConfigProvider, SmoothScroll
│   │   ├── Analytics.tsx          Inert until an analytics ID is configured
│   │   └── StructuredData.tsx     JSON-LD: Organization, WebSite, Course, Book
│   ├── hooks/                     useClock, useCountdown, useOfferActive,
│   │                              useMouseParallax, useWishlist★
│   ├── i18n/                      config (locales/dir), dictionaries (EN/AR/TR),
│   │                              books (localized trading book text)
│   └── lib/
│       ├── payment.ts             NOWPayments REST client
│       ├── lemonsqueezy.ts        Lemon Squeezy client + signature verify
│       ├── download-token.ts      HMAC token mint/verify (TTL, max downloads)
│       ├── download-hash.ts       Keyed public filename for CDN delivery
│       ├── download-store.ts      In-memory fallback download counter
│       ├── rate-limit.ts          Sliding-window limiter + 429 helper
│       ├── repositories.ts        Typed DB access (orders, customers, grants,
│       │                          settings, newsletter, coupons, logs)
│       ├── db.ts                  libSQL/Turso client + schema bootstrap
│       ├── admin-auth.ts          Signed session cookie
│       ├── site-settings.ts       Effective config (DB overrides + defaults)
│       ├── purchasable.ts         Unified book/course resolver
│       ├── pricing.ts             Offer-aware price helpers
│       ├── book-files.ts          Private file paths for uploads
│       ├── locale.ts              Cookie-based locale resolution
│       └── utils.ts               cn, formatUSD, discountPercent
│
├── bookgen/                     ★ Premium book engine (authoring → PDF)
│   ├── engine/theme.css           Book design system (cover, layout, callouts)
│   ├── engine/dsl.mjs             Authoring helpers (chapters, code, tables,
│   │                              quizzes, exercises, projects, diagrams,
│   │                              summary, cheat sheet, glossary, roadmap, refs)
│   ├── engine/appendix.mjs        Localized appendix builder (all courses)
│   ├── engine/render.mjs          Chromium PDF renderer (ToC, bookmarks, footers)
│   ├── engine/fonts.css + fonts/  Self-hosted fonts (EN/TR/AR unicode-ranges)
│   ├── build.mjs                  Render one book or `all`
│   ├── vault.mjs                  Encrypt/restore the private book sources
│   ├── books.vault.enc            ★ Encrypted book sources (the paid content)
│   └── README.md
│
├── assets/
│   ├── books/*.enc                Encrypted trading book PDFs (2)
│   └── courses/*.enc              Encrypted course/bundle deliverables (14)
│
├── scripts/
│   ├── prepare-downloads.mjs      prebuild: decrypt → public/dl/<hmac>.{pdf,zip}
│   ├── pack-premium.mjs           Pack rendered premium PDFs into course blobs
│   ├── pack-courses.mjs           Pack raw source PDFs (dev tool)
│   ├── encrypt-book.mjs           Encrypt a single book asset
│   └── lib/crypto.mjs             AES-256-GCM + keyed filename hash
│
├── tests/                         node:test — crypto round-trip, catalog integrity
├── marketing/
│   ├── PROMO_PACKAGE.md           Storyboard, AR VO, editing, animation prompts
│   ├── subtitles/{en,ar,tr}.srt   Ready-to-burn subtitle tracks
│   └── ASSET_SPECS.md             Thumbnail, trailer & platform export specs
│
├── FINAL_COMPLETION_REPORT.md     Requirement-by-requirement audit
├── CONTENT_REPORT.md              The library + book pipeline
├── SECURITY_REPORT.md             Security posture & audit
├── DEPLOYMENT_GUIDE.md            Env vars + deploy + post-deploy checklist
├── PAYMENT_SETUP.md               NOWPayments + Lemon Squeezy, field by field
├── ADMIN_GUIDE.md                 Using the dashboard
├── PROJECT_STRUCTURE.md           This file
├── README.md                      Overview + doc index
├── next.config.mjs                CSP + security headers, image/pkg optimization
├── eslint.config.mjs              Flat ESLint config (app only)
├── tailwind.config.ts             Design tokens (night/gold/emerald/royal…)
├── tsconfig.json · postcss.config.mjs · package.json
└── .env.example                   Every variable, documented (no secrets)
```

★ = the files you are most likely to edit.

## Never committed (gitignored)

`node_modules/`, `.next/`, `public/dl/` (decrypted deliverables, rebuilt each
build), `private/` (uploaded PDFs), `local.db`, `.env.local`, `bookgen/books/`
(plaintext book sources — the encrypted vault is committed instead),
`bookgen/out/` (rendered PDFs).

## Data flow at a glance

1. **Authoring** — `bookgen/books/*.mjs` → `build.mjs` → premium PDFs.
2. **Packaging** — `pack-premium.mjs` → AES-256-GCM → `assets/courses/*.enc`.
3. **Build** — `prepare-downloads.mjs` decrypts to `public/dl/<hmac>.zip`.
4. **Purchase** — `/api/payment` → provider checkout → verified webhook →
   download grant → `/thank-you` reveals a signed, expiring link.
5. **Delivery** — `/api/download/[id]` verifies + counts, 302s to the CDN file.
