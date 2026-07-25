# Security Report — E-tqan

_Last reviewed: 2026-07-25 · Branch: `claude/premium-trading-bookstore-8vlkhb`_

This document records the security posture of the E-tqan store and the audit
performed across authentication, authorization, delivery, headers, input
handling, payments and secrets.

## Summary

| Area | Status | Where |
|------|--------|-------|
| Secure headers + CSP | ✅ | `next.config.mjs` |
| Rate limiting | ✅ | `src/lib/rate-limit.ts` (payment, newsletter, download, admin login) |
| Admin authentication | ✅ | `src/lib/admin-auth.ts` (HMAC-signed cookie, password-gated) |
| Authorization checks | ✅ | every `/api/admin/*` route calls `isAuthenticated()` |
| Download security | ✅ | signed HMAC token, 10-min TTL, max-2 downloads, per-grant DB counter |
| Encrypted delivery | ✅ | AES-256-GCM at rest, decrypted only at build to the CDN |
| Webhook verification | ✅ | NOWPayments HMAC-SHA512 + Lemon Squeezy HMAC-SHA256, timing-safe |
| Input validation | ✅ | JSON parse guards, email regex, coupon regex, bounded string lengths |
| XSS | ✅ | React auto-escaping; JSON-LD `<` escaped; no `dangerouslySetInnerHTML` of user data |
| CSRF | ✅ | state-changing routes are same-origin JSON POST + `form-action 'self'`; admin cookie is `SameSite=Lax`, `HttpOnly` |
| Secrets management | ✅ | env-only; scanned — no secrets committed |
| Logging | ✅ | `logs` table via `log()`; admin Logs view |

## Details

### Headers & CSP
`next.config.mjs` sets `Content-Security-Policy` (self + explicitly trusted
analytics/payment hosts; `object-src 'none'`; `frame-ancestors 'self'`;
`form-action 'self'`; `upgrade-insecure-requests`), HSTS (2 years, preload),
`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`,
`Permissions-Policy` (camera/mic/geo off + `interest-cohort=()`), COOP, CORP,
and `X-Permitted-Cross-Domain-Policies: none`.

> Note: `style-src` includes `'unsafe-inline'` (required by Tailwind/Framer
> inline styles). Scripts are restricted to self + named analytics hosts.

### Authentication & authorization
- Admin login is password-gated; a failed login is **rate-limited** by IP.
- The session is an **HMAC-SHA256 signed cookie** (`HttpOnly`, `Secure` in prod,
  `SameSite=Lax`), verified on every admin request via the `(dash)` layout and
  in every admin API route.
- There is a **single administrator role** (owner). This is intentional for a
  solo/small store; the authorization model is "authenticated admin = full
  access". Multi-user RBAC is out of scope but the seam (`isAuthenticated()`)
  is centralized for future extension.

### Secure downloads
- After a verified payment, the server mints a **signed download token** (HMAC,
  10-minute expiry, embedded `jti`).
- The download route verifies the token, then **atomically consumes** one of the
  max-2 downloads from the DB grant (race-safe `UPDATE ... WHERE used < max`),
  falling back to an in-memory counter without a DB.
- Files are served by **302 redirect** to an unguessable CDN path
  (`/dl/<hmac>.zip|pdf`) so large files bypass serverless size limits while the
  filename remains a keyed HMAC that can't be enumerated.

### Encrypted delivery at rest
- All product files are stored **AES-256-GCM encrypted** (`assets/courses/*.enc`,
  `assets/books/*.enc`), keyed from `NOWPAYMENTS_IPN_SECRET` via scrypt.
- They are decrypted **only at build time** into `public/dl/` (gitignored),
  never committed in plaintext. Verified by `tests/crypto.test.mjs`.

### Payments
- **NOWPayments** IPN: HMAC-SHA512 signature verified with a timing-safe compare
  before any grant is issued.
- **Lemon Squeezy** webhook: HMAC-SHA256 signature verified (timing-safe).
- Prices and coupon discounts are **server-authoritative** — the browser can
  only suggest a product id and coupon code; the amount is recomputed server-side.

### Input handling
- Every API route guards `request.json()` and returns 400 on malformed bodies.
- Newsletter email validated by regex; coupon code constrained to
  `^[A-Za-z0-9_-]{2,40}$`; percent-off clamped 1–100; coupon input length bounded.
- Admin settings writes are restricted to an allow-list of keys
  (`ALLOWED_SETTING_KEYS`).

### Secrets
- No secrets in source. `.env.example` documents every variable; real values
  live only in the deployment environment. A repo scan for known test tokens
  returns empty (see `git grep` in the QA step).

## Backups
- Primary datastore is **Turso/libSQL**; enable Turso's point-in-time / scheduled
  backups in the Turso dashboard (see DEPLOYMENT_GUIDE.md → Database).
- Source of truth for catalog + content is Git (content stored **encrypted** in
  `bookgen/books.vault.enc`), so the store is fully reproducible from the repo +
  the `NOWPAYMENTS_IPN_SECRET`.

## Residual notes / recommendations
- Rotate `ADMIN_PASSWORD`, `ADMIN_SESSION_SECRET`, `NOWPAYMENTS_IPN_SECRET`
  before go-live and store them only in the host's secret manager.
- For multi-instance scale, swap the in-memory rate limiter and download
  fallback store for Redis/Upstash behind the same interfaces.
