# The Hardening Standard

Every template in this suite is built through one code path and must pass one
automated gate. This document is that standard, and
[`factory/lib/validate.py`](../factory/lib/validate.py) is its executable form —
if a template violates an ERROR-level rule, `build.py` refuses to write it.

That coupling is the point. Published standards drift from shipped reality when
nothing checks them. Here, the standard *is* the check.

---

## Why this exists

Two numbers from the market research shaped everything:

- **~97%** of workflows that pass a happy-path demo fail once they meet real
  traffic.
- **~70%** of published templates fail at install time.

Neither is a discipline problem. Both are *structural* — so both get structural
fixes. A template built through this factory cannot ship without the guarantees
below, because the builder emits them and the validator enforces them.

---

## The rules

### 1. Replay protection — ERROR

Any webhook-triggered template must be idempotent.

Payment gateways retry aggressively: on timeout, on any 5xx, and sometimes for
no visible reason. Stripe may resend the same event for up to three days.
Without a dedupe step, one purchase can deliver a file three times, or issue a
refund twice.

**Implementation:** `Workflow.guard()` keys on the provider's own event id and
records it in n8n static data with TTL-based pruning. A replay produces zero
items, so nothing downstream executes.

**Deliberate choice:** no external database. Requiring Redis or Postgres for
deduplication would put this out of reach of exactly the sellers who need it
most.

### 2. Input validation — ERROR

Required fields are asserted at the entry point, and a malformed payload throws
with the field names that were missing and the keys that actually arrived.

A template that half-processes a broken payload is how silent data corruption
starts — and it surfaces weeks later as unexplainable records.

### 3. Retry on every outbound call — ERROR

Every `httpRequest` node carries `retryOnFail: true`, `maxTries: 3`,
`waitBetweenTries: 2000`.

Transient failures — rate limits, 5xx, DNS blips — are not exceptional. They are
the normal weather of networked systems.

### 4. A wired failure path — ERROR

At least one node must declare `onError: "continueErrorOutput"`, and something
must actually be connected to that error output.

The validator checks the *wiring*, not just the flag, because an error output
that goes nowhere is the same as no error handling at all.

A failure that is logged and surfaced is an incident you can fix. A failure that
vanishes is the one that quietly loses revenue for a month.

### 5. A single config block — ERROR

All tunable values live in one `⚙️ Config` node at the top of the flow.

This is what makes a template installable in minutes instead of requiring a hunt
through twenty nodes for the three that need editing.

**Secrets never go here.** They belong in n8n Credentials.

### 6. No embedded credentials — ERROR

The validator scans every string in the workflow for live key patterns — Stripe
live keys, OpenAI keys, Slack tokens, GitHub tokens, Google API keys, private
key blocks, hardcoded bearer tokens. It also rejects credential objects that pin
an `id` from the author's own account, which is a common and quiet leak in
exported templates.

Placeholders (`YOUR_…`, `<PLACEHOLDER>`, expressions) are expected and allowed.

### 7. On-canvas documentation — ERROR

At least two sticky notes, and inline notes on the majority of functional nodes.

Documentation that lives in a separate PDF is documentation nobody reads while
they are staring at a broken node. It belongs on the canvas, next to the thing
it explains.

### 8. Structural integrity — ERROR

- No duplicate node names or ids.
- Every connection resolves to a node that exists.
- No orphan nodes.
- At least one trigger.
- The file round-trips: what we wrote parses back to what we built.

### 9. Ships inactive — WARN

Templates import switched off. Nobody's first import should start processing
live traffic before they have looked at it.

---

## Version-drift policy

n8n's higher-level nodes have repeatedly changed parameter shape between
typeVersions — the Set node's `fields` → `assignments` migration being the
best-known example. This is the largest single cause of "this template won't
import" reports.

Two rules follow:

1. **Every `typeVersion` is pinned explicitly.** Never left to default.
2. **Data shaping happens in Code nodes.** The `code` (v2) and `if` (v2.2)
   schemas have been stable; we control the logic inside them, so it cannot
   move under us.

### The `require('crypto')` trap

`require('crypto')` inside a Code node **works on n8n Cloud and throws on a
default self-hosted instance** unless the operator sets
`NODE_FUNCTION_ALLOW_BUILTIN`.

This is the archetypal "worked for the author, broken for the buyer" failure. An
author on Cloud tests successfully, publishes, and every self-hosted buyer hits
an error the author cannot reproduce.

**Every signature path in this suite goes through the built-in Crypto node
instead.** It needs no environment changes and behaves identically on both.

---

## What this standard does *not* claim

Honesty is part of the product:

- **It does not make a workflow unbreakable.** Upstream APIs change, credentials
  expire, and providers have outages. It makes failures *visible and
  recoverable* rather than silent.
- **Fraud scoring is heuristic.** It catches common attack patterns. It will
  produce false positives, which is why it ships in shadow mode and reports the
  reason for every point it assigns.
- **Structural validation is not runtime testing.** The validator proves a
  template is well-formed, secret-free and correctly wired. It cannot prove your
  Stripe key is right. That is what the manual verification pass is for — see
  [`04-verification.md`](./04-verification.md).

---

## Running the gate

```bash
cd suite/factory
python3 build.py            # build everything, validate, write only what passes
python3 build.py --check    # validate without writing (CI)
python3 build.py a1_01      # one template
```

A non-zero exit means at least one ERROR-level finding. Nothing with an error
reaches `templates/`.
