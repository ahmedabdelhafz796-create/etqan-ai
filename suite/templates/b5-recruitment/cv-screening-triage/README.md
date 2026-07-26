# DCA-B5-01 · CV Screening & Candidate Triage (ranks, never rejects)

> Reads every application against the requirements you wrote, ranks candidates with stated reasoning for each score, and produces a reviewable shortlist — without ever auto-rejecting anyone.

**Category:** `b5-recruitment` · **Version:** `1.0.0` · **Nodes:** 16 · **Setup:** ~18 min

---

## The problem

A job ad brings two hundred applications and someone has to read them all, so the good candidates wait days and some are never reached at all.

## What you get

Every application scored against your stated requirements with visible reasoning, ordered so the strongest are read first — and nobody filtered out by a machine.

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

- An AI provider API key (Anthropic, OpenAI, or compatible)
- SMTP account for the shortlist digest

---

## Nodes

| Node | Type | Purpose |
| --- | --- | --- |
| `📄 Application received` | `webhook` | POST {candidateId, name, email, cvText}. Wire your form or ATS here. |
| `⚙️ Config` | `code` | mustHaves drive everything. Write requirements a person could check objectively, not aspirations. |
| `🛡️ Guard · validate + dedupe` | `code` | Validates required fields and drops duplicate deliveries. Safe to re-run. |
| `📥 Prepare the application` | `code` | No keyword pre-scoring — it rewards CV-writing skill, not job skill, and carries bias. |
| `🧠 Assess the application` | `httpRequest` | Add your API key as a Header Auth credential. The prompt forbids scoring on personal characteristics. |
| `📊 Record the assessment` | `code` | A failed assessment is an unknown, never a zero — it routes to manual review. |
| `↩️ 200 OK` | `respondToWebhook` | Answer fast so the provider does not retry on timeout. |
| `🕕 Daily shortlist` | `scheduleTrigger` | — |
| `⚙️ Config (digest side)` | `code` | ⚠️ Mirror of the main Config. Change one, change both. |
| `🏅 Build the shortlist` | `code` | Unscored candidates are listed first — they are the ones most at risk of being lost. |
| `📋 Any applications?` | `if` | — |
| `✍️ Write the shortlist digest` | `code` | States plainly that nobody was rejected and that a wrong ranking usually means the requirements need rewording. |
| `📨 Send the shortlist` | `emailSend` | Goes to the reviewer. Nothing is ever sent to candidates by this template. |
| `🤫 No applications yet` | `code` | Logged so an empty day is distinguishable from a stopped schedule. |
| `🚨 Handle failure` | `code` | Structured failure record. Wire to your alert channel. |
| `📒 Screening log` | `code` | Track how many needed manual review — a high number means the intake format needs fixing. |

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
