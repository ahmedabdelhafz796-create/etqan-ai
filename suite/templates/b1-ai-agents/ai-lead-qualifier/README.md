# DCA-B1-02 · AI Lead Qualifier & Router (answer the buyers first)

> Reads every inbound enquiry, scores intent and fit, and routes hot leads to a human immediately while everything else goes to nurture — so the serious buyer never waits behind four tyre-kickers.

**Category:** `b1-ai-agents` · **Version:** `1.0.0` · **Nodes:** 15 · **Setup:** ~18 min

---

## The problem

Enquiries get answered in arrival order, so the buyer with budget waits behind people who were never going to buy — and response time is the strongest predictor of whether a deal closes.

## What you get

Hot leads surface within minutes with a written justification, warm leads go to nurture, and only spam is discarded — with a log of what was thrown away.

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

- An AI provider API key (Anthropic, OpenAI, or any OpenAI-compatible endpoint)
- SMTP account for the hot-lead alert

---

## Nodes

| Node | Type | Purpose |
| --- | --- | --- |
| `📥 New enquiry` | `webhook` | POST {email, message, name?, company?, phone?, source?}. |
| `⚙️ Config` | `code` | whatYouSell / idealCustomer / priceRange drive the fit judgement. Vague answers here give vague scoring. |
| `🛡️ Guard · validate + dedupe` | `code` | Validates required fields and drops duplicate deliveries. Safe to re-run. |
| `🧱 Deterministic pre-score` | `code` | Runs before any model call. An obviously-qualified lead survives a model outage. |
| `🗑️ Obvious spam?` | `if` | — |
| `🧠 Assess the lead` | `httpRequest` | Add your API key as a Header Auth credential. The model refines the score; it does not own it. |
| `🧮 Combine and tier` | `code` | A model failure downgrades to base scoring — it never discards the lead. |
| `🔥 Hot lead?` | `if` | — |
| `✍️ Write the hot-lead alert` | `code` | Everything needed to reply, in one message. No CRM lookup required. |
| `🔥 Alert on hot lead` | `emailSend` | Attach SMTP. Swap for Slack/Telegram for faster response. |
| `📋 Queue warm / nurture` | `code` | Warm and nurture both stay in the pipeline. Nothing here is discarded. |
| `🗑️ Log the spam` | `code` | Spam is logged, not silently dropped. Audit it occasionally. |
| `📒 Lead log` | `code` | Watch the tier mix monthly — it tells you whether hotAt/warmAt are tuned right. |
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
