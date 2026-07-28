"""
DCA-A3-01 · Pre-Payment Fraud Scoring

Why this template exists
------------------------
A survey of the current template market turned up dispute *notification* and
dispute *tracking* workflows, but nothing that scores an order before the money
moves. That gap matters for digital goods specifically: the product is delivered
instantly and costs nothing to copy, so a fraudulent order is a total loss with
no recoverable inventory — and every chargeback also drags the seller toward the
penalty thresholds that get payment accounts frozen.

The design constraint
---------------------
Commercial fraud APIs cost per-check and require an account, a key, and a
billing relationship. Most sellers of $20–$99 digital products will never set
that up, which is exactly why they run with no screening at all.

So every signal here is computed locally from data already present in the order
plus a rolling history kept in n8n static data. No API key, no per-check cost,
no vendor. A seller can turn this on in ten minutes and start catching the
obvious attacks the same day. `enrichment` is left as an opt-in hook for anyone
who later wants to add a paid IP-reputation lookup.

Scoring is transparent on purpose: every point added is reported with the reason
that produced it, so a seller can tune thresholds against their own traffic
instead of trusting a black box.
"""

from lib.core import Workflow, COLOR_BLUE, COLOR_GREEN, COLOR_RED, COLOR_PURPLE

SLUG = "pre-payment-fraud-scoring"


def build() -> Workflow:
    wf = Workflow(
        name="DCA-A3-01 · Pre-Payment Fraud Scoring (no external API required)",
        slug=SLUG,
        category="a3-fraud-security",
        summary="Scores every order for fraud risk before delivery using local signals only — disposable domains, velocity, geo mismatch, amount anomalies — and routes it to allow, review or block.",
        problem="Digital goods are delivered instantly and cost nothing to copy, so a fraudulent order is a total loss — and the resulting chargebacks push the seller toward the ratios that get payment accounts frozen. Existing templates only react after a dispute is already open.",
        outcome="Risky orders are held for review before the file is handed over, with a transparent score and a written reason for every decision — and it runs without a paid fraud API.",
        version="1.0.0",
        tags=["fraud", "chargeback", "security", "digital-products", "hardened"],
        credentials_needed=["None required for scoring", "Optional: Slack/Telegram/email for review alerts"],
        setup_minutes=10,
    )

    wf.sticky(
        "## 🕵️ Pre-Payment Fraud Scoring\n"
        "**Score the order → allow, review, or block — before you hand over the file.**\n\n"
        "### Why this is different\n"
        "Every other fraud workflow on the market reacts *after* a dispute opens.\n"
        "This one runs *before* delivery, and it needs **no paid fraud API** —\n"
        "all signals are computed from the order itself plus a rolling local history.\n\n"
        "### Setup (about 10 minutes)\n"
        "1. Open **⚙️ Config** and set `reviewAt` / `blockAt` thresholds.\n"
        "2. Point your checkout or payment webhook at this workflow's Production URL.\n"
        "3. Wire the three outcome branches to whatever you use (delivery workflow,\n"
        "   Slack channel, refund queue).\n"
        "4. Run for a week in `shadowMode: true` — it scores and reports but never\n"
        "   blocks — then read the numbers and tune before enforcing.\n\n"
        "⚠️ **Start in shadow mode.** Thresholds that are right for one store are\n"
        "wrong for another. Tune on your own traffic, not on someone else's defaults.",
        (-640, -460),
        (580, 600),
        COLOR_BLUE,
    )

    wf.sticky(
        "### 📊 The signals\n"
        "| Signal | Points | Catches |\n"
        "| --- | --- | --- |\n"
        "| Disposable email domain | 35 | throwaway-account abuse |\n"
        "| Brand-new random-looking local part | 15 | scripted signups |\n"
        "| Billing vs IP country mismatch | 25 | stolen card use |\n"
        "| High-risk / sanctioned geo | 20 | known-bad regions |\n"
        "| Email velocity (same buyer, short window) | 30 | card testing |\n"
        "| IP velocity (many buyers, one IP) | 30 | bulk fraud runs |\n"
        "| Amount far above your norm | 20 | maximising a stolen card |\n"
        "| Multiple distinct cards, one email | 25 | card testing |\n"
        "| Name/email mismatch | 10 | weak signal, tune-able |\n\n"
        "Every point is reported with its reason. Nothing is hidden.",
        (-20, -460),
        (500, 480),
        COLOR_GREEN,
    )

    wf.sticky(
        "### 🎯 Tuning honestly\n"
        "Fraud scoring trades false positives against losses. Blocking a real\n"
        "customer costs a sale **and** goodwill; letting fraud through costs the\n"
        "product plus a dispute fee.\n\n"
        "Defaults here are deliberately conservative — `blockAt: 80` blocks only\n"
        "orders carrying several strong signals at once. Most stores should raise\n"
        "`reviewAt` rather than lower `blockAt`.\n\n"
        "**No scoring system is perfect.** Review the `review` queue daily; that is\n"
        "where the value actually is.",
        (520, -460),
        (460, 400),
        COLOR_PURPLE,
    )

    wf.sticky(
        "### 🚨 Outcomes\n"
        "**allow** → continue to delivery.\n"
        "**review** → hold, alert a human, deliver after approval.\n"
        "**block** → do not deliver; refund or let the payment fail.\n\n"
        "In `shadowMode` all three report but always resolve to *allow*, so you can\n"
        "measure before you enforce.",
        (1500, 300),
        (440, 280),
        COLOR_RED,
    )

    hook = wf.webhook(
        "🛒 Order created",
        (-640, 200),
        path="dca/fraud-check",
        notes="Point your checkout / payment-intent webhook here. Runs before delivery.",
    )

    cfg = wf.config(
        {
            "reviewAt": 45,
            "blockAt": 80,
            "shadowMode": True,
            "velocityWindowMinutes": 60,
            "maxOrdersPerEmail": 3,
            "maxOrdersPerIp": 5,
            "typicalOrderAmount": 49,
            "amountAnomalyMultiplier": 4,
            "highRiskCountries": [],
            "trustedEmails": [],
            "trustedDomains": [],
            "historyTtlHours": 24,
        },
        (-420, 200),
        notes="Start with shadowMode:true. Tune reviewAt/blockAt on a week of your own traffic before enforcing.",
    )

    guard = wf.guard(
        (-200, 200),
        required=["body"],
        event_id_expr="j.body?.orderId ?? j.body?.order_id ?? j.body?.id ?? (j.body?.email + '|' + Date.now())",
        ttl_hours=24,
    )

    extract = wf.code(
        "📥 Extract order signals",
        r"""
// Pull the fields we score from whatever shape the checkout sent. Being
// permissive here matters: sellers wire this to Stripe, to a custom checkout,
// or to a form, and the template should not care which.
const cfg = $('⚙️ Config').first().json.__config;

return $input.all().map(item => {
  const b = item.json.body ?? item.json;
  const h = item.json.headers ?? {};

  const email = String(b.email ?? b.customer_email ?? b.customer?.email ?? '').trim().toLowerCase();

  // Prefer the proxy-forwarded client IP; fall back to the socket address.
  const ip = String(
    (h['x-forwarded-for'] || '').split(',')[0].trim() ||
    h['cf-connecting-ip'] || h['x-real-ip'] || b.ip || b.customer_ip || ''
  );

  return {
    json: {
      orderId:        b.orderId ?? b.order_id ?? b.id ?? null,
      email,
      name:           String(b.name ?? b.customer_name ?? b.customer?.name ?? '').trim(),
      amount:         Number(b.amount ?? b.total ?? b.price ?? 0),
      currency:       String(b.currency ?? 'USD').toUpperCase(),
      ip,
      ipCountry:      String(h['cf-ipcountry'] ?? b.ipCountry ?? b.ip_country ?? '').toUpperCase(),
      billingCountry: String(b.country ?? b.billingCountry ?? b.billing_country ?? b.customer?.country ?? '').toUpperCase(),
      cardFingerprint: String(b.cardFingerprint ?? b.card_fingerprint ?? b.payment_method ?? ''),
      userAgent:      String(h['user-agent'] ?? ''),
      __config:       cfg,
    }
  };
});
""",
        (20, 200),
        notes="Normalises checkout payloads. Missing fields simply score as unknown rather than crashing.",
    )

    score = wf.code(
        "🧮 Score the risk",
        r"""
// ═══════════════════════════════════════════════════════════════════
// Transparent, local-only fraud scoring.
//
// Design rule: every point added must come with a human-readable reason.
// A seller who cannot see why an order was blocked cannot tune the system,
// and an untunable system gets switched off within a week.
// ═══════════════════════════════════════════════════════════════════

// A representative sample of throwaway-mail providers. This is intentionally a
// starter list, not an exhaustive one — exhaustive lists go stale within weeks.
// Add the domains you actually see in your own review queue.
const DISPOSABLE = new Set([
  'mailinator.com','guerrillamail.com','10minutemail.com','tempmail.com','temp-mail.org',
  'throwawaymail.com','yopmail.com','trashmail.com','sharklasers.com','getnada.com',
  'maildrop.cc','dispostable.com','fakeinbox.com','mailnesia.com','mytemp.email',
  'moakt.com','emailondeck.com','tempr.email','mohmal.com','spamgourmet.com',
  'grr.la','guerrillamailblock.com','pokemail.net','spam4.me','tempmailo.com',
  'burnermail.io','anonaddy.me','mailsac.com','inboxkitten.com','harakirimail.com',
]);

const FREE_MAIL = new Set([
  'gmail.com','yahoo.com','hotmail.com','outlook.com','icloud.com','aol.com',
  'proton.me','protonmail.com','gmx.com','mail.com','yandex.com','zoho.com',
]);

const store = $getWorkflowStaticData('global');
store.orders = store.orders || [];

const out = [];

for (const item of $input.all()) {
  const o = item.json;
  const cfg = o.__config;
  const now = Date.now();
  const windowMs = Number(cfg.velocityWindowMinutes) * 60 * 1000;
  const ttlMs = Number(cfg.historyTtlHours) * 60 * 60 * 1000;

  // Keep history bounded — both by age and by absolute count, so a traffic
  // spike cannot grow static data without limit.
  store.orders = store.orders.filter(r => now - r.t < ttlMs).slice(-2000);

  let score = 0;
  const reasons = [];
  const add = (points, reason) => { score += points; reasons.push({ points, reason }); };

  const domain = o.email.split('@')[1] || '';

  // ── Allow-list short-circuit ────────────────────────────────────
  const trusted =
    (cfg.trustedEmails || []).includes(o.email) ||
    (cfg.trustedDomains || []).includes(domain);

  if (trusted) {
    out.push({ json: { ...o, riskScore: 0, riskReasons: [{ points: 0, reason: 'Allow-listed buyer' }], decision: 'allow', shadowMode: cfg.shadowMode } });
    store.orders.push({ t: now, email: o.email, ip: o.ip, card: o.cardFingerprint, amount: o.amount });
    continue;
  }

  // ── Email signals ───────────────────────────────────────────────
  if (!o.email || !o.email.includes('@')) {
    add(40, 'No usable email address on the order');
  } else if (DISPOSABLE.has(domain)) {
    add(35, `Disposable email domain (${domain})`);
  }

  const local = o.email.split('@')[0] || '';
  // Long, high-entropy local parts with no separators are a scripted-signup tell.
  if (local.length >= 12 && /^[a-z0-9]+$/.test(local) && !/[._-]/.test(local)) {
    const digits = (local.match(/\d/g) || []).length;
    if (digits >= 4) add(15, 'Email local part looks machine-generated');
  }

  // ── Geography ───────────────────────────────────────────────────
  if (o.ipCountry && o.billingCountry && o.ipCountry !== o.billingCountry) {
    add(25, `Billing country (${o.billingCountry}) does not match IP country (${o.ipCountry})`);
  }
  if (o.ipCountry && (cfg.highRiskCountries || []).includes(o.ipCountry)) {
    add(20, `Order originates from a country on your high-risk list (${o.ipCountry})`);
  }

  // ── Velocity ────────────────────────────────────────────────────
  const recent = store.orders.filter(r => now - r.t < windowMs);

  const sameEmail = recent.filter(r => r.email === o.email).length;
  if (sameEmail >= Number(cfg.maxOrdersPerEmail)) {
    add(30, `${sameEmail + 1} orders from this email within ${cfg.velocityWindowMinutes} minutes`);
  }

  if (o.ip) {
    const sameIp = recent.filter(r => r.ip === o.ip).length;
    if (sameIp >= Number(cfg.maxOrdersPerIp)) {
      add(30, `${sameIp + 1} orders from IP ${o.ip} within ${cfg.velocityWindowMinutes} minutes`);
    }
  }

  // Several different cards behind one email is the classic card-testing shape.
  if (o.cardFingerprint) {
    const cards = new Set(
      recent.filter(r => r.email === o.email && r.card).map(r => r.card)
    );
    cards.add(o.cardFingerprint);
    if (cards.size >= 3) {
      add(25, `${cards.size} different payment methods used by this email — card testing pattern`);
    }
  }

  // ── Amount anomaly ──────────────────────────────────────────────
  const typical = Number(cfg.typicalOrderAmount) || 0;
  if (typical > 0 && o.amount > typical * Number(cfg.amountAnomalyMultiplier)) {
    add(20, `Order value ${o.amount} is more than ${cfg.amountAnomalyMultiplier}× your typical ${typical}`);
  }

  // ── Weak corroborating signals ──────────────────────────────────
  // Deliberately low-weight: plenty of legitimate people buy with a name that
  // does not appear in their email address.
  if (o.name && o.email) {
    const first = o.name.toLowerCase().split(/\s+/)[0] || '';
    if (first.length >= 3 && !local.includes(first)) {
      add(10, 'Buyer name does not appear in the email address');
    }
  }
  if (!o.userAgent) {
    add(10, 'No browser user-agent — request did not come from a normal checkout page');
  }

  // ── Decision ────────────────────────────────────────────────────
  let decision = 'allow';
  if (score >= Number(cfg.blockAt)) decision = 'block';
  else if (score >= Number(cfg.reviewAt)) decision = 'review';

  // Shadow mode measures without enforcing, so a seller can see what the rules
  // *would* have done before letting them touch live revenue.
  const enforced = cfg.shadowMode ? 'allow' : decision;

  store.orders.push({ t: now, email: o.email, ip: o.ip, card: o.cardFingerprint, amount: o.amount });

  out.push({
    json: {
      ...o,
      riskScore: score,
      riskReasons: reasons,
      decision: enforced,
      wouldHaveBeen: decision,
      shadowMode: !!cfg.shadowMode,
      scoredAt: new Date().toISOString(),
    }
  });
}

return out;
""",
        (240, 200),
        notes="All scoring happens here, locally. Every point carries its reason so you can tune it.",
        always_output=True,
    )

    route = wf.node(
        "🔀 Route the decision",
        "n8n-nodes-base.switch",
        {
            "rules": {
                "values": [
                    {
                        "conditions": {
                            "options": {"version": 2, "leftValue": "", "caseSensitive": True, "typeValidation": "loose"},
                            "combinator": "and",
                            "conditions": [
                                {
                                    "id": "r-allow",
                                    "operator": {"type": "string", "operation": "equals"},
                                    "leftValue": "={{ $json.decision }}",
                                    "rightValue": "allow",
                                }
                            ],
                        },
                        "outputKey": "allow",
                    },
                    {
                        "conditions": {
                            "options": {"version": 2, "leftValue": "", "caseSensitive": True, "typeValidation": "loose"},
                            "combinator": "and",
                            "conditions": [
                                {
                                    "id": "r-review",
                                    "operator": {"type": "string", "operation": "equals"},
                                    "leftValue": "={{ $json.decision }}",
                                    "rightValue": "review",
                                }
                            ],
                        },
                        "outputKey": "review",
                    },
                    {
                        "conditions": {
                            "options": {"version": 2, "leftValue": "", "caseSensitive": True, "typeValidation": "loose"},
                            "combinator": "and",
                            "conditions": [
                                {
                                    "id": "r-block",
                                    "operator": {"type": "string", "operation": "equals"},
                                    "leftValue": "={{ $json.decision }}",
                                    "rightValue": "block",
                                }
                            ],
                        },
                        "outputKey": "block",
                    },
                ]
            },
            "options": {"fallbackOutput": 0},
        },
        3.2,
        (480, 200),
        notes="Output 0 = allow · 1 = review · 2 = block. Unknown decisions fall back to allow.",
    )

    allow = wf.code(
        "✅ Allow → deliver",
        r"""
// Clean order. Hand off to DCA-A1-01 (Instant Digital Delivery) or whatever
// fulfilment you already run.
return $input.all().map(i => ({
  json: {
    action: 'deliver',
    orderId: i.json.orderId,
    email: i.json.email,
    amount: i.json.amount,
    currency: i.json.currency,
    riskScore: i.json.riskScore,
    checkedAt: i.json.scoredAt,
  }
}));
""",
        (740, 40),
        notes="Wire to your delivery workflow.",
    )

    review = wf.code(
        "🔍 Review → alert a human",
        r"""
// Held for a person to look at. The alert has to contain enough context to
// decide in seconds, otherwise the queue gets ignored and the whole control
// stops being real.
return $input.all().map(i => {
  const o = i.json;
  const bullets = o.riskReasons.map(r => `• +${r.points} — ${r.reason}`).join('\n');
  return {
    json: {
      action: 'hold_for_review',
      orderId: o.orderId,
      email: o.email,
      amount: `${o.amount} ${o.currency}`,
      ip: o.ip,
      riskScore: o.riskScore,
      shadowMode: o.shadowMode,
      alertText:
        `⚠️ Order held for review\n` +
        `Order: ${o.orderId}\nBuyer: ${o.email}\nAmount: ${o.amount} ${o.currency}\n` +
        `Risk score: ${o.riskScore}\n\nWhy:\n${bullets}\n\n` +
        (o.shadowMode ? '(shadow mode — this order was NOT actually held)' : 'Approve to deliver, or refund.'),
    }
  };
});
""",
        (740, 220),
        notes="Send alertText to Slack/Telegram/email. Review this queue daily — it is where the value is.",
    )

    block = wf.code(
        "⛔ Block → do not deliver",
        r"""
// High confidence of fraud. Nothing is delivered. Keep the full reason set:
// if the buyer turns out to be legitimate and complains, you need to be able to
// explain the decision and add them to trustedEmails.
return $input.all().map(i => {
  const o = i.json;
  return {
    json: {
      action: 'block',
      orderId: o.orderId,
      email: o.email,
      amount: `${o.amount} ${o.currency}`,
      riskScore: o.riskScore,
      reasons: o.riskReasons,
      shadowMode: o.shadowMode,
      note: o.shadowMode
        ? 'Shadow mode — order was allowed through. This is what would have happened.'
        : 'Blocked before delivery. Refund the payment or let it fail.',
    }
  };
});
""",
        (740, 400),
        notes="Nothing is delivered on this branch. Add false positives to trustedEmails in Config.",
    )

    audit = wf.code(
        "📒 Audit log",
        r"""
// One row per scored order. This log is what lets you answer "is the scoring
// actually working?" after a month — and it is the evidence trail if a payment
// provider ever asks how you screen orders.
return $input.all().map(i => ({
  json: {
    ts: new Date().toISOString(),
    orderId: i.json.orderId,
    email: i.json.email,
    action: i.json.action,
    riskScore: i.json.riskScore ?? null,
    shadowMode: i.json.shadowMode ?? null,
  }
}));
""",
        (1020, 220),
        notes="Append to Sheets/Airtable/DB. Review weekly and re-tune thresholds.",
    )

    respond = wf.respond(
        "↩️ Return decision",
        (1260, 220),
        body='={{ JSON.stringify({ ok: true, decision: $json.action, riskScore: $json.riskScore ?? null }) }}',
    )

    wf.chain(hook, cfg, guard, extract, score, route)
    wf.connect(route, allow, out=0)
    wf.connect(route, review, out=1)
    wf.connect(route, block, out=2)
    for n in (allow, review, block):
        wf.connect(n, audit)
    wf.connect(audit, respond)

    return wf
