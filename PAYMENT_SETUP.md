# Payment Setup — E-tqan

The store supports two checkout providers, both server-side and both optional
until you add credentials. No secrets are in the code — everything is env-driven.

- **NOWPayments** — crypto checkout (default). Fully implemented + verified IPN.
- **Lemon Squeezy** — card / PayPal (optional). Full architecture + verified webhook.

Delivery is identical for both: on a confirmed payment the server mints a
secure, expiring download grant and the buyer is redirected to `/thank-you`,
which auto-reveals the download.

---

## 1. NOWPayments (crypto)

1. Create an account at https://nowpayments.io and complete store setup.
2. Dashboard → **Store Settings → API Keys**: copy your API key.
3. Dashboard → **Store Settings → IPN**: set the callback URL to
   `https://YOUR_DOMAIN/api/webhooks/nowpayments` and copy the **IPN secret**.
4. Set environment variables:

   ```
   NOWPAYMENTS_API_KEY=...            # server API key
   NOWPAYMENTS_IPN_SECRET=...         # IPN signing secret (ALSO the file-encryption key)
   NOWPAYMENTS_API_URL=https://api.nowpayments.io/v1
   NOWPAYMENTS_PRICE_CURRENCY=usd
   ```

> ⚠️ `NOWPAYMENTS_IPN_SECRET` is also the key that encrypts/decrypts product
> files. Set it **before** the first build and never change it without re-packing
> the encrypted assets, or downloads will fail.

### Flow
`/api/payment` → `createInvoice()` → hosted checkout → buyer pays → NOWPayments
POSTs the IPN → signature verified (HMAC-SHA512, timing-safe) → grant minted →
buyer returns to `/thank-you` (which also confirms via `getPaymentStatus`).

---

## 2. Lemon Squeezy (card / PayPal) — optional

1. Create a store at https://app.lemonsqueezy.com.
2. **Settings → API**: create an API key.
3. **Settings → Webhooks**: add `https://YOUR_DOMAIN/api/webhooks/lemonsqueezy`,
   subscribe to `order_created`, and copy the signing secret.
4. (Optional) create a product/variant and map catalog ids to variant ids.
5. Set environment variables:

   ```
   LEMONSQUEEZY_API_KEY=...
   LEMONSQUEEZY_STORE_ID=...              # numeric store id
   LEMONSQUEEZY_WEBHOOK_SECRET=...
   LEMONSQUEEZY_VARIANT_MAP={"python":"123456"}   # optional
   LEMONSQUEEZY_DEFAULT_VARIANT_ID=...            # optional fallback
   ```

### Selecting card checkout
`POST /api/payment` with `{ "bookId": "...", "provider": "card" }` routes to
Lemon Squeezy; omit `provider` (or send `"crypto"`) for NOWPayments. If a
variant is mapped, its configured price is used; otherwise a **custom-priced**
checkout is created for the exact (coupon-adjusted) amount.

---

## 3. Coupons

- Create codes in **Admin → Coupons** (percentage off, optional max redemptions).
- The client may send `{ "coupon": "CODE" }` to `/api/payment`; the discount is
  **validated and applied server-side** (`validateCoupon`) — never trusted from
  the browser. Invalid/expired/used-up codes are silently ignored.

---

## 4. Verifying the flow (without going live)

- With no keys set, `/api/payment` returns a clean `503 checkout_unconfigured`
  and the Buy button shows a graceful "checkout opens soon" state — nothing is
  faked.
- With sandbox keys (`NOWPAYMENTS_API_URL=https://api-sandbox.nowpayments.io/v1`),
  you can complete an end-to-end test purchase and confirm the download appears.

---

## 5. What only you can provide

The only things that must come from you (never hardcoded): the **API keys and
webhook secrets** above. Everything else — pricing, catalog, delivery, coupons,
redirect URLs — is already configured in code/DB.
