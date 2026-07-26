# DCA-A2-02 · Automatic Invoice & VAT Record

> Issues a correctly numbered, sequential invoice for every paid order, applies the tax rates you configure, captures the evidence tax authorities ask for, and emails the buyer their receipt.

**Category:** `a2-payments-finance` · **Version:** `1.0.0` · **Nodes:** 10 · **Setup:** ~15 min

---

## The problem

Invoicing is manual, numbering goes wrong under replays and concurrent orders, and cross-border digital sales are taxed where the buyer is — which solo sellers usually discover long after it is cheap to fix.

## What you get

Every paid order produces a gap-free sequential invoice with buyer location evidence attached, sent automatically, ready for an accountant.

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
| `💰 Payment succeeded` | `webhook` | Same event as A1-01. Both can run from one gateway webhook. |
| `⚙️ Config` | `code` | taxRates: only the jurisdictions you are actually registered in. Ask an accountant once, then fill this. |
| `🛡️ Guard · validate + dedupe` | `code` | Validates required fields and drops duplicate deliveries. Safe to re-run. |
| `📥 Read the order` | `code` | Same order shape as A1-01, but independent so this works standalone. |
| `🔢 Assign invoice number` | `code` | Gap-free and replay-safe. On queue mode with multiple workers, move the counter to a database. |
| `🧮 Apply tax and build the invoice` | `code` | Applies YOUR configured rates and flags anything a human should look at. Does not determine liability. |
| `📧 Email the invoice` | `emailSend` | Attach SMTP. The buyer receives a proper itemised invoice. |
| `📒 Invoice ledger` | `code` | ⚠️ Wire this to a Sheet or database. Static data is not a permanent financial record. |
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
