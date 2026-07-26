# DCA-B3-01 · Sales Pipeline & Follow-Up Engine

> Tracks open deals, measures how long each has been silent, and sends one daily digest of who needs chasing — prioritised by value, with a draft for each, so nothing is lost to forgetfulness.

**Category:** `b3-sales-crm` · **Version:** `1.0.0` · **Nodes:** 13 · **Setup:** ~12 min

---

## The problem

Deals are rarely lost to competitors; they are lost to silence. The seller means to follow up, the intention decays, and nothing in their day forces the issue. CRMs make this worse by requiring faithful logging that always slips.

## What you get

One daily digest naming every deal going cold, ordered by what it is worth, with a written draft for each — and nothing is ever sent to a prospect automatically.

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
| `📇 Deal event` | `webhook` | POST a new deal, or {dealId, event:'contacted'|'won'|'lost'}. |
| `⚙️ Config` | `code` | staleDays is the baseline. High-value deals are chased at half that, low-value at double. |
| `🛡️ Guard · validate + dedupe` | `code` | Validates required fields and drops duplicate deliveries. Safe to re-run. |
| `📝 Track the deal` | `code` | Contact events move the clock only — a quick touch cannot wipe the deal's details. |
| `↩️ 200 OK` | `respondToWebhook` | Answer fast so the provider does not retry on timeout. |
| `🕘 Daily digest` | `scheduleTrigger` | — |
| `⚙️ Config (digest side)` | `code` | ⚠️ Mirror of the main Config. Change one, change both. |
| `🔍 Find deals going cold` | `code` | Value-aware thresholds, sorted by what each deal is worth. Abandoned deals drop out. |
| `📋 Anything to chase?` | `if` | — |
| `✍️ Write the digest` | `code` | Short, specific drafts. Long generic ones get rewritten anyway. |
| `📨 Send the digest` | `emailSend` | Goes to you, never to the prospect. |
| `✅ Pipeline is current` | `code` | Distinguishes 'all current' from 'not running'. |
| `📒 Pipeline log` | `code` | Append to a Sheet. Growth vs aging only shows up over weeks. |

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
