# DCA-SYS-00 · Central Error Hub (every failure, one place, in plain language)

> Receives failures from every template in the suite, ranks them by business impact, suppresses repeat storms, and explains each one in language a seller can act on.

**Category:** `sys-spine` · **Version:** `1.0.0` · **Nodes:** 9 · **Setup:** ~8 min

---

## The problem

Seven templates each logging failures to their own execution history is still seven places to look — so nobody looks, and silent failure returns through the back door.

## What you get

One workflow watches everything. Revenue-affecting failures alert immediately with a plain-language fix; noise is counted and summarised instead of drowning the signal.

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
| `🚨 Any workflow failed` | `errorTrigger` | Fires when any workflow that names this one as its Error Workflow fails. |
| `⚙️ Config` | `code` | Set alertEmail and you are done. The template lists control severity ranking. |
| `🎚️ Rank by business impact` | `code` | Severity reflects what it costs, not what it looks like in a stack trace. |
| `🌊 Suppress repeat storms` | `code` | First occurrence alerts; repeats inside the window are counted silently. |
| `🔎 Explain the failure` | `code` | Plain-language cause and fix. Extend PATTERNS as you learn your own recurring errors. |
| `🔔 Alert or just record?` | `code` | Applies the alertOnLow preference on top of storm suppression. |
| `📣 Send it?` | `if` | — |
| `📨 Send alert` | `emailSend` | Attach SMTP. Swap for Slack/Telegram if you prefer — the text is ready either way. |
| `📒 Failure log` | `code` | Append to Sheets/Airtable. Review monthly — the pattern tells you what to fix. |

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
