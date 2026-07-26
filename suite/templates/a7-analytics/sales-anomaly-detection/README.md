# DCA-A7-01 · Sales Anomaly Detection (is demand down, or is something broken?)

> Watches order volume against the same weekday in recent weeks, and when it drops tells you whether demand fell or something in your pipeline broke — which need opposite responses.

**Category:** `a7-analytics` · **Version:** `1.0.0` · **Nodes:** 13 · **Setup:** ~10 min

---

## The problem

Revenue falls and the seller finds out late, then cannot tell whether demand dropped or checkout broke. People spend a week optimising ads while their delivery webhook has been dead the whole time.

## What you get

Meaningful drops are detected against weekday-aware history, and every alert says which of the two causes it is, with the evidence that led to that conclusion.

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

- SMTP account (or Slack/Telegram)

---

## Nodes

| Node | Type | Purpose |
| --- | --- | --- |
| `🛒 Order happened` | `webhook` | POST {orderId, amount, currency?, status?} for every order. Also accepts {event:'checkout_started'}. |
| `⚙️ Config` | `code` | dropThreshold 0.5 = alert when today is 50% below the weekday baseline. Raise it if you get noise. |
| `🛡️ Guard · validate + dedupe` | `code` | Validates required fields and drops duplicate deliveries. Safe to re-run. |
| `📝 Record the event` | `code` | Tracks orders and checkout starts separately — the gap between them is the diagnostic signal. |
| `↩️ 200 OK` | `respondToWebhook` | Answer fast so the provider does not retry on timeout. |
| `🕓 Check every 4 hours` | `scheduleTrigger` | — |
| `⚙️ Config (analysis side)` | `code` | ⚠️ Mirror of the main Config. Change one, change both. |
| `🔬 Compare against the weekday baseline` | `code` | Weekday-aware baseline, day-fraction adjusted, then diagnoses demand vs breakage. |
| `🔔 Alert?` | `if` | — |
| `✍️ Write the alert` | `code` | Leads with the diagnosis and a concrete checklist, not with a percentage. |
| `📨 Send the alert` | `emailSend` | Attach SMTP. Swap for Slack/Telegram for faster response. |
| `🤫 Nothing to report` | `code` | Quiet outcomes are still logged, so you can tell 'all fine' from 'not running'. |
| `📒 Anomaly log` | `code` | Append to a Sheet. Reviewing past diagnoses tells you whether the thresholds are right. |

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
