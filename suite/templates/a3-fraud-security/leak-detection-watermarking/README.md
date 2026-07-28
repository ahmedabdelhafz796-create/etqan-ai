# DCA-A3-03 · Leak Detection & Buyer Watermarking

> Stamps every copy with a buyer-specific marker, detects sharing patterns from download behaviour, traces a leaked file back to the account that leaked it, and drafts the takedown notice.

**Category:** `a3-fraud-security` · **Version:** `1.0.0` · **Nodes:** 16 · **Setup:** ~14 min

---

## The problem

A file is bought once and shared, resold, or posted to a channel with ten thousand members — and the seller has no way to tell whose copy it was or what to do about it.

## What you get

Every copy is attributable, sharing patterns surface automatically from data you already collect, and a confirmed leak produces a named account plus a ready-to-send DMCA notice.

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
| `🔖 Stamp / trace / takedown` | `webhook` | POST {action: 'stamp'|'trace'|'takedown', ...}. One endpoint, three jobs. |
| `⚙️ Config` | `code` | markerSalt must be long, random and never change — old markers stop resolving if it does. |
| `🛡️ Guard · validate + dedupe` | `code` | Validates required fields and drops duplicate deliveries. Safe to re-run. |
| `🔀 Which job?` | `switch` | Output 0 = stamp · 1 = trace · 2 = takedown. |
| `🔖 Create the buyer marker` | `code` | Returns visible + invisible marks and ready-made metadata fields. Apply both. |
| `🔎 Trace a found marker` | `code` | Resolves a marker to the buyer. Includes what to do next, since most sellers have never done this. |
| `⚖️ Draft the takedown notice` | `code` | Standard DMCA structure, pre-filled. Explicitly not legal advice — review before sending. |
| `🕐 Scan download patterns daily` | `scheduleTrigger` | — |
| `⚙️ Config (detection side)` | `code` | ⚠️ Mirror of the main Config. Change one, change both. |
| `📊 Find sharing patterns` | `code` | Reads A1-02's download counters. Zero extra collection cost. |
| `🚩 Anything found?` | `if` | — |
| `✍️ Write the leak alert` | `code` | States plainly that the signal is worth investigating, not proof. |
| `📨 Send the leak alert` | `emailSend` | Attach SMTP. |
| `✅ Nothing unusual` | `code` | Logged so you can tell 'all clear' from 'not running'. |
| `📒 Leak log` | `code` | Append to a Sheet. Repeat offenders show up here. |
| `↩️ Return result` | `respondToWebhook` | Answer fast so the provider does not retry on timeout. |

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
