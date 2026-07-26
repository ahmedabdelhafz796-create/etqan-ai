/**
 * run.mjs — behavioural tests. Run the real templates and assert what they do.
 *
 *     node factory/harness/run.mjs
 *
 * Every scenario here is a failure a real buyer could experience. Structural
 * validation cannot catch any of them, because a workflow can be perfectly
 * well-formed and still deliver a product to someone who has not paid.
 */

import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import crypto from 'node:crypto';
import { execute } from './engine.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const T = join(HERE, '..', '..', 'templates');

const load = (p) => JSON.parse(readFileSync(join(T, p), 'utf8'));

const WEBHOOK_SECRET = 'test_webhook_secret_value';
const LINK_SECRET = 'test_link_signing_secret_value';

let passed = 0, failed = 0;
const failures = [];

function check(name, fn) {
  try {
    fn();
    passed++;
    console.log(`  ✅ ${name}`);
  } catch (e) {
    failed++;
    failures.push({ name, message: e.message });
    console.log(`  ❌ ${name}\n       ${e.message}`);
  }
}

function assert(cond, msg) {
  if (!cond) throw new Error(msg);
}

function section(title) {
  console.log(`\n${title}\n${'─'.repeat(64)}`);
}

// ── helpers ─────────────────────────────────────────────────────────────
function stripeEvent({ id = 'evt_1', status = 'paid', amount = 4900, email = 'buyer@example.com' } = {}) {
  const body = {
    id,
    object: 'event',
    data: {
      object: {
        id: 'cs_test_1',
        payment_status: status,
        amount_total: amount,
        currency: 'usd',
        customer_details: { email, name: 'Test Buyer' },
        metadata: { product_id: 'book-01', product_name: 'Test Product' },
      },
    },
  };
  const sig = crypto.createHmac('sha256', WEBHOOK_SECRET).update(JSON.stringify(body)).digest('hex');
  return { body, headers: { 'stripe-signature': `t=1,v1=${sig}` } };
}

const deliverySecrets = {
  '🔏 Verify signature': WEBHOOK_SECRET,
  '✍️ Sign download link': LINK_SECRET,
};

// ═══════════════════════════════════════════════════════════════════════
section('DCA-A1-01 · Instant Digital Delivery');

const delivery = load('a1-delivery/instant-digital-delivery/workflow.json');

check('a paid order sends exactly one email containing a signed link', () => {
  const r = execute(delivery, { trigger: stripeEvent(), secrets: deliverySecrets, staticData: {} });
  assert(r.effects.errors.length === 0, `unexpected errors: ${JSON.stringify(r.effects.errors)}`);
  assert(r.effects.emails.length === 1, `expected 1 email, got ${r.effects.emails.length}`);
  const mail = r.effects.emails[0];
  assert(mail.to === 'buyer@example.com', `wrong recipient: ${mail.to}`);
  assert(/sig=[a-f0-9]{64}/.test(mail.html), 'email contains no signed download link');
  assert(/expires=\d{10}/.test(mail.html), 'link carries no expiry');
});

check('a replayed webhook does NOT deliver a second time', () => {
  const shared = {};
  const evt = stripeEvent({ id: 'evt_replay' });
  const first = execute(delivery, { trigger: evt, secrets: deliverySecrets, staticData: shared });
  const second = execute(delivery, { trigger: evt, secrets: deliverySecrets, staticData: shared });
  assert(first.effects.emails.length === 1, 'first delivery should send one email');
  assert(second.effects.emails.length === 0,
    `replay sent ${second.effects.emails.length} duplicate email(s) — idempotency is broken`);
});

check('a pending payment delivers nothing', () => {
  const r = execute(delivery, {
    trigger: stripeEvent({ id: 'evt_pending', status: 'unpaid' }),
    secrets: deliverySecrets, staticData: {},
  });
  assert(r.effects.emails.length === 0, 'product was delivered on an unpaid order');
  assert(r.executed.some((e) => e.node.includes('Hold')), 'unpaid order did not reach the hold branch');
});

check('a forged signature is rejected and delivers nothing', () => {
  const evt = stripeEvent({ id: 'evt_forged' });
  evt.headers['stripe-signature'] = 't=1,v1=' + 'f'.repeat(64);
  const r = execute(delivery, { trigger: evt, secrets: deliverySecrets, staticData: {} });
  assert(r.effects.emails.length === 0, 'a forged webhook was delivered — endpoint is forgeable');
  assert(r.effects.errors.length > 0, 'forged signature produced no error');
});

check('an under-paid order is refused', () => {
  const r = execute(delivery, {
    trigger: stripeEvent({ id: 'evt_cheap', amount: 100 }),
    secrets: deliverySecrets, staticData: {},
    configOverride: {
      storeName: 'T', fromEmail: 'a@b.c', supportEmail: 's@b.c', provider: 'stripe',
      downloadBaseUrl: 'https://x.test/d', linkTtlHours: 48, maxDownloads: 5,
      minAmount: 20, currencyAllowList: [], testMode: false,
    },
  });
  assert(r.effects.emails.length === 0, 'an order below minAmount was still delivered');
});

check('two different orders both deliver (dedupe is not over-eager)', () => {
  const shared = {};
  const a = execute(delivery, { trigger: stripeEvent({ id: 'evt_a' }), secrets: deliverySecrets, staticData: shared });
  const b = execute(delivery, { trigger: stripeEvent({ id: 'evt_b' }), secrets: deliverySecrets, staticData: shared });
  assert(a.effects.emails.length === 1 && b.effects.emails.length === 1,
    'distinct orders were incorrectly treated as duplicates');
});

// ═══════════════════════════════════════════════════════════════════════
section('DCA-A1-02 · Secure Download Endpoint');

const download = load('a1-delivery/secure-download-endpoint/workflow.json');
const dlSecrets = { '🔏 Recompute signature': LINK_SECRET };

function signedQuery({ order = 'o1', email = 'buyer@example.com', product = 'book-01',
                       expires = Math.floor(Date.now() / 1000) + 3600, max = 5 } = {}) {
  const payload = [order, email, product, String(expires), String(max)].join('|');
  const sig = crypto.createHmac('sha256', LINK_SECRET).update(payload).digest('hex');
  return { query: { order, email, product, expires: String(expires), max: String(max), sig }, headers: {} };
}

check('a valid link redirects to the file', () => {
  const r = execute(download, { trigger: signedQuery(), secrets: dlSecrets, staticData: {} });
  const redirect = r.effects.responses.find((x) => x.with === 'redirect');
  assert(redirect, 'no redirect was issued for a valid link');
  assert(redirect.redirect.includes('http'), `redirect target looks wrong: ${redirect.redirect}`);
});

check('a tampered signature is refused', () => {
  const q = signedQuery();
  q.query.sig = 'a'.repeat(64);
  const r = execute(download, { trigger: q, secrets: dlSecrets, staticData: {} });
  assert(!r.effects.responses.some((x) => x.with === 'redirect'), 'a tampered link was served');
});

check('changing the product in the URL is refused (signature covers it)', () => {
  const q = signedQuery({ product: 'book-01' });
  q.query.product = 'expensive-course';   // escalate to a different product
  const r = execute(download, { trigger: q, secrets: dlSecrets, staticData: {} });
  assert(!r.effects.responses.some((x) => x.with === 'redirect'),
    'a buyer could swap the product id and get a different file');
});

check('an expired link is refused with a dated explanation', () => {
  const q = signedQuery({ expires: Math.floor(Date.now() / 1000) - 3600 });
  const r = execute(download, { trigger: q, secrets: dlSecrets, staticData: {} });
  assert(!r.effects.responses.some((x) => x.with === 'redirect'), 'an expired link was served');
  const page = r.effects.responses.find((x) => x.with === 'text');
  assert(page && /expired on/i.test(page.body), 'refusal page does not say when the link expired');
});

check('the download cap is enforced', () => {
  const shared = {};
  const q = signedQuery({ order: 'o-cap', max: 2 });
  const runs = [1, 2, 3].map(() => execute(download, { trigger: q, secrets: dlSecrets, staticData: shared }));
  const served = runs.filter((r) => r.effects.responses.some((x) => x.with === 'redirect')).length;
  assert(served === 2, `cap of 2 allowed ${served} downloads`);
});

check('an unknown product tells the buyer what to do', () => {
  const q = signedQuery({ product: 'does-not-exist' });
  const r = execute(download, { trigger: q, secrets: dlSecrets, staticData: {},
    configOverride: {
      fileUrlMap: { 'book-01': 'https://x.test/f.pdf' },   // no default
      graceHours: 0, supportEmail: 'help@x.test', storeName: 'T',
      resendUrl: 'https://x.test/r', abuseIpThreshold: 8, historyTtlHours: 168,
    } });
  const page = r.effects.responses.find((x) => x.with === 'text');
  assert(page && /help@x\.test/.test(page.body), 'refusal page gives the buyer no way forward');
});

// ═══════════════════════════════════════════════════════════════════════
section('DCA-A3-01 · Pre-Payment Fraud Scoring');

const fraud = load('a3-fraud-security/pre-payment-fraud-scoring/workflow.json');

function order(o) {
  return { body: { orderId: 'f1', email: 'real.buyer@company.com', name: 'Real Buyer',
                   amount: 49, currency: 'USD', country: 'US', ipCountry: 'US', ...o },
           headers: { 'user-agent': 'Mozilla/5.0', 'x-forwarded-for': o?.ip ?? '1.2.3.4' } };
}

check('a clean order scores low and is allowed', () => {
  const r = execute(fraud, { trigger: order(), staticData: {} });
  const out = r.outputs['📒 Audit log'][0].json;
  assert(out.action === 'deliver', `clean order was not allowed: ${out.action}`);
  assert(out.riskScore < 45, `clean order scored too high: ${out.riskScore}`);
});

check('a disposable-email order accumulates risk with stated reasons', () => {
  const r = execute(fraud, { trigger: order({ orderId: 'f2', email: 'x9k2m4p8q1@mailinator.com' }), staticData: {} });
  const scored = r.outputs['🧮 Score the risk'][0].json;
  assert(scored.riskScore >= 35, `disposable domain barely scored: ${scored.riskScore}`);
  assert(scored.riskReasons.some((x) => /disposable/i.test(x.reason)), 'no reason mentions the disposable domain');
});

check('geo mismatch plus disposable mail reaches the review threshold', () => {
  const r = execute(fraud, {
    trigger: order({ orderId: 'f3', email: 'zz88qq11xx@guerrillamail.com', country: 'US', ipCountry: 'NG' }),
    staticData: {},
  });
  const s = r.outputs['🧮 Score the risk'][0].json;
  assert(s.wouldHaveBeen !== 'allow', `combined signals still resolved to allow (score ${s.riskScore})`);
});

check('shadow mode reports risk but never blocks', () => {
  const r = execute(fraud, {
    trigger: order({ orderId: 'f4', email: 'aa11bb22cc@mailinator.com', country: 'US', ipCountry: 'RU', amount: 5000 }),
    staticData: {},
  });
  const s = r.outputs['🧮 Score the risk'][0].json;
  assert(s.shadowMode === true, 'shadow mode should default on');
  assert(s.decision === 'allow', 'shadow mode must not enforce');
  assert(s.wouldHaveBeen === 'block', `high-risk order should have been marked block, got ${s.wouldHaveBeen}`);
});

check('enforcing mode actually blocks a high-risk order', () => {
  const r = execute(fraud, {
    trigger: order({ orderId: 'f5', email: 'aa11bb22cc@mailinator.com', country: 'US', ipCountry: 'RU', amount: 5000 }),
    staticData: {},
    configOverride: {
      reviewAt: 45, blockAt: 80, shadowMode: false, velocityWindowMinutes: 60,
      maxOrdersPerEmail: 3, maxOrdersPerIp: 5, typicalOrderAmount: 49,
      amountAnomalyMultiplier: 4, highRiskCountries: ['RU'], trustedEmails: [],
      trustedDomains: [], historyTtlHours: 24,
    },
  });
  const out = r.outputs['📒 Audit log'][0].json;
  assert(out.action === 'block', `high-risk order was not blocked: ${out.action}`);
});

check('velocity catches repeated orders from one email', () => {
  const shared = {};
  let last;
  for (let i = 0; i < 5; i++) {
    last = execute(fraud, {
      trigger: order({ orderId: `v${i}`, email: 'burst@example.com' }),
      staticData: shared,
    });
  }
  const s = last.outputs['🧮 Score the risk'][0].json;
  assert(s.riskReasons.some((x) => /orders from this email/i.test(x.reason)),
    'rapid repeat orders raised no velocity signal');
});

check('an allow-listed buyer bypasses scoring entirely', () => {
  const r = execute(fraud, {
    trigger: order({ orderId: 'f6', email: 'vip@bigclient.com' }),
    staticData: {},
    configOverride: {
      reviewAt: 45, blockAt: 80, shadowMode: false, velocityWindowMinutes: 60,
      maxOrdersPerEmail: 3, maxOrdersPerIp: 5, typicalOrderAmount: 49,
      amountAnomalyMultiplier: 4, highRiskCountries: [],
      trustedEmails: ['vip@bigclient.com'], trustedDomains: [], historyTtlHours: 24,
    },
  });
  const s = r.outputs['🧮 Score the risk'][0].json;
  assert(s.riskScore === 0 && s.decision === 'allow', 'allow-list did not short-circuit scoring');
});

// ═══════════════════════════════════════════════════════════════════════
section('Cross-template contract');

check('a link minted by A1-01 verifies in A1-02 (shared secret + payload order)', () => {
  const d = execute(delivery, { trigger: stripeEvent({ id: 'evt_x' }), secrets: deliverySecrets, staticData: {} });
  const url = d.effects.emails[0].html.match(/href="([^"]+download[^"]*)"/)?.[1];
  assert(url, 'no download URL found in the delivery email');

  const params = Object.fromEntries(new URL(url).searchParams);
  const r = execute(download, { trigger: { query: params, headers: {} }, secrets: dlSecrets, staticData: {} });
  assert(r.effects.responses.some((x) => x.with === 'redirect'),
    'a link produced by A1-01 was rejected by A1-02 — the two templates disagree');
});

// ═══════════════════════════════════════════════════════════════════════
section('DCA-B4-02 · Failed Payment Recovery');

const dunning = load('b4-saas-subscriptions/failed-payment-recovery/workflow.json');

const failedPayment = (o = {}) => ({
  body: { id: 'inv_1', email: 'sub@example.com', amount: 5000, currency: 'USD', name: 'Sub Buyer', ...o },
  headers: {},
});

check('a failed payment opens a case and sends the first notice', () => {
  const r = execute(dunning, { trigger: failedPayment(), staticData: {} });
  assert(r.effects.emails.length === 1, `expected 1 first notice, got ${r.effects.emails.length}`);
  const mail = r.effects.emails[0];
  assert(mail.to === 'sub@example.com', `first notice went to the wrong address: ${mail.to}`);
  // The thing that makes the email useful is the recovery action, not any
  // particular wording — assert the link, not the copy.
  assert(/href="[^"]*billing/i.test(mail.html), 'first notice contains no update-payment link');
  assert(/5000|50/.test(mail.html), 'first notice does not state the amount owed');
});

check('a second failure does NOT restart the sequence', () => {
  const shared = {};
  const a = execute(dunning, { trigger: failedPayment({ id: 'inv_a' }), staticData: shared });
  const b = execute(dunning, { trigger: failedPayment({ id: 'inv_b' }), staticData: shared });
  assert(a.effects.emails.length === 1, 'first failure should send one notice');
  assert(b.effects.emails.length === 0,
    'a repeat failure re-sent the day-one email — the customer would be spammed');
});

check('a recovered payment closes the case', () => {
  const shared = {};
  execute(dunning, { trigger: failedPayment({ id: 'inv_r' }), staticData: shared });
  const r = execute(dunning, { trigger: failedPayment({ id: 'inv_r2', event: 'recovered' }), staticData: shared });
  assert(r.effects.emails.length === 0, 'a recovered customer was emailed again');
  assert(shared.cases['sub@example.com'].recovered === true, 'case was not marked recovered');
});

check('a payment-failed event with no email fails loudly', () => {
  const r = execute(dunning, { trigger: { body: { id: 'x', amount: 100 }, headers: {} }, staticData: {} });
  assert(r.effects.errors.length > 0, 'a payload with no customer email passed silently');
});

// ═══════════════════════════════════════════════════════════════════════
section('DCA-A5-01 · Cart Abandonment Recovery');

const cart = load('a5-marketing-revenue/cart-abandonment-recovery/workflow.json');

const cartEvent = (o = {}) => ({
  body: { email: 'shopper@example.com', cartId: 'c1', total: 49, currency: 'USD', items: [{ name: 'Course' }], ...o },
  headers: {},
});

check('an abandoned cart is tracked', () => {
  const shared = {};
  const r = execute(cart, { trigger: cartEvent(), staticData: shared });
  assert(shared.carts['shopper@example.com'], 'cart was not recorded');
  assert(r.outputs['📝 Track the cart'][0].json.action === 'cart_opened', 'cart was not opened');
});

check('a purchase deletes the cart so the buyer is never chased', () => {
  const shared = {};
  execute(cart, { trigger: cartEvent(), staticData: shared });
  execute(cart, { trigger: cartEvent({ cartId: 'c2', event: 'purchased' }), staticData: shared });
  assert(!shared.carts['shopper@example.com'],
    'a paying customer still has an open cart and would be chased for it');
});

check('adding an item does not restart the abandonment clock', () => {
  const shared = {};
  execute(cart, { trigger: cartEvent(), staticData: shared });
  const firstAt = shared.carts['shopper@example.com'].abandonedAt;
  shared.carts['shopper@example.com'].abandonedAt = firstAt - 3_600_000;  // pretend an hour passed
  const aged = shared.carts['shopper@example.com'].abandonedAt;
  execute(cart, { trigger: cartEvent({ cartId: 'c1b', total: 98 }), staticData: shared });
  assert(shared.carts['shopper@example.com'].abandonedAt === aged,
    'adding an item reset the clock — the reminder would never fire');
});

// ═══════════════════════════════════════════════════════════════════════
section('DCA-B1-01 · AI Support Agent');

const agent = load('b1-ai-agents/ai-customer-support-agent/workflow.json');

const ask = (message, o = {}) => ({
  body: { email: 'cust@example.com', name: 'Cust', subject: 'Question', message, ...o },
  headers: {},
});

check('a refund question is escalated without ever calling the model', () => {
  const r = execute(agent, { trigger: ask('I want a refund please'), staticData: {} });
  assert(r.effects.httpCalls.length === 0,
    'a sensitive request reached the model — it must be caught by deterministic triage first');
  assert(r.executed.some((e) => e.node.includes('Hand to a human')), 'refund request was not escalated');
});

check('an angry customer is escalated, not answered by AI', () => {
  const r = execute(agent, { trigger: ask('THIS IS ABSOLUTELY UNACCEPTABLE AND TERRIBLE') , staticData: {} });
  assert(r.executed.some((e) => e.node.includes('Hand to a human')), 'an upset customer was not escalated');
});

check('a routine question does reach the model', () => {
  const r = execute(agent, { trigger: ask('What format is the book in?'), staticData: {} });
  assert(r.effects.httpCalls.length === 1, 'a routine question did not reach the model');
});

check('a request missing its message fails loudly', () => {
  const r = execute(agent, { trigger: { body: { email: 'a@b.c' }, headers: {} }, staticData: {} });
  assert(r.effects.errors.length > 0, 'a request with no message passed silently');
});

// ═══════════════════════════════════════════════════════════════════════
section('DCA-A3-02 · Chargeback Early Warning');

const cb = load('a3-fraud-security/chargeback-early-warning/workflow.json');

const alertEvt = (o = {}) => ({
  body: { id: 'evt_cb_1', type: 'charge.dispute.created',
          data: { object: { id: 'ch_1', amount: 4900, currency: 'usd', reason: 'product_not_received',
                            customer_email: 'buyer@example.com', metadata: { order_id: 'o-99' } } }, ...o },
  headers: {},
});

check('an early fraud warning recommends refunding now', () => {
  const r = execute(cb, { trigger: alertEvt({ type: 'radar.early_fraud_warning.created' }), staticData: {} });
  const out = r.outputs['📁 Build evidence pack'][0].json;
  assert(out.kind === 'early_warning', `classified as ${out.kind}, expected early_warning`);
  assert(out.recommendation.action === 'refund_now',
    `early warning recommended "${out.recommendation.action}" — the whole point is to act inside this window`);
});

check('an early warning is NOT counted in the chargeback ratio', () => {
  const shared = {};
  const r = execute(cb, { trigger: alertEvt({ id: 'evt_ew', type: 'radar.early_fraud_warning.created' }), staticData: shared });
  const out = r.outputs['📈 Track the chargeback ratio'][0].json;
  assert(out.disputes30d === 0,
    'an early warning was counted as a chargeback — that punishes the seller for acting correctly');
});

check('a real dispute IS counted and produces a deadline', () => {
  const r = execute(cb, { trigger: alertEvt(), staticData: {} });
  const out = r.outputs['📈 Track the chargeback ratio'][0].json;
  assert(out.kind === 'dispute', `classified as ${out.kind}`);
  assert(out.disputes30d === 1, 'a formal dispute was not counted in the ratio');
  assert(out.hoursToRespond > 0, 'no response deadline was computed');
});

check('a fightable reason recommends fighting with evidence', () => {
  const r = execute(cb, { trigger: alertEvt(), staticData: {} });
  const out = r.outputs['📁 Build evidence pack'][0].json;
  assert(out.recommendation.action === 'fight_with_evidence',
    `product_not_received should be fightable, got "${out.recommendation.action}"`);
  assert(out.evidencePack.refundPolicyUrl, 'evidence pack has no terms URL');
});

check('crossing the ratio threshold raises a critical status', () => {
  const shared = {};
  let last;
  // 100 monthly orders, critical at 0.75% → the 1st dispute already crosses it.
  for (let i = 0; i < 2; i++) {
    last = execute(cb, { trigger: alertEvt({ id: `evt_r${i}` }), staticData: shared });
  }
  const out = last.outputs['📈 Track the chargeback ratio'][0].json;
  assert(out.ratioStatus === 'critical',
    `ratio ${out.chargebackRate}% reported status "${out.ratioStatus}" — account-closing risk must escalate`);
});

check('the evidence pack never fabricates values', () => {
  const r = execute(cb, { trigger: alertEvt(), staticData: {} });
  const pack = r.outputs['📁 Build evidence pack'][0].json.evidencePack;
  assert(/⚠️ FILL/.test(pack.downloadIp),
    'evidence fields were invented instead of flagged for the seller to fill');
});

// ═══════════════════════════════════════════════════════════════════════
section('DCA-SYS-00 · Central Error Hub');

const hub = load('sys-spine/central-error-hub/workflow.json');

const failure = (o = {}) => ({
  workflow: { name: 'DCA-A1-01 · Instant Digital Delivery', id: 'w1' },
  execution: { id: 'e1', lastNodeExecuted: '📧 Send the product',
               error: { message: 'Invalid login: 535 Authentication failed' } },
  ...o,
});

check('a delivery failure is ranked critical', () => {
  const r = execute(hub, { trigger: failure(), staticData: {} });
  const out = r.outputs['🔎 Explain the failure'][0].json;
  assert(out.severity === 'critical', `delivery failure ranked "${out.severity}" — a stuck paying customer is the top priority`);
});

check('an SMTP auth error is explained in plain language', () => {
  const r = execute(hub, { trigger: failure(), staticData: {} });
  const out = r.outputs['🔎 Explain the failure'][0].json;
  assert(/SMTP key|password/i.test(out.fix), `fix text is not actionable: ${out.fix}`);
  assert(!/ECONN|535/.test(out.cause), 'cause text just repeats the raw error');
});

check('the SSL/port mismatch we actually hit is explained', () => {
  const r = execute(hub, {
    trigger: failure({ execution: { id: 'e2', lastNodeExecuted: 'x',
      error: { message: 'SSL routines:tls_validate_record_header:wrong version number' } } }),
    staticData: {},
  });
  const out = r.outputs['🔎 Explain the failure'][0].json;
  assert(/587|465/.test(out.fix), 'the port/SSL mismatch has no concrete fix');
});

check('a repeat failure is suppressed instead of paging again', () => {
  const shared = {};
  const a = execute(hub, { trigger: failure(), staticData: shared });
  const b = execute(hub, { trigger: failure(), staticData: shared });
  assert(a.effects.emails.length === 1, 'first failure should alert');
  assert(b.effects.emails.length === 0,
    'an identical repeat alerted again — a storm would bury every other signal');
});

check('a different failure still alerts during another one\'s storm', () => {
  const shared = {};
  execute(hub, { trigger: failure(), staticData: shared });
  const other = execute(hub, {
    trigger: failure({ execution: { id: 'e3', lastNodeExecuted: '🧠 Ask the model',
      error: { message: '429 rate limit exceeded' } } }),
    staticData: shared,
  });
  assert(other.effects.emails.length === 1,
    'suppression is too broad — a distinct failure was silenced by an unrelated storm');
});

check('a logging failure is ranked low and does not alert', () => {
  const r = execute(hub, {
    trigger: failure({
      workflow: { name: 'DCA-SYS-01 · Daily Business Pulse', id: 'w2' },
      execution: { id: 'e4', lastNodeExecuted: '📒 Pulse archive',
                   error: { message: 'sheet write failed' } },
    }),
    staticData: {},
  });
  const out = r.outputs['🔎 Explain the failure'][0].json;
  assert(out.severity === 'low', `analytics failure ranked "${out.severity}"`);
  assert(r.effects.emails.length === 0, 'a low-severity failure paged the seller');
});

// ═══════════════════════════════════════════════════════════════════════
section('DCA-SYS-01 · Daily Business Pulse');

const pulse = load('sys-spine/daily-business-pulse/workflow.json');

check('missing templates report as "not installed", never as zero', () => {
  const r = execute(pulse, { trigger: {}, staticData: {} });
  const text = r.outputs['✍️ Write the pulse'][0].json.pulseText;
  assert(/NOT INSTALLED/.test(text), 'a fresh install did not flag missing templates');
  assert(/not zero activity/i.test(text), 'the zero-vs-no-data distinction is not explained');
});

check('recovered revenue is reported when dunning has data', () => {
  const shared = { cases: { 'a@b.c': { recovered: true, recoveredAt: Date.now(), amount: 50 } } };
  const r = execute(pulse, { trigger: {}, staticData: shared });
  const text = r.outputs['✍️ Write the pulse'][0].json.pulseText;
  assert(/MONEY RECOVERED/.test(text), 'recovered revenue was not surfaced');
  assert(/50/.test(text), 'the recovered amount is missing');
});

check('action items come before good news', () => {
  const shared = {
    errors: { k1: { firstAt: Date.now(), lastAt: Date.now(), count: 3 } },
    cases: { 'a@b.c': { recovered: true, recoveredAt: Date.now(), amount: 50 } },
  };
  const r = execute(pulse, { trigger: {}, staticData: shared });
  const text = r.outputs['✍️ Write the pulse'][0].json.pulseText;
  assert(text.indexOf('NEEDS YOU TODAY') < text.indexOf('MONEY RECOVERED'),
    'good news was placed above the items needing action');
});

check('a leaked download link surfaces as an action item', () => {
  const shared = { downloads: { 'o1|p1': { count: 20, ips: Array.from({ length: 12 }, (_, i) => `1.1.1.${i}`), firstAt: Date.now() } } };
  const r = execute(pulse, { trigger: {}, staticData: shared });
  const text = r.outputs['✍️ Write the pulse'][0].json.pulseText;
  assert(/shared publicly/i.test(text), 'a link used from 12 IPs raised no leak warning');
});

// ═══════════════════════════════════════════════════════════════════════
section('DCA-B1-02 · AI Lead Qualifier');

const lead = load('b1-ai-agents/ai-lead-qualifier/workflow.json');

const enquiry = (message, o = {}) => ({
  body: { email: 'buyer@acmecorp.com', name: 'Real Buyer', message, ...o },
  headers: {},
});

check('spam is discarded before any model call', () => {
  const r = execute(lead, { trigger: enquiry('We offer SEO services and backlink packages'), staticData: {} });
  assert(r.effects.httpCalls.length === 0, 'spam reached the model — wasted spend');
  const out = r.outputs['📒 Lead log'][0].json;
  assert(out.action === 'discarded_spam', `spam was routed as "${out.action}"`);
});

check('discarded spam is still logged for audit', () => {
  const r = execute(lead, { trigger: enquiry('guest post opportunity'), staticData: {} });
  const logged = r.outputs['🗑️ Log the spam'][0].json;
  assert(logged.reason, 'spam was dropped with no recorded reason');
  assert(logged.messagePreview, 'no message preview kept — a real lead here would be unrecoverable');
});

check('a genuine enquiry reaches the model', () => {
  const r = execute(lead, { trigger: enquiry('What is your pricing? We need this urgently for our team.') });
  assert(r.effects.httpCalls.length === 1, 'a real enquiry did not reach the model');
});

check('a business email and buying language score well before the model runs', () => {
  const r = execute(lead, { trigger: enquiry('What does it cost? We have budget and need a demo this week.', { company: 'Acme', phone: '+201234' }) });
  const pre = r.outputs['🧱 Deterministic pre-score'][0].json;
  assert(pre.baseScore >= 60, `strong lead pre-scored only ${pre.baseScore}`);
  assert(pre.baseSignals.some((s) => /Business email/i.test(s.why)), 'business domain was not credited');
});

check('a model outage does NOT lose the lead', () => {
  // Simulate the model returning something unparseable.
  const r = execute(lead, { trigger: enquiry('We want to buy, what is the price? Urgent, we have budget.', { company: 'Acme', phone: '+2012' }) });
  const combined = r.outputs['🧮 Combine and tier']?.[0]?.json;
  assert(combined, 'combine node produced nothing');
  assert(combined.modelUsed === false, 'test expected the mock model response to be unparseable');
  assert(combined.score > 0, 'lead lost its score when the model failed');
  assert(combined.tier !== 'spam', 'a model failure downgraded a real lead to spam');
});

check('a no-budget student enquiry is nurtured, never discarded', () => {
  const r = execute(lead, { trigger: enquiry('I am a student with no budget, can I get this free for my thesis project?', { email: 'me@gmail.com' }) });
  const out = r.outputs['📒 Lead log'][0].json;
  assert(out.tier !== 'spam', 'a genuine low-budget enquiry was treated as spam');
  assert(['nurture_list', 'follow_up_queue'].includes(out.action),
    `low-budget lead routed to "${out.action}" instead of nurture`);
});

check('an enquiry missing its message fails loudly', () => {
  const r = execute(lead, { trigger: { body: { email: 'a@b.c' }, headers: {} }, staticData: {} });
  assert(r.effects.errors.length > 0, 'an empty enquiry passed silently');
});

// ═══════════════════════════════════════════════════════════════════════
section('DCA-A4-01 · Download Problem Self-Service');

const resend = load('a4-support/download-problem-self-service/workflow.json');
const resendSecrets = { '🔑 Sign the new link': LINK_SECRET };

const KNOWN = {
  storeName: 'T', fromEmail: 'support@x.test', humanEmail: 'me@x.test',
  downloadBaseUrl: 'https://x.test/download', linkTtlHours: 48, maxDownloads: 5,
  maxRequestsPerDay: 3, historyTtlHours: 72,
  knownOrders: { 'buyer@example.com': { orderId: 'o-1', productId: 'book-01', email: 'buyer@example.com' } },
};

const helpReq = (o = {}) => ({ body: { email: 'buyer@example.com', ...o }, headers: {} });

check('an entitled buyer gets a fresh link automatically', () => {
  const r = execute(resend, { trigger: helpReq(), secrets: resendSecrets, staticData: {}, configOverride: KNOWN });
  assert(r.effects.emails.length === 1, `expected 1 email, got ${r.effects.emails.length}`);
  assert(/sig=[a-f0-9]{64}/.test(r.effects.emails[0].html), 'reissued email has no signed link');
});

check('the link is sent to the order email, not one supplied in the request', () => {
  // Someone requests a reissue but tries to redirect it elsewhere.
  const r = execute(resend, {
    trigger: { body: { email: 'buyer@example.com', replyTo: 'attacker@evil.test', sendTo: 'attacker@evil.test' }, headers: {} },
    secrets: resendSecrets, staticData: {}, configOverride: KNOWN,
  });
  assert(r.effects.emails[0].to === 'buyer@example.com',
    `link was sent to ${r.effects.emails[0].to} — a supplied address could hijack delivery`);
});

check('an unknown email escalates instead of leaking whether an order exists', () => {
  const r = execute(resend, { trigger: helpReq({ email: 'nobody@example.com' }), secrets: resendSecrets, staticData: {}, configOverride: KNOWN });
  const out = r.outputs['📒 Deflection log'][0].json;
  assert(out.outcome === 'escalated', 'an unknown email was auto-resolved');
  const reply = r.effects.responses[0];
  assert(/If that email has an order/i.test(reply.body),
    'the public response confirms whether an order exists — that is an enumeration leak');
});

check('repeat clicks within a minute are deduped, not emailed five times', () => {
  const shared = {};
  const runs = [1, 2, 3].map(() =>
    execute(resend, { trigger: helpReq(), secrets: resendSecrets, staticData: shared, configOverride: KNOWN }));
  const emails = runs.reduce((n, r) => n + r.effects.emails.length, 0);
  assert(emails === 1,
    `an impatient buyer clicking resend three times got ${emails} emails — the guard should collapse them to one`);
});

check('the rate limit escalates rather than silently refusing', () => {
  const shared = {};
  let last;
  for (let i = 0; i < 5; i++) {
    // The guard dedupes per minute, so clear its replay memory between
    // iterations to simulate requests genuinely spread across the day. Without
    // this the per-minute dedupe fires first and the daily limit is never
    // reached — the two protections are layered and guard the wrong thing here.
    shared.seen = {};
    last = execute(resend, { trigger: helpReq(), secrets: resendSecrets, staticData: shared, configOverride: KNOWN });
  }
  const out = last.outputs['📒 Deflection log'][0].json;
  assert(out.outcome === 'escalated', 'exceeding the rate limit did not escalate');
  assert(last.effects.emails.some((e) => e.to === 'me@x.test'),
    'over-limit request was refused silently — that just creates the ticket this template prevents');
});

check('a mismatched order id escalates', () => {
  const r = execute(resend, { trigger: helpReq({ orderId: 'o-999' }), secrets: resendSecrets, staticData: {}, configOverride: KNOWN });
  const out = r.outputs['📒 Deflection log'][0].json;
  assert(out.outcome === 'escalated', 'a mismatched order id was auto-resolved');
});

check('a reissued link verifies in A1-02 (three templates share one URL contract)', () => {
  const r = execute(resend, { trigger: helpReq(), secrets: resendSecrets, staticData: {}, configOverride: KNOWN });
  const url = r.effects.emails[0].html.match(/href="([^"]+download[^"]*)"/)?.[1];
  assert(url, 'no download URL in the reissued email');

  const params = Object.fromEntries(new URL(url).searchParams);
  const v = execute(download, { trigger: { query: params, headers: {} }, secrets: dlSecrets, staticData: {} });
  assert(v.effects.responses.some((x) => x.with === 'redirect'),
    'a link reissued by A4-01 was rejected by A1-02 — the templates disagree on the URL contract');
});

// ═══════════════════════════════════════════════════════════════════════
console.log('\n' + '═'.repeat(64));
console.log(`${passed} passed · ${failed} failed`);
if (failures.length) {
  console.log('\nFailures:');
  for (const f of failures) console.log(`  • ${f.name}\n    ${f.message}`);
}
process.exit(failed ? 1 : 0);
