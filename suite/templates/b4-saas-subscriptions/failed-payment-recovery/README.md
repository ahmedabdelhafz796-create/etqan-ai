# DCA-B4-02 · Failed Payment Recovery (dunning sequence)

> Catches failed subscription payments the moment they happen and runs a timed, escalating recovery sequence until the customer updates their card or the sequence ends.

**Category:** `b4-saas-subscriptions` · **Version:** `1.0.0` · **Nodes:** 18 · **Setup:** ~12 min

---

## The problem

A renewal fails silently. The customer does not notice, the seller does not notice, and a month later the subscription is simply gone — lost to payment mechanics rather than dissatisfaction.

## What you get

Every failed payment starts a recovery sequence within minutes, escalates on a schedule you control, stops the moment the payment succeeds, and reports exactly how much revenue it recovered.

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
- Optional: Slack/Telegram for the recovery report

---

## Nodes

| Node | Type | Purpose |
| --- | --- | --- |
| `🔔 Payment failed` | `webhook` | Point your gateway's payment-failed webhook here. Also accepts {"event":"recovered"} to stop a sequence. |
| `⚙️ Config` | `code` | followUpDays controls the sequence. pauseAfterDays is when you stop chasing. |
| `🛡️ Guard · validate + dedupe` | `code` | Validates required fields and drops duplicate deliveries. Safe to re-run. |
| `📝 Open or close a recovery case` | `code` | Opens a case on failure, closes it on recovery, and refuses to restart a sequence that is already running. |
| `📨 First contact needed?` | `if` | — |
| `✍️ Compose first notice` | `code` | Friendly, one clear action. No alarm language on day one. |
| `📧 Send first notice` | `emailSend` | Attach your SMTP credential. |
| `⏭️ Nothing to send` | `code` | Closed or duplicate cases end here. |
| `↩️ 200 OK` | `respondToWebhook` | Answer fast so the provider does not retry on timeout. |
| `🚨 Handle failure` | `code` | Structured failure record. Wire to your alert channel. |
| `🕐 Daily follow-up run` | `scheduleTrigger` | — |
| `⚙️ Config (schedule side)` | `code` | ⚠️ Mirror of the main Config. If you change one, change both. |
| `🔍 Find cases due for follow-up` | `code` | Decides who is due, advances their stage, and stops chasing past pauseAfterDays. |
| `👤 A customer to contact?` | `if` | — |
| `✍️ Compose follow-up` | `code` | Escalates in clarity, not in tone. |
| `📧 Send follow-up` | `emailSend` | Attach the same SMTP credential. |
| `📈 Recovery report` | `code` | Wire to Slack/Telegram/email. This is the number that justifies the template. |
| `🚨 Handle follow-up failure` | `code` | Structured failure record. Wire to your alert channel. |

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
