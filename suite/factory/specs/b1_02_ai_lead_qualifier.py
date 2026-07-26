"""
DCA-B1-02 · AI Lead Qualifier & Router

The second agent, aimed at the highest-value horizontal in the catalogue: sales
pipelines. It reads an inbound enquiry, decides whether it is worth a human's
time, and routes it with a written justification.

The problem
-----------
Inbound enquiries are a mix of real buyers, tyre-kickers, students asking for
free help, and outright spam. A small team answers them in arrival order, which
means the serious buyer with budget waits behind four people who were never
going to buy. Response time is the single strongest predictor of whether an
enquiry converts, so answering in arrival order systematically loses the deals
worth most.

Why scoring here is different from the fraud template
-----------------------------------------------------
Fraud scoring is defensive and must be conservative — a false positive blocks a
paying customer, so it refuses to guess. Lead scoring is the opposite shape: the
cost of a false positive is a few wasted minutes, while a false negative is a
lost deal. So this errs toward *including* rather than excluding, and the lowest
tier is still routed to a nurture sequence rather than deleted.

Only spam is discarded outright, and even that keeps a log so the seller can
audit what was thrown away.

The deterministic layer comes first, again
------------------------------------------
Budget, company domain and explicit buying language are read with plain code
before any model call. That is cheaper, and more importantly it means an
obviously-qualified lead is never lost to a model outage or a bad response — the
model refines the score, it does not own it.
"""

from lib.core import Workflow, COLOR_BLUE, COLOR_GREEN, COLOR_RED, COLOR_PURPLE

SLUG = "ai-lead-qualifier"


def build() -> Workflow:
    wf = Workflow(
        name="DCA-B1-02 · AI Lead Qualifier & Router (answer the buyers first)",
        slug=SLUG,
        category="b1-ai-agents",
        summary="Reads every inbound enquiry, scores intent and fit, and routes hot leads to a human immediately while everything else goes to nurture — so the serious buyer never waits behind four tyre-kickers.",
        problem="Enquiries get answered in arrival order, so the buyer with budget waits behind people who were never going to buy — and response time is the strongest predictor of whether a deal closes.",
        outcome="Hot leads surface within minutes with a written justification, warm leads go to nurture, and only spam is discarded — with a log of what was thrown away.",
        version="1.0.0",
        tags=["ai-agent", "sales", "crm", "lead-scoring", "hardened"],
        credentials_needed=[
            "An AI provider API key (Anthropic, OpenAI, or any OpenAI-compatible endpoint)",
            "SMTP account for the hot-lead alert",
        ],
        setup_minutes=18,
    )

    wf.sticky(
        "## 🎯 AI Lead Qualifier & Router\n"
        "**Enquiry arrives → scored for intent and fit → routed with a reason.**\n\n"
        "### Setup (about 18 minutes)\n"
        "1. **⚙️ Config** → describe `whatYouSell`, `idealCustomer`, `priceRange`.\n"
        "   The agent judges fit against **your** definition, not a generic one.\n"
        "2. Set `aiEndpoint` / `aiModel`, add your API key as **Header Auth** on\n"
        "   **🧠 Assess the lead**.\n"
        "3. Attach SMTP to **🔥 Alert on hot lead**.\n"
        "4. Point your contact form / DM inbox at the Production URL.\n"
        "5. Activate.\n\n"
        "### Why response time is the whole game\n"
        "Answering in arrival order means your best lead waits behind four people\n"
        "who were never going to buy. This is what fixes that.",
        (-680, -520),
        (580, 540),
        COLOR_BLUE,
    )

    wf.sticky(
        "### ⚖️ Why this scores differently from fraud\n"
        "**Fraud scoring is defensive** — a false positive blocks a paying\n"
        "customer, so it refuses to guess.\n\n"
        "**Lead scoring is the opposite shape.** A false positive costs a few\n"
        "wasted minutes. A false negative is a **lost deal**.\n\n"
        "So this errs toward *including*. The lowest tier still goes to nurture,\n"
        "never to the bin. Only spam is discarded — and even that is logged so you\n"
        "can audit what was thrown away.",
        (-60, -520),
        (480, 380),
        COLOR_GREEN,
    )

    wf.sticky(
        "### 🚦 Routing\n"
        "| Tier | Means | Goes to |\n"
        "| --- | --- | --- |\n"
        "| 🔥 **hot** | budget + intent + fit | alert you **now** |\n"
        "| 🌤️ **warm** | real interest, unclear budget | follow-up queue |\n"
        "| 🌱 **nurture** | early, or poor fit today | nurture list |\n"
        "| 🗑️ **spam** | bot / irrelevant | logged, discarded |\n\n"
        "Edit the thresholds in **⚙️ Config**. Watch the hot queue for a week\n"
        "before trusting it.",
        (420, -520),
        (460, 380),
        COLOR_PURPLE,
    )

    wf.sticky(
        "### 🧱 Deterministic layer runs FIRST\n"
        "Budget mentions, business email domains and explicit buying language are\n"
        "read with plain code **before** any model call.\n\n"
        "Cheaper — and more importantly, an obviously-qualified lead is never lost\n"
        "to a model outage or a malformed response.\n\n"
        "**The model refines the score. It does not own it.**",
        (1180, 420),
        (460, 300),
        COLOR_RED,
    )

    hook = wf.webhook(
        "📥 New enquiry",
        (-680, 180),
        path="dca/lead",
        notes="POST {email, message, name?, company?, phone?, source?}.",
    )

    cfg = wf.config(
        {
            "businessName": "YOUR_BUSINESS_NAME",
            "alertEmail": "sales@yourdomain.com",
            "fromEmail": "leads@yourdomain.com",
            "whatYouSell": "REPLACE: what you actually sell, in one or two sentences.",
            "idealCustomer": "REPLACE: who gets the most value from it — size, role, situation.",
            "priceRange": "REPLACE: e.g. $49 templates up to $1,500 done-for-you setup.",
            "aiEndpoint": "https://api.anthropic.com/v1/messages",
            "aiModel": "claude-sonnet-5",
            "maxTokens": 500,
            "hotAt": 70,
            "warmAt": 40,
            "freeMailDomains": ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com"],
            "spamPhrases": ["seo services", "guest post", "backlink", "crypto investment", "make money fast", "increase your traffic"],
        },
        (-460, 180),
        notes="whatYouSell / idealCustomer / priceRange drive the fit judgement. Vague answers here give vague scoring.",
    )

    guard = wf.guard(
        (-240, 180),
        required=["body"],
        event_id_expr="(j.body?.email ?? '') + '|' + String(j.body?.message ?? '').slice(0, 60)",
        ttl_hours=12,
    )

    prescore = wf.code(
        "🧱 Deterministic pre-score",
        r"""
// Signals readable without a model. Cheap, and immune to the model being down —
// an obviously-qualified lead must never be lost to an API outage.
const cfg = $('⚙️ Config').first().json.__config;
const out = [];

for (const item of $input.all()) {
  const b = item.json.body ?? item.json;

  const email = String(b.email ?? '').trim().toLowerCase();
  const message = String(b.message ?? b.enquiry ?? b.text ?? '').trim();
  const name = String(b.name ?? '').trim();
  const company = String(b.company ?? '').trim();
  const phone = String(b.phone ?? '').trim();

  if (!email || !message) {
    throw new Error('Lead needs at least an email and a message. Received keys: ' + Object.keys(b).join(', '));
  }

  const text = (message + ' ' + company).toLowerCase();
  const domain = email.split('@')[1] || '';

  let base = 0;
  const signals = [];
  const add = (pts, why) => { base += pts; signals.push({ pts, why }); };

  // Obvious inbound spam. The only category that gets discarded.
  const spamHit = (cfg.spamPhrases || []).find(p => text.includes(String(p).toLowerCase()));
  const looksSpam = !!spamHit || /https?:\/\/\S+\s+https?:\/\/\S+/.test(message);

  // A business domain is the single strongest cheap fit signal.
  if (domain && !(cfg.freeMailDomains || []).includes(domain)) {
    add(20, `Business email domain (${domain})`);
  }
  if (company) add(10, 'Named their company');
  if (phone) add(10, 'Left a phone number — expects to be contacted');

  // Explicit buying language.
  if (/\b(price|pricing|quote|cost|how much|budget|invoice|purchase|buy)\b/i.test(message)) {
    add(20, 'Asked about price or purchasing');
  }
  if (/\b(urgent|asap|this week|deadline|immediately|right away)\b/i.test(message)) {
    add(15, 'Signalled urgency');
  }
  if (/\b(demo|trial|call|meeting|onboard|get started|sign up)\b/i.test(message)) {
    add(15, 'Asked for a next step');
  }
  // A specific question implies they have actually looked at what you sell.
  if (message.length > 200) add(10, 'Wrote a detailed enquiry');
  else if (message.length < 30) add(-10, 'Very short enquiry — low effort');

  // People asking for free help are not bad people, just not buyers today.
  if (/\b(free|student|thesis|homework|for my project|no budget)\b/i.test(message)) {
    add(-20, 'Indicated no budget');
  }

  out.push({ json: {
    email, name, company, phone, message,
    source: String(b.source ?? 'web'),
    baseScore: Math.max(0, Math.min(100, base)),
    baseSignals: signals,
    looksSpam,
    spamReason: spamHit ? `matched spam phrase "${spamHit}"` : (looksSpam ? 'multiple links, no context' : null),
    __config: cfg,
  }});
}

return out;
""",
        (0, 180),
        notes="Runs before any model call. An obviously-qualified lead survives a model outage.",
        always_output=True,
    )

    is_spam = wf.if_(
        "🗑️ Obvious spam?",
        (240, 180),
        left="={{ $json.looksSpam }}",
        operator={"type": "boolean", "operation": "false", "singleValue": True},
    )

    assess = wf.http(
        "🧠 Assess the lead",
        (480, 60),
        url="={{ $json.__config.aiEndpoint }}",
        method="POST",
        headers={"content-type": "application/json", "anthropic-version": "2023-06-01"},
        json_body=(
            "={{ JSON.stringify({\n"
            "  model: $json.__config.aiModel,\n"
            "  max_tokens: $json.__config.maxTokens,\n"
            "  system: 'You qualify inbound sales enquiries for ' + $json.__config.businessName + '.\\n\\n'\n"
            "    + 'WHAT WE SELL: ' + $json.__config.whatYouSell + '\\n'\n"
            "    + 'IDEAL CUSTOMER: ' + $json.__config.idealCustomer + '\\n'\n"
            "    + 'PRICE RANGE: ' + $json.__config.priceRange + '\\n\\n'\n"
            "    + 'Judge two things separately: INTENT (how ready are they to buy) and FIT (are they the kind of '\n"
            "    + 'customer described above). A perfect-fit company that is just browsing is not hot. Someone '\n"
            "    + 'desperate to buy something we do not sell is not hot either.\\n\\n'\n"
            "    + 'Err toward INCLUDING rather than excluding: missing a real buyer costs far more than a few '\n"
            "    + 'wasted minutes on a weak lead.\\n\\n'\n"
            "    + 'Reply with STRICT JSON only, no markdown fence:\\n'\n"
            "    + '{\"intent\": <0..50>, \"fit\": <0..50>, \"reasoning\": \"<one sentence for the salesperson>\", \"suggestedReply\": \"<short opening line they could send>\"}',\n"
            "  messages: [ { role: 'user', content: 'From: ' + $json.name + ' <' + $json.email + '>' + ($json.company ? ' at ' + $json.company : '') + '\\n\\n' + $json.message } ]\n"
            "}) }}"
        ),
        notes="Add your API key as a Header Auth credential. The model refines the score; it does not own it.",
    )

    combine = wf.code(
        "🧮 Combine and tier",
        r"""
// Blend the deterministic base with the model's judgement. If the model failed
// or returned nonsense we fall back to the base score alone rather than
// discarding the lead — losing a real buyer to an API hiccup is the one outcome
// this template exists to prevent.
const cfg = $('⚙️ Config').first().json.__config;
const src = $('🧱 Deterministic pre-score').first().json;

function extract(p) {
  return p?.content?.[0]?.text ?? p?.choices?.[0]?.message?.content ?? '';
}

return $input.all().map(item => {
  const raw = String(extract(item.json) || '').trim();

  let ai = null;
  try {
    ai = JSON.parse(raw.replace(/^```(?:json)?/i, '').replace(/```$/, '').trim());
  } catch {
    const m = raw.match(/\{[\s\S]*\}/);
    if (m) { try { ai = JSON.parse(m[0]); } catch { /* fall through */ } }
  }

  const intent = Number(ai?.intent);
  const fit = Number(ai?.fit);
  const modelOk = Number.isFinite(intent) && Number.isFinite(fit);

  // Model contributes up to 100; average it with the deterministic base so
  // neither can single-handedly dominate the decision.
  const score = modelOk
    ? Math.round((src.baseScore + intent + fit) / 2)
    : src.baseScore;

  let tier = 'nurture';
  if (score >= Number(cfg.hotAt)) tier = 'hot';
  else if (score >= Number(cfg.warmAt)) tier = 'warm';

  return { json: {
    ...src,
    score: Math.max(0, Math.min(100, score)),
    intent: modelOk ? intent : null,
    fit: modelOk ? fit : null,
    tier,
    reasoning: modelOk
      ? String(ai.reasoning || '').trim()
      : 'Model unavailable — scored on deterministic signals only. Review manually.',
    suggestedReply: modelOk ? String(ai.suggestedReply || '').trim() : '',
    modelUsed: modelOk,
  }};
});
""",
        (720, 60),
        notes="A model failure downgrades to base scoring — it never discards the lead.",
    )

    is_hot = wf.if_(
        "🔥 Hot lead?",
        (960, 60),
        left="={{ $json.tier }}",
        operator={"type": "string", "operation": "equals"},
        right="hot",
    )

    alert = wf.code(
        "✍️ Write the hot-lead alert",
        r"""
// The salesperson should be able to act straight from this message without
// opening a CRM. Everything needed to reply is in the body.
return $input.all().map(i => {
  const o = i.json;
  const bullets = o.baseSignals.map(s => `  ${s.pts > 0 ? '+' : ''}${s.pts}  ${s.why}`).join('\n');

  return { json: { ...o,
    subject: `🔥 Hot lead — ${o.name || o.email}${o.company ? ' (' + o.company + ')' : ''}`,
    alertText:
`🔥 HOT LEAD — score ${o.score}/100

${o.name || '(no name)'} <${o.email}>
${o.company ? 'Company: ' + o.company + '\n' : ''}${o.phone ? 'Phone:   ' + o.phone + '\n' : ''}Source:  ${o.source}

── WHY IT SCORED HIGH ──────────────
${o.reasoning}
${o.intent != null ? `\nIntent: ${o.intent}/50 · Fit: ${o.fit}/50` : ''}

Signals:
${bullets}

── THEIR MESSAGE ───────────────────
${o.message}

── SUGGESTED OPENING ───────────────
${o.suggestedReply || '(no draft — model unavailable, write your own)'}

⏱️ Reply fast. Response time is the strongest predictor of whether this closes.`,
  }};
});
""",
        (1200, -40),
        notes="Everything needed to reply, in one message. No CRM lookup required.",
    )

    send_alert = wf.node(
        "🔥 Alert on hot lead",
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
        (1440, -40),
        retry=True,
        max_tries=3,
        wait_ms=2000,
        on_error="continueRegularOutput",
        notes="Attach SMTP. Swap for Slack/Telegram for faster response.",
    )

    queue = wf.code(
        "📋 Queue warm / nurture",
        r"""
// Not hot today. Deliberately not deleted — a 'nurture' lead is someone who was
// early, not someone who was wrong, and they convert later if you keep in touch.
return $input.all().map(i => {
  const o = i.json;
  return { json: {
    action: o.tier === 'warm' ? 'follow_up_queue' : 'nurture_list',
    tier: o.tier,
    score: o.score,
    email: o.email,
    name: o.name,
    company: o.company,
    reasoning: o.reasoning,
    message: o.message,
    note: o.tier === 'warm'
      ? 'Real interest, budget unclear. Worth a short personal follow-up this week.'
      : 'Early or poor fit today. Add to the nurture sequence — not a rejection.',
  }};
});
""",
        (1200, 180),
        notes="Warm and nurture both stay in the pipeline. Nothing here is discarded.",
    )

    spam_log = wf.code(
        "🗑️ Log the spam",
        r"""
// Discarded, but recorded. If a real lead ever lands here you need to be able
// to find it and fix the spam phrases — an unauditable filter is one you cannot
// trust.
return $input.all().map(i => ({ json: {
  action: 'discarded_spam',
  email: i.json.email,
  reason: i.json.spamReason,
  messagePreview: String(i.json.message).slice(0, 200),
  ts: new Date().toISOString(),
  note: 'Review occasionally. If a real lead appears here, edit spamPhrases in Config.',
}}));
""",
        (480, 380),
        notes="Spam is logged, not silently dropped. Audit it occasionally.",
    )

    log = wf.code(
        "📒 Lead log",
        r"""
// One row per lead. The tier distribution over a month tells you whether your
// thresholds are right: all-nurture means hotAt is too high, all-hot means it is
// too low and the alert has stopped meaning anything.
return $input.all().map(i => ({ json: {
  ts: new Date().toISOString(),
  email: i.json.email ?? null,
  company: i.json.company ?? null,
  tier: i.json.tier ?? 'spam',
  score: i.json.score ?? null,
  action: i.json.action ?? 'alerted_hot',
  modelUsed: i.json.modelUsed ?? null,
}}));
""",
        (1680, 180),
        notes="Watch the tier mix monthly — it tells you whether hotAt/warmAt are tuned right.",
    )

    fail = wf.error_sink((960, 300), context="lead-qualifier")

    respond = wf.respond(
        "↩️ 200 OK",
        (1920, 180),
        body='={{ JSON.stringify({ ok: true }) }}',
    )

    wf.chain(hook, cfg, guard, prescore, is_spam)
    wf.connect(is_spam, assess, out=0)
    wf.connect(is_spam, spam_log, out=1)
    wf.connect(assess, combine, out=0)
    wf.connect(assess, fail, out=1)
    wf.connect(combine, is_hot)
    wf.connect(is_hot, alert, out=0)
    wf.connect(is_hot, queue, out=1)
    wf.connect(alert, send_alert)
    wf.connect(send_alert, log)
    wf.connect(queue, log)
    wf.connect(spam_log, log)
    wf.connect(fail, log)
    wf.connect(log, respond)

    return wf
