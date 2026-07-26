"""
DCA-B3-01 · Sales Pipeline & Follow-Up Engine

Pairs with B1-02. That one decides which enquiries deserve attention; this one
makes sure the ones that do are not forgotten.

The problem, stated precisely
-----------------------------
Deals are rarely lost to a competitor. They are lost to silence — a reply that
was going to be sent tomorrow, a proposal nobody chased, a "circle back in two
weeks" that nobody circled back on. The seller genuinely intends to follow up
and the intention decays, because nothing in their day forces the issue.

CRMs solve this badly for solo sellers: they require the seller to log activity
faithfully, and the moment logging slips the reminders become wrong, which makes
them ignorable, which ends the habit.

The design choice that follows
------------------------------
Staleness is measured from the last *recorded* contact, and the seller can
record contact with one message rather than a form. Anything not explicitly
updated is assumed to be going cold, which is the correct default — a deal you
have not thought about is exactly the deal at risk.

Escalation is by deal value
---------------------------
Chasing a $50 deal with the same intensity as a $5,000 one wastes the seller's
scarcest resource. Higher-value deals surface sooner and more insistently, and
the digest says why each one is listed.

What it does not do
-------------------
It does not send anything to the prospect. Automated follow-up to a named
individual you are mid-conversation with reads as exactly what it is, and it
damages the relationship the seller is trying to build. This drafts and reminds;
a human presses send.
"""

from lib.core import Workflow, COLOR_BLUE, COLOR_GREEN, COLOR_RED, COLOR_PURPLE

SLUG = "sales-pipeline-followup"


def build() -> Workflow:
    wf = Workflow(
        name="DCA-B3-01 · Sales Pipeline & Follow-Up Engine",
        slug=SLUG,
        category="b3-sales-crm",
        summary="Tracks open deals, measures how long each has been silent, and sends one daily digest of who needs chasing — prioritised by value, with a draft for each, so nothing is lost to forgetfulness.",
        problem="Deals are rarely lost to competitors; they are lost to silence. The seller means to follow up, the intention decays, and nothing in their day forces the issue. CRMs make this worse by requiring faithful logging that always slips.",
        outcome="One daily digest naming every deal going cold, ordered by what it is worth, with a written draft for each — and nothing is ever sent to a prospect automatically.",
        version="1.0.0",
        tags=["sales", "crm", "pipeline", "follow-up", "hardened"],
        credentials_needed=["SMTP account"],
        setup_minutes=12,
    )

    wf.sticky(
        "## 📊 Sales Pipeline & Follow-Up Engine\n"
        "**Deals tracked → silence measured → one digest of who to chase.**\n\n"
        "### Setup (about 12 minutes)\n"
        "1. **⚙️ Config** → `ownerEmail`, `staleDays`, `valueTiers`.\n"
        "2. POST a deal when one opens:\n"
        "   ```json\n"
        "   { \"dealId\": \"...\", \"contact\": \"name\",\n"
        "     \"email\": \"...\", \"value\": 500, \"stage\": \"proposal\" }\n"
        "   ```\n"
        "3. Record contact with `{dealId, event:'contacted'}` — one line, no form.\n"
        "4. Close with `{dealId, event:'won'}` or `{dealId, event:'lost'}`.\n"
        "5. Attach SMTP. Activate.\n\n"
        "### Pairs with B1-02\n"
        "The lead qualifier decides who deserves attention. This makes sure they\n"
        "actually get it.",
        (-700, -540),
        (600, 560),
        COLOR_BLUE,
    )

    wf.sticky(
        "### 🤐 It never messages the prospect\n"
        "Automated follow-up to someone you are **mid-conversation with** reads as\n"
        "exactly what it is, and it damages the relationship you are building.\n\n"
        "This drafts and reminds. **A human presses send.**\n\n"
        "That is not a limitation — it is the difference between a tool that helps\n"
        "you sell and one that quietly costs you deals.",
        (-80, -540),
        (480, 340),
        COLOR_RED,
    )

    wf.sticky(
        "### 💰 Escalation by value\n"
        "| Deal value | Chased after |\n"
        "| --- | --- |\n"
        "| high | `staleDays` ÷ 2 |\n"
        "| normal | `staleDays` |\n"
        "| low | `staleDays` × 2 |\n\n"
        "Chasing a $50 deal as hard as a $5,000 one wastes your scarcest\n"
        "resource. The digest says **why** each deal is listed, so you can\n"
        "disagree with the ordering.",
        (420, -540),
        (460, 360),
        COLOR_PURPLE,
    )

    wf.sticky(
        "### 🕰️ Silence is the default assumption\n"
        "Staleness is measured from the **last recorded contact**. Anything you\n"
        "have not explicitly updated is assumed to be going cold.\n\n"
        "That is the correct default: a deal you have not thought about is exactly\n"
        "the deal at risk.\n\n"
        "Recording contact takes one POST, not a form — because the moment logging\n"
        "becomes work, it stops happening and the reminders go wrong.",
        (1120, 380),
        (460, 340),
        COLOR_GREEN,
    )

    hook = wf.webhook(
        "📇 Deal event",
        (-700, 200),
        path="dca/deal",
        notes="POST a new deal, or {dealId, event:'contacted'|'won'|'lost'}.",
    )

    cfg = wf.config(
        {
            "ownerEmail": "you@yourdomain.com",
            "fromEmail": "pipeline@yourdomain.com",
            "businessName": "YOUR_BUSINESS_NAME",
            "currency": "USD",
            "staleDays": 4,
            "highValueThreshold": 1000,
            "lowValueThreshold": 100,
            "abandonAfterDays": 45,
            "maxDigestItems": 15,
            "historyTtlDays": 180,
        },
        (-480, 200),
        notes="staleDays is the baseline. High-value deals are chased at half that, low-value at double.",
    )

    guard = wf.guard(
        (-260, 200),
        required=["body"],
        event_id_expr="(j.body?.dealId ?? '') + '|' + (j.body?.event ?? 'new') + '|' + Math.floor(Date.now() / 60000)",
        ttl_hours=6,
    )

    track = wf.code(
        "📝 Track the deal",
        r"""
// One record per deal. Contact events only move the clock — they never overwrite
// the deal's details, so a quick "contacted" POST cannot accidentally wipe the
// value or the contact name.
const cfg = $('⚙️ Config').first().json.__config;
const store = $getWorkflowStaticData('global');
store.deals = store.deals || {};

const now = Date.now();
const ttlMs = Number(cfg.historyTtlDays) * 24 * 60 * 60 * 1000;
for (const [k, d] of Object.entries(store.deals)) {
  if (now - (d.openedAt || 0) > ttlMs) delete store.deals[k];
}

const out = [];

for (const item of $input.all()) {
  const b = item.json.body ?? item.json;
  const dealId = String(b.dealId ?? b.deal_id ?? b.id ?? '').trim();

  if (!dealId) {
    throw new Error('Every deal event needs a dealId. Received keys: ' + Object.keys(b).join(', '));
  }

  const event = String(b.event ?? b.type ?? 'upsert').toLowerCase();
  const existing = store.deals[dealId];

  // ── Closed ───────────────────────────────────────────────────
  if (event === 'won' || event === 'lost') {
    if (!existing) {
      out.push({ json: { action: 'unknown_deal', dealId, note: 'No open deal with that id.' } });
      continue;
    }
    existing.status = event;
    existing.closedAt = now;
    store.deals[dealId] = existing;
    out.push({ json: {
      action: `marked_${event}`, dealId,
      value: existing.value,
      daysOpen: Math.round((now - existing.openedAt) / 86400000),
    }});
    continue;
  }

  // ── Contact recorded ─────────────────────────────────────────
  if (event === 'contacted' || event === 'contact' || event === 'touch') {
    if (!existing) {
      out.push({ json: { action: 'unknown_deal', dealId, note: 'No open deal with that id.' } });
      continue;
    }
    existing.lastContactAt = now;
    existing.touchCount = (existing.touchCount || 0) + 1;
    if (b.note) existing.lastNote = String(b.note).slice(0, 300);
    store.deals[dealId] = existing;
    out.push({ json: {
      action: 'contact_recorded', dealId,
      touchCount: existing.touchCount,
    }});
    continue;
  }

  // ── New or updated deal ──────────────────────────────────────
  const deal = existing || {
    dealId,
    openedAt: now,
    lastContactAt: now,
    touchCount: 0,
    status: 'open',
  };

  // Only overwrite fields that were actually supplied, so a partial update
  // cannot blank out details recorded earlier.
  if (b.contact !== undefined) deal.contact = String(b.contact).trim();
  if (b.email !== undefined) deal.email = String(b.email).trim().toLowerCase();
  if (b.company !== undefined) deal.company = String(b.company).trim();
  if (b.value !== undefined) deal.value = Number(b.value) || 0;
  if (b.stage !== undefined) deal.stage = String(b.stage).trim();
  if (b.note !== undefined) deal.lastNote = String(b.note).slice(0, 300);
  deal.currency = String(b.currency ?? deal.currency ?? cfg.currency).toUpperCase();

  store.deals[dealId] = deal;

  out.push({ json: {
    action: existing ? 'deal_updated' : 'deal_opened',
    dealId, value: deal.value, stage: deal.stage,
  }});
}

return out;
""",
        (-40, 200),
        notes="Contact events move the clock only — a quick touch cannot wipe the deal's details.",
        always_output=True,
    )

    ack = wf.respond(
        "↩️ 200 OK",
        (200, 200),
        body='={{ JSON.stringify({ ok: true, action: $json.action }) }}',
    )

    # ── Daily digest ────────────────────────────────────────────────────
    sched = wf.schedule("🕘 Daily digest", (-700, 620), hours=24)

    cfg2 = wf.code(
        "⚙️ Config (digest side)",
        r"""
// Mirror of the main Config — n8n cannot share a node across trigger branches.
const CONFIG = {
  "ownerEmail": "you@yourdomain.com",
  "fromEmail": "pipeline@yourdomain.com",
  "businessName": "YOUR_BUSINESS_NAME",
  "currency": "USD",
  "staleDays": 4,
  "highValueThreshold": 1000,
  "lowValueThreshold": 100,
  "abandonAfterDays": 45,
  "maxDigestItems": 15
};
return [{ json: { __config: CONFIG } }];
""",
        (-480, 620),
        notes="⚠️ Mirror of the main Config. Change one, change both.",
        always_output=True,
    )

    stale = wf.code(
        "🔍 Find deals going cold",
        r"""
// Work out which open deals have been silent longer than their value warrants.
const cfg = $input.first().json.__config;
const store = $getWorkflowStaticData('global');
store.deals = store.deals || {};

const now = Date.now();
const DAY = 86400000;

const needsChasing = [];
let openCount = 0, openValue = 0;
let wonToday = 0, wonValue = 0;

for (const d of Object.values(store.deals)) {
  if (d.status === 'won') {
    if (now - (d.closedAt || 0) < DAY) { wonToday++; wonValue += Number(d.value) || 0; }
    continue;
  }
  if (d.status === 'lost') continue;

  openCount++;
  openValue += Number(d.value) || 0;

  const silentDays = (now - (d.lastContactAt || d.openedAt)) / DAY;
  const ageDays = (now - d.openedAt) / DAY;

  // Past the abandon point this is not a live deal any more, and listing it
  // every day trains the reader to skim the digest.
  if (ageDays > Number(cfg.abandonAfterDays)) continue;

  const value = Number(d.value) || 0;
  let tier, threshold;
  if (value >= Number(cfg.highValueThreshold)) {
    tier = 'high'; threshold = Number(cfg.staleDays) / 2;
  } else if (value <= Number(cfg.lowValueThreshold)) {
    tier = 'low'; threshold = Number(cfg.staleDays) * 2;
  } else {
    tier = 'normal'; threshold = Number(cfg.staleDays);
  }

  if (silentDays < threshold) continue;

  needsChasing.push({
    dealId: d.dealId,
    contact: d.contact || d.email || d.dealId,
    email: d.email || null,
    company: d.company || null,
    value, currency: d.currency || cfg.currency,
    stage: d.stage || 'unknown',
    tier,
    silentDays: Math.floor(silentDays),
    ageDays: Math.floor(ageDays),
    touchCount: d.touchCount || 0,
    lastNote: d.lastNote || null,
    // State the reason, so the reader can disagree with the ordering.
    reason: `${Math.floor(silentDays)} days silent · ${tier}-value deal (chased after ${threshold} days)`,
  });
}

// Highest value first — the digest should be readable top-down and abandonable
// halfway without missing the deals that matter.
needsChasing.sort((a, b) => b.value - a.value);

return [{ json: {
  needsChasing: needsChasing.slice(0, Number(cfg.maxDigestItems)),
  totalStale: needsChasing.length,
  hidden: Math.max(0, needsChasing.length - Number(cfg.maxDigestItems)),
  openCount,
  openValue: Math.round(openValue * 100) / 100,
  wonToday, wonValue: Math.round(wonValue * 100) / 100,
  hasWork: needsChasing.length > 0,
  __config: cfg,
}}];
""",
        (-260, 620),
        notes="Value-aware thresholds, sorted by what each deal is worth. Abandoned deals drop out.",
        always_output=True,
    )

    has_work = wf.if_(
        "📋 Anything to chase?",
        (-20, 620),
        left="={{ $json.hasWork }}",
        operator={"type": "boolean", "operation": "true", "singleValue": True},
    )

    digest = wf.code(
        "✍️ Write the digest",
        r"""
// A draft for each deal, so the seller edits rather than composes. The drafts
// are deliberately short and specific — a long generic template gets rewritten
// anyway, which defeats the purpose.
const o = $input.first().json;
const cfg = o.__config;

const icon = { high: '🔴', normal: '🟠', low: '🟡' };

const drafts = o.needsChasing.map((d, i) => {
  const stageLine = {
    proposal: `following up on the proposal I sent`,
    demo: `checking in after our call`,
    quote: `seeing where you landed on the quote`,
  }[String(d.stage).toLowerCase()] || `following up on our conversation`;

  return `${icon[d.tier]} ${i + 1}. ${d.contact}${d.company ? ` — ${d.company}` : ''}   [${d.value} ${d.currency}]
   ${d.reason}
   Stage: ${d.stage} · contacted ${d.touchCount}× so far${d.lastNote ? `\n   Last note: ${d.lastNote}` : ''}
   ${d.email ? `Email: ${d.email}` : '(no email on record)'}

   DRAFT:
   "Hi ${String(d.contact).split(' ')[0]}, just ${stageLine} — is this still
    something you're considering? Happy to answer anything outstanding, and
    equally happy to close the file if the timing isn't right."`;
}).join('\n\n');

const text =
`📊 Pipeline digest — ${cfg.businessName}
${new Date().toISOString().slice(0, 10)}

${o.totalStale} deal(s) going cold${o.hidden ? ` (showing top ${o.needsChasing.length})` : ''}
Pipeline: ${o.openCount} open, worth ${o.openValue} ${cfg.currency}${o.wonToday ? `\nClosed today: ${o.wonToday} deal(s), ${o.wonValue} ${cfg.currency} 🎉` : ''}

━━ CHASE THESE ━━━━━━━━━━━━━━━━━━━━

${drafts}

─────────────────────────────────────
Drafts are starting points — send them in your own words.
After you reach out, POST {dealId, event:"contacted"} so this stops
listing them tomorrow.`;

return [{ json: { ...o, digestText: text,
  subject: `📊 ${o.totalStale} deal(s) need chasing — ${o.openValue} ${cfg.currency} open` }}];
""",
        (220, 540),
        notes="Short, specific drafts. Long generic ones get rewritten anyway.",
    )

    send = wf.node(
        "📨 Send the digest",
        "n8n-nodes-base.emailSend",
        {
            "fromEmail": "={{ $json.__config.fromEmail }}",
            "toEmail": "={{ $json.__config.ownerEmail }}",
            "subject": "={{ $json.subject }}",
            "emailFormat": "text",
            "text": "={{ $json.digestText }}",
            "options": {},
        },
        2.1,
        (460, 540),
        retry=True,
        max_tries=3,
        wait_ms=2000,
        on_error="continueRegularOutput",
        notes="Goes to you, never to the prospect.",
    )

    clear = wf.code(
        "✅ Pipeline is current",
        r"""
// Nothing stale. Worth saying so — silence from a digest is ambiguous, and the
// reader should be able to tell "all current" from "the schedule stopped".
const o = $input.first().json;
return [{ json: {
  checkedAt: new Date().toISOString(),
  openCount: o.openCount,
  openValue: o.openValue,
  note: o.openCount
    ? 'Every open deal has been contacted recently. Nothing to chase.'
    : 'No open deals in the pipeline.',
}}];
""",
        (220, 720),
        notes="Distinguishes 'all current' from 'not running'.",
    )

    log = wf.code(
        "📒 Pipeline log",
        r"""
// Daily snapshot. Reviewed over a month this shows whether the pipeline is
// growing or just aging, which a single day never reveals.
return $input.all().map(i => ({ json: {
  ts: new Date().toISOString(),
  openCount: i.json.openCount ?? null,
  openValue: i.json.openValue ?? null,
  staleCount: i.json.totalStale ?? 0,
  wonToday: i.json.wonToday ?? 0,
}}));
""",
        (700, 620),
        notes="Append to a Sheet. Growth vs aging only shows up over weeks.",
    )

    wf.chain(hook, cfg, guard, track, ack)
    wf.chain(sched, cfg2, stale, has_work)
    wf.connect(has_work, digest, out=0)
    wf.connect(has_work, clear, out=1)
    wf.connect(digest, send)
    wf.connect(send, log)
    wf.connect(clear, log)

    return wf
