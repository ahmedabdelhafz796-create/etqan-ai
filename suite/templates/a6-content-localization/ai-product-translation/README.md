# DCA-A6-01 · AI Product Translation & Sync (prices and formatting stay intact)

> Translates product copy into every language you sell in, protects prices, brand names and formatting from being translated, skips unchanged text, and emits text direction so RTL languages render correctly.

**Category:** `a6-content-localization` · **Version:** `1.0.0` · **Nodes:** 12 · **Setup:** ~15 min

---

## The problem

Change a description once and it must be updated in five translations — so translations quietly go stale. Naive AI translation makes it worse by translating prices, destroying formatting, and re-translating unchanged text every run.

## What you get

One source of truth translated into every language, with literals preserved, structure verified, RTL handled, and unchanged content skipped so you only pay for what actually changed.

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
| `📝 Product content` | `webhook` | POST {productId, title, description, price?, features?}. |
| `⚙️ Config` | `code` | protectedTerms: your brand and product names. These are never translated. |
| `🛡️ Guard · validate + dedupe` | `code` | Validates required fields and drops duplicate deliveries. Safe to re-run. |
| `🔒 Protect literals and check what changed` | `code` | Placeholders protect prices/brands/URLs. Hashing skips unchanged text so you only pay for real changes. |
| `🔄 Needs translating?` | `if` | — |
| `🧠 Translate` | `httpRequest` | Add your API key as a Header Auth credential. |
| `🔓 Restore literals and verify` | `code` | Verifies placeholders and structure. A failed check keeps the source rather than publishing something broken. |
| `💾 Remember what was translated` | `code` | Only successful translations are cached, so failures retry next run. |
| `⏭️ Unchanged — reuse existing` | `code` | No API call. This is where the cost saving comes from. |
| `📤 Deliver translations` | `code` | Wire to your CMS. Anything unverified is reported, never silently published. |
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
