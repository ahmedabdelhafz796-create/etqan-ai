# DCA-A3-02 · Chargeback Early Warning & Evidence Builder

> Catches fraud alerts before they become formal disputes, recommends refund-or-fight with reasoning, assembles the evidence pack automatically, and tracks the chargeback ratio that gets payment accounts closed.

**Category:** `a3-fraud-security` · **Version:** `1.0.0` · **Nodes:** 11 · **Setup:** ~15 min

---

## The problem

Most disputes are lost by default rather than argued — the response deadline passes during a busy week. And for digital goods the evidence needed to win has usually expired by the time anyone looks for it.

## What you get

Every alert produces a deadline, a recommendation with reasoning, and a ready-to-submit evidence pack — plus a running chargeback ratio so you see the account-closing risk coming.

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

- SMTP or Slack for alerts
- Optional: your order log for evidence lookup

---

## Nodes

| Node | Type | Purpose |
| --- | --- | --- |
| `⚠️ Fraud alert / dispute` | `webhook` | Point your gateway's fraud-warning and dispute webhooks here. |
| `⚙️ Config` | `code` | monthlyOrderCount drives the ratio. ratioWarnAt 0.005 = 0.5%, half the danger line. |
| `🛡️ Guard · validate + dedupe` | `code` | Validates required fields and drops duplicate deliveries. Safe to re-run. |
| `🔄 Normalise the alert` | `code` | Separates early warnings from formal disputes — that distinction drives everything downstream. |
| `📈 Track the chargeback ratio` | `code` | Early warnings are excluded from the ratio on purpose — acting on them is how you keep them out. |
| `📁 Build evidence pack` | `code` | Recommendation carries its reasoning. Evidence fields are labelled, never invented. |
| `✍️ Compose the alert` | `code` | A single actionable message: what, deadline, recommendation, ratio, evidence. |
| `📨 Send the alert` | `emailSend` | Attach SMTP. Swap for Slack/Telegram if you prefer. |
| `📒 Dispute log` | `code` | Append to Sheets/Airtable. This log is worth keeping. |
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
