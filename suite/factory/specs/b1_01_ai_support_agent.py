"""
DCA-B1-01 · AI Customer Support Agent

The distinction that makes this an agent rather than an autoresponder: it reads
the question, decides whether it can answer from the knowledge you gave it, and
hands over to a human when it cannot. An autoresponder always replies. An agent
sometimes declines — and the declining is the valuable part.

The failure mode this is built against
--------------------------------------
Most AI support workflows on the market pipe the customer's message straight
into a model and send whatever comes back. That works until the model is asked
something the business never told it, at which point it invents an answer:
a refund window that does not exist, a feature that was never built, a delivery
time nobody promised. The customer then holds the seller to it.

A confidently wrong answer is worse than no answer, because it creates an
obligation and destroys trust at the same time. So this template is built around
refusing rather than guessing:

  * The model is given the seller's actual facts and instructed to answer only
    from them.
  * It must return a confidence score and an explicit escalate flag.
  * Anything below the threshold, and anything touching refunds, payments,
    legal or account access, goes to a human regardless of confidence.
  * The draft is still attached to the escalation, so the human edits rather
    than writes.

Model choice is left to the buyer. The HTTP node is provider-shaped rather than
locked to one vendor, and the Config carries the endpoint and model id.
"""

from lib.core import Workflow, COLOR_BLUE, COLOR_GREEN, COLOR_RED, COLOR_PURPLE

SLUG = "ai-customer-support-agent"


def build() -> Workflow:
    wf = Workflow(
        name="DCA-B1-01 · AI Customer Support Agent (answers from your facts, escalates when unsure)",
        slug=SLUG,
        category="b1-ai-agents",
        summary="Answers customer questions from a knowledge base you control, scores its own confidence, and hands anything uncertain or sensitive to a human with a draft already written.",
        problem="AI support workflows that reply to everything eventually invent a refund policy or a feature that does not exist — and the customer holds the seller to it. A confidently wrong answer creates an obligation and destroys trust at once.",
        outcome="Routine questions answered in seconds from your own facts; uncertain and sensitive ones escalated to a human with a draft attached, so nothing is ever invented.",
        version="1.0.0",
        tags=["ai-agent", "support", "customer-service", "hardened"],
        credentials_needed=[
            "An AI provider API key (Anthropic, OpenAI, or any OpenAI-compatible endpoint)",
            "SMTP account for sending replies",
        ],
        setup_minutes=20,
    )

    wf.sticky(
        "## 🤖 AI Customer Support Agent\n"
        "**Reads the question → answers from YOUR facts → escalates when unsure.**\n\n"
        "### Setup (about 20 minutes)\n"
        "1. **⚙️ Config** → fill `knowledgeBase` with your real policies, products,\n"
        "   delivery times and refund terms. **This is the whole job** — the agent\n"
        "   can only be as accurate as what you put here.\n"
        "2. Set `aiEndpoint` and `aiModel` for your provider.\n"
        "3. Add your API key as a **Header Auth** credential on **🧠 Ask the model**.\n"
        "4. Attach SMTP to **📧 Send the reply**.\n"
        "5. Point your contact form / inbox automation at the Production URL.\n"
        "6. Run with `autoReply: false` for a week — it drafts everything and sends\n"
        "   nothing, so you can read what it *would* have said.\n\n"
        "⚠️ **Start with `autoReply: false`.** Read a week of drafts before you let\n"
        "it talk to customers unsupervised.",
        (-680, -520),
        (600, 600),
        COLOR_BLUE,
    )

    wf.sticky(
        "### 🛑 Why it refuses rather than guesses\n"
        "Most AI support templates reply to everything. That works until a\n"
        "customer asks about something the business never wrote down — and the\n"
        "model invents a refund window, a feature, a delivery promise.\n\n"
        "**The customer then holds you to it.**\n\n"
        "So this agent must answer *only* from `knowledgeBase`, must report a\n"
        "confidence score, and must set an escalate flag when it is unsure.\n"
        "Below the threshold → a human sees it.\n\n"
        "A slower correct answer beats an instant invented one.",
        (-40, -520),
        (480, 440),
        COLOR_GREEN,
    )

    wf.sticky(
        "### 🚨 Always escalated, whatever the confidence\n"
        "- refunds and chargebacks\n"
        "- payment and billing disputes\n"
        "- legal, tax, GDPR, privacy demands\n"
        "- account access and deletion\n"
        "- anything with an angry tone\n\n"
        "These carry money or obligation. Confidence is irrelevant — a human\n"
        "decides. Edit the list in **⚙️ Config → alwaysEscalate**.",
        (460, -520),
        (440, 400),
        COLOR_RED,
    )

    wf.sticky(
        "### 💰 Running cost\n"
        "Roughly **$0.001–$0.01 per question**, depending on model and knowledge\n"
        "base size. A hundred questions a day is a few dollars a month.\n\n"
        "The buyer supplies their own API key — **no key ships in this template**,\n"
        "and the build gate rejects any template that contains one.",
        (1480, 380),
        (420, 280),
        COLOR_PURPLE,
    )

    hook = wf.webhook(
        "💬 Customer question",
        (-680, 180),
        path="dca/support",
        notes="POST {email, message, name?, subject?}. Wire your contact form or inbox here.",
    )

    cfg = wf.config(
        {
            "storeName": "YOUR_STORE_NAME",
            "fromEmail": "support@yourdomain.com",
            "humanEmail": "you@yourdomain.com",
            "aiEndpoint": "https://api.anthropic.com/v1/messages",
            "aiModel": "claude-sonnet-5",
            "maxTokens": 700,
            "confidenceThreshold": 0.75,
            "autoReply": False,
            "alwaysEscalate": [
                "refund", "chargeback", "dispute", "money back", "cancel my",
                "lawyer", "legal", "gdpr", "sue", "delete my account",
                "invoice", "tax", "vat", "fraud", "scam",
            ],
            "knowledgeBase": (
                "REPLACE THIS ENTIRELY WITH YOUR OWN FACTS.\n\n"
                "Products: describe what you sell, what is included, and the format.\n"
                "Delivery: how the product arrives and how quickly.\n"
                "Download links: how long they stay valid and how to get a fresh one.\n"
                "Refunds: your actual policy and the exact window.\n"
                "Payment methods you accept.\n"
                "Support hours and expected response time.\n\n"
                "Be specific. Anything missing here is something the agent will "
                "correctly refuse to answer — which is the intended behaviour."
            ),
        },
        (-460, 180),
        notes="knowledgeBase is the whole job. Accuracy here IS the agent's accuracy.",
    )

    guard = wf.guard(
        (-240, 180),
        required=["body"],
        event_id_expr="(j.body?.email ?? '') + '|' + String(j.body?.message ?? '').slice(0, 60)",
        ttl_hours=6,
    )

    triage = wf.code(
        "🔍 Pre-triage",
        r"""
// Cheap deterministic checks BEFORE spending a model call.
//
// Two jobs: catch the categories that must reach a human regardless of what any
// model thinks, and catch obvious junk so it does not cost an API call.
const cfg = $('⚙️ Config').first().json.__config;
const out = [];

for (const item of $input.all()) {
  const b = item.json.body ?? item.json;

  const email = String(b.email ?? b.from ?? '').trim().toLowerCase();
  const message = String(b.message ?? b.text ?? b.body ?? b.question ?? '').trim();
  const name = String(b.name ?? '').trim();
  const subject = String(b.subject ?? '').trim();

  if (!email || !message) {
    throw new Error('Support request needs both an email and a message. Received keys: ' + Object.keys(b).join(', '));
  }

  const haystack = (subject + ' ' + message).toLowerCase();

  // Sensitive categories: money or obligation. A human decides, always.
  const hits = (cfg.alwaysEscalate || []).filter(k => haystack.includes(String(k).toLowerCase()));

  // Crude anger detection. Deliberately conservative — annoyed customers get a
  // person, because an AI reply to a furious message reads as contempt.
  const shouting = message.length > 20 &&
    message.replace(/[^A-Z]/g, '').length / Math.max(1, message.replace(/[^A-Za-z]/g, '').length) > 0.6;
  const angry = shouting || /\b(angry|furious|unacceptable|terrible|worst|disgrace|ripped off)\b/i.test(message);

  const forced = hits.length > 0 || angry;

  out.push({ json: {
    email, name, subject, message,
    forcedEscalation: forced,
    escalationReason: hits.length ? `matched sensitive topic: ${hits.join(', ')}` : (angry ? 'customer appears upset' : null),
    tooShort: message.length < 5,
    __config: cfg,
  }});
}

return out;
""",
        (0, 180),
        notes="Deterministic guardrails run before any model call — cheaper and not overridable by the model.",
        always_output=True,
    )

    needs_ai = wf.if_(
        "🤔 Worth asking the model?",
        (240, 180),
        left="={{ $json.forcedEscalation || $json.tooShort }}",
        operator={"type": "boolean", "operation": "false", "singleValue": True},
    )

    ask = wf.http(
        "🧠 Ask the model",
        (480, 60),
        url="={{ $json.__config.aiEndpoint }}",
        method="POST",
        headers={
            "content-type": "application/json",
            "anthropic-version": "2023-06-01",
        },
        json_body=(
            "={{ JSON.stringify({\n"
            "  model: $json.__config.aiModel,\n"
            "  max_tokens: $json.__config.maxTokens,\n"
            "  system: 'You are a customer support agent for ' + $json.__config.storeName + '.\\n\\n'\n"
            "    + 'ANSWER ONLY FROM THE FACTS BELOW. If the facts do not cover the question, you MUST set '\n"
            "    + '\"escalate\": true and leave the reply empty. Never guess a policy, price, timeframe or feature. '\n"
            "    + 'Inventing an answer creates an obligation the business did not agree to.\\n\\n'\n"
            "    + '=== FACTS ===\\n' + $json.__config.knowledgeBase + '\\n=== END FACTS ===\\n\\n'\n"
            "    + 'Reply with STRICT JSON only, no markdown fence:\\n'\n"
            "    + '{\"reply\": \"<plain text answer to the customer>\", \"confidence\": <0..1>, \"escalate\": <true|false>, \"reason\": \"<short note for the human>\"}\\n\\n'\n"
            "    + 'Set confidence below 0.75 whenever the facts only partly cover the question.',\n"
            "  messages: [ { role: 'user', content: 'Customer: ' + $json.name + ' <' + $json.email + '>\\nSubject: ' + $json.subject + '\\n\\n' + $json.message } ]\n"
            "}) }}"
        ),
        notes="Add your API key as a Header Auth credential (x-api-key for Anthropic, Authorization for OpenAI).",
    )

    parse = wf.code(
        "📖 Read the answer",
        r"""
// Never trust the shape of a model response. Parse defensively and treat any
// failure to parse as a reason to escalate — silence is safer than garbage sent
// to a paying customer.
const cfg = $('⚙️ Config').first().json.__config;
const src = $('🔍 Pre-triage').first().json;

function extract(payload) {
  // Anthropic: content[].text · OpenAI: choices[].message.content
  return payload?.content?.[0]?.text
      ?? payload?.choices?.[0]?.message?.content
      ?? payload?.completion
      ?? '';
}

return $input.all().map(item => {
  const raw = String(extract(item.json) || '').trim();

  let parsed = null;
  try {
    // Models sometimes wrap JSON in a fence despite instructions.
    const cleaned = raw.replace(/^```(?:json)?/i, '').replace(/```$/, '').trim();
    parsed = JSON.parse(cleaned);
  } catch {
    const m = raw.match(/\{[\s\S]*\}/);
    if (m) { try { parsed = JSON.parse(m[0]); } catch { /* fall through */ } }
  }

  if (!parsed || typeof parsed.reply !== 'string') {
    return { json: {
      ...src,
      aiReply: '', confidence: 0, escalate: true,
      escalationReason: 'model returned an unreadable response — escalating rather than guessing',
      rawModelOutput: raw.slice(0, 500),
      __config: cfg,
    }};
  }

  const confidence = Number(parsed.confidence);
  const belowBar = !Number.isFinite(confidence) || confidence < Number(cfg.confidenceThreshold);

  return { json: {
    ...src,
    aiReply: String(parsed.reply || '').trim(),
    confidence: Number.isFinite(confidence) ? confidence : 0,
    escalate: parsed.escalate === true || belowBar || !String(parsed.reply || '').trim(),
    escalationReason: parsed.escalate === true
      ? (parsed.reason || 'model asked for a human')
      : (belowBar ? `confidence ${confidence} below threshold ${cfg.confidenceThreshold}` : null),
    __config: cfg,
  }};
});
""",
        (720, 60),
        notes="Unparseable output escalates instead of sending nonsense to a customer.",
    )

    decide = wf.if_(
        "✅ Safe to send automatically?",
        (960, 60),
        left="={{ !$json.escalate && $json.__config.autoReply === true }}",
        operator={"type": "boolean", "operation": "true", "singleValue": True},
    )

    send = wf.node(
        "📧 Send the reply",
        "n8n-nodes-base.emailSend",
        {
            "fromEmail": "={{ $json.__config.fromEmail }}",
            "toEmail": "={{ $json.email }}",
            "subject": "={{ $json.subject ? 'Re: ' + $json.subject : ('Re: your question — ' + $json.__config.storeName) }}",
            "emailFormat": "html",
            "html": (
                "={{ '<div style=\"font-family:system-ui,-apple-system,Segoe UI,sans-serif;max-width:560px;"
                "margin:0 auto;padding:28px 24px;color:#111;line-height:1.65\">'"
                " + '<p style=\"white-space:pre-wrap;margin:0 0 20px\">' + $json.aiReply + '</p>'"
                " + '<p style=\"color:#777;font-size:13px;margin:0\">If this did not answer your question, just reply "
                "and a person will pick it up.</p>'"
                " + '<hr style=\"border:none;border-top:1px solid #eee;margin:24px 0\">'"
                " + '<p style=\"color:#999;font-size:12px;margin:0\">' + $json.__config.storeName + '</p>'"
                " + '</div>' }}"
            ),
            "options": {},
        },
        2.1,
        (1200, -40),
        retry=True,
        max_tries=3,
        wait_ms=3000,
        on_error="continueErrorOutput",
        notes="Only reached when the agent is confident AND autoReply is on.",
    )

    escalate = wf.code(
        "🙋 Hand to a human",
        r"""
// Everything uncertain, sensitive or unparseable lands here — plus everything
// at all while autoReply is false.
//
// The draft is included on purpose: a human editing a draft is several times
// faster than a human starting from a blank reply, so the agent still saves
// most of the work even when it declines to send.
return $input.all().map(i => {
  const o = i.json;
  const cfg = o.__config;

  const why = o.escalationReason
    || (cfg.autoReply === false ? 'autoReply is off — review mode' : 'flagged for human review');

  return { json: {
    action: 'escalated',
    to: cfg.humanEmail,
    customerEmail: o.email,
    customerName: o.name,
    subject: `[support] ${o.subject || 'question'} — from ${o.email}`,
    confidence: o.confidence ?? null,
    reason: why,
    alertText:
      `🙋 Support request needs you\n\n` +
      `From: ${o.name || '(no name)'} <${o.email}>\n` +
      `Subject: ${o.subject || '(none)'}\n` +
      `Why escalated: ${why}\n` +
      (o.confidence != null ? `Confidence: ${o.confidence}\n` : '') +
      `\n--- Their message ---\n${o.message}\n` +
      (o.aiReply ? `\n--- Suggested draft (edit before sending) ---\n${o.aiReply}\n` : '\n(no draft — the agent declined to answer)\n'),
  }};
});
""",
        (1200, 180),
        notes="Sends you the question plus a draft. Editing a draft is far faster than writing from scratch.",
    )

    notify = wf.node(
        "📨 Notify the human",
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
        (1440, 180),
        retry=True,
        max_tries=3,
        wait_ms=3000,
        on_error="continueErrorOutput",
        notes="Swap for Slack or Telegram if you prefer.",
    )

    log = wf.code(
        "📒 Support log",
        r"""
// Track what the agent handled versus what it escalated. If the escalation rate
// stays high, the knowledge base has gaps — and the escalation reasons tell you
// exactly which gaps.
return $input.all().map(i => ({ json: {
  ts: new Date().toISOString(),
  customer: i.json.customerEmail ?? i.json.email ?? null,
  outcome: i.json.action ?? 'auto_replied',
  confidence: i.json.confidence ?? null,
  reason: i.json.reason ?? null,
}}));
""",
        (1680, 60),
        notes="Review weekly. A high escalation rate is a knowledge-base gap, not an agent failure.",
    )

    fail = wf.error_sink((960, 340), context="ai-support")

    wf.chain(hook, cfg, guard, triage, needs_ai)
    wf.connect(needs_ai, ask, out=0)
    wf.connect(needs_ai, escalate, out=1)
    wf.connect(ask, parse, out=0)
    wf.connect(ask, fail, out=1)
    wf.connect(parse, decide)
    wf.connect(decide, send, out=0)
    wf.connect(decide, escalate, out=1)
    wf.connect(send, log, out=0)
    wf.connect(send, fail, out=1)
    wf.connect(escalate, notify)
    wf.connect(notify, log, out=0)
    wf.connect(notify, fail, out=1)

    return wf
