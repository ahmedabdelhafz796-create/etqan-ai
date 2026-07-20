# Deployment Guide

This is a standard **Next.js (App Router)** app. It deploys with **zero
configuration** on Vercel (recommended) or Netlify. The site is fully
functional with **no environment variables** — every future URL uses a safe
placeholder until you set it.

- **Repository:** https://github.com/ahmedabdelhafz796-create/etqan-ai
- **Finished branch:** `claude/premium-trading-bookstore-8vlkhb`

---

## Option A — Deploy on Vercel (recommended, ~2 minutes)

1. Go to **https://vercel.com/new** and sign in with **GitHub**.
2. Under **Import Git Repository**, pick **`ahmedabdelhafz796-create/etqan-ai`**.
   (If you don't see it, click *Adjust GitHub App Permissions* and grant access.)
3. Vercel auto-detects **Next.js** — leave Framework, Build Command
   (`next build`) and Output as-is.
4. **Production Branch:** if the finished code is already on `main`, skip this.
   Otherwise open **Settings → Git → Production Branch**, set it to
   `claude/premium-trading-bookstore-8vlkhb`, and redeploy.
5. (Optional) Add environment variables — see the table below. You can skip
   all of them for now; the site runs fine on placeholders.
6. Click **Deploy**. In ~1 minute you get a live URL like
   `https://etqan-ai.vercel.app`.

### One-click import link
> https://vercel.com/new/git/external?repository-url=https://github.com/ahmedabdelhafz796-create/etqan-ai

---

## Option B — Deploy on Netlify

1. Go to **https://app.netlify.com/start** and sign in with GitHub.
2. Pick **`ahmedabdelhafz796-create/etqan-ai`**.
3. Netlify auto-detects Next.js (via `@netlify/plugin-nextjs`).
   Build command `next build`, publish handled by the plugin.
4. Choose the branch to deploy (`main` or the finished branch).
5. Click **Deploy site**.

---

## Environment variables (all optional)

Set these in your host's dashboard (Vercel: *Settings → Environment Variables*).
The site works without them — they only replace placeholders.

| Variable | Purpose | Example |
| --- | --- | --- |
| `NEXT_PUBLIC_SITE_URL` | Canonical URL for SEO / OG / sitemap | `https://etqan-ai.vercel.app` |
| `NEXT_PUBLIC_PAYMENT_URL` | Replaces `PAYMENT_URL_PLACEHOLDER` (direct checkout link) | `https://nowpayments.io/payment/...` |
| `NEXT_PUBLIC_TELEGRAM_URL` | Replaces `TELEGRAM_URL_PLACEHOLDER` | `https://t.me/yourchannel` |
| `NOWPAYMENTS_API_KEY` | Enables server-side crypto checkout | `xxxxxxxx` |
| `NOWPAYMENTS_IPN_SECRET` | Verifies NOWPayments webhooks | `xxxxxxxx` |
| `NOWPAYMENTS_API_URL` | API base (prod or sandbox) | `https://api.nowpayments.io/v1` |
| `NEXT_PUBLIC_PAYMENT_SUCCESS_URL` | Post-payment redirect | `https://.../thank-you` |
| `NEXT_PUBLIC_PAYMENT_CANCEL_URL` | Cancel redirect | `https://.../#store` |

See `.env.example` for the full list.

---

## Run locally

```bash
npm install
npm run dev      # http://localhost:3000
```

Production build:

```bash
npm run build && npm start
```
