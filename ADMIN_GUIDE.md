# Admin Guide — E-tqan

The admin dashboard lives at **`/admin`**. It is password-gated and requires a
configured database to show data.

## Access

1. Set `ADMIN_PASSWORD` (a strong value) and `ADMIN_SESSION_SECRET` (random) in
   the environment.
2. Configure the database (`TURSO_DATABASE_URL` + `TURSO_AUTH_TOKEN`); without a
   DB, admin pages show a "Database not configured" notice.
3. Visit `/admin/login`, enter the password. The session is an HMAC-signed,
   `HttpOnly` cookie. Log out from the sidebar.

Failed logins are rate-limited by IP. There is a single **owner** role with
full access (see SECURITY_REPORT.md → authorization).

## Sections

| Page | What you can do |
|------|-----------------|
| **Dashboard** | Totals: orders, paid orders, revenue, customers; recent orders. |
| **Orders** | Every order with payment id, product, amount, status, date. |
| **Customers** | Buyers captured from paid orders (email, name, joined). |
| **Courses** | Read-only catalog overview: all 14 products, category, price, languages, and whether each has a delivery blob committed. |
| **Books & Pricing** | Edit the two trading books' prices/active flag and upload their PDFs. |
| **Coupons** | Create/list/delete percentage discount codes (optional max uses). |
| **Settings** | Live overrides for prices, countdown, links and SEO (allow-listed keys). |
| **Logs** | Structured event log (payments, downloads, settings changes, webhooks). |

## Managing the catalog (courses & bundles)

Courses are **config-driven** in `src/catalog.ts` (the single source of truth for
titles, categories, prices, languages and bundle membership). To change a
course's price or details, edit `catalog.ts` and redeploy. The **Courses** admin
page reflects the live catalog and shows delivery readiness.

Course **content** is authored with the E-tqan book engine in `bookgen/` and
packed into the encrypted delivery blobs (`assets/courses/*.enc`). See
CONTENT_REPORT.md for the pipeline.

## Coupons

- Code: 2–40 letters/numbers (auto-uppercased), e.g. `WELCOME15`.
- Percent off: 1–100.
- Max uses: optional; leave blank for unlimited.
- Discounts are applied **server-side** at checkout only.

## Media / files

- Trading book PDFs can be uploaded from **Books & Pricing** (stored under
  `PRIVATE_FILES_DIR`, default `./private/books`, never committed).
- Course media is produced by the book engine and delivered encrypted; there is
  no per-file upload for courses by design (content is generated, not uploaded).

## Analytics

- The Dashboard shows first-party order/revenue/customer analytics from your DB.
- Optional third-party analytics (GA4, GTM, Meta Pixel, Plausible) are injected
  only when their IDs are set in the environment (`NEXT_PUBLIC_GA_ID`, etc.); no
  scripts or cookies load while those are empty.
