# Deployment Guide

Production-ready **Next.js (App Router)** trading bookstore with crypto
checkout (NOWPayments), secure downloads, a database-backed admin dashboard,
and trilingual (EN / AR / TR) UI with RTL.

- **Repository:** https://github.com/ahmedabdelhafz796-create/etqan-ai
- **Finished branch / default:** `main`

---

## 1. One-time provisioning (free tiers)

### a) Database — Turso (libSQL)
1. Create a free DB at **https://turso.tech**.
2. Copy the **Database URL** and an **auth token**.
   - `TURSO_DATABASE_URL=libsql://<your-db>.turso.io`
   - `TURSO_AUTH_TOKEN=<token>`
   The schema (orders, customers, download grants, settings, logs) is created
   automatically on first use.

> No DB? The storefront and payments still work; only the admin dashboard,
> stored orders and persistent download limits need it. Locally, a `file:local.db`
> is used automatically.

### b) Product files (the paid PDFs)
The PDFs are **never** committed. Put them where the server can read them:
- **Simplest:** commit them to a private storage bucket (S3 / R2 / Vercel Blob)
  and adapt `src/lib/book-files.ts` (single seam), **or**
- mount a volume and set `PRIVATE_FILES_DIR`, **or**
- upload them from the admin **Books & Pricing** page after deploy (note: on
  serverless the local filesystem is ephemeral, so prefer bucket storage for
  durability).

---

## 2. Deploy on Vercel (~2 minutes)

1. Go to **https://vercel.com/new**, sign in with GitHub.
2. Import **`ahmedabdelhafz796-create/etqan-ai`** (Next.js auto-detected).
3. Add the environment variables from the table below
   (**Settings → Environment Variables**).
4. Click **Deploy**. You'll get a URL like `https://etqan-ai.vercel.app`.

### One-click import
> https://vercel.com/new/git/external?repository-url=https://github.com/ahmedabdelhafz796-create/etqan-ai

(Netlify works too: https://app.netlify.com/start — same env vars.)

---

## 3. Wire NOWPayments

After deploy, in your NOWPayments dashboard → **Store Settings → IPN**:

- **IPN callback URL:** `https://YOUR-DOMAIN/api/webhooks/nowpayments`
- Use the **same IPN secret** you set in `NOWPAYMENTS_IPN_SECRET`.

The webhook verifies the HMAC-SHA512 signature, records the order + customer,
and mints a secure download link on a paid status.

---

## 4. Environment variables

| Variable | Required | Purpose |
| --- | --- | --- |
| `NEXT_PUBLIC_SITE_URL` | yes | Canonical URL (SEO, OG, links) |
| `NOWPAYMENTS_API_KEY` | for checkout | NOWPayments API key |
| `NOWPAYMENTS_IPN_SECRET` | for webhook | Verifies IPN callbacks |
| `NOWPAYMENTS_API_URL` | no | Defaults to `https://api.nowpayments.io/v1` |
| `NEXT_PUBLIC_TELEGRAM_URL` | recommended | Telegram invite link |
| `NEXT_PUBLIC_PAYMENT_URL` | no | Direct-checkout fallback link |
| `TURSO_DATABASE_URL` / `TURSO_AUTH_TOKEN` | for admin/orders | Database |
| `ADMIN_PASSWORD` | for admin | Admin login password |
| `ADMIN_SESSION_SECRET` | for admin | Signs the admin session cookie |
| `DOWNLOAD_SIGNING_SECRET` | no | Signs download links (falls back to IPN secret) |
| `DOWNLOAD_TTL_MS` / `DOWNLOAD_MAX` | no | Link lifetime (600000) / max downloads (2) |
| `PRIVATE_FILES_DIR` | no | Where product PDFs live |
| `NEXT_PUBLIC_GA_ID` / `NEXT_PUBLIC_GTM_ID` / `NEXT_PUBLIC_META_PIXEL_ID` / `NEXT_PUBLIC_PLAUSIBLE_DOMAIN` | no | Analytics (inert until set) |
| `NEXT_PUBLIC_TWITTER_URL` / `NEXT_PUBLIC_YOUTUBE_URL` / `NEXT_PUBLIC_INSTAGRAM_URL` | no | Social links |

See `.env.example` for the full list. **Never commit real secrets** — set
them in the host dashboard only.

---

## 5. Key routes

| Route | Purpose |
| --- | --- |
| `/` | Storefront (EN/AR/TR via language switcher) |
| `/admin` | Admin dashboard (password-gated) |
| `/api/webhooks/nowpayments` | NOWPayments IPN webhook |
| `/api/download/[bookId]?token=…` | Secure, expiring download |
| `/api/payment` | Creates a NOWPayments invoice |
| `/thank-you` | Post-payment page |

---

## 6. Run locally

```bash
npm install
cp .env.example .env.local   # fill in values
npm run dev                  # http://localhost:3000
```

Quality gates: `npm run typecheck` · `npm run lint` · `npm run build`.
