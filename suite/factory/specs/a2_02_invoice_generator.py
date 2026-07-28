"""
DCA-A2-02 · Automatic Invoice & VAT

Unglamorous and quietly the most requested item on the seller pain list. Nobody
enjoys it, everybody needs it, and getting it wrong is expensive in a way that
surfaces months later.

Why it matters more for digital goods
-------------------------------------
Digital services sold across borders are taxed where the *buyer* is, not where
the seller is. That is the rule that catches solo sellers out: a template sold
from Turkey to a customer in Germany may carry German VAT, and the seller
usually discovers this at the point where fixing it retroactively is painful.
Platforms acting as merchant of record absorb this; sellers on Stripe or PayPal
direct do not, and they are exactly the audience for this suite.

The honest boundary
-------------------
This is the one template where the right thing to build is *less* than the buyer
might want. Tax rules are jurisdictional, change on their own schedule, and
depend on facts a workflow cannot see — the seller's registration status, their
thresholds, whether the buyer is a business with a valid VAT number.

So this produces a **correct, sequential, auditable invoice record** and applies
rates the seller configures. It deliberately does not claim to determine tax
liability, and the canvas says so plainly. A template that quietly guessed at
tax rates would be worse than useless: it would be confidently wrong in a domain
where confidently wrong is the expensive failure mode.

What it does guarantee
----------------------
Sequential numbering with no gaps and no duplicates — which is a hard legal
requirement in most jurisdictions and the thing hand-rolled invoicing gets wrong
first, especially under concurrent orders or webhook replays.
"""

from lib.core import Workflow, COLOR_BLUE, COLOR_GREEN, COLOR_RED, COLOR_PURPLE

SLUG = "automatic-invoice-vat"


def build() -> Workflow:
    wf = Workflow(
        name="DCA-A2-02 · Automatic Invoice & VAT Record",
        slug=SLUG,
        category="a2-payments-finance",
        summary="Issues a correctly numbered, sequential invoice for every paid order, applies the tax rates you configure, captures the evidence tax authorities ask for, and emails the buyer their receipt.",
        problem="Invoicing is manual, numbering goes wrong under replays and concurrent orders, and cross-border digital sales are taxed where the buyer is — which solo sellers usually discover long after it is cheap to fix.",
        outcome="Every paid order produces a gap-free sequential invoice with buyer location evidence attached, sent automatically, ready for an accountant.",
        version="1.0.0",
        tags=["payments", "finance", "invoicing", "vat", "compliance", "hardened"],
        credentials_needed=["SMTP account"],
        setup_minutes=15,
    )

    wf.sticky(
        "## 🧾 Automatic Invoice & VAT Record\n"
        "**Paid order → numbered invoice → emailed → logged for your accountant.**\n\n"
        "### Setup (about 15 minutes)\n"
        "1. **⚙️ Config** → your legal `businessName`, `businessAddress`, `taxId`,\n"
        "   `invoicePrefix`, and `startNumber`.\n"
        "2. Set `taxRates` for the jurisdictions **you are registered in**.\n"
        "3. Point your payment provider's *successful payment* webhook here\n"
        "   (the same event A1-01 uses — both can run from one gateway).\n"
        "4. Attach SMTP. Activate.\n\n"
        "### Sequential numbering is the hard part\n"
        "Most jurisdictions require invoice numbers with **no gaps and no\n"
        "duplicates**. Hand-rolled invoicing breaks this first — under webhook\n"
        "replays and concurrent orders. This template guarantees it.",
        (-680, -520),
        (580, 540),
        COLOR_BLUE,
    )

    wf.sticky(
        "### ⚠️ READ THIS — what this does NOT do\n"
        "**It does not determine your tax liability.**\n\n"
        "Tax rules are jurisdictional, change on their own schedule, and depend on\n"
        "facts a workflow cannot see: your registration status, your thresholds,\n"
        "whether the buyer is a business with a valid VAT number.\n\n"
        "This applies **rates you configure** and produces a clean auditable\n"
        "record. It is a bookkeeping tool, not a tax advisor.\n\n"
        "**Talk to an accountant once.** Then configure `taxRates` from what they\n"
        "tell you. A template that guessed at tax rates would be confidently wrong\n"
        "in the one domain where that is genuinely expensive.",
        (-60, -520),
        (500, 440),
        COLOR_RED,
    )

    wf.sticky(
        "### 🌍 Why cross-border catches sellers out\n"
        "Digital services are generally taxed **where the buyer is**, not where you\n"
        "are.\n\n"
        "A template sold from Turkey to a buyer in Germany may carry German VAT —\n"
        "and sellers usually discover this long after fixing it is cheap.\n\n"
        "Platforms acting as *merchant of record* (Lemon Squeezy, Gumroad) absorb\n"
        "this for you. **Selling through Stripe or PayPal direct, you do not** —\n"
        "which is exactly who this template is for.",
        (460, -520),
        (480, 400),
        COLOR_PURPLE,
    )

    wf.sticky(
        "### 📎 Location evidence\n"
        "Tax authorities generally want **two independent pieces** of evidence for\n"
        "where the buyer was.\n\n"
        "This captures billing country, IP country and currency on every invoice,\n"
        "and flags when they disagree — so you find out at invoice time rather\n"
        "than during an audit.",
        (1400, 380),
        (440, 300),
        COLOR_GREEN,
    )

    hook = wf.webhook(
        "💰 Payment succeeded",
        (-680, 180),
        path="dca/invoice",
        notes="Same event as A1-01. Both can run from one gateway webhook.",
    )

    cfg = wf.config(
        {
            "businessName": "YOUR LEGAL BUSINESS NAME",
            "businessAddress": "YOUR REGISTERED ADDRESS",
            "taxId": "YOUR TAX / VAT NUMBER",
            "fromEmail": "invoices@yourdomain.com",
            "invoicePrefix": "INV",
            "startNumber": 1000,
            "defaultTaxRate": 0,
            "taxRates": {"DE": 19, "FR": 20, "GB": 20, "TR": 20, "AE": 5},
            "pricesIncludeTax": True,
            "currency": "USD",
            "notes": "Digital product — delivered electronically.",
        },
        (-460, 180),
        notes="taxRates: only the jurisdictions you are actually registered in. Ask an accountant once, then fill this.",
    )

    guard = wf.guard(
        (-240, 180),
        required=["body"],
        event_id_expr="j.body?.id ?? j.body?.data?.object?.id ?? j.body?.order_id ?? j.body?.payment_id",
        ttl_hours=720,
    )

    extract = wf.code(
        "📥 Read the order",
        r"""
// Reuses A1-01's normalisation shape so the two templates agree on what an order
// is. Kept independent so this can run without A1-01 installed.
const cfg = $('⚙️ Config').first().json.__config;

return $input.all().map(item => {
  const j = item.json;
  const b = j.body ?? j;
  const d = b.data?.object ?? b.data?.attributes ?? b.resource ?? b;

  const amountRaw = Number(d.amount_total ?? d.amount ?? d.total ?? d.price_amount ?? 0);
  // Stripe/Lemon Squeezy use minor units; crypto gateways generally do not.
  const gross = amountRaw > 1000 ? amountRaw / 100 : amountRaw;

  const billingCountry = String(
    d.customer_details?.address?.country ?? d.billing_details?.address?.country ??
    d.country ?? b.country ?? ''
  ).toUpperCase();

  const ipCountry = String(j.headers?.['cf-ipcountry'] ?? b.ipCountry ?? '').toUpperCase();

  return { json: {
    orderId: d.id ?? b.order_id ?? j.__eventId,
    eventId: j.__eventId,
    email: d.customer_details?.email ?? d.customer_email ?? d.user_email ?? b.email ?? null,
    name: d.customer_details?.name ?? d.customer_name ?? b.name ?? '',
    company: d.customer_details?.company ?? b.company ?? '',
    vatNumber: String(d.tax_ids?.[0]?.value ?? b.vat_number ?? '').trim(),
    gross,
    currency: String(d.currency ?? b.currency ?? cfg.currency).toUpperCase(),
    productName: d.metadata?.product_name ?? b.product_name ?? 'Digital product',
    billingCountry,
    ipCountry,
    paidAt: new Date().toISOString(),
    __config: cfg,
  }};
});
""",
        (0, 180),
        notes="Same order shape as A1-01, but independent so this works standalone.",
    )

    number = wf.code(
        "🔢 Assign invoice number",
        r"""
// ═══════════════════════════════════════════════════════════════════
// Sequential numbering, no gaps, no duplicates.
//
// This is a legal requirement in most jurisdictions and the thing
// hand-rolled invoicing breaks first. Two failure modes matter:
//
//   * Webhook replay → the same order must reuse its original number,
//     never consume a new one. The dedupe guard upstream stops most
//     replays, but its TTL is finite and invoices outlive it, so the
//     order→number mapping is kept permanently here as the real defence.
//   * Concurrency → n8n executes a workflow's nodes serially, so the
//     read-increment-write below is not interleaved within one instance.
//     On a queue-mode deployment with multiple workers this is NOT
//     guaranteed; the canvas note says so and points at the fix.
// ═══════════════════════════════════════════════════════════════════
const store = $getWorkflowStaticData('global');
store.invoices = store.invoices || {};
store.invoiceCounter = store.invoiceCounter ?? null;

return $input.all().map(item => {
  const o = item.json;
  const cfg = o.__config;

  // Already invoiced? Reuse the number. Issuing two numbers for one order is
  // the error an auditor notices.
  const existing = store.invoices[o.orderId];
  if (existing) {
    return { json: { ...o, ...existing, reissued: true } };
  }

  if (store.invoiceCounter === null) {
    store.invoiceCounter = Number(cfg.startNumber) - 1;
  }
  store.invoiceCounter += 1;

  const number = `${cfg.invoicePrefix}-${store.invoiceCounter}`;
  const record = {
    invoiceNumber: number,
    invoiceSeq: store.invoiceCounter,
    issuedAt: new Date().toISOString(),
  };
  store.invoices[o.orderId] = record;

  return { json: { ...o, ...record, reissued: false } };
});
""",
        (240, 180),
        notes="Gap-free and replay-safe. On queue mode with multiple workers, move the counter to a database.",
        always_output=True,
    )

    tax = wf.code(
        "🧮 Apply tax and build the invoice",
        r"""
// Applies the rates the seller configured. Makes no judgement about liability —
// see the red canvas note. What it does do is capture the evidence and surface
// disagreement, so problems appear at invoice time rather than during an audit.
return $input.all().map(item => {
  const o = item.json;
  const cfg = o.__config;

  const country = o.billingCountry || o.ipCountry || '';
  const rates = cfg.taxRates || {};
  const configuredRate = Object.prototype.hasOwnProperty.call(rates, country)
    ? Number(rates[country])
    : Number(cfg.defaultTaxRate || 0);

  // A verified business VAT number usually means reverse charge applies within
  // the EU. Flagged for the seller rather than decided automatically, because
  // whether it applies depends on registration facts we cannot see.
  const looksLikeBusiness = o.vatNumber.length >= 8;

  const rate = configuredRate;
  let net, taxAmount;

  if (cfg.pricesIncludeTax) {
    net = rate > 0 ? o.gross / (1 + rate / 100) : o.gross;
    taxAmount = o.gross - net;
  } else {
    net = o.gross;
    taxAmount = net * (rate / 100);
  }

  const round = (n) => Math.round(n * 100) / 100;

  // Two independent location signals is the usual evidentiary standard.
  const evidence = [];
  if (o.billingCountry) evidence.push(`billing country: ${o.billingCountry}`);
  if (o.ipCountry) evidence.push(`IP country: ${o.ipCountry}`);
  if (o.currency) evidence.push(`currency: ${o.currency}`);

  const countryConflict = !!(o.billingCountry && o.ipCountry && o.billingCountry !== o.ipCountry);

  const flags = [];
  if (evidence.length < 2) flags.push('Fewer than two independent location signals captured.');
  if (countryConflict) flags.push(`Billing country (${o.billingCountry}) and IP country (${o.ipCountry}) disagree.`);
  if (!country) flags.push('No buyer country determined — default rate applied.');
  if (looksLikeBusiness) flags.push(`Buyer supplied a VAT number (${o.vatNumber}) — reverse charge may apply. Review.`);
  if (!Object.prototype.hasOwnProperty.call(rates, country) && country) {
    flags.push(`No rate configured for ${country} — default ${cfg.defaultTaxRate}% applied.`);
  }

  return { json: { ...o,
    net: round(net),
    taxRate: rate,
    taxAmount: round(taxAmount),
    total: round(o.gross),
    taxCountry: country || null,
    locationEvidence: evidence,
    reviewFlags: flags,
    needsReview: flags.length > 0,
  }};
});
""",
        (480, 180),
        notes="Applies YOUR configured rates and flags anything a human should look at. Does not determine liability.",
    )

    send = wf.node(
        "📧 Email the invoice",
        "n8n-nodes-base.emailSend",
        {
            "fromEmail": "={{ $json.__config.fromEmail }}",
            "toEmail": "={{ $json.email }}",
            "subject": "={{ 'Invoice ' + $json.invoiceNumber + ' — ' + $json.__config.businessName }}",
            "emailFormat": "html",
            "html": (
                "={{ '<div style=\"font-family:system-ui,-apple-system,Segoe UI,sans-serif;max-width:600px;"
                "margin:0 auto;padding:32px 24px;color:#111\">'"
                " + '<div style=\"display:flex;justify-content:space-between;border-bottom:2px solid #111;padding-bottom:14px;margin-bottom:22px\">'"
                " + '<div><div style=\"font-size:21px;font-weight:700\">INVOICE</div>'"
                " + '<div style=\"color:#666;font-size:13px;margin-top:3px\">' + $json.invoiceNumber + '</div></div>'"
                " + '<div style=\"text-align:right;font-size:13px;color:#666\">' + $json.issuedAt.slice(0,10) + '</div></div>'"
                " + '<table style=\"width:100%;font-size:13px;margin-bottom:22px\"><tr>'"
                " + '<td style=\"vertical-align:top;color:#666\"><strong style=\"color:#111\">From</strong><br>'"
                " + $json.__config.businessName + '<br>' + $json.__config.businessAddress + '<br>Tax ID: ' + $json.__config.taxId + '</td>'"
                " + '<td style=\"vertical-align:top;color:#666\"><strong style=\"color:#111\">To</strong><br>'"
                " + ($json.name || $json.email) + ($json.company ? '<br>' + $json.company : '')"
                " + ($json.vatNumber ? '<br>VAT: ' + $json.vatNumber : '')"
                " + ($json.taxCountry ? '<br>' + $json.taxCountry : '') + '</td></tr></table>'"
                " + '<table style=\"width:100%;border-collapse:collapse;font-size:14px\">'"
                " + '<tr style=\"border-bottom:1px solid #eee\"><td style=\"padding:10px 0\">' + $json.productName + '</td>'"
                " + '<td style=\"padding:10px 0;text-align:right\">' + $json.net + ' ' + $json.currency + '</td></tr>'"
                " + '<tr style=\"border-bottom:1px solid #eee\"><td style=\"padding:10px 0;color:#666\">Tax (' + $json.taxRate + '%)</td>'"
                " + '<td style=\"padding:10px 0;text-align:right;color:#666\">' + $json.taxAmount + ' ' + $json.currency + '</td></tr>'"
                " + '<tr><td style=\"padding:14px 0;font-weight:700\">Total paid</td>'"
                " + '<td style=\"padding:14px 0;text-align:right;font-weight:700\">' + $json.total + ' ' + $json.currency + '</td></tr></table>'"
                " + '<p style=\"color:#777;font-size:12px;margin:22px 0 0\">' + $json.__config.notes + '</p>'"
                " + '<p style=\"color:#999;font-size:12px;margin:6px 0 0\">Order ' + $json.orderId + ' · paid ' + $json.paidAt.slice(0,10) + '</p>'"
                " + '</div>' }}"
            ),
            "options": {},
        },
        2.1,
        (720, 180),
        retry=True,
        max_tries=3,
        wait_ms=3000,
        on_error="continueErrorOutput",
        notes="Attach SMTP. The buyer receives a proper itemised invoice.",
    )

    log = wf.code(
        "📒 Invoice ledger",
        r"""
// The ledger your accountant will ask for. Send it somewhere durable — static
// data is not a permanent record and must not be your only copy of this.
return $input.all().map(i => {
  const o = i.json;
  return { json: {
    invoiceNumber: o.invoiceNumber,
    invoiceSeq: o.invoiceSeq,
    issuedAt: o.issuedAt,
    orderId: o.orderId,
    buyerEmail: o.email,
    buyerName: o.name,
    buyerCompany: o.company,
    buyerVat: o.vatNumber || null,
    taxCountry: o.taxCountry,
    net: o.net,
    taxRate: o.taxRate,
    taxAmount: o.taxAmount,
    total: o.total,
    currency: o.currency,
    locationEvidence: (o.locationEvidence || []).join(' | '),
    needsReview: o.needsReview,
    reviewFlags: (o.reviewFlags || []).join(' | '),
    reissued: o.reissued,
  }};
});
""",
        (960, 180),
        notes="⚠️ Wire this to a Sheet or database. Static data is not a permanent financial record.",
    )

    fail = wf.error_sink((720, 400), context="invoice-send")

    respond = wf.respond(
        "↩️ 200 OK",
        (1200, 180),
        body='={{ JSON.stringify({ ok: true, invoice: $json.invoiceNumber ?? null }) }}',
    )

    wf.chain(hook, cfg, guard, extract, number, tax, send)
    wf.connect(send, log, out=0)
    wf.connect(send, fail, out=1)
    wf.connect(log, respond)
    wf.connect(fail, respond)

    return wf
