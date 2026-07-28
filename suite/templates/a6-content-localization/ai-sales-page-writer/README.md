# DCA-A6-02 · AI Sales Page & Listing Writer (writes from your facts, flags unsupported claims)

> Turns a product's facts into a structured sales page — problem, proof, what you get, honest limits — and scans the result for unsupported claims before you publish it.

**Category:** `a6-content-localization` · **Version:** `1.0.0` · **Nodes:** 10 · **Setup:** ~12 min

---

## The problem

Ask a model for a sales page and it invents 'trusted by thousands' and 'guaranteed results'. That copy converts badly because readers discount it, and an invented refund policy is one a customer will hold you to.

## What you get

A complete listing built only from facts you supplied, in the order that actually converts, with every unsupported superlative flagged for removal before publishing.

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

---

## Nodes

| Node | Type | Purpose |
| --- | --- | --- |
| `📋 Product facts` | `webhook` | POST the product's facts. The more specific they are, the better the listing. |
| `⚙️ Config` | `code` | bannedClaims drives the scanner. Add anything your market is tired of hearing. |
| `🛡️ Guard · validate + dedupe` | `code` | Validates required fields and drops duplicate deliveries. Safe to re-run. |
| `📥 Collect the facts` | `code` | Missing facts are reported, never invented. Thin facts produce a thin listing by design. |
| `🧠 Write the listing` | `httpRequest` | Add your API key as a Header Auth credential. |
| `📖 Parse the listing` | `code` | An unreadable response fails clearly rather than publishing an empty page. |
| `🔍 Scan for unsupported claims` | `code` | Deterministic check on the model's output. Advisory, not blocking — but the decision becomes conscious. |
| `📄 Render the listing` | `code` | Markdown for marketplaces, HTML for your site, raw object for a CMS. |
| `🚨 Handle failure` | `code` | Structured failure record. Wire to your alert channel. |
| `↩️ Return the listing` | `respondToWebhook` | Answer fast so the provider does not retry on timeout. |

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
