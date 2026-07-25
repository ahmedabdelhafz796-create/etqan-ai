# Go-Live Checklist — E-tqan

The recommended order to finish professionally. Steps 1–2 are security and
should happen **before** the store takes a real payment.

---

## 1. Rotate the exposed credentials (do this first)

The NOWPayments API key and IPN secret used during development were shared in
plaintext, so treat both as compromised.

**a) In the NOWPayments dashboard**
- Store Settings → **API Keys** → delete the old key, create a new one.
- Store Settings → **IPN** → regenerate the IPN secret.
- Set the IPN callback URL to:
  `https://YOUR_DOMAIN/api/webhooks/nowpayments`

**b) Re-key the encrypted product files (locally, on your machine)**

File encryption is now independent of payments — it uses a dedicated
`DOWNLOAD_SIGNING_SECRET`. Rotate it once with:

```bash
git clone <repo> && cd etqan-ai && npm install

# preview first — writes nothing
OLD_SECRET='Ip/VU0TpB+WXPKuCd+z6o89vcOgSdRo/Y1B' \
NEW_SECRET='<your-new-long-random-secret>' \
npm run rekey -- --dry-run

# then apply
OLD_SECRET='Ip/VU0TpB+WXPKuCd+z6o89vcOgSdRo/Y1B' \
NEW_SECRET='<your-new-long-random-secret>' \
npm run rekey

git add -A && git commit -m "chore: rotate file-encryption key" && git push
```

Generate a strong value with `openssl rand -base64 32`. The new key never
leaves your machine — do not paste it into any chat.

> Public download filenames are an HMAC of this key, so they rotate
> automatically on the next build and old links stop resolving.

---

## 2. Set the environment variables

In Vercel → Project → Settings → **Environment Variables** (Production + Preview):

| Variable | Value |
|---|---|
| `DOWNLOAD_SIGNING_SECRET` | your new re-key secret (step 1b) |
| `NOWPAYMENTS_API_KEY` | new key from step 1a |
| `NOWPAYMENTS_IPN_SECRET` | new IPN secret from step 1a |
| `NEXT_PUBLIC_SITE_URL` | `https://your-domain` |
| `ADMIN_PASSWORD` | strong password you choose |
| `ADMIN_SESSION_SECRET` | `openssl rand -base64 32` |
| `TURSO_DATABASE_URL` | from turso.tech |
| `TURSO_AUTH_TOKEN` | from turso.tech |

Optional: `LEMONSQUEEZY_*` (card/PayPal), `NEXT_PUBLIC_GA_ID` or
`NEXT_PUBLIC_PLAUSIBLE_DOMAIN`, social URLs.

---

## 3. Merge and deploy

- Merge `claude/premium-trading-bookstore-8vlkhb` into `main` (or deploy the
  branch directly).
- Import the repo in Vercel, add the variables above, deploy.
- Add your custom domain in Vercel → Settings → Domains (HTTPS is automatic).

---

## 4. Verify before announcing

- [ ] Homepage loads; all 14 products visible; search + wishlist work.
- [ ] `/admin/login` accepts your password; Dashboard/Orders/Coupons render.
- [ ] **Sandbox purchase**: temporarily set
      `NOWPAYMENTS_API_URL=https://api-sandbox.nowpayments.io/v1`, buy one
      course, confirm `/thank-you` reveals a working download, then remove it.
- [ ] Download link expires after 10 minutes and stops after 2 uses.
- [ ] `robots.txt`, `sitemap.xml`, `manifest.webmanifest`, OG image resolve.
- [ ] Open the site on a phone — layout, RTL Arabic, and buttons all fine.

---

## 5. Launch operations

- Create a launch coupon in **Admin → Coupons** (e.g. `LAUNCH20`, 20% off).
- Confirm the offer deadline in `src/config.ts` (`offerEndsAt`) matches your plan.
- Produce the promo video from `marketing/PROMO_PACKAGE.md` +
  `marketing/ASSET_SPECS.md` (subtitles are ready in `marketing/subtitles/`).
- Enable scheduled backups in the Turso dashboard.
- Announce with the launch offer; support goes to **@Ahm_t_AHZ01**.

---

## Ongoing

- Watch **Admin → Logs** for `download_issued` and webhook events.
- Rotate `ADMIN_PASSWORD` periodically.
- To add or update a course: edit `src/catalog.ts`, author in `bookgen/`, then
  `pack-premium.mjs` → commit → deploy (see DEPLOYMENT_GUIDE.md §8).
