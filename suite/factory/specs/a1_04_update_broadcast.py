"""
DCA-A1-04 · Product Update Broadcast

Solves "عدم وجود تحديثات تلقائية للمنتج بعد الشراء" from the buyer's list, and
"صعوبة تحديث المنتج" from the seller's.

Why this is a revenue template, not a courtesy one
--------------------------------------------------
Shipping an update to past buyers looks like a cost. It is one of the cheapest
sources of repeat revenue a digital seller has, for three reasons:

  * A buyer who receives a free improvement six months after purchase learns
    that this seller keeps their word, which is the entire basis of the second
    purchase.
  * It is a legitimate reason to appear in the inbox of everyone who has ever
    bought — the warmest list the seller owns, and one most never contact again.
  * It is the honest answer to "is this still maintained?", which is the
    question that kills template and course sales.

The hard part is not sending
----------------------------
It is sending *correctly*. This template exists because the naive version causes
real damage: mailing the whole list for a typo fix, mailing people who bought a
different product, mailing the same person twice because the job was re-run, and
sending links that have already expired.

So: updates are classified by significance and minor ones do not mail at all;
recipients are filtered to actual buyers of the specific product; every send is
recorded per buyer per version so a re-run is a no-op; and each recipient gets a
freshly signed link rather than a dead one.

Batching is deliberate
----------------------
Sending five thousand emails in one execution will hit provider rate limits and
can damage sending reputation, which harms every other template in this suite.
The broadcast runs in configurable batches with the reasoning stated on the
canvas.
"""

from lib.core import Workflow, COLOR_BLUE, COLOR_GREEN, COLOR_RED, COLOR_PURPLE

SLUG = "product-update-broadcast"


def build() -> Workflow:
    wf = Workflow(
        name="DCA-A1-04 · Product Update Broadcast (tell past buyers, safely)",
        slug=SLUG,
        category="a1-delivery",
        summary="Notifies past buyers of a product update with a freshly signed download link, filtered to actual buyers of that product, deduplicated per version, batched to protect sending reputation, and silent for trivial changes.",
        problem="Updating a product means past buyers hold an outdated file and a dead link. Sending manually is error-prone: the whole list gets mailed for a typo, people who bought something else get mailed, and a re-run mails everyone twice.",
        outcome="The right buyers hear about meaningful updates exactly once, with a working link — turning maintenance into the cheapest repeat-purchase driver a digital seller has.",
        version="1.0.0",
        tags=["delivery", "retention", "digital-products", "email", "hardened"],
        credentials_needed=["SMTP account"],
        setup_minutes=14,
    )

    wf.sticky(
        "## 📢 Product Update Broadcast\n"
        "**New version → the right buyers told once → fresh working link.**\n\n"
        "### Setup (about 14 minutes)\n"
        "1. **⚙️ Config** → `storeName`, `fromEmail`, `downloadBaseUrl`.\n"
        "2. **✍️ Sign fresh links** → the **same secret** as A1-01 and A1-02.\n"
        "3. Seed `buyers` from your order log, or wire the recipient node to your\n"
        "   real order source.\n"
        "4. POST when you ship an update:\n"
        "   ```json\n"
        "   { \"productId\": \"book-01\", \"version\": \"2.0\",\n"
        "     \"significance\": \"major\",\n"
        "     \"changes\": [\"...\", \"...\"] }\n"
        "   ```\n\n"
        "### This is a revenue template, not a courtesy\n"
        "A buyer who gets a free improvement six months later learns you keep your\n"
        "word — which is the whole basis of the second purchase.",
        (-700, -560),
        (600, 560),
        COLOR_BLUE,
    )

    wf.sticky(
        "### 🔇 Not every change deserves an email\n"
        "| significance | What happens |\n"
        "| --- | --- |\n"
        "| `major` | everyone who bought it is told |\n"
        "| `minor` | told, but low-key wording |\n"
        "| `patch` | **recorded, nobody emailed** |\n\n"
        "Mailing your whole buyer list about a typo fix is how a welcome update\n"
        "becomes an unsubscribe.\n\n"
        "The version is still recorded on `patch`, so the next major update can\n"
        "mention the accumulated fixes.",
        (-80, -560),
        (480, 400),
        COLOR_PURPLE,
    )

    wf.sticky(
        "### 🛡️ Four things that go wrong, prevented\n"
        "1. **Wrong people** — filtered to buyers of *that* product only.\n"
        "2. **Twice** — every send recorded per buyer per version, so re-running\n"
        "   the job mails nobody again.\n"
        "3. **Dead links** — each recipient gets a **freshly signed** link, not the\n"
        "   expired one from their original purchase.\n"
        "4. **Rate limits** — sent in batches.\n\n"
        "Point 4 matters beyond this template: a provider throttling or flagging\n"
        "you damages **every** email the rest of the suite sends.",
        (420, -560),
        (500, 400),
        COLOR_RED,
    )

    wf.sticky(
        "### 📦 Batching\n"
        "`batchSize` recipients per run. Re-POST the same update to send the next\n"
        "batch — already-notified buyers are skipped automatically, so you can\n"
        "simply call it again until `remaining` reaches 0.\n\n"
        "Or schedule the same payload to repeat every few minutes and let it drain\n"
        "the list by itself.",
        (1140, 380),
        (440, 300),
        COLOR_GREEN,
    )

    hook = wf.webhook(
        "🆕 Update shipped",
        (-700, 200),
        path="dca/product-update",
        notes="POST {productId, version, significance, changes[]} when you ship an update.",
    )

    cfg = wf.config(
        {
            "storeName": "YOUR_STORE_NAME",
            "fromEmail": "updates@yourdomain.com",
            "supportEmail": "support@yourdomain.com",
            "downloadBaseUrl": "https://yourdomain.com/download",
            "linkTtlHours": 168,
            "maxDownloads": 5,
            "batchSize": 50,
            "buyers": {},
            "historyTtlDays": 730,
        },
        (-480, 200),
        notes="buyers maps productId → [{email, orderId, name}]. Seed it or wire the recipient node to your order store.",
    )

    guard = wf.guard(
        (-260, 200),
        required=["body"],
        event_id_expr="(j.body?.productId ?? '') + '|' + (j.body?.version ?? '') + '|' + Math.floor(Date.now() / 30000)",
        ttl_hours=1,
    )

    plan = wf.code(
        "📋 Decide who to tell",
        r"""
// Work out whether to mail at all, then who has not already been told about
// this exact version.
//
// WIRING THIS TO YOUR REAL DATA:
// `buyers` in Config is fine for a small catalogue and needs no infrastructure.
// For a real store, replace the lookup below with a read from wherever A1-01
// writes its order log and return the same shape: [{ email, orderId, name }].
const cfg = $('⚙️ Config').first().json.__config;
const store = $getWorkflowStaticData('global');
store.notified = store.notified || {};
store.versions = store.versions || {};

const now = Date.now();
const ttlMs = Number(cfg.historyTtlDays) * 24 * 60 * 60 * 1000;
for (const [k, v] of Object.entries(store.notified)) {
  if (now - (v.at || 0) > ttlMs) delete store.notified[k];
}

const out = [];

for (const item of $input.all()) {
  const b = item.json.body ?? item.json;

  const productId = String(b.productId ?? b.product_id ?? '').trim();
  const version = String(b.version ?? '').trim();
  const significance = String(b.significance ?? 'minor').toLowerCase();
  const changes = Array.isArray(b.changes)
    ? b.changes.map(c => String(c).trim()).filter(Boolean)
    : String(b.changes ?? '').split('\n').map(c => c.trim()).filter(Boolean);

  if (!productId || !version) {
    throw new Error('An update needs productId and version. Received keys: ' + Object.keys(b).join(', '));
  }

  // Record the version regardless — even a silent patch should be on record so
  // the next major release can mention accumulated fixes.
  const vKey = `${productId}|${version}`;
  store.versions[vKey] = store.versions[vKey] || { productId, version, significance, changes, at: now };

  // ── Trivial changes do not earn an email ────────────────────
  if (significance === 'patch') {
    out.push({ json: {
      __send: false,
      productId, version, significance,
      reason: 'patch-level change — recorded but nobody emailed',
      note: 'Mailing your whole buyer list about a typo fix is how a welcome update becomes an unsubscribe.',
      __config: cfg,
    }});
    continue;
  }

  // ── Recipients: buyers of THIS product only ─────────────────
  const all = (cfg.buyers || {})[productId] || [];
  if (!all.length) {
    out.push({ json: {
      __send: false,
      productId, version, significance,
      reason: 'no buyers found for this product',
      note: 'Seed `buyers` in Config, or wire this node to your order log.',
      __config: cfg,
    }});
    continue;
  }

  // ── Skip anyone already told about this exact version ───────
  const pending = all.filter(buyer => {
    const email = String(buyer.email ?? '').trim().toLowerCase();
    if (!email) return false;
    return !store.notified[`${email}|${vKey}`];
  });

  const batch = pending.slice(0, Number(cfg.batchSize));

  if (!batch.length) {
    out.push({ json: {
      __send: false,
      productId, version, significance,
      reason: 'every buyer has already been told about this version',
      totalBuyers: all.length,
      __config: cfg,
    }});
    continue;
  }

  const expiresAt = Math.floor(now / 1000) + Number(cfg.linkTtlHours) * 3600;

  for (const buyer of batch) {
    const email = String(buyer.email).trim().toLowerCase();
    const orderId = String(buyer.orderId ?? buyer.order_id ?? '').trim();

    // Mark as notified up front. Sending twice is worse than missing one, and a
    // failed send still leaves a structured error for manual recovery.
    store.notified[`${email}|${vKey}`] = { at: now, email, version, productId };

    out.push({ json: {
      __send: true,
      productId, version, significance, changes,
      email,
      name: String(buyer.name ?? '').trim(),
      orderId,
      totalBuyers: all.length,
      remaining: Math.max(0, pending.length - batch.length),
      __expires: expiresAt,
      // Must match A1-01's payload ordering exactly or the link will not verify.
      __signaturePayload: [orderId, email, productId, expiresAt, cfg.maxDownloads].join('|'),
      __config: cfg,
    }});
  }
}

return out;
""",
        (-40, 200),
        notes="Filters to real buyers, skips anyone already told, batches, and stays silent on patches.",
        always_output=True,
    )

    should_send = wf.if_(
        "📤 Anyone to tell?",
        (200, 200),
        left="={{ $json.__send }}",
        operator={"type": "boolean", "operation": "true", "singleValue": True},
    )

    sign = wf.hmac(
        "✍️ Sign fresh links",
        (440, 80),
        value="={{ $json.__signaturePayload }}",
        secret="YOUR_OWN_LONG_RANDOM_LINK_SECRET",
        prop="linkSignature",
        encoding="hex",
        notes="⚠️ Must be the SAME secret as A1-01, A1-02 and A4-01.",
    )

    compose = wf.code(
        "✍️ Compose the announcement",
        r"""
// Same URL contract as A1-01, so the fresh link verifies in A1-02 without any
// special-casing. Four templates now agree on this shape.
return $input.all().map(i => {
  const o = i.json;
  const cfg = o.__config;

  const qs = new URLSearchParams({
    order: String(o.orderId),
    email: String(o.email),
    product: String(o.productId),
    expires: String(o.__expires),
    max: String(cfg.maxDownloads),
    sig: String(o.linkSignature),
  });
  const url = cfg.downloadBaseUrl.replace(/\/+$/, '') + '?' + qs.toString();

  const isMajor = o.significance === 'major';
  const changeList = o.changes.length
    ? `<ul style="color:#444;padding-left:20px;margin:0 0 22px">${o.changes.map(c =>
        `<li style="margin-bottom:6px">${String(c).replace(/&/g,'&amp;').replace(/</g,'&lt;')}</li>`).join('')}</ul>`
    : '';

  return { json: { ...o,
    downloadUrl: url,
    subject: isMajor
      ? `${o.productId} has been updated — version ${o.version} is ready`
      : `A small update to ${o.productId}`,
    html:
`<div style="font-family:system-ui,-apple-system,Segoe UI,sans-serif;max-width:560px;margin:0 auto;padding:32px 24px;color:#111">
  <h2 style="margin:0 0 12px;font-size:20px">Hi${o.name ? ' ' + o.name : ''}, there's a new version</h2>
  <p style="color:#555;line-height:1.65;margin:0 0 20px">
    You bought this${o.orderId ? ` (order ${o.orderId})` : ''}, so here is version <strong>${o.version}</strong> —
    free, as always.
  </p>
  ${o.changes.length ? '<p style="font-weight:600;margin:0 0 8px">What changed</p>' + changeList : ''}
  <a href="${url}" style="display:inline-block;background:#111;color:#fff;text-decoration:none;padding:14px 28px;border-radius:8px;font-weight:600">Download version ${o.version}</a>
  <p style="color:#777;font-size:13px;margin:22px 0 0">
    This is a fresh link — your original one has likely expired by now.
  </p>
  <p style="color:#777;font-size:13px;margin:8px 0 0">
    Questions? Reply here or email <a href="mailto:${cfg.supportEmail}">${cfg.supportEmail}</a>.
  </p>
</div>`,
  }};
});
""",
        (680, 80),
        notes="Every recipient gets a freshly signed link, not the dead one from their purchase.",
    )

    send = wf.node(
        "📧 Send the announcement",
        "n8n-nodes-base.emailSend",
        {
            "fromEmail": "={{ $json.__config.fromEmail }}",
            "toEmail": "={{ $json.email }}",
            "subject": "={{ $json.subject }}",
            "emailFormat": "html",
            "html": "={{ $json.html }}",
            "options": {},
        },
        2.1,
        (920, 80),
        retry=True,
        max_tries=3,
        wait_ms=3000,
        on_error="continueErrorOutput",
        notes="Attach SMTP. Batched upstream to protect your sending reputation.",
    )

    skipped = wf.code(
        "⏭️ Nothing sent",
        r"""
// Patch-level change, no buyers, or everyone already told. Recorded so a re-run
// is visibly a no-op rather than looking like a failure.
return $input.all().map(i => ({ json: {
  sent: false,
  productId: i.json.productId,
  version: i.json.version,
  reason: i.json.reason,
  note: i.json.note ?? null,
}}));
""",
        (440, 340),
        notes="A re-run lands here and does nothing, which is correct.",
    )

    fail = wf.error_sink((920, 300), context="update-broadcast")

    log = wf.code(
        "📒 Broadcast log",
        r"""
return $input.all().map(i => ({ json: {
  ts: new Date().toISOString(),
  productId: i.json.productId ?? null,
  version: i.json.version ?? null,
  email: i.json.email ?? null,
  sent: i.json.sent !== false && !i.json.error,
  remaining: i.json.remaining ?? null,
  reason: i.json.reason ?? null,
}}));
""",
        (1160, 200),
        notes="`remaining` tells you whether to call again for the next batch.",
    )

    respond = wf.respond(
        "↩️ 200 OK",
        (1400, 200),
        body='={{ JSON.stringify({ ok: true, remaining: $json.remaining ?? 0 }) }}',
    )

    wf.chain(hook, cfg, guard, plan, should_send)
    wf.connect(should_send, sign, out=0)
    wf.connect(should_send, skipped, out=1)
    wf.chain(sign, compose, send)
    wf.connect(send, log, out=0)
    wf.connect(send, fail, out=1)
    wf.connect(skipped, log)
    wf.connect(fail, log)
    wf.connect(log, respond)

    return wf
