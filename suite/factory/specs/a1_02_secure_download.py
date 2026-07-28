"""
DCA-A1-02 · Secure Download Endpoint

The other half of DCA-A1-01. A1-01 mints a signed link; this verifies it and
decides whether to hand over the file. Both use the same secret and the same
payload ordering, so they must be read together.

Why this is the free template
-----------------------------
It is the most universally painful problem in the catalogue — "the link expired",
"the link stopped working", "someone posted my link on Telegram" — and a seller
who installs this sees the standard working in their own account within ten
minutes. That is a far stronger argument for the paid templates than any sales
page, and it is why this one is given away.

The design problem it solves
----------------------------
Sellers face a genuine trade-off. Permanent links get forwarded and posted
publicly, so the product leaks. Aggressively short links break for legitimate
buyers whose download stalls, who open the mail on a different device the next
day, or who simply pay and read their email on Monday — and every one of those
becomes a support ticket, which is the complaint sellers actually report.

The resolution here is a *stateless, self-describing* link: expiry and download
allowance travel inside the URL and are covered by the signature, so limits are
enforced without a database, and — critically — every refusal returns a specific,
actionable reason instead of a generic 403. A buyer who is told "this link
expired on Tuesday, click here to have a fresh one sent" does not open a ticket.
"""

from lib.core import Workflow, COLOR_BLUE, COLOR_GREEN, COLOR_RED, COLOR_PURPLE

SLUG = "secure-download-endpoint"


def build() -> Workflow:
    wf = Workflow(
        name="DCA-A1-02 · Secure Download Endpoint (signed, expiring, download-limited)",
        slug=SLUG,
        category="a1-delivery",
        summary="Verifies a signed download link, enforces expiry and a download cap, and returns a specific reason for every refusal instead of a bare 403.",
        problem="Permanent download links get forwarded and posted publicly; short-lived ones break for legitimate buyers and generate support tickets. Most download failures return no reason at all, so the buyer emails the seller.",
        outcome="Links that cannot be altered or shared indefinitely, limits enforced with no database, and refusals that tell the buyer exactly what happened and what to do next.",
        version="1.0.0",
        tags=["digital-products", "delivery", "security", "anti-piracy", "free", "hardened"],
        credentials_needed=["None required", "Optional: your file host / S3 for the redirect target"],
        setup_minutes=8,
    )

    wf.sticky(
        "## 🔐 Secure Download Endpoint\n"
        "**Verify the signature → check expiry → check the download cap → serve the file.**\n\n"
        "### The pair\n"
        "`DCA-A1-01` mints the link. **This** verifies it.\n"
        "⚠️ Both must use the **same secret** in their Crypto node, and the payload is\n"
        "joined in this exact order:\n"
        "```\n"
        "order | email | product | expires | max\n"
        "```\n"
        "Change the order in one and you must change it in the other.\n\n"
        "### Setup (about 8 minutes)\n"
        "1. **⚙️ Config** → set `fileUrlMap` (product id → real file URL) and `supportEmail`.\n"
        "2. **🔏 Recompute signature** → paste the *same* secret used in A1-01.\n"
        "3. Copy this workflow's Production URL into A1-01's `downloadBaseUrl`.\n"
        "4. Activate. Test with a real link from A1-01 before going live.\n\n"
        "### Why stateless\n"
        "Expiry and the download cap travel **inside** the URL and are covered by the\n"
        "signature. No database to provision, and nothing to keep in sync.",
        (-660, -460),
        (600, 600),
        COLOR_BLUE,
    )

    wf.sticky(
        "### 🎯 The real trade-off\n"
        "**Permanent links** → forwarded, posted on Telegram, product leaks.\n"
        "**Very short links** → break for real buyers → support tickets.\n\n"
        "Neither extreme is right. Defaults here: **48h** and **5 downloads** — enough\n"
        "for a buyer who reads email on Monday and re-downloads on a second device,\n"
        "short enough that a leaked link dies quickly.\n\n"
        "Raise `graceHours` rather than the TTL if you sell to many time zones.",
        (-40, -460),
        (460, 360),
        COLOR_PURPLE,
    )

    wf.sticky(
        "### 💬 Every refusal explains itself\n"
        "This is the part that removes support tickets.\n\n"
        "| Refusal | Buyer is told |\n"
        "| --- | --- |\n"
        "| Bad signature | link was altered — request a fresh one |\n"
        "| Expired | the exact date it expired + how to get a new one |\n"
        "| Cap reached | how many were used, and to contact support |\n"
        "| Unknown product | the product id, and to contact support |\n\n"
        "A generic `403 Forbidden` is what makes a buyer email you.",
        (460, -460),
        (460, 360),
        COLOR_GREEN,
    )

    wf.sticky(
        "### 🕵️ Abuse signal\n"
        "When a link exceeds its cap the run records how many distinct IPs used it.\n"
        "**One buyer on 40 IPs = the link was published somewhere.**\n\n"
        "Feed `abuseSignal` into `DCA-A3-03 · Leak Detection` to catch a leak while\n"
        "it is still worth acting on.",
        (1420, 360),
        (440, 260),
        COLOR_RED,
    )

    hook = wf.webhook(
        "⬇️ Download request",
        (-660, 180),
        path="dca/download",
        method="GET",
        notes="GET endpoint. This URL goes into A1-01's downloadBaseUrl.",
    )

    cfg = wf.config(
        {
            "fileUrlMap": {
                "book-01": "https://your-storage.example.com/files/book-01.pdf",
                "default": "https://your-storage.example.com/files/default.pdf",
            },
            "graceHours": 0,
            "supportEmail": "support@yourdomain.com",
            "storeName": "YOUR_STORE_NAME",
            "resendUrl": "https://yourdomain.com/resend",
            "abuseIpThreshold": 8,
            "historyTtlHours": 168,
        },
        (-440, 180),
        notes="Map each product id to its real file URL. graceHours extends expiry for late buyers without lengthening the link's life for everyone.",
    )

    prepare = wf.code(
        "📥 Read the link parameters",
        r"""
// Rebuild the exact string that was signed. Field order is part of the
// contract with A1-01 — reorder it here and every existing link breaks.
const cfg = $('⚙️ Config').first().json.__config;

return $input.all().map(item => {
  const q = item.json.query ?? {};
  const h = item.json.headers ?? {};

  const order   = String(q.order   ?? '');
  const email   = String(q.email   ?? '');
  const product = String(q.product ?? '');
  const expires = String(q.expires ?? '');
  const max     = String(q.max     ?? '');
  const sig     = String(q.sig     ?? '');

  const missing = [];
  if (!order)   missing.push('order');
  if (!expires) missing.push('expires');
  if (!sig)     missing.push('sig');

  const ip = String(
    (h['x-forwarded-for'] || '').split(',')[0].trim() ||
    h['cf-connecting-ip'] || h['x-real-ip'] || ''
  );

  return {
    json: {
      order, email, product, expires, max, sig, ip,
      // Must match A1-01's __signaturePayload exactly.
      signaturePayload: [order, email, product, expires, max].join('|'),
      missingParams: missing,
      userAgent: String(h['user-agent'] ?? ''),
      __config: cfg,
    }
  };
});
""",
        (-220, 180),
        notes="Reconstructs the signed payload. Field order must match A1-01.",
    )

    recompute = wf.hmac(
        "🔏 Recompute signature",
        (0, 180),
        value="={{ $json.signaturePayload }}",
        secret="YOUR_OWN_LONG_RANDOM_LINK_SECRET",
        prop="expectedSignature",
        encoding="hex",
        notes="⚠️ Must be the SAME secret as in A1-01's 'Sign download link' node.",
    )

    verify = wf.code(
        "🛡️ Verify and decide",
        r"""
// ═══════════════════════════════════════════════════════════════════
// One place where the allow/deny decision is made, so there is exactly
// one thing to audit. Each refusal carries a message written for the
// buyer, not for a log file.
// ═══════════════════════════════════════════════════════════════════
const store = $getWorkflowStaticData('global');
store.downloads = store.downloads || {};

const out = [];

for (const item of $input.all()) {
  const d = item.json;
  const cfg = d.__config;
  const now = Math.floor(Date.now() / 1000);
  const ttlMs = Number(cfg.historyTtlHours) * 60 * 60 * 1000;

  // Prune old counters so static data stays bounded.
  for (const [k, rec] of Object.entries(store.downloads)) {
    if (Date.now() - (rec.firstAt || 0) > ttlMs) delete store.downloads[k];
  }

  const deny = (code, message, extra = {}) => ({
    json: {
      allowed: false, code, message,
      order: d.order, product: d.product, ip: d.ip,
      supportEmail: cfg.supportEmail, resendUrl: cfg.resendUrl,
      checkedAt: new Date().toISOString(),
      ...extra,
    }
  });

  // ── 1. Completeness ─────────────────────────────────────────────
  if (d.missingParams.length) {
    out.push(deny('malformed_link',
      `This download link is incomplete (missing: ${d.missingParams.join(', ')}). ` +
      `Please use the full link from your purchase email, or request a fresh one.`));
    continue;
  }

  // ── 2. Signature ────────────────────────────────────────────────
  // Length-safe comparison without an early exit on first mismatch.
  const a = String(d.sig).toLowerCase();
  const b = String(d.expectedSignature).toLowerCase();
  let equal = a.length === b.length;
  let diff = 0;
  if (equal) {
    for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
    equal = diff === 0;
  }

  if (!equal) {
    // Either tampering, or a mail client mangled the URL. Both are fixed the
    // same way, so the message covers both without accusing the buyer.
    out.push(deny('invalid_signature',
      `This link could not be verified — it may have been altered or truncated by your email app. ` +
      `Request a fresh link and it will work.`));
    continue;
  }

  // ── 3. Expiry ───────────────────────────────────────────────────
  const expires = Number(d.expires);
  const graceSeconds = Number(cfg.graceHours) * 3600;

  if (!Number.isFinite(expires)) {
    out.push(deny('malformed_link', 'This link has an unreadable expiry. Please request a fresh one.'));
    continue;
  }

  if (now > expires + graceSeconds) {
    const when = new Date(expires * 1000).toUTCString();
    out.push(deny('expired',
      `This link expired on ${when}. Your purchase is still valid — request a fresh link and you will get immediate access.`,
      { expiredAt: when }));
    continue;
  }

  // ── 4. Download cap ─────────────────────────────────────────────
  const key = `${d.order}|${d.product}`;
  const rec = store.downloads[key] || { count: 0, ips: [], firstAt: Date.now() };
  const max = Number(d.max) || 0;

  if (max > 0 && rec.count >= max) {
    // Distinct IPs on one order is the strongest cheap leak signal available.
    const abuse = rec.ips.length >= Number(cfg.abuseIpThreshold);
    out.push(deny('limit_reached',
      `This link has already been used ${rec.count} of ${max} times. ` +
      `If you still need access, contact ${cfg.supportEmail} and it will be restored.`,
      {
        downloadCount: rec.count,
        distinctIps: rec.ips.length,
        abuseSignal: abuse,
        abuseNote: abuse
          ? `⚠️ ${rec.ips.length} distinct IPs used this link — it was probably shared publicly.`
          : null,
      }));
    continue;
  }

  // ── 5. Resolve the file ─────────────────────────────────────────
  const map = cfg.fileUrlMap || {};
  const fileUrl = map[d.product] || map.default;
  if (!fileUrl) {
    out.push(deny('unknown_product',
      `We could not find the file for product "${d.product}". ` +
      `Please contact ${cfg.supportEmail} with your order id (${d.order}) and it will be sent directly.`));
    continue;
  }

  // ── Allow ───────────────────────────────────────────────────────
  rec.count += 1;
  if (d.ip && !rec.ips.includes(d.ip)) rec.ips.push(d.ip);
  if (rec.ips.length > 50) rec.ips = rec.ips.slice(-50);
  store.downloads[key] = rec;

  out.push({
    json: {
      allowed: true,
      code: 'ok',
      order: d.order,
      email: d.email,
      product: d.product,
      fileUrl,
      downloadCount: rec.count,
      remaining: max > 0 ? Math.max(0, max - rec.count) : null,
      distinctIps: rec.ips.length,
      abuseSignal: rec.ips.length >= Number(cfg.abuseIpThreshold),
      ip: d.ip,
      servedAt: new Date().toISOString(),
    }
  });
}

return out;
""",
        (220, 180),
        notes="Signature, expiry and cap in one auditable place. Counters live in static data — no database needed.",
        always_output=True,
    )

    allowed = wf.if_(
        "✅ Allowed?",
        (460, 180),
        left="={{ $json.allowed }}",
        operator={"type": "boolean", "operation": "true", "singleValue": True},
    )

    serve = wf.code(
        "📤 Serve the file",
        r"""
// Hand back a redirect to the real file rather than streaming it through n8n:
// large files would otherwise sit in workflow memory and time the request out.
// Sign this URL at your storage provider too (S3 presigned / Cloudflare signed)
// so the final URL is short-lived even if someone captures the redirect.
return $input.all().map(i => ({
  json: {
    __redirect: i.json.fileUrl,
    order: i.json.order,
    product: i.json.product,
    downloadCount: i.json.downloadCount,
    remaining: i.json.remaining,
  }
}));
""",
        (700, 60),
        notes="Redirects to your storage. Use presigned storage URLs for a second layer.",
    )

    refuse = wf.code(
        "🚫 Explain the refusal",
        r"""
// The page a blocked buyer actually sees. Being specific here is what prevents
// the support ticket — a generic 403 guarantees one.
return $input.all().map(i => {
  const d = i.json;
  const html =
`<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<div style="font-family:system-ui,-apple-system,Segoe UI,sans-serif;max-width:520px;margin:12vh auto;padding:0 24px;color:#111;text-align:center">
  <div style="font-size:44px;line-height:1">🔒</div>
  <h1 style="font-size:21px;margin:16px 0 10px">This download link isn't working</h1>
  <p style="color:#555;line-height:1.65;margin:0 0 26px">${d.message}</p>
  <a href="${d.resendUrl}" style="display:inline-block;background:#111;color:#fff;text-decoration:none;padding:13px 26px;border-radius:8px;font-weight:600">Send me a fresh link</a>
  <p style="color:#888;font-size:13px;margin:26px 0 0">Still stuck? Email <a href="mailto:${d.supportEmail}">${d.supportEmail}</a>${d.order ? ` and quote order <strong>${d.order}</strong>` : ''}.</p>
</div>`;

  return { json: { ...d, html } };
});
""",
        (700, 320),
        notes="Returns a real explanation page, not a bare 403.",
    )

    log = wf.code(
        "📒 Access log",
        r"""
// One row per attempt, allowed or not. Refusal patterns are the useful part:
// a spike in 'expired' means your TTL is too short for your audience, and a
// spike in 'limit_reached' with high distinctIps means a link is circulating.
return $input.all().map(i => ({
  json: {
    ts: new Date().toISOString(),
    order: i.json.order ?? null,
    product: i.json.product ?? null,
    allowed: i.json.allowed ?? false,
    code: i.json.code ?? null,
    ip: i.json.ip ?? null,
    downloadCount: i.json.downloadCount ?? null,
    abuseSignal: i.json.abuseSignal ?? false,
  }
}));
""",
        (940, 180),
        notes="Append to your log. Watch the refusal-code mix — it tells you what to tune.",
    )

    respond_ok = wf.node(
        "↩️ Redirect to file",
        "n8n-nodes-base.respondToWebhook",
        {
            "respondWith": "redirect",
            "redirectURL": "={{ $('📤 Serve the file').first().json.__redirect }}",
            "options": {},
        },
        1.1,
        (1180, 60),
        notes="302 to the real file URL.",
    )

    respond_deny = wf.node(
        "↩️ Show the reason",
        "n8n-nodes-base.respondToWebhook",
        {
            "respondWith": "text",
            "responseBody": "={{ $('🚫 Explain the refusal').first().json.html }}",
            "options": {"responseCode": 403, "responseHeaders": {"entries": [{"name": "content-type", "value": "text/html; charset=utf-8"}]}},
        },
        1.1,
        (1180, 320),
        notes="403 with a human explanation and a one-click way to fix it.",
    )

    wf.chain(hook, cfg, prepare, recompute, verify, allowed)
    wf.connect(allowed, serve, out=0)
    wf.connect(allowed, refuse, out=1)
    wf.connect(serve, log)
    wf.connect(refuse, log)
    wf.connect(log, respond_ok)
    wf.connect(log, respond_deny)

    return wf
