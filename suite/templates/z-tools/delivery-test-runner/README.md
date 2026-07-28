# DCA-TEST · Delivery Test Runner (press Execute, read the verdict)

> Fires three scenarios at a running Instant Digital Delivery endpoint and reports whether delivery, replay protection and payment gating all behave correctly.

**Category:** `z-tools` · **Version:** `1.0.0` · **Nodes:** 8 · **Setup:** ~3 min

---

## The problem

Testing a webhook template normally needs a terminal and hand-written JSON, which is impractical on a phone — so most buyers never test at all and discover problems in production.

## What you get

Import, paste one URL, press Execute. A plain-language verdict on the three failures that actually cost money.

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

- None

---

## Nodes

| Node | Type | Purpose |
| --- | --- | --- |
| `▶️ Press Execute to run the tests` | `manualTrigger` | Use this to dry-run the workflow before you point real traffic at it. |
| `⚙️ Config` | `code` | Paste the Production URL from the delivery workflow's webhook node, and your own email. |
| `1️⃣ Paid order → expect delivery` | `httpRequest` | Should return 200 and send one email. |
| `⏱️ Brief pause` | `code` | Prevents a race between the first request and the replay. |
| `2️⃣ Same order again → expect NO delivery` | `httpRequest` | Identical event id. Must NOT produce a second email. |
| `3️⃣ Unpaid order → expect NO delivery` | `httpRequest` | payment_status is unpaid. Must NOT deliver. |
| `📋 Verdict` | `code` | Open this node's output to read the result. |
| `🚨 Handle failure` | `code` | Structured failure record. Wire to your alert channel. |

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
