# Crypto checkout setup (NOWPayments)

This describes how `checkout.html` → `success.html` → real download hooks
together, and exactly what you need to configure to go live.

## Why there's a backend at all

`checkout.html` is static and can't safely confirm a crypto payment by
itself — anything decided purely in the browser (a timer, a redirect URL)
can be reached by anyone without paying. Real confirmation has to come
from NOWPayments' servers, via a signed webhook, verified server-side.
That's what `server-reference/api/ipn-webhook.js` does. Everything else
(`create-payment`, `order-status`, `download`) exists to support that one
security-critical check.

**Never mark an order paid based on the browser landing on `success.html`
alone.** It only polls `/api/order-status`, which reflects whatever the
webhook wrote after verifying NOWPayments' signature.

## 1. NOWPayments dashboard setup

1. Log in at https://nowpayments.io → **Store Settings**.
2. Under **API keys**, generate an API key → this is `NOWPAYMENTS_API_KEY`.
3. Under the same settings, find/generate your **IPN secret key** → this
   is `NOWPAYMENTS_IPN_SECRET`. Do not confuse this with the API key —
   they're used for different things (creating invoices vs. verifying
   webhook signatures).
4. You don't need to set a callback URL in the dashboard — it's passed
   per-invoice as `ipn_callback_url` in `create-payment.js`.

## 2. Environment variables

Copy `server-reference/.env.example` to `.env` (or your host's secret
manager) and fill in:

| Variable | Value |
|---|---|
| `NOWPAYMENTS_API_KEY` | from step 1.2 |
| `NOWPAYMENTS_IPN_SECRET` | from step 1.3 |
| `BASE_URL` | the public URL serving both the static site and `/api/*`, no trailing slash |
| `PRICE_USD` | `19` (must match the price shown in `checkout.html`) |

`NOWPAYMENTS_API_KEY` and `NOWPAYMENTS_IPN_SECRET` are server-side secrets
— never put them in any HTML/JS file the browser loads.

## 3. Deploying the backend

`server-reference/api/*.js` is written as plain `(req, res) => {}`
handlers — the convention Vercel serverless functions use directly. If
you deploy there, drop the `server-reference/api` and `server-reference/lib`
folders at your project root (so routes resolve to `/api/create-payment`
etc.) and set the env vars in the Vercel dashboard.

Any other Node host works too — wrap each handler in a thin adapter for
Express/Fastify/whatever you use; the request/response contract below
doesn't change.

Before real traffic: replace `server-reference/lib/storage.js`'s
JSON-file store with a real persistence layer (Vercel KV, Upstash Redis,
Postgres, etc.). The file-based version is only for local testing —
serverless instances don't reliably share or persist local disk writes
across invocations.

## 4. Uploading the real course files

Drop the actual files in (already gitignored is not set up, so add them
deliberately when ready):

```
files/ar/course-ar.zip
files/en/course-en.zip
files/tr/course-tr.zip
```

`api/download.js` serves exactly these paths, and only after verifying
the order is paid and the download token matches.

## API contract

### `POST /api/create-payment`
Request:
```json
{ "name": "Customer Name", "email": "customer@example.com", "language": "ar" }
```
`language` must be one of `ar`, `en`, `tr`.

Response `200`:
```json
{ "invoiceUrl": "https://nowpayments.io/payment/...", "orderId": "..." }
```
Response `400`/`502`: `{ "error": "human-readable Arabic message" }`

### `POST /api/ipn-webhook`
Called by NOWPayments only. Verifies `x-nowpayments-sig` against the
body using `NOWPAYMENTS_IPN_SECRET`. On `payment_status` of `finished` or
`confirmed`, marks the order paid and issues a one-time download token.

### `GET /api/order-status?order_id=...`
Response `200`: `{ "status": "pending" }`
or `{ "status": "paid", "downloadToken": "...", "language": "ar" }`
Response `404`: `{ "status": "unknown" }`

### `GET /api/download?order_id=...&token=...`
Streams the course zip for the order's language if the token matches a
paid order. `403` otherwise.

## Front-end flow

1. `checkout.html` collects name/email/language, `POST`s to
   `/api/create-payment`, and redirects the browser to the returned
   `invoiceUrl` (NOWPayments' hosted payment page).
2. Customer pays there. NOWPayments redirects back to
   `success.html?order_id=...` — but that redirect alone proves nothing.
3. `success.html` polls `/api/order-status` every 3s until it sees
   `status: "paid"` (written only after the IPN webhook verified real
   payment), then reveals the real `/api/download` link.
