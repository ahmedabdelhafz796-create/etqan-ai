"""
DCA-SYS-01 · Daily Business Pulse

The second spine piece, and the one that keeps the system installed.

The problem it solves is not technical
--------------------------------------
Automation that works is invisible. A delivery that succeeds produces no email,
no notification, nothing — which is correct behaviour and also the reason
sellers quietly stop trusting their own automation. Six weeks in they cannot
remember whether it is still running, so they start checking manually "just to
be safe", and the automation has failed at its actual job even though every
workflow is green.

A single daily message that says what happened fixes that. It is the difference
between a system the seller owns and a system the seller hopes is working.

What it deliberately does not do
--------------------------------
It does not invent numbers. Every metric here is read from the static data the
other templates already write; anything not yet installed is reported as "not
installed" rather than zero, because a zero that means "no data" and a zero that
means "nothing happened" lead to opposite decisions.

It also reports the things that went *wrong* first. A dashboard that leads with
good news is decoration; the seller needs to see the held orders and the
approaching dispute deadlines before the revenue total, because those are the
only lines that need action today.
"""

from lib.core import Workflow, COLOR_BLUE, COLOR_GREEN, COLOR_RED, COLOR_PURPLE

SLUG = "daily-business-pulse"


def build() -> Workflow:
    wf = Workflow(
        name="DCA-SYS-01 · Daily Business Pulse (one message: what your automation did today)",
        slug=SLUG,
        category="sys-spine",
        summary="Reads the data every other template already writes and sends one daily message covering what needs action, what was recovered, and what ran — so the seller can see the system working instead of hoping.",
        problem="Automation that works is invisible, so sellers stop trusting it and drift back to checking manually — at which point the automation has failed at its real job even though every workflow is green.",
        outcome="One message a day, action items first, with anything not yet installed reported as 'not installed' rather than silently as zero.",
        version="1.0.0",
        tags=["system", "reporting", "spine", "analytics", "hardened"],
        credentials_needed=["SMTP account (or Slack/Telegram)"],
        setup_minutes=6,
    )

    wf.sticky(
        "## 📊 Daily Business Pulse — the second spine piece\n"
        "**One message a day: what your automation actually did.**\n\n"
        "### Setup (about 6 minutes)\n"
        "1. **⚙️ Config** → set `reportEmail` and your local `sendHour` (UTC).\n"
        "2. Attach SMTP to **📨 Send the pulse**.\n"
        "3. Activate. That is all — it reads data the other templates already write.\n\n"
        "### Why this matters more than it looks\n"
        "Automation that works is **invisible**. A delivery that succeeds sends you\n"
        "nothing — correct, and also why sellers quietly stop trusting their own\n"
        "system and drift back to checking manually.\n\n"
        "At that point the automation has failed at its real job even though every\n"
        "workflow is green. One daily message is what prevents that.",
        (-660, -460),
        (580, 520),
        COLOR_BLUE,
    )

    wf.sticky(
        "### 🚩 Action items come FIRST\n"
        "A dashboard that leads with good news is decoration.\n\n"
        "The order is deliberate:\n"
        "1. **Needs you today** — held orders, dispute deadlines, failures\n"
        "2. **Money recovered** — what the system earned back\n"
        "3. **Ran normally** — the quiet confirmation\n\n"
        "You should be able to read line 1 and close the email.",
        (-40, -460),
        (460, 340),
        COLOR_RED,
    )

    wf.sticky(
        "### 🚫 It never invents numbers\n"
        "Anything not installed reports **\"not installed\"**, never `0`.\n\n"
        "A zero meaning *no data* and a zero meaning *nothing happened* lead to\n"
        "opposite decisions — one says install it, the other says relax.\n\n"
        "Conflating them is how dashboards start lying.",
        (440, -460),
        (440, 300),
        COLOR_GREEN,
    )

    wf.sticky(
        "### 🔌 Where the data comes from\n"
        "Everything is read from the static data the other templates already\n"
        "write — no database, no extra setup:\n\n"
        "`cases` → dunning · `carts` → abandonment\n"
        "`chargebacks` → disputes · `downloads` → download endpoint\n"
        "`orders` → fraud screening · `errors` → error hub\n\n"
        "⚠️ Static data is **per workflow**. For a true cross-workflow rollup, wire\n"
        "each template's log node to a shared Sheet and read that here instead —\n"
        "see the note in **📥 Gather**.",
        (1120, 200),
        (480, 340),
        COLOR_PURPLE,
    )

    sched = wf.schedule("🕗 Once a day", (-660, 180), hours=24)

    cfg = wf.config(
        {
            "reportEmail": "you@yourdomain.com",
            "fromEmail": "reports@yourdomain.com",
            "storeName": "YOUR_STORE_NAME",
            "currency": "USD",
            "sendHour": 8,
            "quietIfNothingHappened": False,
        },
        (-440, 180),
        notes="quietIfNothingHappened: set true once you trust it, to skip empty days.",
    )

    gather = wf.code(
        "📥 Gather what the system did",
        r"""
// Read the counters the other templates already maintain.
//
// IMPORTANT LIMITATION, stated rather than hidden: n8n static data is scoped to
// a single workflow, so this only sees keys written by templates running in the
// SAME workflow, or seeded here. For a genuine cross-workflow rollup, point each
// template's log node at a shared Google Sheet / Airtable / database table and
// replace this node with a read from that source. The shape below is what the
// rest of this workflow expects, so only this node needs changing.
const cfg = $input.first().json.__config;
const store = $getWorkflowStaticData('global');

const now = Date.now();
const DAY = 24 * 60 * 60 * 1000;
const since = now - DAY;

// `null` means "this template is not installed / no data reaching us".
// `0` means "installed, and nothing happened". They are not the same.
const present = (key) => Object.prototype.hasOwnProperty.call(store, key);

// ── Dunning ──────────────────────────────────────────────────────
let dunning = null;
if (present('cases')) {
  const cases = Object.values(store.cases || {});
  dunning = {
    open: cases.filter(c => !c.recovered).length,
    recoveredToday: cases.filter(c => c.recovered && (c.recoveredAt || 0) > since).length,
    recoveredValueToday: Math.round(
      cases.filter(c => c.recovered && (c.recoveredAt || 0) > since)
           .reduce((s, c) => s + (Number(c.amount) || 0), 0) * 100) / 100,
  };
}

// ── Carts ────────────────────────────────────────────────────────
let carts = null;
if (present('carts')) {
  const list = Object.values(store.carts || {});
  carts = {
    open: list.length,
    openValue: Math.round(list.reduce((s, c) => s + (Number(c.total) || 0), 0) * 100) / 100,
    newToday: list.filter(c => (c.abandonedAt || 0) > since).length,
  };
}

// ── Disputes ─────────────────────────────────────────────────────
let disputes = null;
if (present('chargebacks')) {
  const cb = store.chargebacks || [];
  const last30 = cb.filter(c => now - c.t < 30 * DAY);
  disputes = {
    newToday: cb.filter(c => c.t > since).length,
    last30: last30.length,
    value30: Math.round(last30.reduce((s, c) => s + (Number(c.amount) || 0), 0) * 100) / 100,
  };
}

// ── Downloads ────────────────────────────────────────────────────
let downloads = null;
if (present('downloads')) {
  const recs = Object.values(store.downloads || {});
  downloads = {
    activeLinks: recs.length,
    totalDownloads: recs.reduce((s, r) => s + (r.count || 0), 0),
    // A single order collected from many IPs is the cheapest leak signal there is.
    suspectedLeaks: recs.filter(r => (r.ips || []).length >= 8).length,
  };
}

// ── Fraud screening ──────────────────────────────────────────────
let fraud = null;
if (present('orders')) {
  const orders = store.orders || [];
  fraud = { screenedToday: orders.filter(o => o.t > since).length };
}

// ── Failures ─────────────────────────────────────────────────────
let errors = null;
if (present('errors')) {
  const errs = Object.values(store.errors || {});
  errors = {
    distinctToday: errs.filter(e => e.lastAt > since).length,
    totalOccurrences: errs.filter(e => e.lastAt > since).reduce((s, e) => s + (e.count || 0), 0),
  };
}

return [{ json: { dunning, carts, disputes, downloads, fraud, errors,
                  windowHours: 24, generatedAt: new Date().toISOString(), __config: cfg } }];
""",
        (-220, 180),
        notes="Reads existing counters. null = not installed, 0 = installed but quiet. Replace this node to read a shared Sheet for a true cross-workflow rollup.",
        always_output=True,
    )

    compose = wf.code(
        "✍️ Write the pulse",
        r"""
// Action items first. The seller should be able to read the top block and close
// the message if it is empty.
const d = $input.first().json;
const cfg = d.__config;
const cur = cfg.currency;

const actions = [];
const recovered = [];
const normal = [];
const notInstalled = [];

// ── 1. Needs you today ───────────────────────────────────────────
if (d.errors === null) notInstalled.push('Error Hub (SYS-00)');
else if (d.errors.distinctToday > 0) {
  actions.push(`🔴 ${d.errors.distinctToday} distinct failure(s) today (${d.errors.totalOccurrences} occurrences) — check the Error Hub alerts.`);
}

if (d.disputes === null) notInstalled.push('Chargeback Early Warning (A3-02)');
else if (d.disputes.newToday > 0) {
  actions.push(`🟠 ${d.disputes.newToday} new dispute(s) today, ${d.disputes.value30} ${cur} disputed in 30 days — respond before the deadlines.`);
}

if (d.downloads?.suspectedLeaks > 0) {
  actions.push(`🟡 ${d.downloads.suspectedLeaks} download link(s) used from 8+ different IPs — likely shared publicly.`);
}

// ── 2. Money recovered ───────────────────────────────────────────
if (d.dunning === null) notInstalled.push('Failed Payment Recovery (B4-02)');
else {
  if (d.dunning.recoveredToday > 0) {
    recovered.push(`💰 ${d.dunning.recoveredToday} subscription(s) recovered — ${d.dunning.recoveredValueToday} ${cur} saved.`);
  }
  if (d.dunning.open > 0) {
    normal.push(`${d.dunning.open} payment(s) still in recovery.`);
  }
}

if (d.carts === null) notInstalled.push('Cart Abandonment (A5-01)');
else {
  if (d.carts.open > 0) {
    normal.push(`${d.carts.open} cart(s) open, worth ${d.carts.openValue} ${cur} — reminders running.`);
  }
  if (d.carts.newToday > 0) normal.push(`${d.carts.newToday} cart(s) abandoned today.`);
}

// ── 3. Ran normally ──────────────────────────────────────────────
if (d.fraud === null) notInstalled.push('Fraud Scoring (A3-01)');
else if (d.fraud.screenedToday > 0) normal.push(`${d.fraud.screenedToday} order(s) screened for fraud.`);

if (d.downloads === null) notInstalled.push('Secure Download Endpoint (A1-02)');
else if (d.downloads.totalDownloads > 0) {
  normal.push(`${d.downloads.totalDownloads} download(s) served across ${d.downloads.activeLinks} active link(s).`);
}

const nothingHappened = actions.length === 0 && recovered.length === 0 && normal.length === 0;

const date = new Date().toISOString().slice(0, 10);
const lines = [];
lines.push(`📊 ${cfg.storeName} — daily pulse, ${date}`);
lines.push('');

if (actions.length) {
  lines.push('━━ NEEDS YOU TODAY ━━━━━━━━━━━━━━');
  actions.forEach(a => lines.push(a));
  lines.push('');
} else {
  lines.push('✅ Nothing needs your attention today.');
  lines.push('');
}

if (recovered.length) {
  lines.push('━━ MONEY RECOVERED ━━━━━━━━━━━━━━');
  recovered.forEach(r => lines.push(r));
  lines.push('');
}

if (normal.length) {
  lines.push('━━ RAN NORMALLY ━━━━━━━━━━━━━━━━━');
  normal.forEach(n => lines.push(`· ${n}`));
  lines.push('');
}

if (notInstalled.length) {
  lines.push('━━ NOT INSTALLED ━━━━━━━━━━━━━━━━');
  lines.push('No data reaching this report from:');
  notInstalled.forEach(n => lines.push(`· ${n}`));
  lines.push('(This is not zero activity — it means nothing is reporting.)');
  lines.push('');
}

if (nothingHappened && !notInstalled.length) {
  lines.push('Everything is installed and quiet. Nothing happened in the last 24h.');
  lines.push('');
}

lines.push('─────────────────────────────────');
lines.push('Generated by your automation suite. If this stops arriving, the');
lines.push('schedule is off — which is itself worth knowing.');

return [{ json: {
  pulseText: lines.join('\n'),
  subject: actions.length
    ? `📊 ${cfg.storeName} — ${actions.length} item(s) need you`
    : `📊 ${cfg.storeName} — all clear, ${date}`,
  actionCount: actions.length,
  nothingHappened,
  __config: cfg,
}}];
""",
        (0, 180),
        notes="Action items first, then recovery, then normal. 'Not installed' is reported explicitly.",
    )

    worth_sending = wf.if_(
        "📤 Worth sending today?",
        (240, 180),
        left="={{ $json.actionCount > 0 || $json.__config.quietIfNothingHappened !== true || !$json.nothingHappened }}",
        operator={"type": "boolean", "operation": "true", "singleValue": True},
    )

    send = wf.node(
        "📨 Send the pulse",
        "n8n-nodes-base.emailSend",
        {
            "fromEmail": "={{ $json.__config.fromEmail }}",
            "toEmail": "={{ $json.__config.reportEmail }}",
            "subject": "={{ $json.subject }}",
            "emailFormat": "text",
            "text": "={{ $json.pulseText }}",
            "options": {},
        },
        2.1,
        (480, 80),
        retry=True,
        max_tries=3,
        wait_ms=3000,
        on_error="continueRegularOutput",
        notes="Attach SMTP. Swap for Slack/Telegram — the text is plain and works anywhere.",
    )

    skipped = wf.code(
        "🤫 Quiet day, nothing sent",
        r"""
// quietIfNothingHappened is on and there was genuinely nothing to say.
return [{ json: { sent: false, reason: 'quiet day — nothing to report', at: new Date().toISOString() } }];
""",
        (480, 300),
        notes="Only reached when you have opted into quiet days.",
    )

    archive = wf.code(
        "📒 Pulse archive",
        r"""
// Keeping the daily pulses gives you a trend nobody else has: how much the
// system recovered month over month. That number is what justifies the whole
// suite when you review it later.
return $input.all().map(i => ({ json: {
  ts: new Date().toISOString(),
  sent: i.json.sent !== false,
  actionCount: i.json.actionCount ?? 0,
  text: i.json.pulseText ?? null,
}}));
""",
        (720, 180),
        notes="Append to a Sheet. Month-over-month recovery is the number that proves the suite's value.",
    )

    wf.chain(sched, cfg, gather, compose, worth_sending)
    wf.connect(worth_sending, send, out=0)
    wf.connect(worth_sending, skipped, out=1)
    wf.connect(send, archive)
    wf.connect(skipped, archive)

    return wf
