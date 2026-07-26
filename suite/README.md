# Digital Commerce Automation Suite

Production-hardened n8n templates for people who sell digital products.

**Status:** Phase 1 in progress — 3 of 68 templates built and passing the gate.

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

## How reliability is guaranteed

Every template is generated through one library and must pass one automated
gate. Guarantees are **structural**, not the result of author discipline:

| Guarantee | Enforced by |
| --- | --- |
| Duplicate webhooks cause no duplicate side effects | `guard()` — event-id dedupe in static data, TTL-pruned, no database |
| Malformed payloads fail loudly at the door | `guard()` — required-field assertion naming what was missing |
| Every network call retries 3× with backoff | validator, **default-deny** across all non-local node types |
| Failures are routed, never silent | validator checks the error output is actually *wired* |
| One obvious place to configure | `config()` — single node, secrets excluded by design |
| Zero credentials in shipped files | validator secret-scan + author-credential-id rejection |
| Docs where you are working | sticky notes + per-node notes, coverage enforced |
| Same behaviour on Cloud and self-hosted | HMAC via Crypto node, never `require('crypto')` |

The standard is in [`docs/03-hardening-standard.md`](./docs/03-hardening-standard.md)
and its executable form is [`factory/lib/validate.py`](./factory/lib/validate.py).
They cannot drift: `build.py` refuses to write any template with an error.

### The gate is itself tested

```bash
python3 factory/test_gate.py     # 12/12 probes
```

This injects real defects into a good template and asserts each is caught. It
exists because the first retry rule enumerated node types and missed
`emailSend` — the most failure-prone node in the delivery template. The rule is
now default-deny, and this test keeps it that way.

---

## Built so far

| Template | Category | Solves |
| --- | --- | --- |
| [`instant-digital-delivery`](./templates/a1-delivery/instant-digital-delivery/) | A1 · Delivery | "Paid and never received it" — 6 gateways → one order shape → signed link |
| [`secure-download-endpoint`](./templates/a1-delivery/secure-download-endpoint/) | A1 · Delivery | Expired/leaked links, and refusals that explain themselves |
| [`pre-payment-fraud-scoring`](./templates/a3-fraud-security/pre-payment-fraud-scoring/) | A3 · Fraud 🎯 | Fraud caught **before** delivery — no paid API |

`instant-digital-delivery` and `secure-download-endpoint` are a matched pair:
one mints the signed link, the other verifies it. Same secret, same payload
order.

### Why fraud scoring is the flagship

Research confirmed the gap: the market has dispute *notification* and *tracking*
workflows, but **nothing that scores an order before the product is handed
over**. For digital goods that gap is expensive — delivery is instant, copies
are free, so a fraudulent order is a total loss that also drags the seller
toward the chargeback ratios that freeze payment accounts.

Commercial fraud APIs need an account, a key and a per-check fee, which is
exactly why sellers of $49 products screen nothing. Every signal here is
computed locally. Every point carries its reason, so thresholds are tunable.
It ships in shadow mode so a seller measures before enforcing.

---

## Usage

```bash
cd factory
python3 build.py            # build all, validate, write only what passes
python3 build.py --check    # validate without writing (CI)
python3 build.py a1_01      # single template
python3 test_gate.py        # prove the gate still rejects bad input
```

Templates land in `templates/<category>/<slug>/` with `workflow.json` and a
generated `README.md`. The README is built from the same metadata as the
workflow, so it cannot go stale.

---

## Before selling: verify by hand

Automated checks prove a template is well-formed, secret-free and correctly
wired. **They cannot prove your Stripe key works or your SMTP sends.**

That step needs a real n8n account, and it is the step that will put these above
the 70% that fail at install. The exact protocol — including how to test
delivery, replay protection and fraud scoring without any real payment — is in
[`docs/04-verification.md`](./docs/04-verification.md).

---

## Roadmap

| Phase | Templates | Bundle |
| --- | --- | --- |
| 1 · Launch | 14 | $149 |
| 2 · Expand | 40 | $249 |
| 3 · Full suite | 68 | $449 |

Catalogue, per-category counts, pricing rationale and why **68 rather than
1000**: [`docs/02-catalogue-and-pricing.md`](./docs/02-catalogue-and-pricing.md).
