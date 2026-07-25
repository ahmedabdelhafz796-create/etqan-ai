# Deployment Guide — E-tqan

The store is a Next.js 16 (App Router) app, optimized for **Vercel**. It builds
and runs anywhere Node 18+ is available.

## 1. Prerequisites

- Node.js 18+ (20 recommended).
- A `NOWPAYMENTS_IPN_SECRET` value — this is also the file-encryption key and
  **must be set before the first build** so product files decrypt.
- (Recommended) a Turso database for orders/customers/coupons/logs.

## 2. Environment variables

Copy `.env.example` → set values in your host's environment. Minimum to go live:

```
NOWPAYMENTS_API_KEY=...
NOWPAYMENTS_IPN_SECRET=...          # ALSO the file-encryption key
NEXT_PUBLIC_SITE_URL=https://your-domain
ADMIN_PASSWORD=...                  # for /admin
ADMIN_SESSION_SECRET=...            # random string
TURSO_DATABASE_URL=...              # optional but recommended
TURSO_AUTH_TOKEN=...
```

Optional: Lemon Squeezy (see PAYMENT_SETUP.md), analytics IDs, social links.

## 3. Build pipeline

`npm run build` runs, in order:

1. **prebuild** (`scripts/prepare-downloads.mjs`) — decrypts every
   `assets/{books,courses}/*.enc` into `public/dl/<hmac>.{pdf,zip}` using
   `NOWPAYMENTS_IPN_SECRET`. Skips gracefully if the secret is unset (downloads
   inactive, site still builds).
2. **next build** — compiles the app.

Verified: with the secret set, prebuild reports `2/2 book` + `14/14 course`
files prepared.

## 4. Deploy to Vercel

1. Import the GitHub repo into Vercel.
2. Add the environment variables above (Production + Preview).
3. Deploy. Every push to the connected branch auto-deploys.
4. Point your custom domain at the project; Vercel provisions HTTPS.

> `public/dl/` is gitignored and regenerated on each build from the encrypted
> assets — never commit decrypted files.

## 5. Post-deploy checklist

- [ ] `https://your-domain` loads; marketplace shows all courses.
- [ ] `/admin/login` works with `ADMIN_PASSWORD`.
- [ ] NOWPayments IPN URL set to `/api/webhooks/nowpayments`.
- [ ] (If used) Lemon Squeezy webhook set to `/api/webhooks/lemonsqueezy`.
- [ ] A sandbox purchase yields a working download on `/thank-you`.
- [ ] `robots.txt`, `sitemap.xml`, `opengraph-image` and `manifest` resolve.

## 6. Database & backups

- Create a free DB at https://turso.tech, paste `TURSO_DATABASE_URL` +
  `TURSO_AUTH_TOKEN`. Schema is created automatically on first use.
- Enable Turso scheduled backups in its dashboard.
- The catalog and all book content are reproducible from Git (content stored
  **encrypted** in `bookgen/books.vault.enc`) + the IPN secret.

## 7. Local verification

```
npm install
npm run lint
npm run typecheck
npm test
NOWPAYMENTS_IPN_SECRET=dev-secret npm run build
NOWPAYMENTS_IPN_SECRET=dev-secret npm start
```

## 8. Regenerating / adding course content

See `bookgen/README.md` and CONTENT_REPORT.md. In short:

```
cd bookgen && npm install
NOWPAYMENTS_IPN_SECRET=... node vault.mjs unpack     # restore book sources
node build.mjs all                                    # render PDFs
NOWPAYMENTS_IPN_SECRET=... node ../scripts/pack-premium.mjs <id...>
NOWPAYMENTS_IPN_SECRET=... node vault.mjs pack        # re-seal sources
```
