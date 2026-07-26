# DCA-SYS-02 · Setup Checker & Install Guide (run this first)

> Checks an installation for the mistakes that cause silent failures — placeholder values left in Config, mismatched signing secrets, missing Error Workflow, inactive templates — and reports each with its fix, ordered by severity.

**Category:** `sys-spine` · **Version:** `1.0.0` · **Nodes:** 11 · **Setup:** ~3 min

---

## The problem

Around 70% of templates fail at install, not because the workflows are wrong but because one small step was missed and the resulting failure appears hours later somewhere unrelated. The buyer cannot tell which step, so they ask for a refund.

## What you get

One run tells the buyer exactly what is still wrong and how to fix it, before anything reaches a real customer.

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

- None to run the check
- SMTP if you want the report emailed

---

## Nodes

| Node | Type | Purpose |
| --- | --- | --- |
| `▶️ Run the setup check` | `manualTrigger` | Use this to dry-run the workflow before you point real traffic at it. |
| `⚙️ Config` | `code` | Copy the real values from your other templates' Config nodes. Be honest about the booleans — this only helps if it reflects reality. |
| `🔬 Build the signature probe` | `code` | One fixed payload, signed with each configured secret. |
| `🔏 Sign with A1-01 secret` | `crypto` | Signs the probe with the secret you pasted from A1-01. |
| `🔏 Sign with A1-02 secret` | `crypto` | Signs the same probe with A1-02's secret. These two must match. |
| `🔏 Sign with A4-01 secret` | `crypto` | A4-01 reissues links, so its secret must match too. |
| `🔏 Sign with A1-04 secret` | `crypto` | A1-04 broadcasts fresh links, so its secret must match as well. |
| `🔎 Run every check` | `code` | Every finding names the node to open and what to type. Ordered by severity. |
| `📋 Setup report` | `code` | Open this node's output and read it. The top line tells you whether you can go live. |
| `📨 Email the report` | `emailSend` | Optional — the report is readable in the previous node's output. Attach SMTP if you want it emailed. |
| `📒 Check outcome` | `code` | Captures the result even if the optional email fails. |

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
