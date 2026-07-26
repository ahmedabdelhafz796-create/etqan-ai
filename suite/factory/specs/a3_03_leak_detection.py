"""
DCA-A3-03 · Leak Detection & Buyer Watermarking

Solves "سرقة الملفات وإعادة بيعها" — the file is bought once and then shared,
resold, or posted to a Telegram channel with ten thousand members.

The honest position, stated up front
------------------------------------
A determined person will always be able to copy a file they can open. Any
template claiming to prevent piracy is lying, and the canvas says so.

What is achievable is different and still valuable: making leaks **attributable
and visible**. If every copy carries an invisible marker tied to the buyer, a
leaked file identifies who leaked it — which changes the economics for the small
number of people doing organised resale, and gives the seller grounds for a
takedown that actually names an account.

Three layers, and why each earns its place
------------------------------------------
1. **Per-buyer stamping.** A visible line ("Licensed to …") plus an invisible
   token. The visible line deters casual sharing on its own — most sharing is
   thoughtless rather than malicious, and a name on the page makes people think.
2. **Behavioural detection.** A single order downloaded from forty IP addresses
   is not one customer on holiday. This reads the counters the download endpoint
   already writes, so it costs nothing extra.
3. **Takedown assistance.** When a leak is confirmed, the seller has minutes of
   motivation and no idea what to do. This produces the DMCA notice, pre-filled.

What it deliberately does not do
--------------------------------
It does not scan the web automatically. Doing that properly needs paid search
APIs and produces mostly false positives on generic product names — a nightly
job reporting forty "possible leaks" that are all unrelated pages gets muted in
a week. Instead it accepts a URL when *you* find one and does the work from
there. Honest scope beats an impressive feature nobody trusts.
"""

from lib.core import Workflow, COLOR_BLUE, COLOR_GREEN, COLOR_RED, COLOR_PURPLE

SLUG = "leak-detection-watermarking"


def build() -> Workflow:
    wf = Workflow(
        name="DCA-A3-03 · Leak Detection & Buyer Watermarking",
        slug=SLUG,
        category="a3-fraud-security",
        summary="Stamps every copy with a buyer-specific marker, detects sharing patterns from download behaviour, traces a leaked file back to the account that leaked it, and drafts the takedown notice.",
        problem="A file is bought once and shared, resold, or posted to a channel with ten thousand members — and the seller has no way to tell whose copy it was or what to do about it.",
        outcome="Every copy is attributable, sharing patterns surface automatically from data you already collect, and a confirmed leak produces a named account plus a ready-to-send DMCA notice.",
        version="1.0.0",
        tags=["security", "anti-piracy", "digital-products", "watermarking", "hardened"],
        credentials_needed=["SMTP account"],
        setup_minutes=14,
    )

    wf.sticky(
        "## 🕵️ Leak Detection & Watermarking\n"
        "**Every copy traceable → sharing detected → takedown drafted.**\n\n"
        "### Setup (about 14 minutes)\n"
        "1. **⚙️ Config** → `storeName`, `alertEmail`, `legalName`.\n"
        "2. Call the Production URL with `{action:'stamp', orderId, email, productId}`\n"
        "   before delivering a file — it returns the marker to embed.\n"
        "3. Schedule handles detection automatically from download data.\n"
        "4. Found a leak? POST `{action:'trace', marker:'<found marker>'}` or\n"
        "   `{action:'takedown', marker, url}`.\n\n"
        "### Pairs with A1-01 and A1-02\n"
        "Stamp at delivery, detect from download behaviour. It reads the counters\n"
        "A1-02 already writes, so detection costs nothing extra.",
        (-700, -560),
        (600, 540),
        COLOR_BLUE,
    )

    wf.sticky(
        "### ⚠️ READ THIS FIRST — what is actually possible\n"
        "**You cannot prevent copying.** Anyone who can open a file can copy it.\n"
        "Any template claiming to stop piracy is lying to you.\n\n"
        "**What you CAN do is make leaks attributable and visible.**\n\n"
        "That is genuinely valuable: it changes the economics for organised\n"
        "resellers, deters casual sharing, and gives you a takedown that names an\n"
        "actual account instead of guessing.\n\n"
        "Aim at the achievable thing and it works. Aim at prevention and you will\n"
        "waste money on tools that do not deliver it.",
        (-80, -560),
        (520, 440),
        COLOR_RED,
    )

    wf.sticky(
        "### 🔍 What it does NOT do — and why\n"
        "**No automatic web scanning.**\n\n"
        "Doing it properly needs paid search APIs and produces mostly false\n"
        "positives on generic product names. A nightly job reporting forty\n"
        "\"possible leaks\" that are all unrelated pages **gets muted in a week**.\n\n"
        "So: you find a leak, this does the work from there — trace, identify,\n"
        "draft the notice.\n\n"
        "Honest scope beats an impressive feature nobody trusts.",
        (460, -560),
        (480, 400),
        COLOR_PURPLE,
    )

    wf.sticky(
        "### 📊 The behavioural signal\n"
        "One order downloaded from **40 different IPs** is not a customer on\n"
        "holiday.\n\n"
        "The schedule reads what A1-02 already records — distinct IPs and download\n"
        "counts per order — so this layer costs you nothing extra.\n\n"
        "⚠️ Tune `suspiciousIpCount` to your audience. Corporate buyers behind a\n"
        "VPN legitimately show several IPs.",
        (1160, 420),
        (460, 320),
        COLOR_GREEN,
    )

    hook = wf.webhook(
        "🔖 Stamp / trace / takedown",
        (-700, 200),
        path="dca/leak",
        notes="POST {action: 'stamp'|'trace'|'takedown', ...}. One endpoint, three jobs.",
    )

    cfg = wf.config(
        {
            "storeName": "YOUR_STORE_NAME",
            "legalName": "YOUR LEGAL NAME OR COMPANY",
            "alertEmail": "you@yourdomain.com",
            "fromEmail": "alerts@yourdomain.com",
            "contactEmail": "legal@yourdomain.com",
            "productUrl": "https://yourdomain.com/product",
            "suspiciousIpCount": 8,
            "criticalIpCount": 20,
            "markerSalt": "CHANGE_THIS_TO_A_LONG_RANDOM_STRING",
            "historyTtlDays": 365,
        },
        (-480, 200),
        notes="markerSalt must be long, random and never change — old markers stop resolving if it does.",
    )

    guard = wf.guard(
        (-260, 200),
        required=["body"],
        event_id_expr="(j.body?.action ?? '') + '|' + (j.body?.orderId ?? j.body?.marker ?? Date.now())",
        ttl_hours=1,
    )

    route = wf.node(
        "🔀 Which job?",
        "n8n-nodes-base.switch",
        {
            "rules": {"values": [
                {"conditions": {"options": {"version": 2, "leftValue": "", "caseSensitive": False, "typeValidation": "loose"},
                                "combinator": "and",
                                "conditions": [{"id": "r-stamp", "operator": {"type": "string", "operation": "equals"},
                                                "leftValue": "={{ $json.body.action }}", "rightValue": "stamp"}]},
                 "outputKey": "stamp"},
                {"conditions": {"options": {"version": 2, "leftValue": "", "caseSensitive": False, "typeValidation": "loose"},
                                "combinator": "and",
                                "conditions": [{"id": "r-trace", "operator": {"type": "string", "operation": "equals"},
                                                "leftValue": "={{ $json.body.action }}", "rightValue": "trace"}]},
                 "outputKey": "trace"},
                {"conditions": {"options": {"version": 2, "leftValue": "", "caseSensitive": False, "typeValidation": "loose"},
                                "combinator": "and",
                                "conditions": [{"id": "r-takedown", "operator": {"type": "string", "operation": "equals"},
                                                "leftValue": "={{ $json.body.action }}", "rightValue": "takedown"}]},
                 "outputKey": "takedown"},
            ]},
            "options": {"fallbackOutput": 0},
        },
        3.2,
        (-40, 200),
        notes="Output 0 = stamp · 1 = trace · 2 = takedown.",
    )

    stamp = wf.code(
        "🔖 Create the buyer marker",
        r"""
// Build a marker that is short enough to embed unobtrusively and long enough not
// to collide, derived from the order so it can be resolved later.
//
// Two parts on purpose:
//   visible   — "Licensed to name (order)". Most sharing is thoughtless rather
//               than malicious, and a name on the page makes people hesitate.
//   invisible — an opaque token to embed in metadata, a zero-width span, or a
//               PDF property. Survives casual removal of the visible line.
const cfg = $('⚙️ Config').first().json.__config;
const store = $getWorkflowStaticData('global');
store.markers = store.markers || {};

const now = Date.now();
const ttlMs = Number(cfg.historyTtlDays) * 24 * 60 * 60 * 1000;
for (const [k, m] of Object.entries(store.markers)) {
  if (now - (m.issuedAt || 0) > ttlMs) delete store.markers[k];
}

// Deterministic, non-reversible-looking token. It does not need to resist
// cryptanalysis — it needs to be unguessable enough that a leaker cannot forge
// someone else's marker, and stable enough to resolve later.
function token(input) {
  let h1 = 0x811c9dc5, h2 = 0x01000193;
  for (let i = 0; i < input.length; i++) {
    h1 = ((h1 ^ input.charCodeAt(i)) * 0x01000193) >>> 0;
    h2 = ((h2 + input.charCodeAt(i) * (i + 7)) * 0x85ebca6b) >>> 0;
  }
  return (h1.toString(36) + h2.toString(36)).toUpperCase().slice(0, 12);
}

const out = [];

for (const item of $input.all()) {
  const b = item.json.body ?? item.json;

  const orderId = String(b.orderId ?? b.order_id ?? '').trim();
  const email = String(b.email ?? '').trim().toLowerCase();
  const productId = String(b.productId ?? b.product_id ?? '').trim();
  const name = String(b.name ?? '').trim();

  if (!orderId || !email) {
    throw new Error('Stamping needs orderId and email. Received keys: ' + Object.keys(b).join(', '));
  }

  const marker = token(`${cfg.markerSalt}|${orderId}|${email}|${productId}`);

  store.markers[marker] = {
    marker, orderId, email, name, productId,
    issuedAt: now,
  };

  out.push({ json: {
    action: 'stamped',
    marker,
    orderId, email, productId,
    // Drop this line into a footer, a title page, or a page header.
    visibleMark: `Licensed to ${name || email} · Order ${orderId} · ${cfg.storeName}`,
    // Embed in PDF metadata, an EPUB property, or a zero-width span in HTML.
    invisibleMark: `DCA-${marker}`,
    // Ready to write straight into document metadata.
    metadataFields: {
      Author: cfg.legalName,
      Subject: `Licensed copy — order ${orderId}`,
      Keywords: `DCA-${marker}`,
      Producer: cfg.storeName,
    },
    guidance: 'Apply BOTH marks. The visible one deters casual sharing; the invisible one survives its removal.',
  }});
}

return out;
""",
        (240, 20),
        notes="Returns visible + invisible marks and ready-made metadata fields. Apply both.",
    )

    trace = wf.code(
        "🔎 Trace a found marker",
        r"""
// Someone found a leaked copy and pulled the marker out of it. Resolve it to the
// account that was issued that copy.
const cfg = $('⚙️ Config').first().json.__config;
const store = $getWorkflowStaticData('global');
store.markers = store.markers || {};

return $input.all().map(item => {
  const b = item.json.body ?? item.json;
  const raw = String(b.marker ?? '').trim().toUpperCase().replace(/^DCA-/, '');

  if (!raw) {
    throw new Error('Tracing needs a marker. Extract it from the leaked file first.');
  }

  const found = store.markers[raw];

  if (!found) {
    return { json: {
      action: 'trace_failed',
      marker: raw,
      message:
        'No record for this marker. Either it predates this workflow, markerSalt was changed since it was issued, ' +
        'or the marker was misread. Check for character confusion — 0/O and 1/I are the usual culprits.',
    }};
  }

  return { json: {
    action: 'traced',
    marker: raw,
    orderId: found.orderId,
    email: found.email,
    name: found.name,
    productId: found.productId,
    issuedAt: new Date(found.issuedAt).toISOString(),
    message: `This copy was issued to ${found.email} (order ${found.orderId}).`,
    nextSteps:
      '1. Decide whether this was deliberate resale or careless sharing — the response differs.\n' +
      '2. Consider contacting the buyer first. Many leaks are thoughtless, and a quiet word costs you nothing.\n' +
      '3. If it is organised resale, POST action:"takedown" with the URL to generate the notice.\n' +
      '4. Revoke their download access if you have not already.',
  }};
});
""",
        (240, 200),
        notes="Resolves a marker to the buyer. Includes what to do next, since most sellers have never done this.",
    )

    takedown = wf.code(
        "⚖️ Draft the takedown notice",
        r"""
// A seller who finds their product being resold has about ten minutes of
// motivation and no idea what a DMCA notice looks like. Pre-filling it is the
// difference between action and a shrug.
//
// Not legal advice, and the notice says so — but the structure is the standard
// one hosts expect, and a correctly-shaped notice gets actioned.
const cfg = $('⚙️ Config').first().json.__config;
const store = $getWorkflowStaticData('global');
store.markers = store.markers || {};

return $input.all().map(item => {
  const b = item.json.body ?? item.json;
  const raw = String(b.marker ?? '').trim().toUpperCase().replace(/^DCA-/, '');
  const url = String(b.url ?? '').trim();

  if (!url) {
    throw new Error('A takedown notice needs the URL where the material is hosted.');
  }

  const found = raw ? store.markers[raw] : null;
  const today = new Date().toISOString().slice(0, 10);

  const notice =
`DMCA TAKEDOWN NOTICE
Date: ${today}

To whom it may concern,

I am the copyright owner of the work described below, and I am writing to
report an infringing copy hosted on your service.

1. IDENTIFICATION OF THE COPYRIGHTED WORK
   Title:        ${b.productName || found?.productId || '[PRODUCT NAME]'}
   Owner:        ${cfg.legalName}
   Original URL: ${cfg.productUrl}

2. IDENTIFICATION OF THE INFRINGING MATERIAL
   Infringing URL: ${url}
${found ? `
3. EVIDENCE
   Each authorised copy of this work carries a unique identifier tied to the
   purchaser. The copy at the URL above carries identifier ${raw}, which was
   issued to a specific customer account on ${new Date(found.issuedAt).toISOString().slice(0, 10)}.
   The copy being distributed is therefore not an authorised distribution.
` : `
3. EVIDENCE
   The material at the URL above is a copy of my work, distributed without
   authorisation. I did not license it for redistribution.
`}
4. STATEMENTS
   I have a good faith belief that the use of the material described above is
   not authorised by the copyright owner, its agent, or the law.

   I state, under penalty of perjury, that the information in this notice is
   accurate and that I am the copyright owner or authorised to act on the
   owner's behalf.

5. CONTACT
   Name:  ${cfg.legalName}
   Email: ${cfg.contactEmail}

Signature: /${cfg.legalName}/

---
⚠️ NOT LEGAL ADVICE. Review this before sending. Requirements vary by
jurisdiction and by host. Send it to the host's designated DMCA agent —
usually found at their /dmca, /legal or /copyright page, or in their WHOIS
record — not to the person who posted the file.`;

  return { json: {
    action: 'takedown_drafted',
    marker: raw || null,
    infringingUrl: url,
    tracedTo: found ? { email: found.email, orderId: found.orderId } : null,
    notice,
    whereToSend:
      'Find the host\'s DMCA agent: check their /dmca or /legal page, or the WHOIS record for the domain. ' +
      'For Telegram, use abuse@telegram.org. For Gumroad, use their report form. ' +
      'Sending it to the uploader instead of the host usually achieves nothing.',
  }};
});
""",
        (240, 380),
        notes="Standard DMCA structure, pre-filled. Explicitly not legal advice — review before sending.",
    )

    # ── Behavioural detection ───────────────────────────────────────────
    sched = wf.schedule("🕐 Scan download patterns daily", (-700, 640), hours=24)

    cfg2 = wf.code(
        "⚙️ Config (detection side)",
        r"""
// Mirror of the main Config — n8n cannot share a node across trigger branches.
const CONFIG = {
  "storeName": "YOUR_STORE_NAME",
  "alertEmail": "you@yourdomain.com",
  "fromEmail": "alerts@yourdomain.com",
  "suspiciousIpCount": 8,
  "criticalIpCount": 20
};
return [{ json: { __config: CONFIG } }];
""",
        (-480, 640),
        notes="⚠️ Mirror of the main Config. Change one, change both.",
        always_output=True,
    )

    detect = wf.code(
        "📊 Find sharing patterns",
        r"""
// Reads the counters DCA-A1-02 already writes. No extra collection, no extra
// cost — the signal was already there, nobody was looking at it.
const cfg = $input.first().json.__config;
const store = $getWorkflowStaticData('global');
const downloads = store.downloads || {};
const markers = store.markers || {};

const suspects = [];

for (const [key, rec] of Object.entries(downloads)) {
  const ipCount = (rec.ips || []).length;
  if (ipCount < Number(cfg.suspiciousIpCount)) continue;

  const [orderId] = String(key).split('|');
  const owner = Object.values(markers).find(m => m.orderId === orderId);

  suspects.push({
    orderId,
    email: owner?.email ?? null,
    marker: owner?.marker ?? null,
    distinctIps: ipCount,
    downloadCount: rec.count || 0,
    severity: ipCount >= Number(cfg.criticalIpCount) ? 'critical' : 'suspicious',
    // Say what the number means, not just what it is.
    interpretation: ipCount >= Number(cfg.criticalIpCount)
      ? `${ipCount} distinct IPs on one order. This is not one person — the link or the file is circulating.`
      : `${ipCount} distinct IPs on one order. Could be a VPN or a shared office, but worth a look.`,
  });
}

suspects.sort((a, b) => b.distinctIps - a.distinctIps);

return [{ json: {
  __detection: true,
  found: suspects.length,
  critical: suspects.filter(s => s.severity === 'critical').length,
  suspects: suspects.slice(0, 20),
  scannedAt: new Date().toISOString(),
  __config: cfg,
}}];
""",
        (-260, 640),
        notes="Reads A1-02's download counters. Zero extra collection cost.",
        always_output=True,
    )

    has_suspects = wf.if_(
        "🚩 Anything found?",
        (-40, 640),
        left="={{ $json.found > 0 }}",
        operator={"type": "boolean", "operation": "true", "singleValue": True},
    )

    alert = wf.code(
        "✍️ Write the leak alert",
        r"""
const o = $input.first().json;
const cfg = o.__config;

const lines = o.suspects.map(s =>
  `${s.severity === 'critical' ? '🔴' : '🟡'} Order ${s.orderId}${s.email ? ` (${s.email})` : ''}\n` +
  `   ${s.distinctIps} distinct IPs · ${s.downloadCount} downloads\n` +
  `   ${s.interpretation}` +
  (s.marker ? `\n   Marker: DCA-${s.marker}` : '')
).join('\n\n');

return [{ json: { ...o,
  subject: `🕵️ ${o.found} order(s) showing sharing patterns`,
  alertText:
`🕵️ Possible sharing detected — ${cfg.storeName}

${o.found} order(s) crossed the threshold${o.critical ? `, ${o.critical} of them clearly` : ''}.

${lines}

── WHAT TO DO ──────────────────────
1. Check the 🔴 ones first. A VPN explains a few IPs, not twenty.
2. Consider contacting the buyer before acting. Most sharing is careless,
   not malicious, and a quiet word costs you nothing.
3. If you find the file being resold publicly, POST action:"takedown" with
   the URL to get a pre-filled DMCA notice.
4. Revoke access for confirmed leaks.

⚠️ Do not act on this number alone. It is a signal worth investigating,
not proof of wrongdoing.`,
}}];
""",
        (200, 560),
        notes="States plainly that the signal is worth investigating, not proof.",
    )

    send = wf.node(
        "📨 Send the leak alert",
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
        (440, 560),
        retry=True,
        max_tries=3,
        wait_ms=2000,
        on_error="continueRegularOutput",
        notes="Attach SMTP.",
    )

    clean = wf.code(
        "✅ Nothing unusual",
        r"""
return [{ json: { scannedAt: new Date().toISOString(), found: 0,
                  note: 'No orders crossed the sharing threshold.' }}];
""",
        (200, 740),
        notes="Logged so you can tell 'all clear' from 'not running'.",
    )

    log = wf.code(
        "📒 Leak log",
        r"""
return $input.all().map(i => ({ json: {
  ts: new Date().toISOString(),
  action: i.json.action ?? 'scan',
  found: i.json.found ?? null,
  marker: i.json.marker ?? null,
  orderId: i.json.orderId ?? null,
  infringingUrl: i.json.infringingUrl ?? null,
}}));
""",
        (700, 380),
        notes="Append to a Sheet. Repeat offenders show up here.",
    )

    respond = wf.respond(
        "↩️ Return result",
        (940, 200),
        body='={{ JSON.stringify($json) }}',
    )

    wf.chain(hook, cfg, guard, route)
    wf.connect(route, stamp, out=0)
    wf.connect(route, trace, out=1)
    wf.connect(route, takedown, out=2)
    for n in (stamp, trace, takedown):
        wf.connect(n, log)
    wf.connect(log, respond)

    wf.chain(sched, cfg2, detect, has_suspects)
    wf.connect(has_suspects, alert, out=0)
    wf.connect(has_suspects, clean, out=1)
    wf.connect(alert, send)
    wf.connect(send, log)
    wf.connect(clean, log)

    return wf
