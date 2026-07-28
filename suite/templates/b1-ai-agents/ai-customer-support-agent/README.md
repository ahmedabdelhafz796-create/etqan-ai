# DCA-B1-01 · AI Customer Support Agent (answers from your facts, escalates when unsure)

> Answers customer questions from a knowledge base you control, scores its own confidence, and hands anything uncertain or sensitive to a human with a draft already written.

**Category:** `b1-ai-agents` · **Version:** `1.0.0` · **Nodes:** 13 · **Setup:** ~20 min

---

## The problem

AI support workflows that reply to everything eventually invent a refund policy or a feature that does not exist — and the customer holds the seller to it. A confidently wrong answer creates an obligation and destroys trust at once.

## What you get

Routine questions answered in seconds from your own facts; uncertain and sensitive ones escalated to a human with a draft attached, so nothing is ever invented.

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
- SMTP account for sending replies

---

## Nodes

| Node | Type | Purpose |
| --- | --- | --- |
| `💬 Customer question` | `webhook` | POST {email, message, name?, subject?}. Wire your contact form or inbox here. |
| `⚙️ Config` | `code` | knowledgeBase is the whole job. Accuracy here IS the agent's accuracy. |
| `🛡️ Guard · validate + dedupe` | `code` | Validates required fields and drops duplicate deliveries. Safe to re-run. |
| `🔍 Pre-triage` | `code` | Deterministic guardrails run before any model call — cheaper and not overridable by the model. |
| `🤔 Worth asking the model?` | `if` | — |
| `🧠 Ask the model` | `httpRequest` | Add your API key as a Header Auth credential (x-api-key for Anthropic, Authorization for OpenAI). |
| `📖 Read the answer` | `code` | Unparseable output escalates instead of sending nonsense to a customer. |
| `✅ Safe to send automatically?` | `if` | — |
| `📧 Send the reply` | `emailSend` | Only reached when the agent is confident AND autoReply is on. |
| `🙋 Hand to a human` | `code` | Sends you the question plus a draft. Editing a draft is far faster than writing from scratch. |
| `📨 Notify the human` | `emailSend` | Swap for Slack or Telegram if you prefer. |
| `📒 Support log` | `code` | Review weekly. A high escalation rate is a knowledge-base gap, not an agent failure. |
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
