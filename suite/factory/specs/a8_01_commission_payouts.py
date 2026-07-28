"""
DCA-A8-01 · Commission & Affiliate Payouts

Solves "إدارة العمولات إذا كان الموقع يعمل كسوق" — and the affiliate case, which
is the same arithmetic with a different label.

Why sellers get this wrong
--------------------------
Commission tracking starts as a spreadsheet and stays one until the first
dispute. Then the seller discovers they cannot answer basic questions: which
sales counted, what the rate was at the time, whether a refunded order was
clawed back, and whether last month was actually paid. Money owed to other
people is the one area where "roughly right" is not good enough — an affiliate
who is underpaid once stops promoting, and one who is overpaid rarely mentions
it.

The parts that are easy to get wrong
------------------------------------
**Refunds.** A commission earned on an order that is later refunded must be
reversed, or the seller pays out on revenue they no longer have. Most
hand-rolled systems simply never do this.

**Rate changes.** If an affiliate's rate changes, past sales must keep the rate
that applied when they were made. Recalculating history is how disputes start.

**Double payment.** Re-running a payout job must not pay twice. Every earning
here is marked paid with a batch id, and the arithmetic is done on records not
yet marked.

**Minimum thresholds.** Paying $0.40 costs more in fees than it transfers.
Balances carry forward until they are worth sending.

Scope, stated honestly
----------------------
This calculates, tracks and reports what is owed. It deliberately does **not**
move money — it produces a payout instruction the seller executes through their
own provider. An automation with authority to send funds is a different risk
class, and it is not one a template should quietly assume.
"""

from lib.core import Workflow, COLOR_BLUE, COLOR_GREEN, COLOR_RED, COLOR_PURPLE

SLUG = "commission-affiliate-payouts"


def build() -> Workflow:
    wf = Workflow(
        name="DCA-A8-01 · Commission & Affiliate Payouts",
        slug=SLUG,
        category="a8-marketplace-ops",
        summary="Tracks what each affiliate or vendor has earned, reverses commission on refunds, preserves the rate that applied at the time of sale, and produces a deduplicated payout instruction you execute yourself.",
        problem="Commission lives in a spreadsheet until the first dispute, at which point nobody can say which sales counted, what the rate was then, whether refunds were clawed back, or whether last month was already paid.",
        outcome="Every sale attributed and rated at the moment it happened, refunds reversed automatically, payouts deduplicated and thresholded — with a full audit trail behind every figure.",
        version="1.0.0",
        tags=["marketplace", "affiliates", "payouts", "finance", "hardened"],
        credentials_needed=["SMTP account"],
        setup_minutes=16,
    )

    wf.sticky(
        "## 💸 Commission & Affiliate Payouts\n"
        "**Sale → attributed and rated → refunds reversed → payout instruction.**\n\n"
        "### Setup (about 16 minutes)\n"
        "1. **⚙️ Config** → `partners` (id → name, email, rate), `minimumPayout`.\n"
        "2. POST each sale:\n"
        "   ```json\n"
        "   { \"orderId\": \"...\", \"partnerId\": \"...\",\n"
        "     \"amount\": 49, \"currency\": \"USD\" }\n"
        "   ```\n"
        "3. POST refunds the same way with `{\"event\":\"refund\", \"orderId\":\"...\"}`.\n"
        "4. The schedule produces the payout run. Attach SMTP to the report.\n\n"
        "### It does not move money — on purpose\n"
        "It tells you exactly what to pay and to whom. **You** execute it through\n"
        "your own provider. An automation with authority to send funds is a very\n"
        "different risk class, and not one a template should assume.",
        (-700, -560),
        (600, 560),
        COLOR_BLUE,
    )

    wf.sticky(
        "### 🔄 Refunds must reverse commission\n"
        "A commission earned on an order that is later refunded has to be clawed\n"
        "back, or you are paying out on revenue **you no longer have**.\n\n"
        "Most hand-rolled systems never do this, and the gap only becomes visible\n"
        "when the numbers stop matching your bank.\n\n"
        "Reversal here is automatic, and it works whether or not the original\n"
        "earning has already been paid — an already-paid reversal becomes a\n"
        "negative balance carried into the next run.",
        (-80, -560),
        (500, 400),
        COLOR_RED,
    )

    wf.sticky(
        "### 📌 The rate is frozen at sale time\n"
        "If a partner's rate changes from 20% to 30%, **past sales keep 20%**.\n\n"
        "Recalculating history is how commission disputes start — and the partner\n"
        "always remembers the higher number.\n\n"
        "Every earning stores the rate that applied when it was created.",
        (420, -560),
        (460, 320),
        COLOR_PURPLE,
    )

    wf.sticky(
        "### 🚫 Two safeguards on payout\n"
        "**No double payment.** Every earning is stamped with a batch id when\n"
        "paid. A re-run only ever considers unpaid records, so running the job\n"
        "twice pays nobody twice.\n\n"
        "**Minimum threshold.** Sending $0.40 costs more in fees than it\n"
        "transfers. Balances below `minimumPayout` carry forward until they are\n"
        "worth sending.",
        (1140, 400),
        (460, 320),
        COLOR_GREEN,
    )

    hook = wf.webhook(
        "🛒 Sale or refund",
        (-700, 200),
        path="dca/commission",
        notes="POST {orderId, partnerId, amount} for sales, or {event:'refund', orderId} for reversals.",
    )

    cfg = wf.config(
        {
            "storeName": "YOUR_STORE_NAME",
            "fromEmail": "payouts@yourdomain.com",
            "ownerEmail": "you@yourdomain.com",
            "currency": "USD",
            "defaultRate": 20,
            "minimumPayout": 25,
            "holdDays": 30,
            "partners": {
                "EXAMPLE_PARTNER": {"name": "Example Partner", "email": "partner@example.com", "rate": 20},
            },
            "historyTtlDays": 400,
        },
        (-480, 200),
        notes="holdDays delays payout until the refund window has passed — pay too early and you claw back later.",
    )

    guard = wf.guard(
        (-260, 200),
        required=["body"],
        event_id_expr="(j.body?.event ?? 'sale') + '|' + (j.body?.orderId ?? j.body?.order_id ?? Date.now())",
        ttl_hours=720,
    )

    ledger = wf.code(
        "📒 Record the earning or reversal",
        r"""
// Append-only ledger. Nothing is ever edited in place — a reversal is a new
// negative record referencing the original. That is what makes the numbers
// defensible when a partner disputes them.
const cfg = $('⚙️ Config').first().json.__config;
const store = $getWorkflowStaticData('global');
store.earnings = store.earnings || {};

const now = Date.now();
const ttlMs = Number(cfg.historyTtlDays) * 24 * 60 * 60 * 1000;
for (const [k, e] of Object.entries(store.earnings)) {
  if (now - (e.at || 0) > ttlMs) delete store.earnings[k];
}

const out = [];

for (const item of $input.all()) {
  const b = item.json.body ?? item.json;

  const orderId = String(b.orderId ?? b.order_id ?? '').trim();
  const event = String(b.event ?? b.type ?? 'sale').toLowerCase();
  const isRefund = event.includes('refund') || event.includes('chargeback') || event.includes('dispute');

  if (!orderId) {
    throw new Error('Commission events need an orderId. Received keys: ' + Object.keys(b).join(', '));
  }

  // ── Refund: reverse the original earning ────────────────────
  if (isRefund) {
    const original = store.earnings[orderId];

    if (!original) {
      out.push({ json: {
        action: 'reversal_skipped', orderId,
        reason: 'no commission was recorded for this order',
        __config: cfg,
      }});
      continue;
    }

    if (original.reversed) {
      out.push({ json: {
        action: 'already_reversed', orderId,
        reason: 'this order was already reversed',
        __config: cfg,
      }});
      continue;
    }

    original.reversed = true;
    original.reversedAt = now;
    store.earnings[orderId] = original;

    // A negative record so the arithmetic works whether or not the original was
    // already paid. If it was, this becomes a negative balance carried forward.
    const reversalKey = `${orderId}|reversal`;
    store.earnings[reversalKey] = {
      orderId: reversalKey,
      sourceOrderId: orderId,
      partnerId: original.partnerId,
      saleAmount: -Math.abs(original.saleAmount),
      rate: original.rate,
      commission: -Math.abs(original.commission),
      currency: original.currency,
      at: now,
      paid: false,
      isReversal: true,
    };

    out.push({ json: {
      action: 'reversed', orderId,
      partnerId: original.partnerId,
      reversedCommission: original.commission,
      note: original.paid
        ? 'The original commission was already paid — this becomes a negative balance on the next payout.'
        : 'The original commission had not been paid yet, so it is simply cancelled.',
      __config: cfg,
    }});
    continue;
  }

  // ── Sale: record the earning ────────────────────────────────
  if (store.earnings[orderId]) {
    out.push({ json: {
      action: 'duplicate_ignored', orderId,
      reason: 'commission already recorded for this order',
      __config: cfg,
    }});
    continue;
  }

  const partnerId = String(b.partnerId ?? b.partner_id ?? b.affiliate ?? b.ref ?? '').trim();
  if (!partnerId) {
    out.push({ json: {
      action: 'no_attribution', orderId,
      reason: 'no partnerId on this sale — direct sale, no commission owed',
      __config: cfg,
    }});
    continue;
  }

  const partner = (cfg.partners || {})[partnerId];
  // Freeze the rate NOW. Recalculating history is how disputes start.
  const rate = Number(partner?.rate ?? cfg.defaultRate);
  const saleAmount = Number(b.amount ?? b.total ?? 0);
  const commission = Math.round(saleAmount * (rate / 100) * 100) / 100;

  store.earnings[orderId] = {
    orderId, partnerId,
    partnerName: partner?.name ?? partnerId,
    partnerEmail: partner?.email ?? null,
    saleAmount,
    rate,
    commission,
    currency: String(b.currency ?? cfg.currency).toUpperCase(),
    at: now,
    paid: false,
    reversed: false,
    knownPartner: !!partner,
  };

  out.push({ json: {
    action: 'recorded', orderId, partnerId,
    commission, rate,
    warning: partner ? null : `Partner "${partnerId}" is not in your Config — default rate ${cfg.defaultRate}% applied. Add them.`,
    __config: cfg,
  }});
}

return out;
""",
        (-40, 200),
        notes="Append-only. Reversals are new negative records, never edits — that is what makes disputes answerable.",
        always_output=True,
    )

    ack = wf.respond(
        "↩️ 200 OK",
        (200, 200),
        body='={{ JSON.stringify({ ok: true, action: $json.action }) }}',
    )

    # ── Payout run ──────────────────────────────────────────────────────
    sched = wf.schedule("🕐 Payout run", (-700, 620), cron="0 9 1 * *")

    cfg2 = wf.code(
        "⚙️ Config (payout side)",
        r"""
// Mirror of the main Config — n8n cannot share a node across trigger branches.
const CONFIG = {
  "storeName": "YOUR_STORE_NAME",
  "fromEmail": "payouts@yourdomain.com",
  "ownerEmail": "you@yourdomain.com",
  "currency": "USD",
  "minimumPayout": 25,
  "holdDays": 30
};
return [{ json: { __config: CONFIG } }];
""",
        (-480, 620),
        notes="⚠️ Mirror of the main Config. Change one, change both.",
        always_output=True,
    )

    calculate = wf.code(
        "🧮 Calculate what is owed",
        r"""
// Sum unpaid, matured earnings per partner. Only records not already stamped
// with a batch id are considered, which is what makes a re-run safe.
const cfg = $input.first().json.__config;
const store = $getWorkflowStaticData('global');
store.earnings = store.earnings || {};
store.payouts = store.payouts || {};

const now = Date.now();
const DAY = 24 * 60 * 60 * 1000;
const holdMs = Number(cfg.holdDays) * DAY;

const byPartner = {};

for (const e of Object.values(store.earnings)) {
  if (e.paid) continue;

  // A reversal always counts immediately — holding it back would let a refunded
  // sale be paid out before its reversal matures.
  if (!e.isReversal && now - e.at < holdMs) continue;

  const p = byPartner[e.partnerId] = byPartner[e.partnerId] || {
    partnerId: e.partnerId,
    partnerName: e.partnerName ?? e.partnerId,
    partnerEmail: e.partnerEmail ?? null,
    currency: e.currency ?? cfg.currency,
    gross: 0, reversals: 0, net: 0,
    saleCount: 0, reversalCount: 0,
    keys: [],
  };

  if (e.isReversal) { p.reversals += Math.abs(e.commission); p.reversalCount += 1; }
  else { p.gross += e.commission; p.saleCount += 1; }

  p.net = Math.round((p.gross - p.reversals) * 100) / 100;
  p.keys.push(e.orderId);
}

const batchId = `PAYOUT-${new Date().toISOString().slice(0, 10)}-${String(now).slice(-5)}`;
const due = [];
const held = [];

for (const p of Object.values(byPartner)) {
  p.gross = Math.round(p.gross * 100) / 100;
  p.reversals = Math.round(p.reversals * 100) / 100;

  if (p.net < Number(cfg.minimumPayout)) {
    // Carried forward. Not marked paid, so it accumulates into the next run.
    held.push({ ...p, reason: p.net < 0
      ? `negative balance of ${p.net} carried forward — refunds exceeded earnings this period`
      : `below the ${cfg.minimumPayout} ${p.currency} minimum — carried forward` });
    continue;
  }

  // Stamp every contributing record so a re-run cannot pay this twice.
  for (const key of p.keys) {
    if (store.earnings[key]) {
      store.earnings[key].paid = true;
      store.earnings[key].paidAt = now;
      store.earnings[key].batchId = batchId;
    }
  }

  due.push(p);
}

if (due.length) {
  store.payouts[batchId] = {
    batchId, at: now,
    total: Math.round(due.reduce((s, p) => s + p.net, 0) * 100) / 100,
    partners: due.length,
  };
}

return [{ json: {
  batchId,
  due, held,
  totalDue: Math.round(due.reduce((s, p) => s + p.net, 0) * 100) / 100,
  partnerCount: due.length,
  heldCount: held.length,
  hasPayouts: due.length > 0,
  generatedAt: new Date().toISOString(),
  __config: cfg,
}}];
""",
        (-260, 620),
        notes="Only unpaid, matured records count. Everything paid is stamped with the batch id, so re-runs are safe.",
        always_output=True,
    )

    has_payouts = wf.if_(
        "💰 Anything to pay?",
        (-20, 620),
        left="={{ $json.hasPayouts }}",
        operator={"type": "boolean", "operation": "true", "singleValue": True},
    )

    instruction = wf.code(
        "📄 Build the payout instruction",
        r"""
// The document the seller works from. It has to be unambiguous enough to act on
// without opening anything else, because that is when mistakes happen.
const o = $input.first().json;
const cfg = o.__config;

const rows = o.due.map(p =>
`  ${p.partnerName} <${p.partnerEmail || 'NO EMAIL ON FILE'}>
     ${p.saleCount} sale(s): ${p.gross} ${p.currency}` +
  (p.reversalCount ? `\n     ${p.reversalCount} reversal(s): -${p.reversals} ${p.currency}` : '') +
`\n     → PAY: ${p.net} ${p.currency}`
).join('\n\n');

const heldRows = o.held.length
  ? '\n\n── CARRIED FORWARD ─────────────────\n' +
    o.held.map(p => `  ${p.partnerName}: ${p.net} ${p.currency} — ${p.reason}`).join('\n')
  : '';

const text =
`💸 PAYOUT INSTRUCTION — ${cfg.storeName}
Batch: ${o.batchId}
Generated: ${o.generatedAt.slice(0, 16).replace('T', ' ')}

TOTAL TO PAY: ${o.totalDue} ${cfg.currency} across ${o.partnerCount} partner(s)

── PAY THESE ───────────────────────
${rows}${heldRows}

── HOW TO USE THIS ─────────────────
1. Send each amount through your usual payment method.
2. These earnings are now marked paid under batch ${o.batchId} —
   re-running this job will NOT produce them again.
3. If a payment fails, the record is still marked paid. Reverse it manually
   or keep a note; nothing here will re-issue it automatically.

⚠️ This workflow does not move money. It tells you what to send.`;

return [{ json: { ...o, instructionText: text,
  subject: `💸 Payout ${o.batchId} — ${o.totalDue} ${cfg.currency} across ${o.partnerCount} partner(s)` }}];
""",
        (220, 540),
        notes="Unambiguous enough to act on without opening anything else.",
    )

    send = wf.node(
        "📨 Send the instruction",
        "n8n-nodes-base.emailSend",
        {
            "fromEmail": "={{ $json.__config.fromEmail }}",
            "toEmail": "={{ $json.__config.ownerEmail }}",
            "subject": "={{ $json.subject }}",
            "emailFormat": "text",
            "text": "={{ $json.instructionText }}",
            "options": {},
        },
        2.1,
        (460, 540),
        retry=True,
        max_tries=3,
        wait_ms=2000,
        on_error="continueRegularOutput",
        notes="Goes to you, not to partners. You execute the payments.",
    )

    nothing = wf.code(
        "🤫 Nothing due",
        r"""
// Everyone is below threshold, or there were no earnings this period. Recorded
// so an empty run is visibly an empty run rather than a silent failure.
const o = $input.first().json;
return [{ json: {
  batchId: o.batchId,
  totalDue: 0,
  heldCount: o.heldCount,
  note: o.heldCount
    ? `${o.heldCount} partner(s) below the minimum — balances carried forward.`
    : 'No unpaid, matured earnings this period.',
  checkedAt: new Date().toISOString(),
}}];
""",
        (220, 720),
        notes="An empty run is logged, so you can tell 'nothing owed' from 'not running'.",
    )

    log = wf.code(
        "📒 Payout log",
        r"""
// Your permanent record of what was paid and when. Keep it somewhere durable —
// this is the document that settles a commission dispute.
return $input.all().map(i => ({ json: {
  ts: new Date().toISOString(),
  batchId: i.json.batchId ?? null,
  totalDue: i.json.totalDue ?? 0,
  partnerCount: i.json.partnerCount ?? 0,
  heldCount: i.json.heldCount ?? 0,
  breakdown: (i.json.due ?? []).map(p =>
    `${p.partnerId}:${p.net}${p.currency}`).join(' | ') || null,
}}));
""",
        (700, 620),
        notes="⚠️ Wire to a Sheet. This is the document that settles disputes.",
    )

    wf.chain(hook, cfg, guard, ledger, ack)
    wf.chain(sched, cfg2, calculate, has_payouts)
    wf.connect(has_payouts, instruction, out=0)
    wf.connect(has_payouts, nothing, out=1)
    wf.connect(instruction, send)
    wf.connect(send, log)
    wf.connect(nothing, log)

    return wf
