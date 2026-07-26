# DCA-A1-04 · Product Update Broadcast (tell past buyers, safely)

> Notifies past buyers of a product update with a freshly signed download link, filtered to actual buyers of that product, deduplicated per version, batched to protect sending reputation, and silent for trivial changes.

**Category:** `a1-delivery` · **Version:** `1.0.0` · **Nodes:** 12 · **Setup:** ~14 min

---

## The problem

Updating a product means past buyers hold an outdated file and a dead link. Sending manually is error-prone: the whole list gets mailed for a typo, people who bought something else get mailed, and a re-run mails everyone twice.

## What you get

The right buyers hear about meaningful updates exactly once, with a working link — turning maintenance into the cheapest repeat-purchase driver a digital seller has.

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
| `🆕 Update shipped` | `webhook` | POST {productId, version, significance, changes[]} when you ship an update. |
| `⚙️ Config` | `code` | buyers maps productId → [{email, orderId, name}]. Seed it or wire the recipient node to your order store. |
| `🛡️ Guard · validate + dedupe` | `code` | Validates required fields and drops duplicate deliveries. Safe to re-run. |
| `📋 Decide who to tell` | `code` | Filters to real buyers, skips anyone already told, batches, and stays silent on patches. |
| `📤 Anyone to tell?` | `if` | — |
| `✍️ Sign fresh links` | `crypto` | ⚠️ Must be the SAME secret as A1-01, A1-02 and A4-01. |
| `✍️ Compose the announcement` | `code` | Every recipient gets a freshly signed link, not the dead one from their purchase. |
| `📧 Send the announcement` | `emailSend` | Attach SMTP. Batched upstream to protect your sending reputation. |
| `⏭️ Nothing sent` | `code` | A re-run lands here and does nothing, which is correct. |
| `🚨 Handle failure` | `code` | Structured failure record. Wire to your alert channel. |
| `📒 Broadcast log` | `code` | `remaining` tells you whether to call again for the next batch. |
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
