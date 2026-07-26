# DCA-A1-02 · Secure Download Endpoint (signed, expiring, download-limited)

> Verifies a signed download link, enforces expiry and a download cap, and returns a specific reason for every refusal instead of a bare 403.

**Category:** `a1-delivery` · **Version:** `1.0.0` · **Nodes:** 11 · **Setup:** ~8 min

---

## The problem

Permanent download links get forwarded and posted publicly; short-lived ones break for legitimate buyers and generate support tickets. Most download failures return no reason at all, so the buyer emails the seller.

## What you get

Links that cannot be altered or shared indefinitely, limits enforced with no database, and refusals that tell the buyer exactly what happened and what to do next.

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

- None required
- Optional: your file host / S3 for the redirect target

---

## Nodes

| Node | Type | Purpose |
| --- | --- | --- |
| `⬇️ Download request` | `webhook` | GET endpoint. This URL goes into A1-01's downloadBaseUrl. |
| `⚙️ Config` | `code` | Map each product id to its real file URL. graceHours extends expiry for late buyers without lengthening the link's life for everyone. |
| `📥 Read the link parameters` | `code` | Reconstructs the signed payload. Field order must match A1-01. |
| `🔏 Recompute signature` | `crypto` | ⚠️ Must be the SAME secret as in A1-01's 'Sign download link' node. |
| `🛡️ Verify and decide` | `code` | Signature, expiry and cap in one auditable place. Counters live in static data — no database needed. |
| `✅ Allowed?` | `if` | — |
| `📤 Serve the file` | `code` | Redirects to your storage. Use presigned storage URLs for a second layer. |
| `🚫 Explain the refusal` | `code` | Returns a real explanation page, not a bare 403. |
| `📒 Access log` | `code` | Append to your log. Watch the refusal-code mix — it tells you what to tune. |
| `↩️ Redirect to file` | `respondToWebhook` | 302 to the real file URL. |
| `↩️ Show the reason` | `respondToWebhook` | 403 with a human explanation and a one-click way to fix it. |

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
