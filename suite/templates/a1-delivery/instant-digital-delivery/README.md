# DCA-A1-01 · Instant Digital Delivery (Stripe / PayPal / Lemon Squeezy / Gumroad / Paddle / NOWPayments)

> One endpoint that turns a confirmed payment from any major gateway into a signed, expiring download link in the buyer's inbox.

**Category:** `a1-delivery` · **Version:** `1.0.0` · **Nodes:** 15 · **Setup:** ~12 min

---

## The problem

Buyers pay and the product never arrives, because delivery automations have no verification, no retry and no failure alarm.

## What you get

Every paid order is verified, de-duplicated, delivered and logged — and any delivery that fails raises an alert with enough detail to recover it by hand.

---

## Install

1. In n8n choose **Workflows → Import from File** and pick `workflow.json`.
2. Open the **⚙️ Config** node and fill in your values. This is the only node
   you are required to edit.
3. Attach credentials where the canvas notes ask for them. Nothing is
   pre-filled — this file ships with no keys in it, by design.
4. Run once with the manual trigger (or with `testMode: true`) and confirm the
   output looks right.
5. Activate.

### Credentials required

- SMTP account (or your email API of choice)
- Your payment provider's webhook signing secret

---

## Nodes

| Node | Type | Purpose |
| --- | --- | --- |
| `💳 Payment webhook` | `webhook` | Raw body is kept on purpose — signatures must be computed over the exact bytes received. |
| `⚙️ Config` | `code` | The only node you must edit. Secrets go in Credentials / the Crypto nodes, never here. |
| `🔏 Verify signature` | `crypto` | Replace the Secret with your gateway's webhook signing secret. Stripe: whsec_… · Lemon Squeezy: your signing secret · Paddle: your notification key. |
| `🔒 Reject forged calls` | `code` | Set testMode:true in Config to bypass while testing. Never leave it on in production. |
| `🛡️ Guard · validate + dedupe` | `code` | Validates required fields and drops duplicate deliveries. Safe to re-run. |
| `🔄 Normalise to one order shape` | `code` | Translates six gateway formats into one canonical order object. |
| `✅ Is the money really in?` | `if` | — |
| `⏸️ Hold — not payable yet` | `code` | Non-paid events end here safely. This is the branch that prevents free-product leakage. |
| `🧮 Sanity-check the amount` | `code` | Blocks under-paid and wrong-currency orders before anything is handed over. |
| `✍️ Sign download link` | `crypto` | Invent a long random string and use the SAME one in your download endpoint (and in DCA-A1-02). |
| `🔗 Build the delivery link` | `code` | Produces the final signed URL plus a human-readable expiry for the email. |
| `📧 Send the product` | `emailSend` | Attach your SMTP credential. Retries 3×; a final failure leaves via the red output and raises an alert. |
| `🧾 Record the order` | `code` | Append this to your order log. Keep it — it is your chargeback evidence. |
| `🚨 Handle failure` | `code` | Structured failure record. Wire to your alert channel. |
| `↩️ 200 OK` | `respondToWebhook` | Answer fast so the provider does not retry on timeout. |

---

## Reliability guarantees

This template is built through the suite's hardened core, so it ships with:

- **Replay protection** — duplicate webhook deliveries produce no duplicate side effects.
- **Input validation** — malformed payloads fail loudly at the entry point instead of corrupting data downstream.
- **Retry with backoff** — every outbound call retries 3× before giving up.
- **A wired failure path** — failures produce a structured alert, never silence.
- **No embedded credentials** — verified automatically before release.
- **On-canvas documentation** — every section is explained where you are working.

See [`../../../docs/03-hardening-standard.md`](../../../docs/03-hardening-standard.md) for the full standard and the checks that enforce it.

---

## Support

Something not working? Include your n8n version, the failing node's name and the
execution error, and it can usually be resolved in one reply.
