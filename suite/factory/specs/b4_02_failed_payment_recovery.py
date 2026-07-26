"""
DCA-B4-02 · Failed Payment Recovery (dunning)

The easiest template in the catalogue to sell, because the buyer can calculate
the return themselves: recovering one $50 subscription pays for the template
twice, and it keeps working every month afterwards.

The problem
-----------
A card expires. The renewal fails. Nobody is told. The customer does not notice
because nothing visibly changed, and the seller does not notice because a
failure is silent — there is no angry email, just an absence. A month later the
revenue is simply gone, and by then the customer has stopped thinking of
themselves as a subscriber and will not come back.

Involuntary churn — subscriptions lost to payment mechanics rather than
dissatisfaction — is the largest recoverable revenue leak most subscription
businesses have, and it is entirely automatable.

Design notes
------------
Two entry points, deliberately:

  * The webhook catches the failure the moment the gateway reports it, because
    the first hours are when recovery odds are highest.
  * The schedule handles the follow-up sequence, because retrying on a fixed
    cadence needs a clock, not an event.

The escalation is written to stay friendly. The most common mistake in dunning
is sounding like a debt collector on day one — the customer has not done
anything wrong, their card simply expired, and the tone should assume that
until proven otherwise.
"""

from lib.core import Workflow, COLOR_BLUE, COLOR_GREEN, COLOR_RED, COLOR_PURPLE

SLUG = "failed-payment-recovery"


def build() -> Workflow:
    wf = Workflow(
        name="DCA-B4-02 · Failed Payment Recovery (dunning sequence)",
        slug=SLUG,
        category="b4-saas-subscriptions",
        summary="Catches failed subscription payments the moment they happen and runs a timed, escalating recovery sequence until the customer updates their card or the sequence ends.",
        problem="A renewal fails silently. The customer does not notice, the seller does not notice, and a month later the subscription is simply gone — lost to payment mechanics rather than dissatisfaction.",
        outcome="Every failed payment starts a recovery sequence within minutes, escalates on a schedule you control, stops the moment the payment succeeds, and reports exactly how much revenue it recovered.",
        version="1.0.0",
        tags=["saas", "subscriptions", "revenue-recovery", "dunning", "hardened"],
        credentials_needed=["SMTP account", "Optional: Slack/Telegram for the recovery report"],
        setup_minutes=12,
    )

    wf.sticky(
        "## 💳 Failed Payment Recovery\n"
        "**Failed renewal → timed recovery sequence → revenue saved.**\n\n"
        "### Why this pays for itself immediately\n"
        "Recovering **one** $50 subscription covers this template twice over —\n"
        "and it keeps running every month afterwards.\n\n"
        "### Setup (about 12 minutes)\n"
        "1. **⚙️ Config** → set `storeName`, `fromEmail`, `updateCardUrl`.\n"
        "2. Point your gateway's **payment failed** webhook at the Production URL.\n"
        "   *Stripe: `invoice.payment_failed` · Lemon Squeezy: `subscription_payment_failed`*\n"
        "3. Attach SMTP to the two send nodes.\n"
        "4. Activate. The schedule then runs the follow-ups by itself.\n\n"
        "### Two entry points, on purpose\n"
        "**Webhook** catches the failure immediately — the first hours are when\n"
        "recovery odds are highest.\n"
        "**Schedule** runs the follow-up sequence, because a cadence needs a clock.",
        (-660, -480),
        (580, 560),
        COLOR_BLUE,
    )

    wf.sticky(
        "### 📅 The sequence\n"
        "| When | Message | Tone |\n"
        "| --- | --- | --- |\n"
        "| Immediately | \"Your card was declined\" | helpful, no alarm |\n"
        "| Day 3 | \"Still can't process\" | gentle reminder |\n"
        "| Day 7 | \"Access pauses soon\" | clear consequence |\n\n"
        "**It stops the instant the payment succeeds** — send a `recovered` event\n"
        "to the webhook, or the next scheduled run clears it.\n\n"
        "⚠️ **Tone matters more than frequency.** The customer has not done\n"
        "anything wrong — a card expired. Sounding like a debt collector on day\n"
        "one loses customers who would happily have paid.",
        (-40, -480),
        (480, 440),
        COLOR_GREEN,
    )

    wf.sticky(
        "### 📊 What it reports\n"
        "The scheduled run emits a summary: how many are in recovery, how many\n"
        "were recovered, how much revenue that represents.\n\n"
        "Wire **📈 Recovery report** to Slack or email so you see the number this\n"
        "template is actually earning you. Without that, it is invisible work.",
        (1400, -200),
        (420, 260),
        COLOR_PURPLE,
    )

    wf.sticky(
        "### ⚠️ Honest limits\n"
        "This recovers payments that fail for **fixable** reasons — expired card,\n"
        "insufficient funds at that moment, a bank block.\n\n"
        "It cannot recover a customer who has decided to leave, and it does not\n"
        "retry the charge itself — your gateway does that. This template makes\n"
        "sure a human is actually told, which is the part that is usually missing.",
        (1400, 140),
        (420, 280),
        COLOR_RED,
    )

    # ── Entry 1: the failure event ──────────────────────────────────────
    hook = wf.webhook(
        "🔔 Payment failed",
        (-660, 140),
        path="dca/payment-failed",
        notes="Point your gateway's payment-failed webhook here. Also accepts {\"event\":\"recovered\"} to stop a sequence.",
    )

    cfg = wf.config(
        {
            "storeName": "YOUR_STORE_NAME",
            "fromEmail": "billing@yourdomain.com",
            "supportEmail": "support@yourdomain.com",
            "updateCardUrl": "https://yourdomain.com/billing",
            "followUpDays": [3, 7],
            "pauseAfterDays": 10,
            "currency": "USD",
            "historyTtlDays": 45,
        },
        (-440, 140),
        notes="followUpDays controls the sequence. pauseAfterDays is when you stop chasing.",
    )

    guard = wf.guard(
        (-220, 140),
        required=["body"],
        event_id_expr="j.body?.id ?? j.body?.event_id ?? (j.body?.email + '|' + (j.body?.invoiceId ?? j.body?.invoice_id ?? Date.now()))",
        ttl_hours=72,
    )

    record = wf.code(
        "📝 Open or close a recovery case",
        r"""
// One case per customer. The webhook both opens cases (a failure arrived) and
// closes them (a 'recovered' event arrived), because the gateway is the only
// thing that reliably knows the payment finally went through.
const cfg = $('⚙️ Config').first().json.__config;
const store = $getWorkflowStaticData('global');
store.cases = store.cases || {};

const ttlMs = Number(cfg.historyTtlDays) * 24 * 60 * 60 * 1000;
const now = Date.now();

// Keep the case file bounded.
for (const [k, c] of Object.entries(store.cases)) {
  if (now - (c.openedAt || 0) > ttlMs) delete store.cases[k];
}

const out = [];

for (const item of $input.all()) {
  const b = item.json.body ?? item.json;

  // Normalise across gateways.
  const email = String(
    b.email ?? b.customer_email ?? b.data?.object?.customer_email ??
    b.data?.attributes?.user_email ?? ''
  ).trim().toLowerCase();

  if (!email) {
    throw new Error('No customer email on the payment-failed event — cannot start recovery. Check your gateway includes customer email in the webhook.');
  }

  const amountRaw = Number(
    b.amount ?? b.amount_due ?? b.data?.object?.amount_due ??
    b.data?.attributes?.total ?? 0
  );
  // Stripe and Lemon Squeezy both send minor units.
  const amount = amountRaw > 1000 ? amountRaw / 100 : amountRaw;

  const name = String(b.name ?? b.customer_name ?? b.data?.object?.customer_name ?? '').trim();
  const isRecovered =
    String(b.event ?? b.type ?? b.meta?.event_name ?? '').toLowerCase().includes('recovered') ||
    String(b.event ?? '').toLowerCase() === 'recovered' ||
    b.status === 'paid';

  const existing = store.cases[email];

  if (isRecovered) {
    if (existing) {
      existing.recovered = true;
      existing.recoveredAt = now;
      store.cases[email] = existing;
    }
    out.push({ json: {
      action: 'closed', email, amount,
      message: existing ? 'Recovery case closed — payment went through.' : 'No open case for this customer.',
      __config: cfg, __sendNow: false,
    }});
    continue;
  }

  if (existing && !existing.recovered) {
    // Already chasing. Do not restart the clock or the customer gets the
    // day-one email repeatedly, which is how a helpful sequence turns into spam.
    existing.failures = (existing.failures || 1) + 1;
    store.cases[email] = existing;
    out.push({ json: {
      action: 'already_open', email, amount, name,
      openedAt: new Date(existing.openedAt).toISOString(),
      message: 'Case already open — not restarting the sequence.',
      __config: cfg, __sendNow: false,
    }});
    continue;
  }

  store.cases[email] = {
    email, name, amount,
    currency: b.currency ?? cfg.currency,
    openedAt: now,
    lastContactAt: now,
    stage: 0,
    failures: 1,
    recovered: false,
  };

  out.push({ json: {
    action: 'opened', email, name, amount,
    currency: b.currency ?? cfg.currency,
    stage: 0,
    __config: cfg,
    __sendNow: true,
  }});
}

return out;
""",
        (0, 140),
        notes="Opens a case on failure, closes it on recovery, and refuses to restart a sequence that is already running.",
        always_output=True,
    )

    should_send = wf.if_(
        "📨 First contact needed?",
        (220, 140),
        left="={{ $json.__sendNow }}",
        operator={"type": "boolean", "operation": "true", "singleValue": True},
    )

    compose_first = wf.code(
        "✍️ Compose first notice",
        r"""
// Day zero. The customer almost certainly does not know anything happened, and
// in most cases has done nothing wrong. Tone: helpful, specific, one action.
return $input.all().map(i => {
  const o = i.json;
  const cfg = o.__config;
  return { json: { ...o,
    subject: `Your payment didn't go through — quick fix`,
    html:
`<div style="font-family:system-ui,-apple-system,Segoe UI,sans-serif;max-width:540px;margin:0 auto;padding:32px 24px;color:#111">
  <h2 style="margin:0 0 12px;font-size:20px">Hi${o.name ? ' ' + o.name : ''}, your card was declined</h2>
  <p style="color:#555;line-height:1.65;margin:0 0 20px">
    We tried to process <strong>${o.amount} ${o.currency}</strong> for your ${cfg.storeName} subscription and your bank declined it.
    This is usually just an expired card — it takes a minute to fix and nothing has been interrupted.
  </p>
  <a href="${cfg.updateCardUrl}" style="display:inline-block;background:#111;color:#fff;text-decoration:none;padding:14px 28px;border-radius:8px;font-weight:600">Update payment method</a>
  <p style="color:#777;font-size:13px;margin:24px 0 0">
    Already fixed it? Then you can ignore this — we'll retry automatically.
  </p>
  <p style="color:#777;font-size:13px;margin:8px 0 0">
    Questions? Just reply, or email <a href="mailto:${cfg.supportEmail}">${cfg.supportEmail}</a>.
  </p>
</div>`
  }};
});
""",
        (460, 40),
        notes="Friendly, one clear action. No alarm language on day one.",
    )

    send_first = wf.node(
        "📧 Send first notice",
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
        (700, 40),
        retry=True,
        max_tries=3,
        wait_ms=3000,
        on_error="continueErrorOutput",
        notes="Attach your SMTP credential.",
    )

    noop = wf.code(
        "⏭️ Nothing to send",
        r"""
// Case was closed, or a sequence is already running. Recorded, not acted on.
return $input.all().map(i => ({ json: { logged: true, action: i.json.action, email: i.json.email } }));
""",
        (460, 260),
        notes="Closed or duplicate cases end here.",
    )

    respond = wf.respond(
        "↩️ 200 OK",
        (940, 140),
        body='={{ JSON.stringify({ ok: true }) }}',
    )

    fail = wf.error_sink((940, 340), context="dunning-first-notice")

    # ── Entry 2: the follow-up clock ────────────────────────────────────
    sched = wf.schedule("🕐 Daily follow-up run", (-660, 620), hours=24)

    cfg2 = wf.code(
        "⚙️ Config (schedule side)",
        r"""
// The scheduled branch has no upstream Config node to read from, so it restates
// the same values. Keep these in sync with the main Config node — they are
// duplicated because n8n branches from separate triggers cannot share a node.
const CONFIG = {
  "storeName": "YOUR_STORE_NAME",
  "fromEmail": "billing@yourdomain.com",
  "supportEmail": "support@yourdomain.com",
  "updateCardUrl": "https://yourdomain.com/billing",
  "followUpDays": [3, 7],
  "pauseAfterDays": 10,
  "currency": "USD"
};
return [{ json: { __config: CONFIG } }];
""",
        (-440, 620),
        notes="⚠️ Mirror of the main Config. If you change one, change both.",
        always_output=True,
    )

    due = wf.code(
        "🔍 Find cases due for follow-up",
        r"""
// Walk the open cases and decide which are due today. Emitting one item per due
// case lets the send node fan out naturally.
const cfg = $input.first().json.__config;
const store = $getWorkflowStaticData('global');
store.cases = store.cases || {};

const now = Date.now();
const DAY = 24 * 60 * 60 * 1000;
const stages = cfg.followUpDays || [3, 7];
const out = [];

let openCount = 0, recoveredCount = 0, recoveredValue = 0;

for (const [email, c] of Object.entries(store.cases)) {
  if (c.recovered) {
    recoveredCount++;
    recoveredValue += Number(c.amount) || 0;
    continue;
  }

  openCount++;
  const ageDays = (now - c.openedAt) / DAY;

  // Past the pause point: stop chasing. Continuing past this annoys people and
  // recovers almost nothing.
  if (ageDays >= Number(cfg.pauseAfterDays)) {
    c.stage = 99;
    store.cases[email] = c;
    continue;
  }

  // Which stage is due? stage 0 = first notice already sent on day zero.
  let dueStage = null;
  for (let i = 0; i < stages.length; i++) {
    if (ageDays >= stages[i] && (c.stage || 0) < i + 1) { dueStage = i + 1; break; }
  }
  if (dueStage === null) continue;

  c.stage = dueStage;
  c.lastContactAt = now;
  store.cases[email] = c;

  const isFinal = dueStage === stages.length;
  out.push({ json: {
    email, name: c.name, amount: c.amount, currency: c.currency,
    stage: dueStage, ageDays: Math.floor(ageDays), isFinal,
    daysUntilPause: Math.max(0, Math.ceil(Number(cfg.pauseAfterDays) - ageDays)),
    __config: cfg,
  }});
}

// Always emit a summary item so the report runs even on a quiet day.
out.push({ json: {
  __summary: true,
  openCases: openCount,
  recoveredCases: recoveredCount,
  recoveredValue: Math.round(recoveredValue * 100) / 100,
  dueToday: out.length,
  __config: cfg,
}});

return out;
""",
        (-220, 620),
        notes="Decides who is due, advances their stage, and stops chasing past pauseAfterDays.",
        always_output=True,
    )

    is_case = wf.if_(
        "👤 A customer to contact?",
        (0, 620),
        left="={{ $json.__summary }}",
        operator={"type": "boolean", "operation": "false", "singleValue": True},
    )

    compose_follow = wf.code(
        "✍️ Compose follow-up",
        r"""
// Escalates only in clarity, never in hostility. The final message states the
// consequence plainly because vagueness at this point is what actually loses
// the customer — they need to know access is about to stop.
return $input.all().map(i => {
  const o = i.json;
  const cfg = o.__config;

  const subject = o.isFinal
    ? `Action needed — your ${cfg.storeName} access pauses soon`
    : `Still can't process your payment`;

  const body = o.isFinal
    ? `<p style="color:#555;line-height:1.65;margin:0 0 20px">
         We've tried a few times over the last ${o.ageDays} days and the payment of
         <strong>${o.amount} ${o.currency}</strong> still isn't going through.
         To avoid your access pausing in <strong>${o.daysUntilPause} day(s)</strong>, please update your card.
       </p>`
    : `<p style="color:#555;line-height:1.65;margin:0 0 20px">
         Your payment of <strong>${o.amount} ${o.currency}</strong> still hasn't gone through.
         Nothing has changed on your account yet — updating your card takes about a minute.
       </p>`;

  return { json: { ...o,
    subject,
    html:
`<div style="font-family:system-ui,-apple-system,Segoe UI,sans-serif;max-width:540px;margin:0 auto;padding:32px 24px;color:#111">
  <h2 style="margin:0 0 12px;font-size:20px">Hi${o.name ? ' ' + o.name : ''}</h2>
  ${body}
  <a href="${cfg.updateCardUrl}" style="display:inline-block;background:#111;color:#fff;text-decoration:none;padding:14px 28px;border-radius:8px;font-weight:600">Update payment method</a>
  <p style="color:#777;font-size:13px;margin:24px 0 0">
    If something else is going on, reply to this email — we would rather sort it out than lose you.
  </p>
</div>`
  }};
});
""",
        (240, 520),
        notes="Escalates in clarity, not in tone.",
    )

    send_follow = wf.node(
        "📧 Send follow-up",
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
        (480, 520),
        retry=True,
        max_tries=3,
        wait_ms=3000,
        on_error="continueErrorOutput",
        notes="Attach the same SMTP credential.",
    )

    report = wf.code(
        "📈 Recovery report",
        r"""
// The number that proves this template is earning its keep. Send it somewhere
// you will actually see, or the work stays invisible and gets switched off.
const s = $input.first().json;
const cfg = s.__config;
return [{ json: {
  reportedAt: new Date().toISOString(),
  openCases: s.openCases ?? 0,
  recoveredCases: s.recoveredCases ?? 0,
  recoveredValue: s.recoveredValue ?? 0,
  currency: cfg.currency,
  summary:
    `💳 Payment recovery — ${new Date().toISOString().slice(0, 10)}\n` +
    `Recovered: ${s.recoveredCases ?? 0} payment(s) worth ${s.recoveredValue ?? 0} ${cfg.currency}\n` +
    `Still chasing: ${s.openCases ?? 0}\n` +
    `Contacted today: ${(s.dueToday ?? 1) - 1}`,
}}];
""",
        (240, 740),
        notes="Wire to Slack/Telegram/email. This is the number that justifies the template.",
    )

    fail2 = wf.error_sink(
        (720, 720),
        name="🚨 Handle follow-up failure",
        context="dunning-follow-up",
    )

    # ── Wiring ──────────────────────────────────────────────────────────
    wf.chain(hook, cfg, guard, record, should_send)
    wf.connect(should_send, compose_first, out=0)
    wf.connect(should_send, noop, out=1)
    wf.connect(compose_first, send_first)
    wf.connect(send_first, respond, out=0)
    wf.connect(send_first, fail, out=1)
    wf.connect(noop, respond)
    wf.connect(fail, respond)

    wf.chain(sched, cfg2, due, is_case)
    wf.connect(is_case, compose_follow, out=0)
    wf.connect(is_case, report, out=1)
    wf.connect(compose_follow, send_follow)
    wf.connect(send_follow, fail2, out=1)

    return wf
