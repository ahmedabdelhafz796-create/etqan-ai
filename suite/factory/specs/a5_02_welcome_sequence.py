"""
DCA-A5-02 · Post-Purchase Sequence & Review Collection

Covers two items from the pain list at once — "جمع المراجعات" and the retention
gap after a sale — because they are the same sequence viewed from two ends.

The window that gets wasted
---------------------------
The days immediately after a purchase are the only period when a buyer is
reliably paying attention to the seller. Almost every digital seller spends that
window in silence, then months later wonders why they have no reviews and no
repeat customers. Both problems have the same cause and the same fix.

Why the ordering here is deliberate
-----------------------------------
The obvious sequence asks for a review immediately. That is the wrong order and
it costs the seller twice: the buyer has not used the product yet, so the review
is thin and unconvincing, and the ask arrives before any value has been
delivered, so it reads as extraction.

So this sequence gives first — a help nudge that reduces support tickets, then a
usage tip — and asks for a review only after the buyer has had time to get value.
It also asks *whether they got value* before asking for a public review, which
means unhappy buyers reach the seller privately instead of a review page.

That last point is the commercially important one: a template that routes
dissatisfaction into a private reply rather than a one-star review is worth more
than one that simply harvests ratings.

The refund window matters
-------------------------
Asking for an upsell before the refund window closes invites a buyer to
reconsider both purchases at once. The upsell step is gated on that window
having passed.
"""

from lib.core import Workflow, COLOR_BLUE, COLOR_GREEN, COLOR_RED, COLOR_PURPLE

SLUG = "post-purchase-sequence"


def build() -> Workflow:
    wf = Workflow(
        name="DCA-A5-02 · Post-Purchase Sequence & Review Collection",
        slug=SLUG,
        category="a5-marketing-revenue",
        summary="Runs a timed post-purchase sequence that helps first and asks second, checks privately whether the buyer is happy before requesting a public review, and only mentions an upsell once the refund window has closed.",
        problem="The days after a purchase are the only time a buyer is reliably paying attention, and almost every seller spends them in silence — then wonders why they have no reviews and no repeat customers.",
        outcome="Fewer support tickets, more reviews from buyers who actually got value, and unhappy customers reaching you privately instead of a review page.",
        version="1.0.0",
        tags=["marketing", "retention", "reviews", "digital-products", "hardened"],
        credentials_needed=["SMTP account"],
        setup_minutes=12,
    )

    wf.sticky(
        "## 🌱 Post-Purchase Sequence\n"
        "**Help → tip → \"did it work?\" → review or rescue.**\n\n"
        "### Setup (about 12 minutes)\n"
        "1. **⚙️ Config** → `storeName`, `fromEmail`, `reviewUrl`, `usageTip`.\n"
        "2. POST each completed order:\n"
        "   ```json\n"
        "   { \"orderId\": \"...\", \"email\": \"...\",\n"
        "     \"name\": \"...\", \"productName\": \"...\" }\n"
        "   ```\n"
        "   *(Or chain it from A1-01 after delivery succeeds.)*\n"
        "3. Attach SMTP. Activate. The schedule runs the sequence.\n\n"
        "### Two problems, one sequence\n"
        "No reviews and no repeat customers have the same cause: silence during\n"
        "the only window when the buyer is paying attention.",
        (-700, -540),
        (600, 500),
        COLOR_BLUE,
    )

    wf.sticky(
        "### 🔄 Why the review ask comes LAST\n"
        "The obvious build asks for a review immediately. That costs you twice:\n\n"
        "1. The buyer **has not used it yet**, so the review is thin and\n"
        "   unconvincing.\n"
        "2. The ask arrives **before any value was delivered**, so it reads as\n"
        "   extraction.\n\n"
        "This gives first — a help nudge, then a usage tip — and asks only after\n"
        "the buyer has had time to get something out of it.",
        (-80, -540),
        (500, 380),
        COLOR_PURPLE,
    )

    wf.sticky(
        "### 🛟 The step that protects your rating\n"
        "Before asking for a **public** review, it asks privately:\n"
        "**\"did this work for you?\"**\n\n"
        "· Happy → review link\n"
        "· Not happy → replies to **you**, not to a review page\n\n"
        "A sequence that routes dissatisfaction into a private reply is worth far\n"
        "more than one that simply harvests ratings — and it is more honest.",
        (420, -540),
        (480, 360),
        COLOR_GREEN,
    )

    wf.sticky(
        "### ⏳ The upsell waits for the refund window\n"
        "Mentioning another product before the refund window closes invites the\n"
        "buyer to reconsider **both** purchases at once.\n\n"
        "`upsellAfterDays` should be **longer** than your refund period. Set\n"
        "`enableUpsell: false` to skip it entirely — the sequence works fine\n"
        "without it.",
        (1140, 360),
        (460, 300),
        COLOR_RED,
    )

    hook = wf.webhook(
        "🎉 Order completed",
        (-700, 180),
        path="dca/post-purchase",
        notes="POST {orderId, email, name, productName}. Chain from A1-01 after delivery.",
    )

    cfg = wf.config(
        {
            "storeName": "YOUR_STORE_NAME",
            "fromEmail": "hello@yourdomain.com",
            "supportEmail": "support@yourdomain.com",
            "reviewUrl": "https://yourdomain.com/review",
            "usageTip": "REPLACE: one genuinely useful tip for getting value from your product.",
            "helpAfterHours": 24,
            "tipAfterDays": 3,
            "checkInAfterDays": 7,
            "upsellAfterDays": 21,
            "enableUpsell": False,
            "upsellText": "REPLACE: one sentence about your other product, and its link.",
            "batchSize": 50,
            "historyTtlDays": 60,
        },
        (-480, 180),
        notes="upsellAfterDays must exceed your refund window. usageTip should be genuinely useful — filler here undoes the whole sequence.",
    )

    guard = wf.guard(
        (-260, 180),
        required=["body"],
        event_id_expr="j.body?.orderId ?? j.body?.order_id ?? (j.body?.email + '|' + Date.now())",
        ttl_hours=168,
    )

    enrol = wf.code(
        "📝 Enrol the buyer",
        r"""
// One sequence per buyer per order. A buyer who purchases twice gets two
// sequences, which is correct — the second product needs its own help and its
// own tip.
const cfg = $('⚙️ Config').first().json.__config;
const store = $getWorkflowStaticData('global');
store.sequences = store.sequences || {};

const now = Date.now();
const ttlMs = Number(cfg.historyTtlDays) * 24 * 60 * 60 * 1000;
for (const [k, s] of Object.entries(store.sequences)) {
  if (now - (s.startedAt || 0) > ttlMs) delete store.sequences[k];
}

const out = [];

for (const item of $input.all()) {
  const b = item.json.body ?? item.json;

  const email = String(b.email ?? '').trim().toLowerCase();
  const orderId = String(b.orderId ?? b.order_id ?? '').trim();

  if (!email) {
    throw new Error('Post-purchase sequence needs a buyer email. Received keys: ' + Object.keys(b).join(', '));
  }

  const key = `${email}|${orderId || 'no-order'}`;

  // Unsubscribe and opt-out arrive here too.
  const event = String(b.event ?? '').toLowerCase();
  if (event.includes('unsubscribe') || event.includes('optout') || b.unsubscribe === true) {
    if (store.sequences[key]) {
      store.sequences[key].stopped = true;
      store.sequences[key].stoppedReason = 'buyer unsubscribed';
    }
    // Remember the opt-out even if there is no sequence yet, so a later order
    // does not restart contact with someone who asked to be left alone.
    store.optOuts = store.optOuts || {};
    store.optOuts[email] = now;
    out.push({ json: { action: 'unsubscribed', email } });
    continue;
  }

  if ((store.optOuts || {})[email]) {
    out.push({ json: { action: 'skipped_opted_out', email,
                       note: 'This buyer previously unsubscribed. No sequence started.' } });
    continue;
  }

  if (store.sequences[key]) {
    out.push({ json: { action: 'already_enrolled', email, orderId } });
    continue;
  }

  store.sequences[key] = {
    key, email, orderId,
    name: String(b.name ?? '').trim(),
    productName: String(b.productName ?? b.product_name ?? 'your purchase').trim(),
    startedAt: now,
    stage: 0,
    stopped: false,
    happy: null,
  };

  out.push({ json: { action: 'enrolled', email, orderId } });
}

return out;
""",
        (-40, 180),
        notes="Honours unsubscribes permanently, including for future orders.",
        always_output=True,
    )

    ack = wf.respond(
        "↩️ 200 OK",
        (200, 180),
        body='={{ JSON.stringify({ ok: true, action: $json.action }) }}',
    )

    # ── The sequence clock ──────────────────────────────────────────────
    sched = wf.schedule("🕐 Advance sequences", (-700, 600), hours=6)

    cfg2 = wf.code(
        "⚙️ Config (sequence side)",
        r"""
// Mirror of the main Config — n8n cannot share a node across trigger branches.
const CONFIG = {
  "storeName": "YOUR_STORE_NAME",
  "fromEmail": "hello@yourdomain.com",
  "supportEmail": "support@yourdomain.com",
  "reviewUrl": "https://yourdomain.com/review",
  "usageTip": "REPLACE: one genuinely useful tip for getting value from your product.",
  "helpAfterHours": 24,
  "tipAfterDays": 3,
  "checkInAfterDays": 7,
  "upsellAfterDays": 21,
  "enableUpsell": false,
  "upsellText": "REPLACE: one sentence about your other product, and its link.",
  "batchSize": 50
};
return [{ json: { __config: CONFIG } }];
""",
        (-480, 600),
        notes="⚠️ Mirror of the main Config. Change one, change both.",
        always_output=True,
    )

    advance = wf.code(
        "⏭️ Find who is due a message",
        r"""
// Advance each sequence by at most one stage per run. Sending two stages in one
// day defeats the point of a timed sequence.
const cfg = $input.first().json.__config;
const store = $getWorkflowStaticData('global');
store.sequences = store.sequences || {};

const now = Date.now();
const HOUR = 3600000;
const DAY = 86400000;

const due = [];
let active = 0;

for (const s of Object.values(store.sequences)) {
  if (s.stopped) continue;
  active++;

  const age = now - s.startedAt;

  // Stages in order. The first match that has not been sent wins.
  const stages = [
    { n: 1, at: Number(cfg.helpAfterHours) * HOUR, kind: 'help' },
    { n: 2, at: Number(cfg.tipAfterDays) * DAY, kind: 'tip' },
    { n: 3, at: Number(cfg.checkInAfterDays) * DAY, kind: 'checkin' },
  ];

  // The upsell only exists if enabled AND the refund window has passed.
  if (cfg.enableUpsell === true) {
    stages.push({ n: 4, at: Number(cfg.upsellAfterDays) * DAY, kind: 'upsell' });
  }

  const next = stages.find(st => (s.stage || 0) < st.n && age >= st.at);
  if (!next) continue;

  s.stage = next.n;
  s.lastSentAt = now;

  // The final stage retires the sequence.
  const isLast = next.n === stages[stages.length - 1].n;
  if (isLast) { s.stopped = true; s.stoppedReason = 'sequence complete'; }

  due.push({ json: {
    __summary: false,
    email: s.email,
    name: s.name,
    productName: s.productName,
    orderId: s.orderId,
    kind: next.kind,
    stage: next.n,
    daysSincePurchase: Math.floor(age / DAY),
    __config: cfg,
  }});
}

const batch = due.slice(0, Number(cfg.batchSize));
batch.push({ json: { __summary: true, activeSequences: active, sentThisRun: batch.length, __config: cfg } });

return batch;
""",
        (-260, 600),
        notes="One stage per run maximum. The upsell stage only exists when enabled.",
        always_output=True,
    )

    is_msg = wf.if_(
        "✉️ A message to send?",
        (-20, 600),
        left="={{ $json.__summary }}",
        operator={"type": "boolean", "operation": "false", "singleValue": True},
    )

    compose = wf.code(
        "✍️ Compose for this stage",
        r"""
// Four different messages with four different jobs. Each is short — a long
// post-purchase email gets skimmed, and skimmed help is no help.
return $input.all().map(i => {
  const o = i.json;
  const cfg = o.__config;
  const first = (o.name || '').split(' ')[0];
  const hi = `Hi${first ? ' ' + first : ''}`;

  const wrap = (inner) =>
`<div style="font-family:system-ui,-apple-system,Segoe UI,sans-serif;max-width:540px;margin:0 auto;padding:32px 24px;color:#111;line-height:1.65">
  ${inner}
  <p style="color:#999;font-size:12px;margin:28px 0 0;border-top:1px solid #eee;padding-top:14px">
    ${cfg.storeName} · <a href="mailto:${cfg.supportEmail}?subject=unsubscribe" style="color:#999">unsubscribe</a>
  </p>
</div>`;

  let subject, html;

  if (o.kind === 'help') {
    // Deflects a support ticket before it is written.
    subject = `Got everything OK?`;
    html = wrap(
`<h2 style="margin:0 0 12px;font-size:19px">${hi}, quick check</h2>
 <p style="color:#555;margin:0 0 18px">Just making sure your download of <strong>${o.productName}</strong> came through and opened properly.</p>
 <p style="color:#555;margin:0 0 18px">If anything did not work — the link, the file, anything at all — reply to this email and I will sort it out. No form, no ticket number.</p>
 <p style="color:#777;font-size:13px;margin:0">If it all worked, no need to reply. Enjoy it.</p>`);

  } else if (o.kind === 'tip') {
    // Gives value with nothing asked in return.
    subject = `One thing that helps with ${o.productName}`;
    html = wrap(
`<h2 style="margin:0 0 12px;font-size:19px">${hi}</h2>
 <p style="color:#555;margin:0 0 18px">A few days in — here is the one thing most people find useful:</p>
 <div style="background:#f7f7f7;border-radius:8px;padding:16px;margin:0 0 18px;color:#333">${cfg.usageTip}</div>
 <p style="color:#777;font-size:13px;margin:0">Nothing to do here. Reply if you want to ask something.</p>`);

  } else if (o.kind === 'checkin') {
    // Asks privately BEFORE asking publicly. This is the step that protects
    // the seller's rating and gets unhappy buyers to the right place.
    subject = `Did ${o.productName} work out for you?`;
    html = wrap(
`<h2 style="margin:0 0 12px;font-size:19px">${hi}, honest question</h2>
 <p style="color:#555;margin:0 0 20px">You have had <strong>${o.productName}</strong> for about a week. Did it do what you needed?</p>
 <p style="margin:0 0 10px">
   <a href="${cfg.reviewUrl}" style="display:inline-block;background:#111;color:#fff;text-decoration:none;padding:12px 22px;border-radius:8px;font-weight:600">Yes — leave a review</a>
 </p>
 <p style="color:#555;margin:16px 0 0">
   <strong>If not</strong> — please reply to this email and tell me what went wrong. I would much rather fix it than have you quietly disappointed.
 </p>`);

  } else {
    subject = `Something else you might find useful`;
    html = wrap(
`<h2 style="margin:0 0 12px;font-size:19px">${hi}</h2>
 <p style="color:#555;margin:0 0 18px">${cfg.upsellText}</p>
 <p style="color:#777;font-size:13px;margin:0">Last email in this sequence — you will not hear from me about this again.</p>`);
  }

  return { json: { ...o, subject, html } };
});
""",
        (220, 520),
        notes="Four short messages. The check-in asks privately before asking publicly.",
    )

    send = wf.node(
        "📧 Send it",
        "n8n-nodes-base.emailSend",
        {
            "fromEmail": "={{ $json.__config.fromEmail }}",
            "toEmail": "={{ $json.email }}",
            "subject": "={{ $json.subject }}",
            "emailFormat": "html",
            "html": "={{ $json.html }}",
            "options": {},
        },
        2.1,
        (460, 520),
        retry=True,
        max_tries=3,
        wait_ms=3000,
        on_error="continueErrorOutput",
        notes="Attach SMTP. Batched upstream to protect sending reputation.",
    )

    summary = wf.code(
        "📊 Sequence summary",
        r"""
const s = $input.first().json;
return [{ json: {
  ts: new Date().toISOString(),
  activeSequences: s.activeSequences ?? 0,
  sentThisRun: s.sentThisRun ?? 0,
}}];
""",
        (220, 720),
        notes="Optional. Wire to a Sheet if you want a record.",
    )

    fail = wf.error_sink((700, 700), context="post-purchase-send")

    log = wf.code(
        "📒 Sequence log",
        r"""
return $input.all().map(i => ({ json: {
  ts: new Date().toISOString(),
  email: i.json.email ?? null,
  stage: i.json.stage ?? null,
  kind: i.json.kind ?? null,
  sent: !i.json.error,
}}));
""",
        (700, 520),
        notes="Track which stage people reach. A drop-off at one stage means that message needs rewriting.",
    )

    wf.chain(hook, cfg, guard, enrol, ack)
    wf.chain(sched, cfg2, advance, is_msg)
    wf.connect(is_msg, compose, out=0)
    wf.connect(is_msg, summary, out=1)
    wf.connect(compose, send)
    wf.connect(send, log, out=0)
    wf.connect(send, fail, out=1)
    wf.connect(fail, log)

    return wf
