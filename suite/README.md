# Digital Commerce Automation Suite

Production-hardened n8n templates for people who sell digital products.

**20 templates · 3 system workflows · 285 functional nodes**
**151 behavioural tests · 14 gate probes · 0 failures**

---

## The premise

The template market is saturated with quantity. There are 9,300+ workflows in
n8n's library and 4,343+ free ones on GitHub alone, and bundles of 365 templates
sell for "pay what you want."

Quantity is not scarce. Trust is. Two findings shaped this entire project:

- **~97%** of workflows that pass a demo fail on real traffic — no retries, no
  idempotency, no error path.
- **~70%** of published templates fail at install — version drift, thin docs,
  embedded credentials.

So this suite does not compete on count. It competes on the one thing the market
does not supply: templates that hold up when real money moves through them.

Full evidence in [`docs/01-market-research.md`](./docs/01-market-research.md).

---

## Three levels of verification

Most templates are verified once, by their author, by hand. These pass three
independent gates, all of which run on every build.

### 1. Structural — the gate

[`factory/lib/validate.py`](./factory/lib/validate.py) is the executable form of
the published standard. `build.py` refuses to write a template that fails it.

| Guarantee | Enforced by |
| --- | --- |
| Duplicate webhooks cause no duplicate side effects | event-id dedupe in static data, TTL-pruned, no database |
| Malformed payloads fail loudly at the door | required-field assertion naming what was missing |
| Every network call retries 3× with backoff | **default-deny** across all non-local node types |
| Failures are routed, never silent | checked **per node**, both handling strategies accepted |
| One obvious place to configure | single Config node, secrets excluded by design |
| Zero credentials in shipped files | secret-scan + author-credential-id rejection |
| Docs where you are working | sticky notes + per-node notes, coverage enforced |
| Same behaviour on Cloud and self-hosted | HMAC via Crypto node, never `require('crypto')` |

### 2. Behavioural — the engine

[`factory/harness/`](./factory/harness/) is a minimal n8n executor. It walks the
real `workflow.json`, runs the real Code-node JavaScript, computes real HMACs,
and evaluates real branch conditions — so tests exercise the file we ship rather
than a paraphrase of it. It makes no network calls; email and HTTP nodes record
intent.

151 tests, each a failure a real buyer could hit:

```
✅ a replayed webhook does NOT deliver a second time
✅ a pending payment delivers nothing
✅ changing the product id in a download URL is refused
✅ a repeat card failure does not re-send the day-one dunning email
✅ a buyer who completes checkout is never chased for their cart
✅ a refund question never reaches the AI model
✅ a model outage does not lose a qualified lead
✅ a replayed order never consumes a second invoice number
✅ re-running a payout pays nobody twice
✅ no email is ever sent to a job candidate
```

### 3. Gate integrity — testing the tester

[`factory/test_gate.py`](./factory/test_gate.py) injects 14 real defects into a
known-good template and asserts each is caught. A gate that only ever reports
PASS is decoration.

It exists because the first retry rule enumerated node types and missed
`emailSend` — the most failure-prone node in the delivery template.

```bash
python3 factory/build.py      # build + validate; writes only what passes
python3 factory/test_gate.py  # 14/14 probes
node factory/harness/run.mjs  # 151/151 tests
```

---

## The system spine

These three are what make the rest a *system* rather than a folder of files, and
they are what justifies a suite price over a per-template price.

| Workflow | Does |
| --- | --- |
| [`setup-checker`](./templates/sys-spine/setup-checker/) | **Run this first.** Catches the install mistakes that cause silent failures — mismatched signing secrets, placeholders left in Config, testMode still on |
| [`central-error-hub`](./templates/sys-spine/central-error-hub/) | Every failure, ranked by business impact, storm-suppressed, explained in plain language |
| [`daily-business-pulse`](./templates/sys-spine/daily-business-pulse/) | One daily message: what needs you, what was recovered, what ran |

The setup checker earns its place on one check alone: four templates share a
link-signing secret, and if any two disagree every download fails with an
"invalid signature" error that looks like tampering rather than a typo. It signs
a fixed probe with each configured secret and compares — catching even trailing
whitespace, which is invisible on screen.

---

## The templates

| Template | Category | Solves |
| --- | --- | --- |
| [`instant-digital-delivery`](./templates/a1-delivery/instant-digital-delivery/) | A1 · Delivery | "Paid and never received it" — 6 gateways → one order shape → signed link |
| [`secure-download-endpoint`](./templates/a1-delivery/secure-download-endpoint/) | A1 · Delivery | Expired and leaked links; refusals that explain themselves |
| [`product-update-broadcast`](./templates/a1-delivery/product-update-broadcast/) | A1 · Delivery | Past buyers holding an outdated file and a dead link |
| [`automatic-invoice-vat`](./templates/a2-payments-finance/automatic-invoice-vat/) | A2 · Finance | Gap-free sequential invoices; cross-border tax evidence |
| [`pre-payment-fraud-scoring`](./templates/a3-fraud-security/pre-payment-fraud-scoring/) | A3 · Fraud 🎯 | Fraud caught **before** delivery — no paid API |
| [`chargeback-early-warning`](./templates/a3-fraud-security/chargeback-early-warning/) | A3 · Fraud 🎯 | Disputes lost by default; evidence that expires before it's collected |
| [`leak-detection-watermarking`](./templates/a3-fraud-security/leak-detection-watermarking/) | A3 · Fraud | Files resold and reshared with no way to trace the source |
| [`download-problem-self-service`](./templates/a4-support/download-problem-self-service/) | A4 · Support | The one message that dominates a digital seller's inbox |
| [`cart-abandonment-recovery`](./templates/a5-marketing-revenue/cart-abandonment-recovery/) | A5 · Revenue 💰 | Interrupted checkouts, without training buyers to expect a coupon |
| [`post-purchase-sequence`](./templates/a5-marketing-revenue/post-purchase-sequence/) | A5 · Revenue | No reviews and no repeat buyers — same cause, same fix |
| [`ai-product-translation`](./templates/a6-content-localization/ai-product-translation/) | A6 · Content 🤖 | Translations going stale; prices and formatting destroyed by AI |
| [`ai-sales-page-writer`](./templates/a6-content-localization/ai-sales-page-writer/) | A6 · Content 🤖 | AI sales copy that invents guarantees you'll be held to |
| [`sales-anomaly-detection`](./templates/a7-analytics/sales-anomaly-detection/) | A7 · Analytics | "Revenue is down" — but is demand down, or is checkout broken? |
| [`commission-affiliate-payouts`](./templates/a8-marketplace-ops/commission-affiliate-payouts/) | A8 · Marketplace | Commission in a spreadsheet until the first dispute |
| [`ai-customer-support-agent`](./templates/b1-ai-agents/ai-customer-support-agent/) | B1 · AI Agent 🤖 | AI support that invents policies — this one refuses instead |
| [`ai-lead-qualifier`](./templates/b1-ai-agents/ai-lead-qualifier/) | B1 · AI Agent 🤖 | Buyers waiting behind tyre-kickers in an arrival-order inbox |
| [`sales-pipeline-followup`](./templates/b3-sales-crm/sales-pipeline-followup/) | B3 · CRM | Deals lost to silence rather than to competitors |
| [`failed-payment-recovery`](./templates/b4-saas-subscriptions/failed-payment-recovery/) | B4 · SaaS 💰 | Subscriptions lost silently to an expired card |
| [`cv-screening-triage`](./templates/b5-recruitment/cv-screening-triage/) | B5 · Hiring 🤖 | 200 applications and nobody to read them |
| [`delivery-test-runner`](./templates/z-tools/delivery-test-runner/) | Tool | Testing a webhook template with no terminal (works from a phone) |

---

## How they connect

**One URL contract, four templates.** `instant-digital-delivery` mints a signed
link, `download-problem-self-service` reissues one,
`product-update-broadcast` sends a fresh one, and `secure-download-endpoint`
verifies all three. They share a secret and a payload field order, and tests
assert they still agree — nothing else would catch them drifting apart.

**Screening, then defence.** `pre-payment-fraud-scoring` stops fraud before
delivery; `chargeback-early-warning` handles what gets through and tracks the
ratio that closes payment accounts; `leak-detection-watermarking` reads the
download counters the endpoint already writes, so that layer costs nothing extra.

**Two templates sell themselves** 💰 because the buyer does the arithmetic:
recovering one $50 subscription or one $49 cart pays for the template, and it
keeps working every month.

---

## Where the AI templates draw their lines

Four templates use a model. Each runs a **deterministic layer before any model
call** — cheaper, and an obviously-sensitive support request or an obviously
qualified lead never depends on a model being up.

They also score in deliberately opposite directions:

- **Support agent** — defensive. It must not invent a refund policy, so it
  refuses when unsure. Refunds, disputes, legal demands and angry messages never
  reach the model at all.
- **Lead qualifier** — inclusive. A false positive costs minutes; a false
  negative costs a deal. The lowest tier goes to nurture, never the bin.
- **CV screening** — ranks and **never rejects**, with no setting to enable it.
  A wrong score here filters a person out of a job, so the model is instructed
  to ignore names, photos, age, gender and nationality, and every score carries
  its reasoning so a human can overrule it.
- **Sales page writer** — refuses to write marketing prose, then a deterministic
  pass scans its own output for unsupported claims.

And `download-problem-self-service` uses **no AI at all**, deliberately. It
performs a transaction, not a judgement.

---

## Before selling: verify by hand

Three automated gates prove a template is well-formed, secret-free, correctly
wired, and behaves correctly under adversarial input. **They cannot prove your
Stripe key works or your SMTP sends.**

The delivery template and test runner have been imported into a live n8n Cloud
instance and rendered correctly, and an SMTP credential was connected end to end
— so the format is confirmed against the real product. A full live send remains
unverified. The protocol is in
[`docs/04-verification.md`](./docs/04-verification.md).

---

## Documentation

| Doc | Contents |
| --- | --- |
| [`01-market-research.md`](./docs/01-market-research.md) | The evidence: failure rates, the confirmed fraud-template gap, real pricing |
| [`02-catalogue-and-pricing.md`](./docs/02-catalogue-and-pricing.md) | Per-category counts, phases, pricing rationale, and why not 1000 |
| [`03-hardening-standard.md`](./docs/03-hardening-standard.md) | Every rule, mapped to the check that enforces it |
| [`04-verification.md`](./docs/04-verification.md) | The manual test protocol, and what is genuinely unverified |
| [`05-accounts-to-open.md`](./docs/05-accounts-to-open.md) | Which accounts to create, in order, and what each costs |
| [`06-listing-and-sales.md`](./docs/06-listing-and-sales.md) | How buyers evaluate a listing, and what actually converts |
