# DCA-A5-02 · Post-Purchase Sequence & Review Collection

> Runs a timed post-purchase sequence that helps first and asks second, checks privately whether the buyer is happy before requesting a public review, and only mentions an upsell once the refund window has closed.

**Category:** `a5-marketing-revenue` · **Version:** `1.0.0` · **Nodes:** 14 · **Setup:** ~12 min

---

## The problem

The days after a purchase are the only time a buyer is reliably paying attention, and almost every seller spends them in silence — then wonders why they have no reviews and no repeat customers.

## What you get

Fewer support tickets, more reviews from buyers who actually got value, and unhappy customers reaching you privately instead of a review page.

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
| `🎉 Order completed` | `webhook` | POST {orderId, email, name, productName}. Chain from A1-01 after delivery. |
| `⚙️ Config` | `code` | upsellAfterDays must exceed your refund window. usageTip should be genuinely useful — filler here undoes the whole sequence. |
| `🛡️ Guard · validate + dedupe` | `code` | Validates required fields and drops duplicate deliveries. Safe to re-run. |
| `📝 Enrol the buyer` | `code` | Honours unsubscribes permanently, including for future orders. |
| `↩️ 200 OK` | `respondToWebhook` | Answer fast so the provider does not retry on timeout. |
| `🕐 Advance sequences` | `scheduleTrigger` | — |
| `⚙️ Config (sequence side)` | `code` | ⚠️ Mirror of the main Config. Change one, change both. |
| `⏭️ Find who is due a message` | `code` | One stage per run maximum. The upsell stage only exists when enabled. |
| `✉️ A message to send?` | `if` | — |
| `✍️ Compose for this stage` | `code` | Four short messages. The check-in asks privately before asking publicly. |
| `📧 Send it` | `emailSend` | Attach SMTP. Batched upstream to protect sending reputation. |
| `📊 Sequence summary` | `code` | Optional. Wire to a Sheet if you want a record. |
| `🚨 Handle failure` | `code` | Structured failure record. Wire to your alert channel. |
| `📒 Sequence log` | `code` | Track which stage people reach. A drop-off at one stage means that message needs rewriting. |

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
