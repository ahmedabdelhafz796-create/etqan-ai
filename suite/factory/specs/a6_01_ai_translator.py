"""
DCA-A6-01 · AI Product Translation & Sync

Solves "صعوبة تحديث المنتج في جميع اللغات" — the seller changes a price or a
description in one place and must then find and update the same thing in five
translations, which in practice means the translations quietly go stale.

The failure this is built against
---------------------------------
Naive translation workflows pipe the whole description through a model and store
whatever comes back. Three things break:

  * **Prices and product names get translated.** "$49" becomes "٤٩ دولارًا" and
    now a price-matching script fails, or a brand name gets helpfully rendered
    into Arabic and stops being findable.
  * **Formatting is destroyed.** Markdown, HTML tags and line breaks come back
    rearranged, so the sales page renders wrong in exactly the languages the
    seller cannot read.
  * **Everything is re-translated on every run**, costing money on unchanged
    text and producing gratuitous diffs.

So this protects literals before translating, verifies structure afterwards, and
hashes source content so unchanged text is skipped entirely.

RTL is a first-class concern here
---------------------------------
Arabic, Hebrew, Farsi and Urdu need `dir="rtl"` on the rendered output. A
translation that is linguistically perfect and renders left-to-right looks
broken to the reader, so direction is emitted alongside the text rather than
left for the seller to remember.
"""

from lib.core import Workflow, COLOR_BLUE, COLOR_GREEN, COLOR_RED, COLOR_PURPLE

SLUG = "ai-product-translation"


def build() -> Workflow:
    wf = Workflow(
        name="DCA-A6-01 · AI Product Translation & Sync (prices and formatting stay intact)",
        slug=SLUG,
        category="a6-content-localization",
        summary="Translates product copy into every language you sell in, protects prices, brand names and formatting from being translated, skips unchanged text, and emits text direction so RTL languages render correctly.",
        problem="Change a description once and it must be updated in five translations — so translations quietly go stale. Naive AI translation makes it worse by translating prices, destroying formatting, and re-translating unchanged text every run.",
        outcome="One source of truth translated into every language, with literals preserved, structure verified, RTL handled, and unchanged content skipped so you only pay for what actually changed.",
        version="1.0.0",
        tags=["ai-agent", "localization", "content", "i18n", "hardened"],
        credentials_needed=["An AI provider API key (Anthropic, OpenAI, or compatible)"],
        setup_minutes=15,
    )

    wf.sticky(
        "## 🌍 AI Product Translation & Sync\n"
        "**Write once → translated everywhere → prices and formatting untouched.**\n\n"
        "### Setup (about 15 minutes)\n"
        "1. **⚙️ Config** → set `targetLanguages` and `protectedTerms`\n"
        "   (your brand, product names — anything that must never be translated).\n"
        "2. Set `aiEndpoint` / `aiModel`, add your API key as **Header Auth** on\n"
        "   **🧠 Translate**.\n"
        "3. POST your product to the Production URL:\n"
        "   ```json\n"
        "   { \"productId\": \"book-01\", \"title\": \"...\",\n"
        "     \"description\": \"...\", \"price\": \"$49\" }\n"
        "   ```\n"
        "4. Wire **📤 Deliver translations** to your CMS / site / database.\n\n"
        "### It only pays for what changed\n"
        "Source text is hashed. Re-send the same product and unchanged fields are\n"
        "**skipped entirely** — no API call, no cost, no gratuitous diff.",
        (-680, -540),
        (600, 560),
        COLOR_BLUE,
    )

    wf.sticky(
        "### 🔒 What must never be translated\n"
        "Naive translation workflows break these three things:\n\n"
        "**Prices** — `$49` becomes `٤٩ دولارًا` and your checkout breaks.\n"
        "**Brand and product names** — helpfully rendered into Arabic and now\n"
        "nobody can find them.\n"
        "**Formatting** — markdown and HTML come back rearranged, so the page\n"
        "renders wrong in exactly the languages you cannot read.\n\n"
        "This replaces them with placeholders **before** translating and restores\n"
        "them after, then verifies every placeholder came back.",
        (-40, -540),
        (500, 420),
        COLOR_RED,
    )

    wf.sticky(
        "### ↔️ RTL is handled, not assumed\n"
        "Arabic · Hebrew · Farsi · Urdu need `dir=\"rtl\"`.\n\n"
        "A translation that is linguistically perfect and renders left-to-right\n"
        "**looks broken** to the reader.\n\n"
        "Direction is emitted with every translation so your site does not have to\n"
        "remember which languages need it.",
        (480, -540),
        (440, 320),
        COLOR_PURPLE,
    )

    wf.sticky(
        "### ✅ Structure is verified after translation\n"
        "Every translation is checked before it is delivered:\n\n"
        "· all protected placeholders returned\n"
        "· markdown/HTML tag counts match the source\n"
        "· output is not suspiciously short or empty\n\n"
        "A failed check **does not silently publish**. It is flagged and the\n"
        "original is kept, because a broken translation on a live sales page is\n"
        "worse than no translation.",
        (1160, 420),
        (460, 340),
        COLOR_GREEN,
    )

    hook = wf.webhook(
        "📝 Product content",
        (-680, 200),
        path="dca/translate",
        notes="POST {productId, title, description, price?, features?}.",
    )

    cfg = wf.config(
        {
            "targetLanguages": ["ar", "tr", "es", "fr", "de"],
            "sourceLanguage": "en",
            "protectedTerms": ["YOUR_BRAND_NAME"],
            "rtlLanguages": ["ar", "he", "fa", "ur"],
            "aiEndpoint": "https://api.anthropic.com/v1/messages",
            "aiModel": "claude-sonnet-5",
            "maxTokens": 2000,
            "tone": "professional but warm; keep sentences short",
            "minLengthRatio": 0.4,
            "skipUnchanged": True,
            "historyTtlDays": 90,
        },
        (-460, 200),
        notes="protectedTerms: your brand and product names. These are never translated.",
    )

    guard = wf.guard(
        (-240, 200),
        required=["body"],
        event_id_expr="(j.body?.productId ?? '') + '|' + String(j.body?.title ?? '').slice(0, 40)",
        ttl_hours=1,
    )

    prepare = wf.code(
        "🔒 Protect literals and check what changed",
        r"""
// Two jobs before any model sees the text.
//
// 1. Replace anything that must survive translation with an opaque placeholder.
//    Models are helpful by default and will happily convert "$49" into local
//    numerals or translate a brand name, both of which break things downstream.
// 2. Hash the source so unchanged content is skipped. Re-running a catalogue
//    should cost nothing for the parts that did not change.
const cfg = $('⚙️ Config').first().json.__config;
const store = $getWorkflowStaticData('global');
store.translations = store.translations || {};

const now = Date.now();
const ttlMs = Number(cfg.historyTtlDays) * 24 * 60 * 60 * 1000;
for (const [k, r] of Object.entries(store.translations)) {
  if (now - (r.at || 0) > ttlMs) delete store.translations[k];
}

// Small, dependency-free string hash. Only needs to detect change, not resist
// attack, so a cryptographic digest would be ceremony here.
function hash(s) {
  let h = 5381;
  for (let i = 0; i < s.length; i++) h = ((h << 5) + h + s.charCodeAt(i)) | 0;
  return String(h >>> 0);
}

const out = [];

for (const item of $input.all()) {
  const b = item.json.body ?? item.json;

  const productId = String(b.productId ?? b.product_id ?? b.id ?? '').trim();
  const title = String(b.title ?? b.name ?? '').trim();
  const description = String(b.description ?? b.body ?? '').trim();

  if (!productId || !title) {
    throw new Error('Translation needs at least productId and title. Received keys: ' + Object.keys(b).join(', '));
  }

  // Everything the model must not touch, in one place.
  const protect = [];
  const stash = (value) => {
    const token = `«${protect.length}»`;
    protect.push({ token, value });
    return token;
  };

  const protectText = (text) => {
    let t = text;
    // Order matters: longest/most specific patterns first, or a shorter pattern
    // eats part of a longer one and the restore comes back wrong.
    // Currency amounts in several common shapes.
    t = t.replace(/(?:[$€£¥₺]\s?\d[\d.,]*|\d[\d.,]*\s?(?:USD|EUR|GBP|TRY|AED|SAR|EGP))/gi, m => stash(m));
    // URLs and emails.
    t = t.replace(/https?:\/\/\S+/gi, m => stash(m));
    t = t.replace(/[\w.+-]+@[\w-]+\.[\w.]+/gi, m => stash(m));
    // Seller-declared terms — brand names, product names.
    for (const term of (cfg.protectedTerms || [])) {
      if (!term) continue;
      const esc = String(term).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      t = t.replace(new RegExp(esc, 'g'), m => stash(m));
    }
    return t;
  };

  const protectedTitle = protectText(title);
  const protectedDescription = protectText(description);

  // Structural fingerprint of the source, checked again after translation.
  const countStructure = (s) => ({
    markdownBold: (s.match(/\*\*/g) || []).length,
    markdownLinks: (s.match(/\[[^\]]*\]\([^)]*\)/g) || []).length,
    htmlTags: (s.match(/<[^>]+>/g) || []).length,
    lineBreaks: (s.match(/\n/g) || []).length,
    bullets: (s.match(/^\s*[-*•]\s/gm) || []).length,
  });

  const sourceHash = hash(title + '\u241F' + description);

  for (const lang of (cfg.targetLanguages || [])) {
    const key = `${productId}|${lang}`;
    const prior = store.translations[key];

    if (cfg.skipUnchanged && prior && prior.sourceHash === sourceHash) {
      out.push({ json: {
        productId, lang, skipped: true,
        reason: 'source unchanged since last translation',
        title: prior.title, description: prior.description,
        dir: prior.dir,
        __config: cfg,
      }});
      continue;
    }

    out.push({ json: {
      productId, lang, skipped: false,
      sourceTitle: title,
      sourceDescription: description,
      protectedTitle, protectedDescription,
      protectedMap: protect,
      sourceStructure: countStructure(description),
      sourceHash,
      isRtl: (cfg.rtlLanguages || []).includes(lang),
      __config: cfg,
    }});
  }
}

return out;
""",
        (0, 200),
        notes="Placeholders protect prices/brands/URLs. Hashing skips unchanged text so you only pay for real changes.",
        always_output=True,
    )

    needs_work = wf.if_(
        "🔄 Needs translating?",
        (240, 200),
        left="={{ $json.skipped }}",
        operator={"type": "boolean", "operation": "false", "singleValue": True},
    )

    translate = wf.http(
        "🧠 Translate",
        (480, 80),
        url="={{ $json.__config.aiEndpoint }}",
        method="POST",
        headers={"content-type": "application/json", "anthropic-version": "2023-06-01"},
        json_body=(
            "={{ JSON.stringify({\n"
            "  model: $json.__config.aiModel,\n"
            "  max_tokens: $json.__config.maxTokens,\n"
            "  system: 'You translate e-commerce product copy from ' + $json.__config.sourceLanguage + ' to the requested language.\\n\\n'\n"
            "    + 'ABSOLUTE RULES:\\n'\n"
            "    + '1. Any token shaped like «0», «1», «2» is a placeholder. Copy it EXACTLY and UNCHANGED into your output. '\n"
            "    + 'Never translate it, never renumber it, never add or remove one. They hold prices, URLs and brand names.\\n'\n"
            "    + '2. Preserve ALL formatting exactly: markdown, HTML tags, line breaks, bullet points.\\n'\n"
            "    + '3. Translate meaning, not words. Marketing copy should read as if written natively.\\n'\n"
            "    + '4. Tone: ' + $json.__config.tone + '\\n\\n'\n"
            "    + 'Reply with STRICT JSON only, no markdown fence:\\n'\n"
            "    + '{\"title\": \"<translated title>\", \"description\": \"<translated description>\"}',\n"
            "  messages: [ { role: 'user', content: 'Target language code: ' + $json.lang + '\\n\\nTITLE:\\n' + $json.protectedTitle + '\\n\\nDESCRIPTION:\\n' + $json.protectedDescription } ]\n"
            "}) }}"
        ),
        notes="Add your API key as a Header Auth credential.",
    )

    restore = wf.code(
        "🔓 Restore literals and verify",
        r"""
// Put the protected values back, then check the model actually respected the
// contract. A translation that lost its placeholders or mangled its markup must
// NOT reach a live sales page — in these languages the seller cannot see the
// damage themselves.
const src = $('🔒 Protect literals and check what changed').all();

function extract(p) {
  return p?.content?.[0]?.text ?? p?.choices?.[0]?.message?.content ?? '';
}

return $input.all().map((item, idx) => {
  // Items stay aligned because the model call is one-in-one-out.
  const o = src[idx]?.json ?? src[0].json;
  const cfg = o.__config;
  const raw = String(extract(item.json) || '').trim();

  let parsed = null;
  try {
    parsed = JSON.parse(raw.replace(/^```(?:json)?/i, '').replace(/```$/, '').trim());
  } catch {
    const m = raw.match(/\{[\s\S]*\}/);
    if (m) { try { parsed = JSON.parse(m[0]); } catch { /* fall through */ } }
  }

  const problems = [];

  if (!parsed || typeof parsed.title !== 'string' || typeof parsed.description !== 'string') {
    return { json: { ...o,
      ok: false, published: false,
      problems: ['model returned an unreadable response'],
      title: o.sourceTitle, description: o.sourceDescription,
      dir: o.isRtl ? 'rtl' : 'ltr',
    }};
  }

  let title = parsed.title;
  let description = parsed.description;

  // ── Placeholder integrity, checked BEFORE restoring ──────────
  for (const p of (o.protectedMap || [])) {
    const inOutput = (title + description).includes(p.token);
    if (!inOutput) {
      problems.push(`placeholder ${p.token} (${p.value}) was lost in translation`);
    }
  }

  // Restore. Done after the check so a lost placeholder is still detectable.
  for (const p of (o.protectedMap || [])) {
    const re = new RegExp(p.token.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g');
    title = title.replace(re, p.value);
    description = description.replace(re, p.value);
  }

  // Any leftover placeholder means the model invented one we cannot resolve.
  if (/«\d+»/.test(title + description)) {
    problems.push('output contains placeholders that do not map to any protected value');
  }

  // ── Structure ────────────────────────────────────────────────
  const s = o.sourceStructure || {};
  const t = {
    markdownBold: (description.match(/\*\*/g) || []).length,
    markdownLinks: (description.match(/\[[^\]]*\]\([^)]*\)/g) || []).length,
    htmlTags: (description.match(/<[^>]+>/g) || []).length,
    bullets: (description.match(/^\s*[-*•]\s/gm) || []).length,
  };
  for (const k of ['markdownBold', 'markdownLinks', 'htmlTags', 'bullets']) {
    if ((s[k] ?? 0) !== (t[k] ?? 0)) {
      problems.push(`${k} count changed (${s[k] ?? 0} → ${t[k] ?? 0})`);
    }
  }

  // ── Plausibility ─────────────────────────────────────────────
  // Languages legitimately differ in length, so the bar is deliberately low —
  // this catches truncation and empty output, not stylistic variation.
  const ratio = o.sourceDescription.length > 0
    ? description.length / o.sourceDescription.length
    : 1;
  if (description.length === 0 || ratio < Number(cfg.minLengthRatio)) {
    problems.push(`translation is suspiciously short (${Math.round(ratio * 100)}% of source length)`);
  }

  const ok = problems.length === 0;

  return { json: { ...o,
    ok, published: ok, problems,
    // On failure keep the source. A broken sales page is worse than an
    // untranslated one.
    title: ok ? title : o.sourceTitle,
    description: ok ? description : o.sourceDescription,
    dir: o.isRtl ? 'rtl' : 'ltr',
    lang: o.lang,
  }};
});
""",
        (720, 80),
        notes="Verifies placeholders and structure. A failed check keeps the source rather than publishing something broken.",
    )

    record = wf.code(
        "💾 Remember what was translated",
        r"""
// Cache successful translations against the source hash so an unchanged rerun
// costs nothing. Failures are deliberately NOT cached — they should be retried.
const store = $getWorkflowStaticData('global');
store.translations = store.translations || {};

return $input.all().map(i => {
  const o = i.json;
  if (o.ok) {
    store.translations[`${o.productId}|${o.lang}`] = {
      sourceHash: o.sourceHash,
      title: o.title,
      description: o.description,
      dir: o.dir,
      at: Date.now(),
    };
  }
  return { json: o };
});
""",
        (960, 80),
        notes="Only successful translations are cached, so failures retry next run.",
    )

    passthrough = wf.code(
        "⏭️ Unchanged — reuse existing",
        r"""
// Source has not changed since the last successful translation. Emit the cached
// result so downstream sees a complete set for every language regardless.
return $input.all().map(i => ({ json: {
  ...i.json, ok: true, published: true, problems: [], fromCache: true,
}}));
""",
        (480, 340),
        notes="No API call. This is where the cost saving comes from.",
    )

    deliver = wf.code(
        "📤 Deliver translations",
        r"""
// Final payload for your CMS, site or database. Includes `dir` so RTL renders
// correctly without the site having to know which languages need it, and
// reports anything that failed verification rather than hiding it.
const out = [];
const failures = [];

for (const i of $input.all()) {
  const o = i.json;
  if (!o.ok) failures.push({ lang: o.lang, problems: o.problems });

  out.push({ json: {
    productId: o.productId,
    lang: o.lang,
    dir: o.dir,
    title: o.title,
    description: o.description,
    verified: !!o.ok,
    fromCache: !!o.fromCache,
    problems: o.problems || [],
    // Ready to drop into an HTML attribute set.
    htmlAttrs: `lang="${o.lang}" dir="${o.dir}"`,
    updatedAt: new Date().toISOString(),
  }});
}

if (failures.length) {
  out.push({ json: {
    __alert: true,
    message: `⚠️ ${failures.length} translation(s) failed verification and were NOT published. Source text kept.`,
    failures,
  }});
}

return out;
""",
        (1200, 200),
        notes="Wire to your CMS. Anything unverified is reported, never silently published.",
    )

    fail = wf.error_sink((720, 340), context="translation")

    respond = wf.respond(
        "↩️ 200 OK",
        (1440, 200),
        body='={{ JSON.stringify({ ok: true }) }}',
    )

    wf.chain(hook, cfg, guard, prepare, needs_work)
    wf.connect(needs_work, translate, out=0)
    wf.connect(needs_work, passthrough, out=1)
    wf.connect(translate, restore, out=0)
    wf.connect(translate, fail, out=1)
    wf.connect(restore, record)
    wf.connect(record, deliver)
    wf.connect(passthrough, deliver)
    wf.connect(fail, deliver)
    wf.connect(deliver, respond)

    return wf
