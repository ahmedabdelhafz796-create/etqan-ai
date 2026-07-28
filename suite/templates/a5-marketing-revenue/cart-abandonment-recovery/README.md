# DCA-A5-01 · Cart Abandonment Recovery

> Recovers interrupted checkouts with a timed two-message sequence that stops the moment the buyer purchases, and keeps discounting off by default so you stop paying for sales you would have made anyway.

**Category:** `a5-marketing-revenue` · **Version:** `1.0.0` · **Nodes:** 13 · **Setup:** ~12 min

---

## The problem

Most abandoned carts are interruptions, not rejections — a closed tab, a phone call. The intent was real and often still is an hour later, but nobody follows up, so the sale is simply lost.

## What you get

Every abandoned cart triggers a controlled recovery sequence, capped at two messages, that stops instantly on purchase and reports what it recovered.

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
| `🛒 Cart event` | `webhook` | Accepts abandonment events and {"event":"purchased"} to stop a sequence. |
| `⚙️ Config` | `code` | enableDiscount is false on purpose. Read the green note before turning it on. |
| `🛡️ Guard · validate + dedupe` | `code` | Validates required fields and drops duplicate deliveries. Safe to re-run. |
| `📝 Track the cart` | `code` | Opens/updates a cart, or closes it on purchase. Adding items never restarts the clock. |
| `↩️ 200 OK` | `respondToWebhook` | Answer fast so the provider does not retry on timeout. |
| `🕐 Check carts every 30 min` | `scheduleTrigger` | — |
| `⚙️ Config (schedule side)` | `code` | ⚠️ Mirror of the main Config. Change one, change both. |
| `🔍 Find carts due a reminder` | `code` | Two messages then the cart is retired. The cap is enforced here. |
| `👤 A cart to chase?` | `if` | — |
| `✍️ Compose the reminder` | `code` | Discount block only renders when enableDiscount is true AND it is the final message. |
| `📧 Send the reminder` | `emailSend` | Attach your SMTP credential. |
| `📈 Recovery summary` | `code` | Optional. Wire to Slack/Sheets if you want a running record. |
| `🚨 Handle failure` | `code` | Structured failure record. Wire to your alert channel. |

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
