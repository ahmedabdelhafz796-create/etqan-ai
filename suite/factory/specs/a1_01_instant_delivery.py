"""
DCA-A1-01 · Instant Digital Delivery (multi-gateway)

The problem this exists for
---------------------------
"Paid and never received the product" is the single most damaging failure a
digital seller can have: it produces a refund, a chargeback, a support ticket
and a bad review from one event. It happens because most delivery automations
are a straight line — webhook, email, done — with no verification, no retry and
no record. When the email provider rate-limits, the purchase is simply lost and
nobody finds out until the customer complains.

What this template does differently
-----------------------------------
  * Accepts Stripe, PayPal, Lemon Squeezy, Gumroad, Paddle and NOWPayments on
    one endpoint and normalises them to a single internal event shape, so the
    rest of the suite has exactly one contract to code against.
  * Verifies the webhook signature before trusting anything. An unverified
    delivery endpoint is a free-products endpoint for anyone who finds the URL.
  * Refuses to deliver on any status other than a confirmed, fully-paid event —
    pending crypto confirmations and authorised-but-not-captured cards included.
  * Issues a signed, expiring, download-limited link instead of attaching the
    file, so a forwarded email does not become permanent public distribution.
  * Treats a failed send as an incident: retried, then routed to an alert with
    the buyer's details so it can be recovered manually within minutes.
"""

from lib.core import Workflow, COLOR_BLUE, COLOR_GREEN, COLOR_RED, COLOR_PURPLE

SLUG = "instant-digital-delivery"


def build() -> Workflow:
    wf = Workflow(
        name="DCA-A1-01 · Instant Digital Delivery (Stripe / PayPal / Lemon Squeezy / Gumroad / Paddle / NOWPayments)",
        slug=SLUG,
        category="a1-delivery",
        summary="One endpoint that turns a confirmed payment from any major gateway into a signed, expiring download link in the buyer's inbox.",
        problem="Buyers pay and the product never arrives, because delivery automations have no verification, no retry and no failure alarm.",
        outcome="Every paid order is verified, de-duplicated, delivered and logged — and any delivery that fails raises an alert with enough detail to recover it by hand.",
        version="1.0.0",
        tags=["digital-products", "delivery", "payments", "hardened"],
        credentials_needed=[
            "SMTP account (or your email API of choice)",
            "Your payment provider's webhook signing secret",
        ],
        setup_minutes=12,
    )

    # ── Canvas documentation ────────────────────────────────────────────
    wf.sticky(
        "## 📦 Instant Digital Delivery\n"
        "**Payment confirmed → signed download link delivered → order logged.**\n\n"
        "### Setup (about 12 minutes)\n"
        "1. Open **⚙️ Config** and set `storeName`, `fromEmail`, `downloadBaseUrl`, `provider`.\n"
        "2. Put your webhook signing secret in the **Verify signature** node's *Secret* field.\n"
        "3. Put your link-signing secret (any long random string you invent) in **Sign download link**.\n"
        "4. Copy this workflow's **Production URL** into your payment provider's webhook settings.\n"
        "5. Attach your SMTP credential to **Send the product**.\n"
        "6. Activate.\n\n"
        "### Supported providers\n"
        "`stripe` · `paypal` · `lemonsqueezy` · `gumroad` · `paddle` · `nowpayments`\n\n"
        "⚠️ Set `provider` to match your gateway. `auto` guesses from the payload shape and is\n"
        "fine for testing, but pin it explicitly in production.",
        (-620, -420),
        (560, 560),
        COLOR_BLUE,
    )

    wf.sticky(
        "### 🛡️ Why this does not double-deliver\n"
        "Every gateway retries webhooks — on timeout, on a 500, and sometimes for no\n"
        "reason at all. Stripe alone may resend the same event for up to 3 days.\n\n"
        "**Guard** keys on the provider's own event id and remembers it for 72h in n8n\n"
        "static data, so a replay produces zero items and nothing downstream runs again.\n"
        "No database required.",
        (-40, -420),
        (420, 300),
        COLOR_GREEN,
    )

    wf.sticky(
        "### 🔐 Why a signed link, not an attachment\n"
        "Attachments get forwarded, and forwarded means unlimited free copies.\n\n"
        "This issues a URL carrying `expires`, `maxDownloads`, the order id and an\n"
        "HMAC signature. Your download endpoint recomputes the HMAC and rejects\n"
        "anything altered or past expiry.\n\n"
        "**Pair with `DCA-A1-02 · Secure Download Endpoint`**, which implements the\n"
        "matching verifier — or verify server-side yourself using the same secret.",
        (900, -420),
        (440, 320),
        COLOR_PURPLE,
    )

    wf.sticky(
        "### 🚨 Failure path\n"
        "If the email send fails after 3 retries the run does **not** die quietly.\n"
        "It leaves via the red error output and produces a structured alert record\n"
        "containing the buyer's email, the order id and the signed link — everything\n"
        "needed to recover the sale manually.\n\n"
        "Wire **🚨 Handle failure** to Slack, Telegram or email. Recommended: also set\n"
        "*Settings → Error Workflow* so every template in the suite reports to one place.",
        (1600, 120),
        (440, 300),
        COLOR_RED,
    )

    # ── Entry ───────────────────────────────────────────────────────────
    hook = wf.webhook(
        "💳 Payment webhook",
        (-620, 160),
        path="dca/payment",
        raw_body=True,
        notes="Raw body is kept on purpose — signatures must be computed over the exact bytes received.",
    )

    cfg = wf.config(
        {
            "storeName": "YOUR_STORE_NAME",
            "fromEmail": "orders@yourdomain.com",
            "supportEmail": "support@yourdomain.com",
            "provider": "auto",
            "downloadBaseUrl": "https://yourdomain.com/download",
            "linkTtlHours": 48,
            "maxDownloads": 5,
            "minAmount": 0,
            "currencyAllowList": [],
            "testMode": False,
        },
        (-400, 160),
        notes="The only node you must edit. Secrets go in Credentials / the Crypto nodes, never here.",
    )

    # ── Signature verification ──────────────────────────────────────────
    sig = wf.hmac(
        "🔏 Verify signature",
        (-180, 160),
        value="={{ $json.body ? JSON.stringify($json.body) : ($json.rawBody || '') }}",
        secret="YOUR_WEBHOOK_SIGNING_SECRET",
        prop="computedSignature",
        encoding="hex",
        notes="Replace the Secret with your gateway's webhook signing secret. Stripe: whsec_… · Lemon Squeezy: your signing secret · Paddle: your notification key.",
    )

    check_sig = wf.code(
        "🔒 Reject forged calls",
        r"""
// Compare the signature the gateway sent against the one we just computed.
// Without this, the endpoint URL alone is enough for anyone to mint free orders.
//
// Header names differ per gateway, so we look for all of the common ones.
const cfg = $('⚙️ Config').first().json.__config;
const item = $input.first().json;
const headers = item.headers || {};

const sent = String(
  headers['stripe-signature'] ||
  headers['x-signature'] ||
  headers['x-event-signature'] ||
  headers['paypal-transmission-sig'] ||
  headers['x-nowpayments-sig'] ||
  headers['x-paddle-signature'] ||
  ''
);

const computed = String(item.computedSignature || '');

// Stripe sends `t=…,v1=<hex>`; pull out the v1 part when present.
const normalisedSent = sent.includes('v1=')
  ? (sent.split('v1=')[1] || '').split(',')[0].trim()
  : sent.trim();

// Constant-time-ish comparison. Not perfect in JS, but it removes the trivial
// early-exit timing signal of `===` on strings.
function safeEqual(a, b) {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

const ok = normalisedSent.length > 0 && safeEqual(normalisedSent.toLowerCase(), computed.toLowerCase());

if (!ok && !cfg.testMode) {
  throw new Error(
    'Webhook signature verification failed. ' +
    'Check that the secret in "Verify signature" matches your gateway, ' +
    'or set testMode:true in Config while you are still wiring things up.'
  );
}

return [{ json: { ...item, __signatureVerified: ok, __config: cfg } }];
""",
        (40, 160),
        notes="Set testMode:true in Config to bypass while testing. Never leave it on in production.",
    )

    # ── Guard ───────────────────────────────────────────────────────────
    guard = wf.guard(
        (260, 160),
        required=["body"],
        event_id_expr=(
            "j.body?.id ?? j.body?.event_id ?? j.body?.data?.id ?? "
            "j.body?.meta?.event_id ?? j.body?.payment_id ?? j.body?.order_id ?? "
            "j.body?.sale_id ?? j.headers?.['stripe-signature']"
        ),
        ttl_hours=72,
    )

    # ── Normalise ───────────────────────────────────────────────────────
    normalise = wf.code(
        "🔄 Normalise to one order shape",
        r"""
// Every gateway invents its own payload shape. Rather than sprinkle provider
// conditionals through the whole suite, we translate once, here, into a single
// canonical order. Every other template in the suite consumes THIS shape.
const cfg = $('⚙️ Config').first().json.__config;
const out = [];

function detect(b) {
  if (b?.object === 'event' && String(b?.id || '').startsWith('evt_')) return 'stripe';
  if (b?.meta?.event_name && b?.data?.attributes) return 'lemonsqueezy';
  if (b?.alert_name || b?.event_type === 'transaction.completed') return 'paddle';
  if (b?.payment_status && b?.payment_id) return 'nowpayments';
  if (b?.resource_type || b?.event_type?.startsWith?.('PAYMENT.')) return 'paypal';
  if (b?.seller_id && b?.product_id) return 'gumroad';
  return 'unknown';
}

for (const item of $input.all()) {
  const j = item.json;
  const b = j.body ?? j;
  const provider = cfg.provider && cfg.provider !== 'auto' ? cfg.provider : detect(b);

  let o = {
    provider,
    eventId: j.__eventId,
    orderId: null,
    email: null,
    name: null,
    productId: null,
    productName: null,
    amount: null,
    currency: null,
    status: 'unknown',
    paidAt: new Date().toISOString(),
    raw: b,
  };

  if (provider === 'stripe') {
    const d = b?.data?.object ?? {};
    o.orderId    = d.id ?? b.id;
    o.email      = d.customer_details?.email ?? d.customer_email ?? d.receipt_email ?? null;
    o.name       = d.customer_details?.name ?? null;
    o.amount     = (d.amount_total ?? d.amount ?? 0) / 100;   // Stripe uses minor units
    o.currency   = (d.currency ?? '').toUpperCase();
    o.productId  = d.metadata?.product_id ?? null;
    o.productName= d.metadata?.product_name ?? null;
    // 'paid' is the only status that means the money actually moved.
    o.status     = (d.payment_status === 'paid' || d.status === 'succeeded') ? 'paid' : String(d.payment_status ?? d.status ?? 'pending');

  } else if (provider === 'lemonsqueezy') {
    const a = b?.data?.attributes ?? {};
    o.orderId    = String(b?.data?.id ?? '');
    o.email      = a.user_email ?? null;
    o.name       = a.user_name ?? null;
    o.amount     = (a.total ?? 0) / 100;
    o.currency   = (a.currency ?? '').toUpperCase();
    o.productId  = String(a.first_order_item?.product_id ?? '');
    o.productName= a.first_order_item?.product_name ?? null;
    o.status     = a.status === 'paid' ? 'paid' : String(a.status ?? 'pending');

  } else if (provider === 'gumroad') {
    o.orderId    = b.sale_id ?? b.order_number ?? null;
    o.email      = b.email ?? b.purchaser_email ?? null;
    o.name       = b.full_name ?? null;
    o.amount     = Number(b.price ?? 0) / 100;
    o.currency   = (b.currency ?? 'USD').toUpperCase();
    o.productId  = b.product_id ?? b.product_permalink ?? null;
    o.productName= b.product_name ?? null;
    // Gumroad posts refunds/disputes through the same hook — do not deliver on those.
    o.status     = (b.refunded === 'true' || b.refunded === true || b.disputed === 'true') ? 'refunded' : 'paid';

  } else if (provider === 'paddle') {
    const d = b?.data ?? b;
    o.orderId    = d.id ?? b.order_id ?? null;
    o.email      = d.customer?.email ?? b.email ?? null;
    o.name       = d.customer?.name ?? null;
    o.amount     = Number(d.details?.totals?.total ?? b.sale_gross ?? 0) / 100;
    o.currency   = (d.currency_code ?? b.currency ?? '').toUpperCase();
    o.productId  = d.items?.[0]?.price?.product_id ?? b.product_id ?? null;
    o.productName= d.items?.[0]?.price?.name ?? b.product_name ?? null;
    o.status     = (d.status === 'completed' || b.alert_name === 'payment_succeeded') ? 'paid' : String(d.status ?? 'pending');

  } else if (provider === 'nowpayments') {
    o.orderId    = b.order_id ?? String(b.payment_id ?? '');
    o.email      = b.order_description?.email ?? b.customer_email ?? null;
    o.amount     = Number(b.price_amount ?? b.actually_paid ?? 0);
    o.currency   = (b.price_currency ?? '').toUpperCase();
    o.productId  = b.order_id ?? null;
    // Crypto settles in stages. 'confirmed'/'finished' mean the funds are final;
    // 'confirming' does NOT — delivering there is how you get robbed on a reorg.
    o.status     = ['finished', 'confirmed'].includes(String(b.payment_status)) ? 'paid' : String(b.payment_status ?? 'pending');

  } else if (provider === 'paypal') {
    const r = b?.resource ?? {};
    o.orderId    = r.id ?? b.id ?? null;
    o.email      = r.payer?.email_address ?? b.email ?? null;
    o.name       = [r.payer?.name?.given_name, r.payer?.name?.surname].filter(Boolean).join(' ') || null;
    o.amount     = Number(r.amount?.value ?? r.purchase_units?.[0]?.amount?.value ?? 0);
    o.currency   = (r.amount?.currency_code ?? 'USD').toUpperCase();
    o.status     = ['COMPLETED', 'APPROVED'].includes(String(r.status)) ? 'paid' : String(r.status ?? 'pending');

  } else {
    // Unknown shapes are surfaced loudly rather than half-processed.
    throw new Error(
      'Unrecognised webhook payload. Set "provider" explicitly in Config ' +
      '(stripe | paypal | lemonsqueezy | gumroad | paddle | nowpayments). ' +
      'Top-level keys received: ' + Object.keys(b || {}).join(', ')
    );
  }

  if (!o.email) {
    throw new Error('No buyer email in the payload for order ' + o.orderId + ' — cannot deliver. Check the gateway is configured to include customer email.');
  }

  o.__config = cfg;
  out.push({ json: o });
}

return out;
""",
        (480, 160),
        notes="Translates six gateway formats into one canonical order object.",
    )

    # ── Payment actually confirmed? ─────────────────────────────────────
    is_paid = wf.if_(
        "✅ Is the money really in?",
        (700, 160),
        left="={{ $json.status }}",
        operator={"type": "string", "operation": "equals"},
        right="paid",
    )

    not_paid = wf.code(
        "⏸️ Hold — not payable yet",
        r"""
// Reached for pending, authorised-not-captured, failed, refunded and disputed
// events. We deliberately do nothing here except record the reason, because
// delivering on any of these is how sellers give product away for free.
return $input.all().map(i => ({
  json: {
    delivered: false,
    reason: 'status=' + i.json.status,
    orderId: i.json.orderId,
    email: i.json.email,
    provider: i.json.provider,
    note: 'No delivery attempted. Crypto payments often arrive here first and pass on the follow-up webhook.',
  }
}));
""",
        (920, 400),
        notes="Non-paid events end here safely. This is the branch that prevents free-product leakage.",
    )

    # ── Amount / currency sanity ────────────────────────────────────────
    amount_ok = wf.code(
        "🧮 Sanity-check the amount",
        r"""
// A confirmed status is not the same as a correct amount. Tampered checkouts and
// misconfigured test keys both show up as "paid" for the wrong number.
const out = [];
for (const i of $input.all()) {
  const o = i.json;
  const cfg = o.__config;

  if (cfg.minAmount > 0 && Number(o.amount) < Number(cfg.minAmount)) {
    throw new Error(
      'Order ' + o.orderId + ' paid ' + o.amount + ' ' + o.currency +
      ' which is below minAmount (' + cfg.minAmount + '). Refusing to deliver — review this order by hand.'
    );
  }

  const allow = cfg.currencyAllowList || [];
  if (allow.length && o.currency && !allow.includes(o.currency)) {
    throw new Error(
      'Order ' + o.orderId + ' is in ' + o.currency + ', which is not in currencyAllowList. Refusing to deliver.'
    );
  }

  // Precompute the values the signature is built from, so the Crypto node has a
  // single flat string to sign and we are not duplicating logic in expressions.
  const expires = Math.floor(Date.now() / 1000) + (Number(cfg.linkTtlHours) * 3600);
  const payload = [o.orderId, o.email, o.productId ?? '', expires, cfg.maxDownloads].join('|');

  out.push({ json: { ...o, __expires: expires, __signaturePayload: payload } });
}
return out;
""",
        (920, 60),
        notes="Blocks under-paid and wrong-currency orders before anything is handed over.",
    )

    # ── Sign the download link ──────────────────────────────────────────
    sign = wf.hmac(
        "✍️ Sign download link",
        (1140, 60),
        value="={{ $json.__signaturePayload }}",
        secret="YOUR_OWN_LONG_RANDOM_LINK_SECRET",
        prop="linkSignature",
        encoding="hex",
        notes="Invent a long random string and use the SAME one in your download endpoint (and in DCA-A1-02).",
    )

    build_link = wf.code(
        "🔗 Build the delivery link",
        r"""
// Assemble the tamper-evident URL. Everything the endpoint needs to make an
// allow/deny decision travels in the URL and is covered by the signature, so
// the endpoint stays stateless.
return $input.all().map(i => {
  const o = i.json;
  const cfg = o.__config;
  const qs = new URLSearchParams({
    order: String(o.orderId),
    email: String(o.email),
    product: String(o.productId ?? ''),
    expires: String(o.__expires),
    max: String(cfg.maxDownloads),
    sig: String(o.linkSignature),
  });

  const url = cfg.downloadBaseUrl.replace(/\/+$/, '') + '?' + qs.toString();
  const expiresHuman = new Date(o.__expires * 1000).toUTCString();

  return { json: { ...o, downloadUrl: url, expiresHuman } };
});
""",
        (1360, 60),
        notes="Produces the final signed URL plus a human-readable expiry for the email.",
    )

    # ── Deliver ─────────────────────────────────────────────────────────
    send = wf.node(
        "📧 Send the product",
        "n8n-nodes-base.emailSend",
        {
            "fromEmail": "={{ $json.__config.fromEmail }}",
            "toEmail": "={{ $json.email }}",
            "subject": "={{ 'Your download from ' + $json.__config.storeName + ' is ready' }}",
            "emailFormat": "html",
            "html": (
                "={{ '<div style=\"font-family:system-ui,-apple-system,Segoe UI,sans-serif;"
                "max-width:560px;margin:0 auto;padding:32px 24px;color:#111\">'"
                " + '<h2 style=\"margin:0 0 8px\">Thank you' + ($json.name ? ', ' + $json.name : '') + '!</h2>'"
                " + '<p style=\"color:#555;margin:0 0 24px\">Your order <strong>' + $json.orderId + '</strong> is confirmed"
                " and your download is ready.</p>'"
                " + '<a href=\"' + $json.downloadUrl + '\" style=\"display:inline-block;background:#111;color:#fff;"
                "text-decoration:none;padding:14px 28px;border-radius:8px;font-weight:600\">Download now</a>'"
                " + '<p style=\"color:#777;font-size:13px;margin:24px 0 0\">This link expires on <strong>' + $json.expiresHuman + '</strong>"
                " and allows up to ' + $json.__config.maxDownloads + ' downloads.</p>'"
                " + '<p style=\"color:#777;font-size:13px;margin:8px 0 0\">Trouble downloading? Reply to this email or contact "
                "<a href=\"mailto:' + $json.__config.supportEmail + '\">' + $json.__config.supportEmail + '</a> and we will sort it out.</p>'"
                " + '<hr style=\"border:none;border-top:1px solid #eee;margin:28px 0\">'"
                " + '<p style=\"color:#999;font-size:12px;margin:0\">' + $json.__config.storeName + '</p>'"
                " + '</div>' }}"
            ),
            "options": {},
        },
        2.1,
        (1580, 60),
        retry=True,
        max_tries=3,
        wait_ms=3000,
        on_error="continueErrorOutput",
        notes="Attach your SMTP credential. Retries 3×; a final failure leaves via the red output and raises an alert.",
    )

    log = wf.code(
        "🧾 Record the order",
        r"""
// A delivery you cannot prove is a dispute you will lose. Emit a flat, complete
// record and send it wherever you keep order history — Sheets, Airtable,
// Postgres, Notion. Chargeback templates in this suite read exactly this shape.
return $input.all().map(i => {
  const o = i.json;
  return {
    json: {
      ok: true,
      deliveredAt: new Date().toISOString(),
      orderId: o.orderId,
      eventId: o.eventId,
      provider: o.provider,
      email: o.email,
      name: o.name,
      productId: o.productId,
      productName: o.productName,
      amount: o.amount,
      currency: o.currency,
      downloadUrl: o.downloadUrl,
      linkExpiresAt: new Date(o.__expires * 1000).toISOString(),
      maxDownloads: o.__config.maxDownloads,
    }
  };
});
""",
        (1800, 60),
        notes="Append this to your order log. Keep it — it is your chargeback evidence.",
    )

    fail = wf.error_sink(
        (1800, 260),
        context="delivery-email",
    )

    respond = wf.respond(
        "↩️ 200 OK",
        (2020, 160),
        body='={{ JSON.stringify({ ok: true, received: true }) }}',
    )

    # ── Wiring ──────────────────────────────────────────────────────────
    wf.chain(hook, cfg, sig, check_sig, guard, normalise, is_paid)
    wf.connect(is_paid, amount_ok, out=0)   # true  → paid
    wf.connect(is_paid, not_paid, out=1)    # false → hold
    wf.chain(amount_ok, sign, build_link, send)
    wf.connect(send, log, out=0)            # success
    wf.connect(send, fail, out=1)           # error output
    wf.connect(log, respond)
    wf.connect(fail, respond)
    wf.connect(not_paid, respond)

    return wf
