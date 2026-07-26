"""
DCA-A4-01 · Download Problem Self-Service

Narrow on purpose, and the highest-leverage template in the support category.

The observation behind it
-------------------------
For a digital seller the support inbox is not a wide variety of problems. It is
overwhelmingly one problem wearing different clothes: *"I can't get my file."*
Expired link, wrong email address, lost email, hit the download cap, bought on a
work address and reading on a personal one. Every one of those is resolvable
without a human — the buyer is entitled to the file, they simply cannot reach it.

Yet it consumes the seller's day, because each message arrives individually and
demands a lookup, a decision and a reply.

Why this is separate from the AI support agent
----------------------------------------------
B1-01 handles questions, which need judgement and sometimes a model. This
handles a *transaction*: verify entitlement, reissue access. No model, no
judgement, no API cost, no possibility of inventing a policy — which makes it
both cheaper and safer than routing the same request through an LLM.

The security question this raises
---------------------------------
Automatic reissue is an access-granting endpoint, so it can be abused. Anyone
who learns a customer's email could request their file. The mitigations are
deliberate and stated on the canvas: the new link is only ever sent to the email
on the original order (never to a reply-to address supplied in the request),
requests are rate-limited per email, and anything past the limit escalates to a
human instead of being silently refused.

That last point matters — a security control that fails closed and says nothing
just produces a support ticket, which is what the template exists to prevent.
"""

from lib.core import Workflow, COLOR_BLUE, COLOR_GREEN, COLOR_RED, COLOR_PURPLE

SLUG = "download-problem-self-service"


def build() -> Workflow:
    wf = Workflow(
        name="DCA-A4-01 · Download Problem Self-Service (reissue access without a human)",
        slug=SLUG,
        category="a4-support",
        summary="Handles the one message that dominates a digital seller's inbox — 'I can't get my file' — by verifying entitlement and reissuing a fresh signed link automatically, with rate limits and human escalation for anything unusual.",
        problem="Most digital-product support is a single problem in different clothes: expired link, lost email, download cap reached. The buyer is entitled to the file and simply cannot reach it, yet each case costs the seller a lookup, a decision and a reply.",
        outcome="Entitled buyers get a fresh link in seconds without anyone being involved; abuse is rate-limited; and anything unusual reaches a human rather than failing silently.",
        version="1.0.0",
        tags=["support", "delivery", "digital-products", "deflection", "hardened"],
        credentials_needed=["SMTP account"],
        setup_minutes=12,
    )

    wf.sticky(
        "## 🔁 Download Problem Self-Service\n"
        "**\"I can't get my file\" → verified → fresh link sent. No human.**\n\n"
        "### Setup (about 12 minutes)\n"
        "1. **⚙️ Config** → `storeName`, `fromEmail`, `downloadBaseUrl`.\n"
        "2. **🔑 Sign the new link** → use the **same secret** as A1-01 and A1-02.\n"
        "3. Seed `knownOrders` from your order log, **or** wire the lookup node to\n"
        "   your real order source (see the note in **🔎 Verify entitlement**).\n"
        "4. Attach SMTP. Activate.\n"
        "5. Put the form URL in your delivery emails: *\"Trouble downloading?\"*\n\n"
        "### Why this one is worth building first\n"
        "It is not a wide variety of problems. It is **one problem** wearing\n"
        "different clothes — and it dominates a digital seller's inbox.",
        (-680, -520),
        (580, 540),
        COLOR_BLUE,
    )

    wf.sticky(
        "### 🤖 Why no AI here\n"
        "B1-01 answers *questions* — that needs judgement, and sometimes a model.\n\n"
        "This performs a **transaction**: verify entitlement, reissue access.\n\n"
        "No model means no API cost, no latency, and **no possibility of inventing\n"
        "a policy**. Routing this through an LLM would be slower, more expensive\n"
        "and less safe.\n\n"
        "Use the right tool. Not everything needs an agent.",
        (-60, -520),
        (460, 360),
        COLOR_GREEN,
    )

    wf.sticky(
        "### 🔐 This is an access-granting endpoint\n"
        "Automatic reissue can be abused — anyone who learns a customer's email\n"
        "could request their file.\n\n"
        "**Three deliberate controls:**\n"
        "1. The link is sent **only** to the email on the original order — never\n"
        "   to a reply-to address supplied in the request.\n"
        "2. Requests are rate-limited per email per day.\n"
        "3. Anything over the limit **escalates to you**, it does not silently\n"
        "   refuse.\n\n"
        "⚠️ Point 3 matters: a control that fails closed and says nothing just\n"
        "creates the support ticket this template exists to prevent.",
        (420, -520),
        (500, 420),
        COLOR_RED,
    )

    wf.sticky(
        "### 📊 What it deflects\n"
        "| Case | Handled |\n"
        "| --- | --- |\n"
        "| Link expired | ✅ auto |\n"
        "| Download cap reached | ✅ auto |\n"
        "| Lost the email | ✅ auto |\n"
        "| Wrong email on order | 🙋 escalates |\n"
        "| No order found | 🙋 escalates |\n"
        "| Over rate limit | 🙋 escalates |\n\n"
        "The first three are most of the volume.",
        (1400, 340),
        (420, 340),
        COLOR_PURPLE,
    )

    hook = wf.webhook(
        "🆘 Download help request",
        (-680, 180),
        path="dca/resend",
        notes="POST {email, orderId?}. Link this form from your delivery emails.",
    )

    cfg = wf.config(
        {
            "storeName": "YOUR_STORE_NAME",
            "fromEmail": "support@yourdomain.com",
            "humanEmail": "you@yourdomain.com",
            "downloadBaseUrl": "https://yourdomain.com/download",
            "linkTtlHours": 48,
            "maxDownloads": 5,
            "maxRequestsPerDay": 3,
            "knownOrders": {},
            "historyTtlHours": 72,
        },
        (-460, 180),
        notes="knownOrders maps email → {orderId, productId}. Seed it, or wire the verify node to your real order store.",
    )

    guard = wf.guard(
        (-240, 180),
        required=["body"],
        event_id_expr="(j.body?.email ?? '') + '|' + Math.floor(Date.now() / 60000)",
        ttl_hours=1,
    )

    verify = wf.code(
        "🔎 Verify entitlement",
        r"""
// Decide whether this person actually bought something.
//
// WIRING THIS TO YOUR REAL DATA:
// The lookup below reads `knownOrders` from Config, which is fine for a small
// catalogue and lets the template work with zero infrastructure. For a real
// store, replace the lookup with a read from wherever A1-01 writes its order
// log (Sheets, Airtable, Postgres) and return the same shape:
//     { orderId, productId, email, purchasedAt }
// Nothing downstream needs to change.
const cfg = $('⚙️ Config').first().json.__config;
const store = $getWorkflowStaticData('global');
store.resendRequests = store.resendRequests || {};

const now = Date.now();
const DAY = 24 * 60 * 60 * 1000;
const ttlMs = Number(cfg.historyTtlHours) * 60 * 60 * 1000;

for (const [k, r] of Object.entries(store.resendRequests)) {
  if (now - (r.firstAt || 0) > ttlMs) delete store.resendRequests[k];
}

const out = [];

for (const item of $input.all()) {
  const b = item.json.body ?? item.json;
  const email = String(b.email ?? '').trim().toLowerCase();
  const claimedOrder = String(b.orderId ?? b.order_id ?? '').trim();

  if (!email || !email.includes('@')) {
    throw new Error('A valid email is required to look up the order.');
  }

  // ── Rate limit ────────────────────────────────────────────────
  // Escalates rather than refusing silently: an unexplained refusal produces
  // the support ticket this template exists to prevent.
  const rec = store.resendRequests[email] || { count: 0, firstAt: now };
  if (now - rec.firstAt > DAY) { rec.count = 0; rec.firstAt = now; }
  rec.count += 1;
  store.resendRequests[email] = rec;

  if (rec.count > Number(cfg.maxRequestsPerDay)) {
    out.push({ json: {
      outcome: 'escalate',
      email,
      reason: `${rec.count} resend requests from this address in 24h (limit ${cfg.maxRequestsPerDay})`,
      humanNote: 'Could be a frustrated customer, could be someone probing. Check before reissuing manually.',
      __config: cfg,
    }});
    continue;
  }

  // ── Entitlement lookup ────────────────────────────────────────
  const orders = cfg.knownOrders || {};
  const found = orders[email];

  if (!found) {
    out.push({ json: {
      outcome: 'escalate',
      email,
      reason: 'no order found for this email address',
      humanNote: 'Most often the buyer paid with a different address (work vs personal) — ask which one they used.',
      __config: cfg,
    }});
    continue;
  }

  // A mismatched order id is worth a human's eyes, not an automatic refusal.
  if (claimedOrder && String(found.orderId) !== claimedOrder) {
    out.push({ json: {
      outcome: 'escalate',
      email,
      reason: `order id mismatch — they quoted "${claimedOrder}", we have "${found.orderId}"`,
      humanNote: 'Could be a typo, or they own more than one order. Verify before reissuing.',
      __config: cfg,
    }});
    continue;
  }

  const expires = Math.floor(now / 1000) + Number(cfg.linkTtlHours) * 3600;

  out.push({ json: {
    outcome: 'reissue',
    // Deliberately the email ON THE ORDER, never one supplied in the request.
    email: found.email || email,
    orderId: found.orderId,
    productId: found.productId ?? '',
    requestCount: rec.count,
    __expires: expires,
    // Must match A1-01's payload ordering exactly.
    __signaturePayload: [found.orderId, found.email || email, found.productId ?? '', expires, cfg.maxDownloads].join('|'),
    __config: cfg,
  }});
}

return out;
""",
        (0, 180),
        notes="Entitlement + rate limit. Replace the lookup with your real order store; keep the return shape.",
        always_output=True,
    )

    can_reissue = wf.if_(
        "✅ Entitled?",
        (240, 180),
        left="={{ $json.outcome }}",
        operator={"type": "string", "operation": "equals"},
        right="reissue",
    )

    sign = wf.hmac(
        "🔑 Sign the new link",
        (480, 60),
        value="={{ $json.__signaturePayload }}",
        secret="YOUR_OWN_LONG_RANDOM_LINK_SECRET",
        prop="linkSignature",
        encoding="hex",
        notes="⚠️ Must be the SAME secret used in A1-01 and A1-02, or the link will not verify.",
    )

    build_link = wf.code(
        "🔗 Build the fresh link",
        r"""
// Identical construction to A1-01 so the link verifies in A1-02 without any
// special-casing. The three templates share one URL contract.
return $input.all().map(i => {
  const o = i.json;
  const cfg = o.__config;
  const qs = new URLSearchParams({
    order: String(o.orderId),
    email: String(o.email),
    product: String(o.productId ?? ''),
    expires: String(o.__expires),
    max: String(cfg.maxDownloads),
    sig: String(o.linkSignature),
  });
  return { json: { ...o,
    downloadUrl: cfg.downloadBaseUrl.replace(/\/+$/, '') + '?' + qs.toString(),
    expiresHuman: new Date(o.__expires * 1000).toUTCString(),
  }};
});
""",
        (720, 60),
        notes="Same URL contract as A1-01 — verified by a cross-template test.",
    )

    send = wf.node(
        "📧 Send the fresh link",
        "n8n-nodes-base.emailSend",
        {
            "fromEmail": "={{ $json.__config.fromEmail }}",
            "toEmail": "={{ $json.email }}",
            "subject": "={{ 'Your download link — ' + $json.__config.storeName }}",
            "emailFormat": "html",
            "html": (
                "={{ '<div style=\"font-family:system-ui,-apple-system,Segoe UI,sans-serif;max-width:540px;"
                "margin:0 auto;padding:32px 24px;color:#111\">'"
                " + '<h2 style=\"margin:0 0 12px;font-size:20px\">Here is your download</h2>'"
                " + '<p style=\"color:#555;line-height:1.65;margin:0 0 22px\">No problem — here is a fresh link for order "
                "<strong>' + $json.orderId + '</strong>.</p>'"
                " + '<a href=\"' + $json.downloadUrl + '\" style=\"display:inline-block;background:#111;color:#fff;"
                "text-decoration:none;padding:14px 28px;border-radius:8px;font-weight:600\">Download now</a>'"
                " + '<p style=\"color:#777;font-size:13px;margin:24px 0 0\">Valid until <strong>' + $json.expiresHuman + '</strong>, "
                "up to ' + $json.__config.maxDownloads + ' downloads.</p>'"
                " + '<p style=\"color:#777;font-size:13px;margin:8px 0 0\">Still stuck? Reply to this email and a person will help.</p>'"
                " + '</div>' }}"
            ),
            "options": {},
        },
        2.1,
        (960, 60),
        retry=True,
        max_tries=3,
        wait_ms=3000,
        on_error="continueErrorOutput",
        notes="Sent to the address on the ORDER, not one supplied in the request.",
    )

    escalate = wf.code(
        "🙋 Escalate to a human",
        r"""
// Anything not automatically resolvable. Deliberately not a dead end: the
// message tells the seller what happened, what it usually means, and what to do.
return $input.all().map(i => {
  const o = i.json;
  const cfg = o.__config;
  return { json: {
    action: 'escalated',
    to: cfg.humanEmail,
    subject: `[download help] ${o.email} — needs you`,
    alertText:
`🙋 Download help request needs a human

From:   ${o.email}
Reason: ${o.reason}

What this usually means:
${o.humanNote}

To resolve: find their order, then either send them a fresh link from
A1-01, or add their email to knownOrders in this workflow's Config so it
resolves automatically next time.`,
  }};
});
""",
        (480, 320),
        notes="Explains what happened and what it usually means — not just a bare handoff.",
    )

    notify = wf.node(
        "📨 Tell the human",
        "n8n-nodes-base.emailSend",
        {
            "fromEmail": "={{ $('⚙️ Config').first().json.__config.fromEmail }}",
            "toEmail": "={{ $json.to }}",
            "subject": "={{ $json.subject }}",
            "emailFormat": "text",
            "text": "={{ $json.alertText }}",
            "options": {},
        },
        2.1,
        (720, 320),
        retry=True,
        max_tries=3,
        wait_ms=3000,
        on_error="continueRegularOutput",
        notes="Swap for Slack/Telegram if you prefer.",
    )

    log = wf.code(
        "📒 Deflection log",
        r"""
// The deflection rate is the number that proves this template's worth: what
// fraction of "I can't get my file" was resolved without you. If escalations
// dominate, your knownOrders source is incomplete — that is a wiring problem,
// not a template failure.
return $input.all().map(i => ({ json: {
  ts: new Date().toISOString(),
  email: i.json.email ?? null,
  outcome: i.json.action === 'escalated' ? 'escalated' : 'auto_resolved',
  orderId: i.json.orderId ?? null,
  requestCount: i.json.requestCount ?? null,
}}));
""",
        (1200, 180),
        notes="Track the auto-resolved vs escalated ratio. That ratio is the template's value.",
    )

    fail = wf.error_sink((960, 320), context="download-resend")

    respond = wf.respond(
        "↩️ Confirm to the buyer",
        (1440, 180),
        body='={{ JSON.stringify({ ok: true, message: "If that email has an order with us, a fresh download link is on its way." }) }}',
    )

    wf.chain(hook, cfg, guard, verify, can_reissue)
    wf.connect(can_reissue, sign, out=0)
    wf.connect(can_reissue, escalate, out=1)
    wf.chain(sign, build_link, send)
    wf.connect(send, log, out=0)
    wf.connect(send, fail, out=1)
    wf.connect(escalate, notify)
    wf.connect(notify, log)
    wf.connect(fail, log)
    wf.connect(log, respond)

    return wf
