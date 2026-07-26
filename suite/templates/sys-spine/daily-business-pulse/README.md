# DCA-SYS-01 · Daily Business Pulse (one message: what your automation did today)

> Reads the data every other template already writes and sends one daily message covering what needs action, what was recovered, and what ran — so the seller can see the system working instead of hoping.

**Category:** `sys-spine` · **Version:** `1.0.0` · **Nodes:** 8 · **Setup:** ~6 min

---

## The problem

Automation that works is invisible, so sellers stop trusting it and drift back to checking manually — at which point the automation has failed at its real job even though every workflow is green.

## What you get

One message a day, action items first, with anything not yet installed reported as 'not installed' rather than silently as zero.

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
| `🕗 Once a day` | `scheduleTrigger` | — |
| `⚙️ Config` | `code` | quietIfNothingHappened: set true once you trust it, to skip empty days. |
| `📥 Gather what the system did` | `code` | Reads existing counters. null = not installed, 0 = installed but quiet. Replace this node to read a shared Sheet for a true cross-workflow rollup. |
| `✍️ Write the pulse` | `code` | Action items first, then recovery, then normal. 'Not installed' is reported explicitly. |
| `📤 Worth sending today?` | `if` | — |
| `📨 Send the pulse` | `emailSend` | Attach SMTP. Swap for Slack/Telegram — the text is plain and works anywhere. |
| `🤫 Quiet day, nothing sent` | `code` | Only reached when you have opted into quiet days. |
| `📒 Pulse archive` | `code` | Append to a Sheet. Month-over-month recovery is the number that proves the suite's value. |

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
