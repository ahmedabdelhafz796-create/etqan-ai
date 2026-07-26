"""
DCA-A5-01 · Cart Abandonment Recovery

The other template a buyer can justify with arithmetic: if it recovers one sale
a month it has paid for itself, and abandonment rates on digital products are
high enough that it will.

Why carts get abandoned
-----------------------
Most abandonment is not rejection. It is interruption — a phone call, a closed
tab, a price the buyer wanted to think about for ten minutes. The purchase
intent was real and is often still there an hour later; nobody reminded them.

Design decisions worth stating
------------------------------
**Discounting is off by default.** The obvious implementation offers a discount
immediately, and it is a trap: buyers learn that abandoning a cart produces a
coupon, so you end up paying a discount on sales you would have made at full
price. This template sends a plain reminder first and only introduces an
incentive on the final message, which the seller must switch on deliberately.

**A hard cap on contact.** Two messages, then stop. A third message converts
almost nobody and reliably generates spam complaints, which damage the sending
reputation that every other template in this suite depends on.

**Purchases stop the sequence.** The checkout webhook accepts a `purchased`
event, because nothing burns goodwill faster than chasing someone for a cart
they already paid for.
"""

from lib.core import Workflow, COLOR_BLUE, COLOR_GREEN, COLOR_RED, COLOR_PURPLE

SLUG = "cart-abandonment-recovery"


def build() -> Workflow:
    wf = Workflow(
        name="DCA-A5-01 · Cart Abandonment Recovery",
        slug=SLUG,
        category="a5-marketing-revenue",
        summary="Recovers interrupted checkouts with a timed two-message sequence that stops the moment the buyer purchases, and keeps discounting off by default so you stop paying for sales you would have made anyway.",
        problem="Most abandoned carts are interruptions, not rejections — a closed tab, a phone call. The intent was real and often still is an hour later, but nobody follows up, so the sale is simply lost.",
        outcome="Every abandoned cart triggers a controlled recovery sequence, capped at two messages, that stops instantly on purchase and reports what it recovered.",
        version="1.0.0",
        tags=["marketing", "revenue-recovery", "ecommerce", "digital-products", "hardened"],
        credentials_needed=["SMTP account"],
        setup_minutes=12,
    )

    wf.sticky(
        "## 🛒 Cart Abandonment Recovery\n"
        "**Cart abandoned → timed reminder → sale recovered.**\n\n"
        "### Setup (about 12 minutes)\n"
        "1. **⚙️ Config** → `storeName`, `fromEmail`, `checkoutUrl`.\n"
        "2. Send a POST to the Production URL when someone reaches checkout and\n"
        "   does not complete. Minimum payload:\n"
        "   ```json\n"
        "   { \"email\": \"...\", \"cartId\": \"...\",\n"
        "     \"items\": [...], \"total\": 49 }\n"
        "   ```\n"
        "3. **Also** send `{\"email\":\"...\",\"event\":\"purchased\"}` when they buy —\n"
        "   this is what stops the sequence.\n"
        "4. Attach SMTP. Activate.\n\n"
        "⚠️ **Step 3 is not optional.** Without it you will email people about a\n"
        "cart they already paid for, which is worse than sending nothing at all.",
        (-660, -500),
        (580, 580),
        COLOR_BLUE,
    )

    wf.sticky(
        "### 💸 Why discounting is OFF by default\n"
        "The obvious build offers a discount straight away. It is a trap.\n\n"
        "Buyers learn quickly that abandoning a cart produces a coupon — so you\n"
        "end up **paying a discount on sales you would have made at full price**,\n"
        "and you train your best customers to always abandon first.\n\n"
        "This sends a plain reminder first. The incentive appears only on the\n"
        "final message, and only if you set `enableDiscount: true` yourself.\n\n"
        "**Try it with discounts off for a month.** Most stores recover more than\n"
        "they expect on the reminder alone.",
        (-40, -500),
        (500, 440),
        COLOR_GREEN,
    )

    wf.sticky(
        "### ⏱️ The sequence\n"
        "| When | Message |\n"
        "| --- | --- |\n"
        "| +1 hour | \"You left something behind\" |\n"
        "| +24 hours | Last reminder *(+ discount if enabled)* |\n"
        "| — | **Stop.** |\n\n"
        "**Two messages, hard cap.** A third converts almost nobody and reliably\n"
        "produces spam complaints — which damage the sending reputation that every\n"
        "other template here depends on.",
        (500, -500),
        (440, 380),
        COLOR_PURPLE,
    )

    wf.sticky(
        "### ⚠️ Honest expectations\n"
        "Recovery rates for digital products typically land in the **single digits\n"
        "to low teens**. Anyone promising 30% is selling something.\n\n"
        "At a 5% recovery rate on 100 carts of $49, that is ~$245/month from a\n"
        "template you configure once. That is the real case — not a miracle, just\n"
        "money that was otherwise left on the table.",
        (1180, 400),
        (440, 300),
        COLOR_RED,
    )

    hook = wf.webhook(
        "🛒 Cart event",
        (-660, 160),
        path="dca/cart",
        notes="Accepts abandonment events and {\"event\":\"purchased\"} to stop a sequence.",
    )

    cfg = wf.config(
        {
            "storeName": "YOUR_STORE_NAME",
            "fromEmail": "hello@yourdomain.com",
            "supportEmail": "support@yourdomain.com",
            "checkoutUrl": "https://yourdomain.com/checkout",
            "firstReminderHours": 1,
            "finalReminderHours": 24,
            "enableDiscount": False,
            "discountCode": "COMEBACK10",
            "discountText": "10% off",
            "currency": "USD",
            "minCartValue": 0,
            "historyTtlDays": 14,
        },
        (-440, 160),
        notes="enableDiscount is false on purpose. Read the green note before turning it on.",
    )

    guard = wf.guard(
        (-220, 160),
        required=["body"],
        event_id_expr="(j.body?.email ?? '') + '|' + (j.body?.cartId ?? j.body?.cart_id ?? j.body?.event ?? Date.now())",
        ttl_hours=24,
    )

    track = wf.code(
        "📝 Track the cart",
        r"""
// One open cart per email. A buyer who adds more items should not start a
// second sequence — they should update the one already running.
const cfg = $('⚙️ Config').first().json.__config;
const store = $getWorkflowStaticData('global');
store.carts = store.carts || {};

const now = Date.now();
const ttlMs = Number(cfg.historyTtlDays) * 24 * 60 * 60 * 1000;
for (const [k, c] of Object.entries(store.carts)) {
  if (now - (c.abandonedAt || 0) > ttlMs) delete store.carts[k];
}

const out = [];

for (const item of $input.all()) {
  const b = item.json.body ?? item.json;
  const email = String(b.email ?? b.customer_email ?? '').trim().toLowerCase();

  if (!email) {
    throw new Error('No email on the cart event — nothing to recover. Capture the email before checkout, not after.');
  }

  const isPurchase =
    String(b.event ?? b.type ?? '').toLowerCase().includes('purchas') ||
    b.status === 'paid' || b.completed === true;

  if (isPurchase) {
    // Stop chasing immediately. Chasing a paying customer is the fastest way to
    // turn a good sequence into a complaint.
    const had = !!store.carts[email];
    delete store.carts[email];
    out.push({ json: {
      action: 'purchased', email,
      message: had ? 'Cart recovered — sequence stopped.' : 'No open cart for this buyer.',
      __config: cfg,
    }});
    continue;
  }

  const total = Number(b.total ?? b.amount ?? b.value ?? 0);
  if (cfg.minCartValue > 0 && total < Number(cfg.minCartValue)) {
    out.push({ json: { action: 'ignored_below_min', email, total, __config: cfg }});
    continue;
  }

  const items = Array.isArray(b.items) ? b.items : [];
  const existing = store.carts[email];

  store.carts[email] = {
    email,
    name: String(b.name ?? b.customer_name ?? '').trim(),
    cartId: b.cartId ?? b.cart_id ?? null,
    total,
    currency: b.currency ?? cfg.currency,
    items: items.slice(0, 10),
    // Preserve the original timestamp so adding an item does not reset the clock.
    abandonedAt: existing?.abandonedAt ?? now,
    stage: existing?.stage ?? 0,
    updatedAt: now,
  };

  out.push({ json: {
    action: existing ? 'cart_updated' : 'cart_opened',
    email, total, __config: cfg,
  }});
}

return out;
""",
        (0, 160),
        notes="Opens/updates a cart, or closes it on purchase. Adding items never restarts the clock.",
        always_output=True,
    )

    respond = wf.respond(
        "↩️ 200 OK",
        (240, 160),
        body='={{ JSON.stringify({ ok: true, action: $json.action }) }}',
    )

    # ── The clock ───────────────────────────────────────────────────────
    sched = wf.schedule("🕐 Check carts every 30 min", (-660, 560), minutes=30)

    cfg2 = wf.code(
        "⚙️ Config (schedule side)",
        r"""
// Mirror of the main Config. n8n cannot share a node between two trigger
// branches, so these values are duplicated — keep them in sync.
const CONFIG = {
  "storeName": "YOUR_STORE_NAME",
  "fromEmail": "hello@yourdomain.com",
  "supportEmail": "support@yourdomain.com",
  "checkoutUrl": "https://yourdomain.com/checkout",
  "firstReminderHours": 1,
  "finalReminderHours": 24,
  "enableDiscount": false,
  "discountCode": "COMEBACK10",
  "discountText": "10% off",
  "currency": "USD"
};
return [{ json: { __config: CONFIG } }];
""",
        (-440, 560),
        notes="⚠️ Mirror of the main Config. Change one, change both.",
        always_output=True,
    )

    due = wf.code(
        "🔍 Find carts due a reminder",
        r"""
// Decide which carts are due, advance their stage, and retire anything that has
// had both messages. The hard cap lives here.
const cfg = $input.first().json.__config;
const store = $getWorkflowStaticData('global');
store.carts = store.carts || {};

const now = Date.now();
const HOUR = 60 * 60 * 1000;
const out = [];
let open = 0;

for (const [email, c] of Object.entries(store.carts)) {
  const ageHours = (now - c.abandonedAt) / HOUR;
  open++;

  let stage = null;
  if ((c.stage || 0) < 1 && ageHours >= Number(cfg.firstReminderHours)) stage = 1;
  else if ((c.stage || 0) < 2 && ageHours >= Number(cfg.finalReminderHours)) stage = 2;

  if (stage === null) continue;

  c.stage = stage;
  store.carts[email] = c;

  // Both messages sent — retire the cart. Two is the cap, deliberately.
  if (stage === 2) delete store.carts[email];

  const itemNames = (c.items || [])
    .map(i => (typeof i === 'string' ? i : (i.name ?? i.title ?? i.product_name ?? 'item')))
    .filter(Boolean);

  out.push({ json: {
    email, name: c.name, total: c.total, currency: c.currency,
    itemNames, itemCount: itemNames.length || 1,
    stage, isFinal: stage === 2,
    ageHours: Math.floor(ageHours),
    __config: cfg,
  }});
}

out.push({ json: { __summary: true, openCarts: open, remindersSent: out.length, __config: cfg }});
return out;
""",
        (-220, 560),
        notes="Two messages then the cart is retired. The cap is enforced here.",
        always_output=True,
    )

    is_cart = wf.if_(
        "👤 A cart to chase?",
        (0, 560),
        left="={{ $json.__summary }}",
        operator={"type": "boolean", "operation": "false", "singleValue": True},
    )

    compose = wf.code(
        "✍️ Compose the reminder",
        r"""
// Two messages, different jobs. The first assumes interruption and simply
// restores context. The second acknowledges it is the last one — and only
// mentions a discount if the seller explicitly enabled it.
return $input.all().map(i => {
  const o = i.json;
  const cfg = o.__config;

  const itemLine = o.itemNames.length
    ? o.itemNames.slice(0, 3).join(', ') + (o.itemNames.length > 3 ? ` and ${o.itemNames.length - 3} more` : '')
    : 'your items';

  const showDiscount = o.isFinal && cfg.enableDiscount === true;

  const subject = o.isFinal
    ? (showDiscount
        ? `${cfg.discountText} on the items you left behind`
        : `Last reminder about your cart`)
    : `You left something behind at ${cfg.storeName}`;

  const lead = o.isFinal
    ? `This is the last we'll mention it — <strong>${itemLine}</strong> is still waiting in your cart.`
    : `You were partway through checking out and left <strong>${itemLine}</strong> behind. Your cart is still saved.`;

  const discountBlock = showDiscount
    ? `<div style="background:#f5f5f5;border-radius:8px;padding:16px;margin:0 0 20px;text-align:center">
         <div style="color:#555;font-size:13px;margin-bottom:6px">Use this code at checkout</div>
         <div style="font-size:22px;font-weight:700;letter-spacing:1px">${cfg.discountCode}</div>
         <div style="color:#555;font-size:13px;margin-top:6px">${cfg.discountText}</div>
       </div>`
    : '';

  return { json: { ...o,
    subject,
    html:
`<div style="font-family:system-ui,-apple-system,Segoe UI,sans-serif;max-width:540px;margin:0 auto;padding:32px 24px;color:#111">
  <h2 style="margin:0 0 12px;font-size:20px">Hi${o.name ? ' ' + o.name : ' there'}</h2>
  <p style="color:#555;line-height:1.65;margin:0 0 20px">${lead}</p>
  ${discountBlock}
  <a href="${cfg.checkoutUrl}" style="display:inline-block;background:#111;color:#fff;text-decoration:none;padding:14px 28px;border-radius:8px;font-weight:600">Finish checkout${o.total ? ` — ${o.total} ${o.currency}` : ''}</a>
  <p style="color:#777;font-size:13px;margin:24px 0 0">
    Changed your mind? No problem — you won't hear from us about this again.
  </p>
  <p style="color:#777;font-size:13px;margin:8px 0 0">
    Something not working? Reply here or email <a href="mailto:${cfg.supportEmail}">${cfg.supportEmail}</a>.
  </p>
</div>`
  }};
});
""",
        (240, 460),
        notes="Discount block only renders when enableDiscount is true AND it is the final message.",
    )

    send = wf.node(
        "📧 Send the reminder",
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
        (480, 460),
        retry=True,
        max_tries=3,
        wait_ms=3000,
        on_error="continueErrorOutput",
        notes="Attach your SMTP credential.",
    )

    summary = wf.code(
        "📈 Recovery summary",
        r"""
// Runs every cycle so the seller can see the sequence working. Pair it with
// your order log to compute the actual recovery rate over a month.
const s = $input.first().json;
return [{ json: {
  reportedAt: new Date().toISOString(),
  openCarts: s.openCarts ?? 0,
  remindersSent: Math.max(0, (s.remindersSent ?? 1) - 1),
  note: 'Compare against your order log to measure the real recovery rate. Expect single digits to low teens.',
}}];
""",
        (240, 680),
        notes="Optional. Wire to Slack/Sheets if you want a running record.",
    )

    fail = wf.error_sink((720, 660), context="cart-reminder")

    wf.chain(hook, cfg, guard, track, respond)
    wf.chain(sched, cfg2, due, is_cart)
    wf.connect(is_cart, compose, out=0)
    wf.connect(is_cart, summary, out=1)
    wf.connect(compose, send)
    wf.connect(send, fail, out=1)

    return wf
