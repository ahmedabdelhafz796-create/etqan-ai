# DCA-A8-01 · Commission & Affiliate Payouts

> Tracks what each affiliate or vendor has earned, reverses commission on refunds, preserves the rate that applied at the time of sale, and produces a deduplicated payout instruction you execute yourself.

**Category:** `a8-marketplace-ops` · **Version:** `1.0.0` · **Nodes:** 13 · **Setup:** ~16 min

---

## The problem

Commission lives in a spreadsheet until the first dispute, at which point nobody can say which sales counted, what the rate was then, whether refunds were clawed back, or whether last month was already paid.

## What you get

Every sale attributed and rated at the moment it happened, refunds reversed automatically, payouts deduplicated and thresholded — with a full audit trail behind every figure.

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
| `🛒 Sale or refund` | `webhook` | POST {orderId, partnerId, amount} for sales, or {event:'refund', orderId} for reversals. |
| `⚙️ Config` | `code` | holdDays delays payout until the refund window has passed — pay too early and you claw back later. |
| `🛡️ Guard · validate + dedupe` | `code` | Validates required fields and drops duplicate deliveries. Safe to re-run. |
| `📒 Record the earning or reversal` | `code` | Append-only. Reversals are new negative records, never edits — that is what makes disputes answerable. |
| `↩️ 200 OK` | `respondToWebhook` | Answer fast so the provider does not retry on timeout. |
| `🕐 Payout run` | `scheduleTrigger` | — |
| `⚙️ Config (payout side)` | `code` | ⚠️ Mirror of the main Config. Change one, change both. |
| `🧮 Calculate what is owed` | `code` | Only unpaid, matured records count. Everything paid is stamped with the batch id, so re-runs are safe. |
| `💰 Anything to pay?` | `if` | — |
| `📄 Build the payout instruction` | `code` | Unambiguous enough to act on without opening anything else. |
| `📨 Send the instruction` | `emailSend` | Goes to you, not to partners. You execute the payments. |
| `🤫 Nothing due` | `code` | An empty run is logged, so you can tell 'nothing owed' from 'not running'. |
| `📒 Payout log` | `code` | ⚠️ Wire to a Sheet. This is the document that settles disputes. |

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
