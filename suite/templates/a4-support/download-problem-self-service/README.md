# DCA-A4-01 · Download Problem Self-Service (reissue access without a human)

> Handles the one message that dominates a digital seller's inbox — 'I can't get my file' — by verifying entitlement and reissuing a fresh signed link automatically, with rate limits and human escalation for anything unusual.

**Category:** `a4-support` · **Version:** `1.0.0` · **Nodes:** 13 · **Setup:** ~12 min

---

## The problem

Most digital-product support is a single problem in different clothes: expired link, lost email, download cap reached. The buyer is entitled to the file and simply cannot reach it, yet each case costs the seller a lookup, a decision and a reply.

## What you get

Entitled buyers get a fresh link in seconds without anyone being involved; abuse is rate-limited; and anything unusual reaches a human rather than failing silently.

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

- SMTP account

---

## Nodes

| Node | Type | Purpose |
| --- | --- | --- |
| `🆘 Download help request` | `webhook` | POST {email, orderId?}. Link this form from your delivery emails. |
| `⚙️ Config` | `code` | knownOrders maps email → {orderId, productId}. Seed it, or wire the verify node to your real order store. |
| `🛡️ Guard · validate + dedupe` | `code` | Validates required fields and drops duplicate deliveries. Safe to re-run. |
| `🔎 Verify entitlement` | `code` | Entitlement + rate limit. Replace the lookup with your real order store; keep the return shape. |
| `✅ Entitled?` | `if` | — |
| `🔑 Sign the new link` | `crypto` | ⚠️ Must be the SAME secret used in A1-01 and A1-02, or the link will not verify. |
| `🔗 Build the fresh link` | `code` | Same URL contract as A1-01 — verified by a cross-template test. |
| `📧 Send the fresh link` | `emailSend` | Sent to the address on the ORDER, not one supplied in the request. |
| `🙋 Escalate to a human` | `code` | Explains what happened and what it usually means — not just a bare handoff. |
| `📨 Tell the human` | `emailSend` | Swap for Slack/Telegram if you prefer. |
| `📒 Deflection log` | `code` | Track the auto-resolved vs escalated ratio. That ratio is the template's value. |
| `🚨 Handle failure` | `code` | Structured failure record. Wire to your alert channel. |
| `↩️ Confirm to the buyer` | `respondToWebhook` | Answer fast so the provider does not retry on timeout. |

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
