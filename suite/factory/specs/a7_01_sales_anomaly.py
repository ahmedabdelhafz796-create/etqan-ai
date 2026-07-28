"""
DCA-A7-01 · Sales Anomaly Detection

Solves "عدم معرفة سبب انخفاض المبيعات" — the seller notices revenue is down,
usually late, and has no way to tell whether demand fell or something broke.

Why "revenue is down" is the wrong alarm
----------------------------------------
Sales are noisy. A quiet Tuesday is not a signal, and an alert that fires on
normal variation gets muted within a week — at which point the seller has an
alerting system that actively conceals problems. So this compares against the
same weekday over recent weeks rather than against yesterday, and requires a
drop to be large relative to that history before it says anything.

The distinction that actually matters
-------------------------------------
Revenue can fall for two completely different reasons and the response is
opposite in each case:

  * **Demand fell** — fewer people are arriving or buying. That is a marketing
    problem, and there is no emergency today.
  * **Something broke** — checkout is failing, the delivery webhook stopped, the
    payment provider is rejecting cards. Revenue looks identical from the
    outside, but every hour costs money and the fix is technical.

Sellers routinely spend a week optimising ads while their checkout has been
silently broken the whole time. So this template's real job is not detecting the
drop — it is telling those two cases apart, using signals it already has:
whether traffic-independent events (webhooks arriving, orders being screened)
also stopped, or only conversions did.

A zero that means "nothing arrived" is the loudest signal in the system, and it
is the one a naive revenue chart cannot show you.
"""

from lib.core import Workflow, COLOR_BLUE, COLOR_GREEN, COLOR_RED, COLOR_PURPLE

SLUG = "sales-anomaly-detection"


def build() -> Workflow:
    wf = Workflow(
        name="DCA-A7-01 · Sales Anomaly Detection (is demand down, or is something broken?)",
        slug=SLUG,
        category="a7-analytics",
        summary="Watches order volume against the same weekday in recent weeks, and when it drops tells you whether demand fell or something in your pipeline broke — which need opposite responses.",
        problem="Revenue falls and the seller finds out late, then cannot tell whether demand dropped or checkout broke. People spend a week optimising ads while their delivery webhook has been dead the whole time.",
        outcome="Meaningful drops are detected against weekday-aware history, and every alert says which of the two causes it is, with the evidence that led to that conclusion.",
        version="1.0.0",
        tags=["analytics", "monitoring", "revenue", "alerting", "hardened"],
        credentials_needed=["SMTP account (or Slack/Telegram)"],
        setup_minutes=10,
    )

    wf.sticky(
        "## 📉 Sales Anomaly Detection\n"
        "**Not just \"sales are down\" — *why* they are down.**\n\n"
        "### Setup (about 10 minutes)\n"
        "1. **⚙️ Config** → `alertEmail`, `minDailyOrders`, `dropThreshold`.\n"
        "2. POST every order to the Production URL as it happens\n"
        "   (or run this in the same workflow as A1-01 and reuse its data).\n"
        "3. Attach SMTP to **📨 Send the alert**.\n"
        "4. Activate. It builds its own baseline over the first two weeks.\n\n"
        "⚠️ **Give it 14 days before trusting it.** With less history there is no\n"
        "baseline to compare against, and it says so rather than guessing.",
        (-680, -540),
        (580, 500),
        COLOR_BLUE,
    )

    wf.sticky(
        "### 🎯 The distinction that matters\n"
        "Revenue falls for two reasons needing **opposite** responses:\n\n"
        "**📉 Demand fell** — fewer people buying. A marketing problem. No\n"
        "emergency today.\n\n"
        "**🔴 Something broke** — checkout failing, webhook dead, cards being\n"
        "rejected. Every hour costs money. Fix it **now**.\n\n"
        "From a revenue chart these look **identical**. Sellers routinely spend a\n"
        "week optimising ads while checkout has been broken the whole time.\n\n"
        "**Telling them apart is this template's actual job.**",
        (-60, -540),
        (500, 440),
        COLOR_RED,
    )

    wf.sticky(
        "### 📅 Why compare to the same weekday\n"
        "Sales are noisy. Sunday is not Wednesday.\n\n"
        "Comparing to *yesterday* fires constantly on normal variation — and an\n"
        "alert that cries wolf gets muted within a week, leaving you with a system\n"
        "that **actively conceals** problems.\n\n"
        "So the baseline is the same weekday over recent weeks, and a drop must be\n"
        "large relative to that history before anything is said.",
        (460, -540),
        (460, 380),
        COLOR_PURPLE,
    )

    wf.sticky(
        "### 🔇 The loudest signal is silence\n"
        "**Zero orders when you normally have twenty** is not a slow day. It means\n"
        "nothing is reaching you at all.\n"
        "\n"
        "That is the signal a revenue chart cannot show — it just draws a line to\n"
        "zero and says nothing about why.\n\n"
        "A total stop always reports as **broken**, never as \"demand fell\".",
        (1160, 400),
        (440, 320),
        COLOR_GREEN,
    )

    # ── Ingest ──────────────────────────────────────────────────────────
    hook = wf.webhook(
        "🛒 Order happened",
        (-680, 180),
        path="dca/order-event",
        notes="POST {orderId, amount, currency?, status?} for every order. Also accepts {event:'checkout_started'}.",
    )

    cfg = wf.config(
        {
            "storeName": "YOUR_STORE_NAME",
            "alertEmail": "you@yourdomain.com",
            "fromEmail": "alerts@yourdomain.com",
            "currency": "USD",
            "minDailyOrders": 3,
            "dropThreshold": 0.5,
            "baselineWeeks": 4,
            "minHistoryDays": 14,
            "alertCooldownHours": 12,
            "historyTtlDays": 60,
        },
        (-460, 180),
        notes="dropThreshold 0.5 = alert when today is 50% below the weekday baseline. Raise it if you get noise.",
    )

    guard = wf.guard(
        (-240, 180),
        required=["body"],
        event_id_expr="j.body?.orderId ?? j.body?.order_id ?? j.body?.id ?? (j.body?.event + '|' + Date.now())",
        ttl_hours=24,
    )

    record = wf.code(
        "📝 Record the event",
        r"""
// Keep a per-day tally. Two counters matter and they are deliberately separate:
//
//   orders          — money actually taken
//   checkoutStarts  — intent, regardless of whether payment completed
//
// The gap between them is what distinguishes "nobody came" from "everybody
// came and checkout failed", which is the whole point of this template.
const cfg = $('⚙️ Config').first().json.__config;
const store = $getWorkflowStaticData('global');
store.dailyStats = store.dailyStats || {};

const now = Date.now();
const DAY = 24 * 60 * 60 * 1000;
const ttlMs = Number(cfg.historyTtlDays) * DAY;

for (const [k, v] of Object.entries(store.dailyStats)) {
  if (now - (v.ts || 0) > ttlMs) delete store.dailyStats[k];
}

const out = [];

for (const item of $input.all()) {
  const b = item.json.body ?? item.json;
  const d = new Date();
  const key = d.toISOString().slice(0, 10);

  const day = store.dailyStats[key] || {
    date: key,
    weekday: d.getUTCDay(),
    ts: now,
    orders: 0,
    revenue: 0,
    checkoutStarts: 0,
    failures: 0,
  };

  const event = String(b.event ?? b.type ?? 'order').toLowerCase();
  const amount = Number(b.amount ?? b.total ?? 0);

  if (event.includes('checkout') || event.includes('started')) {
    day.checkoutStarts += 1;
  } else if (event.includes('fail') || b.status === 'failed') {
    day.failures += 1;
    day.checkoutStarts += 1;   // a failure means someone did try
  } else {
    day.orders += 1;
    day.revenue += amount;
    day.checkoutStarts += 1;
  }

  day.ts = now;
  store.dailyStats[key] = day;

  out.push({ json: { recorded: true, date: key, todayOrders: day.orders } });
}

return out;
""",
        (0, 180),
        notes="Tracks orders and checkout starts separately — the gap between them is the diagnostic signal.",
        always_output=True,
    )

    ack = wf.respond(
        "↩️ 200 OK",
        (240, 180),
        body='={{ JSON.stringify({ ok: true }) }}',
    )

    # ── Analysis ────────────────────────────────────────────────────────
    sched = wf.schedule("🕓 Check every 4 hours", (-680, 560), hours=4)

    cfg2 = wf.code(
        "⚙️ Config (analysis side)",
        r"""
// Mirror of the main Config — n8n cannot share a node across trigger branches.
const CONFIG = {
  "storeName": "YOUR_STORE_NAME",
  "alertEmail": "you@yourdomain.com",
  "fromEmail": "alerts@yourdomain.com",
  "currency": "USD",
  "minDailyOrders": 3,
  "dropThreshold": 0.5,
  "baselineWeeks": 4,
  "minHistoryDays": 14,
  "alertCooldownHours": 12
};
return [{ json: { __config: CONFIG } }];
""",
        (-460, 560),
        notes="⚠️ Mirror of the main Config. Change one, change both.",
        always_output=True,
    )

    analyse = wf.code(
        "🔬 Compare against the weekday baseline",
        r"""
// Build a baseline from the same weekday in recent weeks, then decide whether
// today is meaningfully below it — and if so, which of the two causes it is.
const cfg = $input.first().json.__config;
const store = $getWorkflowStaticData('global');
store.dailyStats = store.dailyStats || {};

const days = Object.values(store.dailyStats).sort((a, b) => a.date.localeCompare(b.date));
const todayKey = new Date().toISOString().slice(0, 10);
const today = store.dailyStats[todayKey] || {
  date: todayKey, weekday: new Date().getUTCDay(),
  orders: 0, revenue: 0, checkoutStarts: 0, failures: 0,
};

// ── Not enough history ────────────────────────────────────────
// Say so plainly rather than comparing against noise.
if (days.length < Number(cfg.minHistoryDays)) {
  return [{ json: {
    verdict: 'insufficient_history',
    daysCollected: days.length,
    daysNeeded: Number(cfg.minHistoryDays),
    shouldAlert: false,
    __config: cfg,
  }}];
}

// ── Weekday-aware baseline ────────────────────────────────────
const sameWeekday = days.filter(d =>
  d.weekday === today.weekday && d.date !== todayKey
).slice(-Number(cfg.baselineWeeks));

if (sameWeekday.length < 2) {
  return [{ json: {
    verdict: 'insufficient_history',
    daysCollected: days.length,
    reason: `only ${sameWeekday.length} prior sample(s) for this weekday`,
    shouldAlert: false,
    __config: cfg,
  }}];
}

const avg = (arr, k) => arr.reduce((s, x) => s + (Number(x[k]) || 0), 0) / arr.length;

const baselineOrders = avg(sameWeekday, 'orders');
const baselineStarts = avg(sameWeekday, 'checkoutStarts');
const baselineRevenue = avg(sameWeekday, 'revenue');

// How far through the day are we? Comparing a half-finished day against a full
// one manufactures a drop that is not real.
const hoursElapsed = new Date().getUTCHours() + 1;
const dayFraction = Math.min(1, hoursElapsed / 24);
const expectedOrders = baselineOrders * dayFraction;
const expectedStarts = baselineStarts * dayFraction;

// Too small to reason about. Two orders instead of three is not a signal.
if (baselineOrders < Number(cfg.minDailyOrders)) {
  return [{ json: {
    verdict: 'volume_too_low',
    baselineOrders: Math.round(baselineOrders * 10) / 10,
    shouldAlert: false,
    note: 'Daily volume is below minDailyOrders — statistically there is nothing to detect here.',
    __config: cfg,
  }}];
}

const orderRatio = expectedOrders > 0 ? today.orders / expectedOrders : 1;
const startRatio = expectedStarts > 0 ? today.checkoutStarts / expectedStarts : 1;
const dropPct = Math.round((1 - orderRatio) * 100);

const isDrop = orderRatio < (1 - Number(cfg.dropThreshold));

if (!isDrop) {
  return [{ json: {
    verdict: 'normal',
    todayOrders: today.orders,
    expectedOrders: Math.round(expectedOrders * 10) / 10,
    shouldAlert: false,
    __config: cfg,
  }}];
}

// ═══ The diagnosis ════════════════════════════════════════════
// Demand and breakage look identical on a revenue chart. They are told apart
// by whether *intent* also fell:
//
//   starts down + orders down  → fewer people arriving   → demand
//   starts normal + orders down → they came, couldn't pay → broken
//   nothing at all              → not even events arriving → broken
let cause, confidence, evidence, urgency;

if (today.checkoutStarts === 0 && baselineStarts >= Number(cfg.minDailyOrders)) {
  cause = 'broken';
  confidence = 'high';
  urgency = 'immediate';
  evidence = `Zero events of any kind today, against a typical ${Math.round(baselineStarts)}. ` +
             `This is not a slow day — nothing is reaching this workflow at all. ` +
             `Check that your site is up and that the webhook posting to this endpoint is still firing.`;
} else if (today.failures > 0 && today.failures >= today.orders) {
  cause = 'broken';
  confidence = 'high';
  urgency = 'immediate';
  evidence = `${today.failures} failed payment(s) against ${today.orders} successful. ` +
             `People are trying to buy and cannot. Check your payment provider status and your gateway keys.`;
} else if (startRatio > 0.7 && orderRatio < 0.5) {
  cause = 'broken';
  confidence = 'medium';
  urgency = 'immediate';
  evidence = `Checkout starts are near normal (${Math.round(startRatio * 100)}% of typical) but completed orders ` +
             `are at ${Math.round(orderRatio * 100)}%. People are arriving and not completing — ` +
             `that pattern points at checkout or payment, not at demand.`;
} else if (startRatio < 0.6) {
  cause = 'demand';
  confidence = 'medium';
  urgency = 'today';
  evidence = `Both traffic and orders are down together (starts at ${Math.round(startRatio * 100)}% of typical). ` +
             `Fewer people are arriving, which points at traffic or marketing rather than a technical fault. ` +
             `Check your ad spend, campaign status and referral sources.`;
} else {
  cause = 'unclear';
  confidence = 'low';
  urgency = 'today';
  evidence = `Orders are down ${dropPct}% but the pattern is not conclusive. ` +
             `Worth 10 minutes: place a test order yourself and confirm the whole path works end to end.`;
}

// ── Cooldown ──────────────────────────────────────────────────
// Runs every 4h; without this the same ongoing drop pages four times a day and
// gets muted, which is the failure mode this template exists to avoid.
const nowMs = Date.now();
store.lastAnomalyAlert = store.lastAnomalyAlert || 0;
const cooldownMs = Number(cfg.alertCooldownHours) * 60 * 60 * 1000;
const inCooldown = nowMs - store.lastAnomalyAlert < cooldownMs;
if (!inCooldown) store.lastAnomalyAlert = nowMs;

return [{ json: {
  verdict: 'anomaly',
  cause, confidence, urgency, evidence,
  dropPct,
  todayOrders: today.orders,
  expectedOrders: Math.round(expectedOrders * 10) / 10,
  todayStarts: today.checkoutStarts,
  expectedStarts: Math.round(expectedStarts * 10) / 10,
  todayFailures: today.failures,
  todayRevenue: Math.round(today.revenue * 100) / 100,
  expectedRevenue: Math.round(baselineRevenue * dayFraction * 100) / 100,
  baselineFrom: `${sameWeekday.length} previous ${['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'][today.weekday]}s`,
  shouldAlert: !inCooldown,
  suppressedByCooldown: inCooldown,
  __config: cfg,
}}];
""",
        (-240, 560),
        notes="Weekday-aware baseline, day-fraction adjusted, then diagnoses demand vs breakage.",
        always_output=True,
    )

    should_alert = wf.if_(
        "🔔 Alert?",
        (0, 560),
        left="={{ $json.shouldAlert }}",
        operator={"type": "boolean", "operation": "true", "singleValue": True},
    )

    compose = wf.code(
        "✍️ Write the alert",
        r"""
// Lead with the diagnosis, not the number. "Sales are down 60%" prompts a
// question; "sales are down 60% and it looks like checkout is broken" prompts
// an action.
const o = $input.first().json;
const cfg = o.__config;

const icon = o.cause === 'broken' ? '🔴' : (o.cause === 'demand' ? '📉' : '🟠');
const heading = o.cause === 'broken'
  ? 'SOMETHING IS BROKEN'
  : (o.cause === 'demand' ? 'DEMAND IS DOWN' : 'SALES DROP — CAUSE UNCLEAR');

const next = o.cause === 'broken'
  ? `1. Place a test order yourself, right now.
2. Check your payment provider's status page.
3. Open the Error Hub (SYS-00) for failures in the last few hours.
4. Confirm your delivery workflow is still Activated.`
  : (o.cause === 'demand'
    ? `1. Check whether your ads are still running and funded.
2. Look at your traffic sources for anything that stopped.
3. Check for a campaign that ended or a link that broke.
4. No emergency — but do not leave it a week.`
    : `1. Place a test order end to end.
2. If that works, treat it as a demand question.
3. If it fails, treat it as broken and check the Error Hub.`);

const text =
`${icon} ${heading} — ${cfg.storeName}

Orders today:   ${o.todayOrders}  (typically ${o.expectedOrders} by now)
Checkout starts: ${o.todayStarts}  (typically ${o.expectedStarts})
${o.todayFailures ? `Failed payments: ${o.todayFailures}\n` : ''}Revenue today:  ${o.todayRevenue} ${cfg.currency}  (typically ${o.expectedRevenue})

Down ${o.dropPct}% against ${o.baselineFrom}.

── DIAGNOSIS (${o.confidence} confidence) ──
${o.evidence}

── DO THIS ─────────────────────────
${next}

Urgency: ${o.urgency === 'immediate' ? 'now — every hour costs money' : 'today'}`;

return [{ json: { ...o, alertText: text,
  subject: `${icon} ${heading} — orders down ${o.dropPct}%` } }];
""",
        (240, 460),
        notes="Leads with the diagnosis and a concrete checklist, not with a percentage.",
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
        (480, 460),
        retry=True,
        max_tries=3,
        wait_ms=2000,
        on_error="continueRegularOutput",
        notes="Attach SMTP. Swap for Slack/Telegram for faster response.",
    )

    quiet = wf.code(
        "🤫 Nothing to report",
        r"""
// Normal, too little history, volume too low, or inside the alert cooldown.
// Recorded so the seller can confirm the check is genuinely running.
const o = $input.first().json;
return [{ json: {
  checkedAt: new Date().toISOString(),
  verdict: o.verdict,
  alerted: false,
  note: o.suppressedByCooldown
    ? 'Anomaly still present but inside the alert cooldown — not re-paging.'
    : (o.note ?? o.reason ?? 'Sales within the normal range for this weekday.'),
}}];
""",
        (240, 660),
        notes="Quiet outcomes are still logged, so you can tell 'all fine' from 'not running'.",
    )

    log = wf.code(
        "📒 Anomaly log",
        r"""
return $input.all().map(i => ({ json: {
  ts: new Date().toISOString(),
  verdict: i.json.verdict ?? 'anomaly',
  cause: i.json.cause ?? null,
  confidence: i.json.confidence ?? null,
  dropPct: i.json.dropPct ?? null,
  todayOrders: i.json.todayOrders ?? null,
  expectedOrders: i.json.expectedOrders ?? null,
  alerted: i.json.alerted !== false,
}}));
""",
        (720, 560),
        notes="Append to a Sheet. Reviewing past diagnoses tells you whether the thresholds are right.",
    )

    wf.chain(hook, cfg, guard, record, ack)
    wf.chain(sched, cfg2, analyse, should_alert)
    wf.connect(should_alert, compose, out=0)
    wf.connect(should_alert, quiet, out=1)
    wf.connect(compose, send)
    wf.connect(send, log)
    wf.connect(quiet, log)

    return wf
