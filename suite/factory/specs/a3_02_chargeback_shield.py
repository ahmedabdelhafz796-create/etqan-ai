"""
DCA-A3-02 · Chargeback Early Warning & Evidence Builder

Partner to A3-01. That one screens orders before delivery; this one handles what
happens when a dispute is filed anyway.

Two jobs, and the second is the one nobody automates
----------------------------------------------------
**Warn early.** Card networks emit fraud alerts before a formal dispute exists.
Refunding inside that window costs the sale but avoids the dispute fee *and*
keeps the chargeback off the ratio that gets payment accounts frozen — which is
usually the far larger cost.

**Assemble evidence automatically.** Most disputes are lost by default, not
argued and lost. The seller has 7–21 days to respond, the deadline passes in a
busy week, and the money leaves. Digital goods are the worst case here, because
"the customer received the product" has to be proven with delivery logs, IP
records and download timestamps that nobody thinks to collect until they are
needed — by which point the link has expired and the log has rolled over.

So this template builds the evidence pack the moment the alert arrives, while
the records still exist.

The ratio is the real risk
--------------------------
Sellers focus on the disputed amount. The number that actually ends businesses
is the chargeback *rate*: cross roughly 1% and processors impose monitoring
programmes, hold reserves, or close the account. This template tracks the
running rate and warns before that threshold, because at that point losing the
account costs far more than any individual dispute.
"""

from lib.core import Workflow, COLOR_BLUE, COLOR_GREEN, COLOR_RED, COLOR_PURPLE

SLUG = "chargeback-early-warning"


def build() -> Workflow:
    wf = Workflow(
        name="DCA-A3-02 · Chargeback Early Warning & Evidence Builder",
        slug=SLUG,
        category="a3-fraud-security",
        summary="Catches fraud alerts before they become formal disputes, recommends refund-or-fight with reasoning, assembles the evidence pack automatically, and tracks the chargeback ratio that gets payment accounts closed.",
        problem="Most disputes are lost by default rather than argued — the response deadline passes during a busy week. And for digital goods the evidence needed to win has usually expired by the time anyone looks for it.",
        outcome="Every alert produces a deadline, a recommendation with reasoning, and a ready-to-submit evidence pack — plus a running chargeback ratio so you see the account-closing risk coming.",
        version="1.0.0",
        tags=["fraud", "chargeback", "disputes", "digital-products", "hardened"],
        credentials_needed=["SMTP or Slack for alerts", "Optional: your order log for evidence lookup"],
        setup_minutes=15,
    )

    wf.sticky(
        "## 🛡️ Chargeback Early Warning\n"
        "**Alert arrives → evidence assembled → recommendation with reasoning.**\n\n"
        "### Setup (about 15 minutes)\n"
        "1. **⚙️ Config** → `storeName`, `alertEmail`, `monthlyOrderCount`.\n"
        "2. Point these gateway webhooks at the Production URL:\n"
        "   - Stripe: `radar.early_fraud_warning.created`, `charge.dispute.created`\n"
        "   - PayPal: `CUSTOMER.DISPUTE.CREATED`\n"
        "   - Paddle / Lemon Squeezy: their dispute events\n"
        "3. Attach SMTP to **📨 Send the alert**.\n"
        "4. Activate.\n\n"
        "### Pairs with A3-01\n"
        "A3-01 stops fraud **before** delivery. This handles what gets through.\n"
        "Run both — screening alone never catches everything.",
        (-680, -520),
        (600, 540),
        COLOR_BLUE,
    )

    wf.sticky(
        "### ⚡ Why the early window matters\n"
        "Card networks emit a fraud alert **before** a formal dispute exists.\n\n"
        "Refunding inside that window costs you the sale — but avoids the dispute\n"
        "fee **and keeps the chargeback off your ratio**.\n\n"
        "That second part is usually worth far more than the sale itself.",
        (-40, -520),
        (460, 300),
        COLOR_GREEN,
    )

    wf.sticky(
        "### 📈 The ratio is the real risk\n"
        "Sellers watch the disputed amount. The number that ends businesses is the\n"
        "chargeback **rate**.\n\n"
        "Cross roughly **1%** and processors impose monitoring programmes, hold\n"
        "reserves, or close the account entirely.\n\n"
        "This tracks your running rate and warns **before** that line — because\n"
        "losing your payment account costs more than every dispute combined.\n\n"
        "⚠️ Set `monthlyOrderCount` honestly or the rate is meaningless.",
        (-40, -180),
        (460, 340),
        COLOR_RED,
    )

    wf.sticky(
        "### 📁 The evidence pack\n"
        "Built the moment the alert lands, **while the records still exist**.\n\n"
        "For digital goods you must prove the customer received the product:\n"
        "delivery timestamp · download IP · download count · link expiry ·\n"
        "the terms they accepted.\n\n"
        "Wire **📁 Build evidence pack** to your order log (A1-01 writes exactly\n"
        "this shape) so it fills in automatically.\n\n"
        "⚠️ **Honest note:** a strong pack improves your odds. Nothing wins a\n"
        "dispute reliably — the issuer decides, and they favour the cardholder.",
        (940, -520),
        (480, 400),
        COLOR_PURPLE,
    )

    hook = wf.webhook(
        "⚠️ Fraud alert / dispute",
        (-680, 180),
        path="dca/chargeback",
        notes="Point your gateway's fraud-warning and dispute webhooks here.",
    )

    cfg = wf.config(
        {
            "storeName": "YOUR_STORE_NAME",
            "alertEmail": "you@yourdomain.com",
            "fromEmail": "alerts@yourdomain.com",
            "monthlyOrderCount": 100,
            "ratioWarnAt": 0.005,
            "ratioCriticalAt": 0.0075,
            "autoRefundUnder": 0,
            "termsUrl": "https://yourdomain.com/terms",
            "responseDays": 7,
            "historyTtlDays": 90,
        },
        (-460, 180),
        notes="monthlyOrderCount drives the ratio. ratioWarnAt 0.005 = 0.5%, half the danger line.",
    )

    guard = wf.guard(
        (-240, 180),
        required=["body"],
        event_id_expr="j.body?.id ?? j.body?.data?.object?.id ?? j.body?.dispute_id ?? j.body?.resource?.dispute_id",
        ttl_hours=168,
    )

    normalise = wf.code(
        "🔄 Normalise the alert",
        r"""
// Gateways disagree on everything here — field names, amount units, and most
// importantly on whether this is an early warning or an actual dispute. That
// distinction drives the whole recommendation, so it is resolved once, here.
const cfg = $('⚙️ Config').first().json.__config;
const out = [];

for (const item of $input.all()) {
  const b = item.json.body ?? item.json;
  const type = String(b.type ?? b.event_type ?? b.meta?.event_name ?? '').toLowerCase();
  const d = b.data?.object ?? b.resource ?? b.data?.attributes ?? b;

  // An early fraud warning is a chance to act. A dispute is a deadline.
  const isEarlyWarning =
    type.includes('early_fraud') || type.includes('fraud_warning') ||
    String(b.alert_type ?? '').toLowerCase().includes('fraud');

  const isDispute =
    type.includes('dispute') || type.includes('chargeback') || !!d.reason;

  const amountRaw = Number(d.amount ?? d.disputed_amount?.value ?? d.total ?? 0);
  const amount = amountRaw > 1000 ? amountRaw / 100 : amountRaw;

  const reason = String(d.reason ?? d.reason_code ?? b.reason ?? 'unknown');

  // Deadline: use the gateway's if given, else assume the shorter end of the
  // typical 7-21 day window. Assuming short is the safe direction to be wrong.
  const dueTs = d.evidence_details?.due_by
    ? Number(d.evidence_details.due_by) * 1000
    : Date.now() + Number(cfg.responseDays) * 24 * 60 * 60 * 1000;

  out.push({ json: {
    alertId: item.json.__eventId,
    kind: isEarlyWarning ? 'early_warning' : (isDispute ? 'dispute' : 'unknown'),
    chargeId: d.charge ?? d.id ?? d.transaction_id ?? null,
    orderId: d.metadata?.order_id ?? d.invoice ?? d.order_id ?? null,
    email: d.customer_email ?? d.billing_details?.email ?? b.email ?? null,
    amount,
    currency: String(d.currency ?? 'USD').toUpperCase(),
    reason,
    // Friendly-fraud reasons are the ones worth fighting for digital goods,
    // because delivery evidence directly contradicts "I never got it".
    reasonIsFightable: /product_not_received|not_received|unrecognized|subscription_canceled|duplicate|product_unacceptable/i.test(reason),
    dueBy: new Date(dueTs).toISOString(),
    hoursToRespond: Math.max(0, Math.round((dueTs - Date.now()) / 3600000)),
    receivedAt: new Date().toISOString(),
    __config: cfg,
  }});
}

return out;
""",
        (0, 180),
        notes="Separates early warnings from formal disputes — that distinction drives everything downstream.",
    )

    ratio = wf.code(
        "📈 Track the chargeback ratio",
        r"""
// Rolling 30-day count against declared monthly volume. This is the number that
// decides whether the seller keeps a payment account at all.
const store = $getWorkflowStaticData('global');
store.chargebacks = store.chargebacks || [];

const now = Date.now();
const DAY = 24 * 60 * 60 * 1000;

return $input.all().map(i => {
  const o = i.json;
  const cfg = o.__config;

  store.chargebacks = store.chargebacks
    .filter(c => now - c.t < Number(cfg.historyTtlDays) * DAY)
    .slice(-1000);

  // Early warnings are counted separately: acting on them is precisely how you
  // keep them OUT of the ratio, so counting them as chargebacks would punish
  // the seller for the behaviour we want.
  if (o.kind === 'dispute') {
    store.chargebacks.push({ t: now, amount: o.amount, id: o.alertId });
  }

  const last30 = store.chargebacks.filter(c => now - c.t < 30 * DAY);
  const monthly = Math.max(1, Number(cfg.monthlyOrderCount));
  const rate = last30.length / monthly;

  let ratioStatus = 'ok';
  if (rate >= Number(cfg.ratioCriticalAt)) ratioStatus = 'critical';
  else if (rate >= Number(cfg.ratioWarnAt)) ratioStatus = 'warning';

  return { json: { ...o,
    disputes30d: last30.length,
    disputedValue30d: Math.round(last30.reduce((s, c) => s + (c.amount || 0), 0) * 100) / 100,
    chargebackRate: Math.round(rate * 10000) / 100,   // percent, 2dp
    ratioStatus,
  }};
});
""",
        (240, 180),
        notes="Early warnings are excluded from the ratio on purpose — acting on them is how you keep them out.",
        always_output=True,
    )

    evidence = wf.code(
        "📁 Build evidence pack",
        r"""
// Assemble the pack now, while the records still exist. For digital goods the
// central claim is "the customer received and used the product", and the proof
// for that expires: links lapse, logs roll over, download counters reset.
//
// The lookup fields are left empty and clearly labelled rather than invented —
// a fabricated evidence pack is worse than none, because submitting one you
// cannot support damages your standing with the processor.
return $input.all().map(i => {
  const o = i.json;
  const cfg = o.__config;

  const recommendation = (() => {
    if (o.kind === 'early_warning') {
      return {
        action: 'refund_now',
        confidence: 'high',
        why: 'This is a fraud warning, not yet a dispute. Refunding now costs the sale but avoids the dispute fee AND keeps it off your chargeback ratio — usually worth far more than the sale.',
      };
    }
    if (o.amount > 0 && o.amount <= Number(cfg.autoRefundUnder)) {
      return {
        action: 'refund_now',
        confidence: 'high',
        why: `Disputed amount (${o.amount}) is at or below your autoRefundUnder threshold. Fighting costs more in time than the amount at stake.`,
      };
    }
    if (o.reasonIsFightable) {
      return {
        action: 'fight_with_evidence',
        confidence: 'medium',
        why: `Reason "${o.reason}" is contradicted by delivery evidence. Fill the pack below and submit before the deadline.`,
      };
    }
    return {
      action: 'review_manually',
      confidence: 'low',
      why: `Reason "${o.reason}" is not one delivery records reliably rebut. Judge this one yourself.`,
    };
  })();

  return { json: { ...o,
    recommendation,
    evidencePack: {
      // Fill these from your order log. A1-01 writes exactly this shape.
      productDescription: '⚠️ FILL: what was sold',
      deliveryTimestamp: '⚠️ FILL from order log: when the link was sent',
      deliveryEmail: o.email || '⚠️ FILL: buyer email',
      downloadIp: '⚠️ FILL from download log: IP that collected the file',
      downloadCount: '⚠️ FILL from download log: times it was downloaded',
      downloadTimestamp: '⚠️ FILL from download log: when',
      linkExpiry: '⚠️ FILL: when access expired',
      customerCommunication: '⚠️ FILL: any support thread with this buyer',
      refundPolicyUrl: cfg.termsUrl,
      termsAcceptedAt: '⚠️ FILL: when they accepted terms at checkout',
      note: 'Submit only what you can actually evidence. A pack you cannot support is worse than a thin one.',
    },
  }};
});
""",
        (480, 180),
        notes="Recommendation carries its reasoning. Evidence fields are labelled, never invented.",
    )

    compose = wf.code(
        "✍️ Compose the alert",
        r"""
// One message that a busy person can act on immediately: what happened, how
// long they have, what to do, and whether the account-level risk is rising.
return $input.all().map(i => {
  const o = i.json;
  const r = o.recommendation;

  const urgency = o.hoursToRespond < 48 ? '🔴 URGENT' : (o.kind === 'early_warning' ? '🟡 ACT NOW' : '🟠');

  const ratioLine =
    o.ratioStatus === 'critical'
      ? `\n🚨 CHARGEBACK RATE ${o.chargebackRate}% — ABOVE YOUR CRITICAL LINE.\n   Processors close accounts over this. Address it now.`
      : o.ratioStatus === 'warning'
        ? `\n⚠️ Chargeback rate ${o.chargebackRate}% — approaching the danger zone.`
        : `\nChargeback rate: ${o.chargebackRate}% (${o.disputes30d} in 30 days)`;

  const text =
`${urgency} ${o.kind === 'early_warning' ? 'FRAUD WARNING' : 'DISPUTE OPENED'}

Amount:   ${o.amount} ${o.currency}
Order:    ${o.orderId || '(not supplied)'}
Buyer:    ${o.email || '(not supplied)'}
Reason:   ${o.reason}
Deadline: ${o.dueBy}  (${o.hoursToRespond}h left)

── RECOMMENDATION ──────────────────
${r.action.replace(/_/g, ' ').toUpperCase()}  (confidence: ${r.confidence})
${r.why}
${ratioLine}

── EVIDENCE PACK ───────────────────
Fill the ⚠️ fields from your order and download logs, then submit through
your gateway's dispute form BEFORE the deadline above.

${JSON.stringify(o.evidencePack, null, 2)}

Note: most disputes are lost by default, not argued and lost. Responding at
all puts you ahead of the majority.`;

  return { json: { ...o, alertText: text, subject: `${urgency} ${o.kind === 'early_warning' ? 'Fraud warning' : 'Dispute'} — ${o.amount} ${o.currency}` } };
});
""",
        (720, 180),
        notes="A single actionable message: what, deadline, recommendation, ratio, evidence.",
    )

    send = wf.node(
        "📨 Send the alert",
        "n8n-nodes-base.emailSend",
        {
            "fromEmail": "={{ $json.__config.fromEmail }}",
            "toEmail": "={{ $json.__config.alertEmail }}",
            "subject": "={{ $json.subject }}",
            "emailFormat": "text",
            "text": "={{ $json.alertText }}",
            "options": {},
        },
        2.1,
        (960, 180),
        retry=True,
        max_tries=3,
        wait_ms=3000,
        on_error="continueErrorOutput",
        notes="Attach SMTP. Swap for Slack/Telegram if you prefer.",
    )

    log = wf.code(
        "📒 Dispute log",
        r"""
// Your record of what was disputed, what you decided, and how the ratio moved.
// Keep it — processors sometimes ask how you handle disputes, and a log is the
// difference between a conversation and a closed account.
return $input.all().map(i => ({ json: {
  ts: new Date().toISOString(),
  alertId: i.json.alertId,
  kind: i.json.kind,
  orderId: i.json.orderId,
  amount: i.json.amount,
  currency: i.json.currency,
  reason: i.json.reason,
  recommendedAction: i.json.recommendation?.action,
  dueBy: i.json.dueBy,
  chargebackRate: i.json.chargebackRate,
  ratioStatus: i.json.ratioStatus,
}}));
""",
        (1200, 180),
        notes="Append to Sheets/Airtable. This log is worth keeping.",
    )

    fail = wf.error_sink((960, 400), context="chargeback-alert")

    respond = wf.respond(
        "↩️ 200 OK",
        (1440, 180),
        body='={{ JSON.stringify({ ok: true, kind: $json.kind, action: $json.recommendedAction }) }}',
    )

    wf.chain(hook, cfg, guard, normalise, ratio, evidence, compose, send)
    wf.connect(send, log, out=0)
    wf.connect(send, fail, out=1)
    wf.connect(log, respond)
    wf.connect(fail, respond)

    return wf
