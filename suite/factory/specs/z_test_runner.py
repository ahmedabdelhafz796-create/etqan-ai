"""
DCA-TEST · Delivery Test Runner

A companion workflow, not a product. It exists because the people most likely to
install these templates are working from a phone, where `curl` is not available
and typing JSON by hand is painful enough that testing simply does not happen.

So the test harness becomes a workflow itself: import it, paste one URL, press
Execute. It fires three scenarios at a running Instant Digital Delivery endpoint
and reports pass/fail in plain language.

The three scenarios are the ones that actually matter:

  1. A paid order must deliver exactly once.
  2. The *same* order sent again must deliver nothing — this is the check that
     catches broken idempotency, and it is the failure that quietly refunds a
     seller's revenue twice.
  3. An unpaid order must deliver nothing.

Requires `testMode: true` in the delivery template's Config, which bypasses
signature verification only. That flag exists precisely so a buyer can prove the
pipeline works before wiring a real gateway secret.
"""

from lib.core import Workflow, COLOR_BLUE, COLOR_GREEN, COLOR_RED

SLUG = "delivery-test-runner"

# Sent three times: twice with the same id (replay), once unpaid.
PAID = """{
  "id": "evt_test_replay_001",
  "object": "event",
  "data": { "object": {
    "id": "cs_test_001",
    "payment_status": "paid",
    "amount_total": 4900,
    "currency": "usd",
    "customer_details": { "email": "{{ $json.__config.testEmail }}", "name": "Test Buyer" },
    "metadata": { "product_id": "book-01", "product_name": "Test Product" }
  }}
}"""

UNPAID = """{
  "id": "evt_test_unpaid_002",
  "object": "event",
  "data": { "object": {
    "id": "cs_test_002",
    "payment_status": "unpaid",
    "amount_total": 4900,
    "currency": "usd",
    "customer_details": { "email": "{{ $json.__config.testEmail }}", "name": "Test Buyer" },
    "metadata": { "product_id": "book-01", "product_name": "Test Product" }
  }}
}"""


def build() -> Workflow:
    wf = Workflow(
        name="DCA-TEST · Delivery Test Runner (press Execute, read the verdict)",
        slug=SLUG,
        category="z-tools",
        summary="Fires three scenarios at a running Instant Digital Delivery endpoint and reports whether delivery, replay protection and payment gating all behave correctly.",
        problem="Testing a webhook template normally needs a terminal and hand-written JSON, which is impractical on a phone — so most buyers never test at all and discover problems in production.",
        outcome="Import, paste one URL, press Execute. A plain-language verdict on the three failures that actually cost money.",
        version="1.0.0",
        tags=["testing", "tools", "internal"],
        credentials_needed=["None"],
        setup_minutes=3,
    )

    wf.sticky(
        "## 🧪 Delivery Test Runner\n"
        "**No terminal needed. Works from a phone.**\n\n"
        "### Before running\n"
        "1. Open **DCA-A1-01 · Instant Digital Delivery** and set `testMode: true`\n"
        "   in its Config. *(This bypasses signature checking only — set it back\n"
        "   to `false` before you go live.)*\n"
        "2. **Activate** that workflow, then copy its **Production URL** from the\n"
        "   webhook node.\n"
        "3. Paste it into **⚙️ Config → deliveryWebhookUrl** below.\n"
        "4. Put your own email in `testEmail` so you can see what arrives.\n"
        "5. Press **Execute Workflow**.\n\n"
        "### Then check your inbox\n"
        "You should receive **exactly one** email. Two means replay protection is\n"
        "broken; zero means delivery is broken.",
        (-560, -420),
        (540, 480),
        COLOR_BLUE,
    )

    wf.sticky(
        "### What each test proves\n\n"
        "**1 · Paid order** → must deliver.\n"
        "If this fails, nothing else matters.\n\n"
        "**2 · Same order again** → must deliver **nothing**.\n"
        "Gateways replay webhooks constantly. Without dedupe one purchase\n"
        "delivers twice — or one refund is issued twice.\n\n"
        "**3 · Unpaid order** → must deliver **nothing**.\n"
        "This is the one that gives product away free.",
        (20, -420),
        (440, 400),
        COLOR_GREEN,
    )

    wf.sticky(
        "### ⚠️ Reading the result\n"
        "Open the **📋 Verdict** node's output. Each line says PASS or FAIL with\n"
        "what to check.\n\n"
        "A `404` means the delivery workflow is not **Activated**.\n"
        "A `500` usually means the Config still has placeholder values.\n\n"
        "Confirm the email count in your inbox too — the HTTP response alone\n"
        "cannot see whether a message was actually sent.",
        (1120, 220),
        (440, 320),
        COLOR_RED,
    )

    trigger = wf.manual_trigger((-560, 160), name="▶️ Press Execute to run the tests")

    cfg = wf.config(
        {
            "deliveryWebhookUrl": "PASTE_YOUR_PRODUCTION_WEBHOOK_URL_HERE",
            "testEmail": "your-own-email@example.com",
        },
        (-340, 160),
        notes="Paste the Production URL from the delivery workflow's webhook node, and your own email.",
    )

    t1 = wf.http(
        "1️⃣ Paid order → expect delivery",
        (-120, 160),
        url="={{ $json.__config.deliveryWebhookUrl }}",
        method="POST",
        json_body="=" + PAID,
        headers={"content-type": "application/json"},
        notes="Should return 200 and send one email.",
    )

    hold1 = wf.code(
        "⏱️ Brief pause",
        r"""
// Give the first request time to finish writing its dedupe key before the
// replay goes out, otherwise the two can race and the test reports a false
// failure.
const started = Date.now();
while (Date.now() - started < 1500) { /* deliberate short block */ }
return $input.all();
""",
        (100, 160),
        notes="Prevents a race between the first request and the replay.",
    )

    t2 = wf.http(
        "2️⃣ Same order again → expect NO delivery",
        (320, 160),
        url="={{ $('⚙️ Config').first().json.__config.deliveryWebhookUrl }}",
        method="POST",
        json_body="=" + PAID,
        headers={"content-type": "application/json"},
        notes="Identical event id. Must NOT produce a second email.",
    )

    t3 = wf.http(
        "3️⃣ Unpaid order → expect NO delivery",
        (540, 160),
        url="={{ $('⚙️ Config').first().json.__config.deliveryWebhookUrl }}",
        method="POST",
        json_body="=" + UNPAID,
        headers={"content-type": "application/json"},
        notes="payment_status is unpaid. Must NOT deliver.",
    )

    verdict = wf.code(
        "📋 Verdict",
        r"""
// Turn three HTTP responses into something a non-engineer can act on.
//
// Deliberate limitation, stated plainly in the output: this can see HTTP status
// codes, not mailboxes. It can prove the endpoint accepted or rejected each
// call, but only the inbox proves how many emails were actually sent — so the
// verdict tells the reader to go and count them.
const url = $('⚙️ Config').first().json.__config.deliveryWebhookUrl;
const email = $('⚙️ Config').first().json.__config.testEmail;

function statusOf(nodeName) {
  try {
    const r = $(nodeName).first().json;
    if (r?.error) return { ok: false, detail: String(r.error.message || r.error) };
    return { ok: true, detail: JSON.stringify(r).slice(0, 160) };
  } catch (e) {
    return { ok: false, detail: 'no response captured' };
  }
}

const r1 = statusOf('1️⃣ Paid order → expect delivery');
const r2 = statusOf('2️⃣ Same order again → expect NO delivery');
const r3 = statusOf('3️⃣ Unpaid order → expect NO delivery');

const lines = [];
lines.push('═══ DELIVERY TEST RESULTS ═══');
lines.push('');

if (String(url).includes('PASTE_YOUR')) {
  lines.push('❌ STOP — you have not set deliveryWebhookUrl in Config yet.');
  return [{ json: { verdict: lines.join('\n') } }];
}

lines.push(r1.ok
  ? '✅ TEST 1 — endpoint accepted the paid order'
  : '❌ TEST 1 — endpoint did not accept the paid order');
lines.push('   ' + r1.detail);
if (!r1.ok) {
  lines.push('   → 404? The delivery workflow is not Activated.');
  lines.push('   → 500? Config still holds placeholder values, or testMode is false.');
}
lines.push('');

lines.push(r2.ok
  ? '✅ TEST 2 — replay was accepted at HTTP level (expected)'
  : '⚠️ TEST 2 — replay errored: ' + r2.detail);
lines.push('   The real check is your inbox: this must NOT have produced a 2nd email.');
lines.push('');

lines.push(r3.ok
  ? '✅ TEST 3 — unpaid order was accepted at HTTP level (expected)'
  : '⚠️ TEST 3 — unpaid order errored: ' + r3.detail);
lines.push('   The real check is your inbox: this must NOT have produced an email.');
lines.push('');
lines.push('─────────────────────────────');
lines.push('NOW CHECK ' + email + ':');
lines.push('');
lines.push('  Exactly 1 email  → 🎉 PERFECT. Delivery, replay protection and');
lines.push('                      payment gating all work.');
lines.push('  2 or more        → ❌ Replay protection failed. Report this.');
lines.push('  0 emails         → ❌ Delivery failed. Check the delivery');
lines.push('                      workflow Executions tab for the failing node.');
lines.push('');
lines.push('⚠️ Set testMode back to false before going live.');

return [{ json: { verdict: lines.join('\n'), checkedAt: new Date().toISOString() } }];
""",
        (760, 160),
        notes="Open this node's output to read the result.",
    )

    fail = wf.error_sink((760, 380), context="test-runner")

    wf.chain(trigger, cfg, t1)
    wf.connect(t1, hold1, out=0)
    wf.connect(t1, fail, out=1)
    wf.chain(hold1, t2)
    wf.connect(t2, t3, out=0)
    wf.connect(t2, fail, out=1)
    wf.connect(t3, verdict, out=0)
    wf.connect(t3, fail, out=1)

    return wf
