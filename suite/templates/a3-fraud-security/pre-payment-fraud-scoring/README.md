# DCA-A3-01 · Pre-Payment Fraud Scoring (no external API required)

> Scores every order for fraud risk before delivery using local signals only — disposable domains, velocity, geo mismatch, amount anomalies — and routes it to allow, review or block.

**Category:** `a3-fraud-security` · **Version:** `1.0.0` · **Nodes:** 11 · **Setup:** ~10 min

---

## The problem

Digital goods are delivered instantly and cost nothing to copy, so a fraudulent order is a total loss — and the resulting chargebacks push the seller toward the ratios that get payment accounts frozen. Existing templates only react after a dispute is already open.

## What you get

Risky orders are held for review before the file is handed over, with a transparent score and a written reason for every decision — and it runs without a paid fraud API.

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

- None required for scoring
- Optional: Slack/Telegram/email for review alerts

---

## Nodes

| Node | Type | Purpose |
| --- | --- | --- |
| `🛒 Order created` | `webhook` | Point your checkout / payment-intent webhook here. Runs before delivery. |
| `⚙️ Config` | `code` | Start with shadowMode:true. Tune reviewAt/blockAt on a week of your own traffic before enforcing. |
| `🛡️ Guard · validate + dedupe` | `code` | Validates required fields and drops duplicate deliveries. Safe to re-run. |
| `📥 Extract order signals` | `code` | Normalises checkout payloads. Missing fields simply score as unknown rather than crashing. |
| `🧮 Score the risk` | `code` | All scoring happens here, locally. Every point carries its reason so you can tune it. |
| `🔀 Route the decision` | `switch` | Output 0 = allow · 1 = review · 2 = block. Unknown decisions fall back to allow. |
| `✅ Allow → deliver` | `code` | Wire to your delivery workflow. |
| `🔍 Review → alert a human` | `code` | Send alertText to Slack/Telegram/email. Review this queue daily — it is where the value is. |
| `⛔ Block → do not deliver` | `code` | Nothing is delivered on this branch. Add false positives to trustedEmails in Config. |
| `📒 Audit log` | `code` | Append to Sheets/Airtable/DB. Review weekly and re-tune thresholds. |
| `↩️ Return decision` | `respondToWebhook` | Answer fast so the provider does not retry on timeout. |

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
