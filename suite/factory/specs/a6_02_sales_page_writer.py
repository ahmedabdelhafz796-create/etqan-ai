"""
DCA-A6-02 · AI Sales Page & Listing Writer

Solves "إنشاء صفحات بيع احترافية بالذكاء الاصطناعي" — and, usefully, it is the
template the seller of this suite will use on their own listings.

The failure mode it avoids
--------------------------
Ask a model for a sales page and it produces confident marketing prose full of
claims the product cannot support: "trusted by thousands", "guaranteed results",
"the industry standard". That copy converts badly because readers have learned
to discount it, and worse, it creates obligations. A refund policy invented in a
sales page is a refund policy a customer will hold you to.

So the model here is given the product's *facts* and instructed to write from
them only. Anything it cannot support from the facts must be omitted rather than
softened, and a deterministic pass afterwards scans the output for unsupported
superlatives and flags them before anything is published.

Structure over persuasion
-------------------------
The output follows the ordering that actually sells, which the suite's own
research established: lead with the problem the reader recognises, then proof,
then what they get, then explicit limits. "What this does not do" is included on
purpose — it is the section that separates a listing readers trust from one they
skim past, and it reduces refunds by setting accurate expectations before the
sale rather than after.
"""

from lib.core import Workflow, COLOR_BLUE, COLOR_GREEN, COLOR_RED, COLOR_PURPLE

SLUG = "ai-sales-page-writer"


def build() -> Workflow:
    wf = Workflow(
        name="DCA-A6-02 · AI Sales Page & Listing Writer (writes from your facts, flags unsupported claims)",
        slug=SLUG,
        category="a6-content-localization",
        summary="Turns a product's facts into a structured sales page — problem, proof, what you get, honest limits — and scans the result for unsupported claims before you publish it.",
        problem="Ask a model for a sales page and it invents 'trusted by thousands' and 'guaranteed results'. That copy converts badly because readers discount it, and an invented refund policy is one a customer will hold you to.",
        outcome="A complete listing built only from facts you supplied, in the order that actually converts, with every unsupported superlative flagged for removal before publishing.",
        version="1.0.0",
        tags=["ai-agent", "marketing", "copywriting", "seo", "content", "hardened"],
        credentials_needed=["An AI provider API key (Anthropic, OpenAI, or compatible)"],
        setup_minutes=12,
    )

    wf.sticky(
        "## ✍️ AI Sales Page & Listing Writer\n"
        "**Your facts → a structured listing → unsupported claims flagged.**\n\n"
        "### Setup (about 12 minutes)\n"
        "1. **⚙️ Config** → set `aiEndpoint`, `aiModel`, and your `bannedClaims`.\n"
        "2. Add your API key as **Header Auth** on **🧠 Write the listing**.\n"
        "3. POST the product's facts:\n"
        "   ```json\n"
        "   { \"productName\": \"...\", \"whatItIs\": \"...\",\n"
        "     \"problemItSolves\": \"...\", \"whatsIncluded\": [...],\n"
        "     \"price\": \"$49\", \"proof\": \"...\", \"limits\": \"...\" }\n"
        "   ```\n"
        "4. Read the output. **Publish nothing that is flagged.**\n\n"
        "### Use it on your own listings\n"
        "This is the template you will use to write the sales pages for every\n"
        "other template in this suite.",
        (-680, -540),
        (600, 560),
        COLOR_BLUE,
    )

    wf.sticky(
        "### 🚫 Why it refuses to write marketing prose\n"
        "Ask a model for a sales page and you get *\"trusted by thousands\"*,\n"
        "*\"guaranteed results\"*, *\"the industry standard\"*.\n\n"
        "Two problems:\n"
        "1. **It converts badly.** Readers have learned to discount that language.\n"
        "2. **It creates obligations.** A refund policy invented in a sales page\n"
        "   is one a customer will hold you to.\n\n"
        "The model here writes **only** from the facts you supply. Anything it\n"
        "cannot support is omitted, not softened.",
        (-40, -540),
        (500, 420),
        COLOR_RED,
    )

    wf.sticky(
        "### 📐 The structure that converts\n"
        "| # | Section | Job |\n"
        "| --- | --- | --- |\n"
        "| 1 | The problem | make them feel it is about them |\n"
        "| 2 | Proof | earn the right to be believed |\n"
        "| 3 | What you get | outcomes, not features |\n"
        "| 4 | How it works | remove installation fear |\n"
        "| 5 | **Honest limits** | the section that builds trust |\n"
        "| 6 | Price and next step | one clear action |\n\n"
        "Section 5 is not optional. It separates a listing readers trust from one\n"
        "they skim — and it cuts refunds by setting expectations **before** the\n"
        "sale.",
        (480, -540),
        (480, 440),
        COLOR_PURPLE,
    )

    wf.sticky(
        "### 🔍 The claim scanner\n"
        "After the model writes, a deterministic pass scans for superlatives and\n"
        "guarantees that no supplied fact supports.\n\n"
        "Each hit is reported with the sentence it appeared in, so you can delete\n"
        "or substantiate it.\n\n"
        "**A flagged listing is not blocked** — you may have proof the workflow\n"
        "cannot see. It is flagged so the decision is yours and conscious.",
        (1180, 420),
        (460, 340),
        COLOR_GREEN,
    )

    hook = wf.webhook(
        "📋 Product facts",
        (-680, 200),
        path="dca/write-listing",
        notes="POST the product's facts. The more specific they are, the better the listing.",
    )

    cfg = wf.config(
        {
            "storeName": "YOUR_STORE_NAME",
            "aiEndpoint": "https://api.anthropic.com/v1/messages",
            "aiModel": "claude-sonnet-5",
            "maxTokens": 2500,
            "targetAudience": "REPLACE: who this is for, in one sentence",
            "toneNotes": "direct, concrete, no hype; short sentences",
            "bannedClaims": [
                "guaranteed", "guarantee", "best in the world", "industry standard",
                "trusted by thousands", "everyone", "never fails", "100%",
                "revolutionary", "game-chang", "cutting-edge", "world-class",
                "instantly doubles", "risk-free", "unlimited earnings",
            ],
            "requireLimitsSection": True,
        },
        (-460, 200),
        notes="bannedClaims drives the scanner. Add anything your market is tired of hearing.",
    )

    guard = wf.guard(
        (-240, 200),
        required=["body"],
        event_id_expr="(j.body?.productName ?? '') + '|' + String(j.body?.whatItIs ?? '').slice(0, 40)",
        ttl_hours=1,
    )

    collect = wf.code(
        "📥 Collect the facts",
        r"""
// Gather what the seller actually knows. Missing facts are reported rather than
// filled in — an absent fact should produce a shorter listing, never an invented
// sentence.
const cfg = $('⚙️ Config').first().json.__config;

return $input.all().map(item => {
  const b = item.json.body ?? item.json;

  const productName = String(b.productName ?? b.name ?? '').trim();
  const whatItIs = String(b.whatItIs ?? b.description ?? '').trim();

  if (!productName || !whatItIs) {
    throw new Error('Need at least productName and whatItIs. Received keys: ' + Object.keys(b).join(', '));
  }

  const asList = (v) => Array.isArray(v)
    ? v.map(x => String(x).trim()).filter(Boolean)
    : String(v ?? '').split('\n').map(x => x.trim()).filter(Boolean);

  const facts = {
    productName,
    whatItIs,
    problemItSolves: String(b.problemItSolves ?? b.problem ?? '').trim(),
    whatsIncluded: asList(b.whatsIncluded ?? b.included ?? b.features),
    price: String(b.price ?? '').trim(),
    proof: String(b.proof ?? b.evidence ?? '').trim(),
    limits: String(b.limits ?? b.notFor ?? '').trim(),
    setupTime: String(b.setupTime ?? '').trim(),
    requirements: asList(b.requirements),
  };

  // Tell the seller what is missing. A thin listing is a symptom of thin facts,
  // and that is worth knowing before blaming the copy.
  const missing = [];
  if (!facts.problemItSolves) missing.push('problemItSolves — the listing will have a weak opening');
  if (!facts.whatsIncluded.length) missing.push('whatsIncluded — no concrete deliverables to list');
  if (!facts.proof) missing.push('proof — nothing to substantiate claims with');
  if (!facts.limits) missing.push('limits — the trust-building section will be generic');
  if (!facts.price) missing.push('price — no clear call to action');

  return { json: { ...facts, missingFacts: missing, __config: cfg } };
});
""",
        (0, 200),
        notes="Missing facts are reported, never invented. Thin facts produce a thin listing by design.",
    )

    write = wf.http(
        "🧠 Write the listing",
        (240, 200),
        url="={{ $json.__config.aiEndpoint }}",
        method="POST",
        headers={"content-type": "application/json", "anthropic-version": "2023-06-01"},
        json_body=(
            "={{ JSON.stringify({\n"
            "  model: $json.__config.aiModel,\n"
            "  max_tokens: $json.__config.maxTokens,\n"
            "  system: 'You write product listings for ' + $json.__config.storeName + '.\\n\\n'\n"
            "    + 'AUDIENCE: ' + $json.__config.targetAudience + '\\n'\n"
            "    + 'TONE: ' + $json.__config.toneNotes + '\\n\\n'\n"
            "    + 'ABSOLUTE RULE: write ONLY from the facts given. If a fact is missing, omit that '\n"
            "    + 'section rather than inventing content. Never claim numbers, testimonials, guarantees, '\n"
            "    + 'user counts or results that were not supplied. An invented refund policy is one the '\n"
            "    + 'seller will be held to.\\n\\n'\n"
            "    + 'Banned language: ' + ($json.__config.bannedClaims || []).join(', ') + '\\n\\n'\n"
            "    + 'Write these sections in this order:\\n'\n"
            "    + '1. headline — one line naming the problem, not the product\\n'\n"
            "    + '2. problem — 2-3 sentences the reader recognises as their situation\\n'\n"
            "    + '3. proof — only what the supplied facts support; empty string if none\\n'\n"
            "    + '4. whatYouGet — array of outcomes, not features. \"You stop losing sales to X\", not \"has X\"\\n'\n"
            "    + '5. howItWorks — numbered steps, concrete, removes fear of setup\\n'\n"
            "    + '6. limits — what this does NOT do. Be specific and honest. This section builds trust\\n'\n"
            "    + '7. callToAction — one clear next step including the price if supplied\\n'\n"
            "    + '8. metaDescription — under 160 characters for search results\\n\\n'\n"
            "    + 'Reply with STRICT JSON only, no markdown fence, with exactly those 8 keys.',\n"
            "  messages: [ { role: 'user', content: JSON.stringify({\n"
            "    productName: $json.productName, whatItIs: $json.whatItIs,\n"
            "    problemItSolves: $json.problemItSolves, whatsIncluded: $json.whatsIncluded,\n"
            "    price: $json.price, proof: $json.proof, limits: $json.limits,\n"
            "    setupTime: $json.setupTime, requirements: $json.requirements\n"
            "  }, null, 2) } ]\n"
            "}) }}"
        ),
        notes="Add your API key as a Header Auth credential.",
    )

    parse = wf.code(
        "📖 Parse the listing",
        r"""
// Defensive parse. An unreadable response must not be published as an empty
// page, so it returns a clear failure instead.
const src = $('📥 Collect the facts').first().json;

function extract(p) {
  return p?.content?.[0]?.text ?? p?.choices?.[0]?.message?.content ?? '';
}

return $input.all().map(item => {
  const raw = String(extract(item.json) || '').trim();

  let l = null;
  try {
    l = JSON.parse(raw.replace(/^```(?:json)?/i, '').replace(/```$/, '').trim());
  } catch {
    const m = raw.match(/\{[\s\S]*\}/);
    if (m) { try { l = JSON.parse(m[0]); } catch { /* fall through */ } }
  }

  if (!l || typeof l.headline !== 'string') {
    return { json: { ...src, ok: false,
      problems: ['model returned an unreadable response — nothing was written'],
      listing: null } };
  }

  const str = (v) => String(v ?? '').trim();
  const arr = (v) => Array.isArray(v) ? v.map(x => str(x)).filter(Boolean) : [];

  return { json: { ...src, ok: true, listing: {
    headline: str(l.headline),
    problem: str(l.problem),
    proof: str(l.proof),
    whatYouGet: arr(l.whatYouGet),
    howItWorks: arr(l.howItWorks),
    limits: str(l.limits),
    callToAction: str(l.callToAction),
    metaDescription: str(l.metaDescription).slice(0, 160),
  }}};
});
""",
        (480, 200),
        notes="An unreadable response fails clearly rather than publishing an empty page.",
    )

    scan = wf.code(
        "🔍 Scan for unsupported claims",
        r"""
// Deterministic second pass. Models drift toward marketing language even when
// told not to, so the instruction alone is not a control — this is.
//
// Deliberately advisory, not blocking: the seller may hold proof this workflow
// cannot see. The point is that the decision becomes conscious.
const out = [];

for (const item of $input.all()) {
  const o = item.json;

  if (!o.ok || !o.listing) {
    out.push({ json: { ...o, flags: [], safeToPublish: false } });
    continue;
  }

  const cfg = o.__config;
  const l = o.listing;

  // Every piece of prose the model produced, with its section name.
  const sections = [
    ['headline', l.headline], ['problem', l.problem], ['proof', l.proof],
    ['limits', l.limits], ['callToAction', l.callToAction],
    ['metaDescription', l.metaDescription],
    ...l.whatYouGet.map((t, i) => [`whatYouGet[${i}]`, t]),
    ...l.howItWorks.map((t, i) => [`howItWorks[${i}]`, t]),
  ];

  const flags = [];

  // ── Banned language ──────────────────────────────────────────
  for (const [where, text] of sections) {
    if (!text) continue;
    for (const claim of (cfg.bannedClaims || [])) {
      const c = String(claim).toLowerCase();
      if (!c) continue;
      const idx = text.toLowerCase().indexOf(c);
      if (idx >= 0) {
        // Show the sentence it appeared in, so the fix is obvious.
        const sentence = text.slice(Math.max(0, idx - 60), idx + c.length + 60).trim();
        flags.push({ type: 'banned_claim', where, claim, context: `…${sentence}…` });
      }
    }
  }

  // ── Numbers with no supporting fact ──────────────────────────
  // A statistic the seller never supplied was invented.
  const supplied = (o.proof + ' ' + o.whatItIs + ' ' + o.problemItSolves + ' ' + o.price).toLowerCase();
  for (const [where, text] of sections) {
    if (!text) continue;
    const stats = text.match(/\b\d{1,3}(?:[.,]\d+)?\s?(?:%|percent|x\b|times)\b/gi) || [];
    for (const s of stats) {
      if (!supplied.includes(s.toLowerCase().replace(/\s+/g, ' ').trim())) {
        flags.push({ type: 'unsupported_statistic', where, claim: s,
                     context: 'This figure does not appear in the facts you supplied.' });
      }
    }
  }

  // ── Proof claimed without evidence supplied ──────────────────
  if (l.proof && !o.proof) {
    flags.push({ type: 'invented_proof', where: 'proof',
                 claim: l.proof.slice(0, 120),
                 context: 'You supplied no proof, but the listing has a proof section.' });
  }

  // ── Missing limits section ───────────────────────────────────
  if (cfg.requireLimitsSection && !l.limits) {
    flags.push({ type: 'missing_limits', where: 'limits', claim: '(empty)',
                 context: 'The honest-limits section is empty. It is the section that builds trust and reduces refunds.' });
  }

  out.push({ json: { ...o, flags, safeToPublish: flags.length === 0 } });
}

return out;
""",
        (720, 200),
        notes="Deterministic check on the model's output. Advisory, not blocking — but the decision becomes conscious.",
        always_output=True,
    )

    render = wf.code(
        "📄 Render the listing",
        r"""
// Emit the listing three ways so it can be pasted wherever it is needed:
// markdown for marketplaces, HTML for a site, and the raw object for a CMS.
return $input.all().map(item => {
  const o = item.json;

  if (!o.ok || !o.listing) {
    return { json: { ok: false, problems: o.problems, markdown: null, html: null } };
  }

  const l = o.listing;

  const md = [
    `# ${l.headline}`, '',
    l.problem, '',
    l.proof ? `## Why you can believe this\n\n${l.proof}\n` : '',
    l.whatYouGet.length ? `## What you get\n\n${l.whatYouGet.map(x => `- ${x}`).join('\n')}\n` : '',
    l.howItWorks.length ? `## How it works\n\n${l.howItWorks.map((x, i) => `${i + 1}. ${x}`).join('\n')}\n` : '',
    l.limits ? `## What this does not do\n\n${l.limits}\n` : '',
    l.callToAction ? `---\n\n**${l.callToAction}**` : '',
  ].filter(Boolean).join('\n');

  const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

  const html =
`<article style="font-family:system-ui,-apple-system,Segoe UI,sans-serif;max-width:680px;margin:0 auto;line-height:1.65;color:#111">
  <h1 style="font-size:30px;line-height:1.25;margin:0 0 18px">${esc(l.headline)}</h1>
  <p style="font-size:17px;color:#444">${esc(l.problem)}</p>
  ${l.proof ? `<h2 style="font-size:19px;margin:34px 0 10px">Why you can believe this</h2><p style="color:#444">${esc(l.proof)}</p>` : ''}
  ${l.whatYouGet.length ? `<h2 style="font-size:19px;margin:34px 0 10px">What you get</h2><ul style="color:#444;padding-left:20px">${l.whatYouGet.map(x => `<li style="margin-bottom:7px">${esc(x)}</li>`).join('')}</ul>` : ''}
  ${l.howItWorks.length ? `<h2 style="font-size:19px;margin:34px 0 10px">How it works</h2><ol style="color:#444;padding-left:20px">${l.howItWorks.map(x => `<li style="margin-bottom:7px">${esc(x)}</li>`).join('')}</ol>` : ''}
  ${l.limits ? `<h2 style="font-size:19px;margin:34px 0 10px">What this does not do</h2><p style="color:#444">${esc(l.limits)}</p>` : ''}
  ${l.callToAction ? `<p style="margin:34px 0 0"><strong style="font-size:17px">${esc(l.callToAction)}</strong></p>` : ''}
</article>`;

  const flagReport = o.flags.length
    ? `⚠️ ${o.flags.length} claim(s) need your attention before publishing:\n\n` +
      o.flags.map(f => `[${f.type}] in ${f.where}\n  "${f.claim}"\n  ${f.context}`).join('\n\n')
    : '✅ No unsupported claims detected. Still read it once before publishing.';

  return { json: {
    ok: true,
    productName: o.productName,
    safeToPublish: o.safeToPublish,
    flags: o.flags,
    flagReport,
    missingFacts: o.missingFacts,
    metaDescription: l.metaDescription,
    markdown: md,
    html,
    listing: l,
  }};
});
""",
        (960, 200),
        notes="Markdown for marketplaces, HTML for your site, raw object for a CMS.",
    )

    fail = wf.error_sink((480, 420), context="listing-writer")

    respond = wf.respond(
        "↩️ Return the listing",
        (1200, 200),
        body='={{ JSON.stringify({ ok: $json.ok, safeToPublish: $json.safeToPublish ?? false, flags: $json.flags ?? [], markdown: $json.markdown }) }}',
    )

    wf.chain(hook, cfg, guard, collect, write)
    wf.connect(write, parse, out=0)
    wf.connect(write, fail, out=1)
    wf.chain(parse, scan, render, respond)
    wf.connect(fail, render)

    return wf
