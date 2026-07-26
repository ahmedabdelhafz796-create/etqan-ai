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
section('DCA-A2-02 · Automatic Invoice & VAT');

const invoice = load('a2-payments-finance/automatic-invoice-vat/workflow.json');

const paidOrder = (o = {}, headers = {}) => ({
  body: {
    id: o.id ?? 'evt_inv_1',
    data: { object: {
      id: o.orderId ?? 'ord-1',
      amount_total: o.amount ?? 11900,
      currency: 'eur',
      customer_details: { email: 'buyer@example.com', name: 'Buyer',
                          address: { country: o.country ?? 'DE' } },
      metadata: { product_name: 'Course' },
      ...(o.vat ? { tax_ids: [{ value: o.vat }] } : {}),
    }},
  },
  headers,
});

check('invoice numbers are sequential with no gaps', () => {
  const shared = {};
  const nums = ['a', 'b', 'c'].map((id) => {
    const r = execute(invoice, { trigger: paidOrder({ id: `evt_${id}`, orderId: `ord-${id}` }), staticData: shared });
    return r.outputs['🔢 Assign invoice number'][0].json.invoiceSeq;
  });
  assert(JSON.stringify(nums) === JSON.stringify([1000, 1001, 1002]),
    `numbering was not sequential: ${nums.join(', ')}`);
});

check('a replayed order reuses its original number, never consuming a new one', () => {
  const shared = {};
  const first = execute(invoice, { trigger: paidOrder({ id: 'evt_x', orderId: 'ord-x' }), staticData: shared });
  // Simulate a replay arriving after the dedupe guard's TTL has expired.
  shared.seen = {};
  const second = execute(invoice, { trigger: paidOrder({ id: 'evt_x', orderId: 'ord-x' }), staticData: shared });

  const n1 = first.outputs['🔢 Assign invoice number'][0].json.invoiceNumber;
  const n2 = second.outputs['🔢 Assign invoice number'][0].json.invoiceNumber;
  assert(n1 === n2, `replay issued a second number (${n1} then ${n2}) — an auditor notices that`);
  assert(shared.invoiceCounter === 1000, `counter advanced on a replay: ${shared.invoiceCounter}`);
});

check('tax is extracted correctly from a tax-inclusive price', () => {
  const r = execute(invoice, { trigger: paidOrder({ country: 'DE', amount: 11900 }), staticData: {} });
  const out = r.outputs['🧮 Apply tax and build the invoice'][0].json;
  // 119.00 gross at 19% inclusive → 100.00 net, 19.00 tax
  assert(out.net === 100 && out.taxAmount === 19,
    `expected net 100 / tax 19, got net ${out.net} / tax ${out.taxAmount}`);
  assert(out.net + out.taxAmount === out.total, 'net + tax does not equal the total charged');
});

check('an unconfigured country falls back and says so', () => {
  const r = execute(invoice, { trigger: paidOrder({ country: 'JP' }), staticData: {} });
  const out = r.outputs['🧮 Apply tax and build the invoice'][0].json;
  assert(out.needsReview, 'an unconfigured jurisdiction was invoiced without any flag');
  assert(out.reviewFlags.some((f) => /No rate configured for JP/.test(f)),
    'the flag does not name the unconfigured country');
});

check('conflicting location signals are flagged, not silently resolved', () => {
  const r = execute(invoice, { trigger: paidOrder({ country: 'DE' }, { 'cf-ipcountry': 'BR' }), staticData: {} });
  const out = r.outputs['🧮 Apply tax and build the invoice'][0].json;
  assert(out.reviewFlags.some((f) => /disagree/i.test(f)),
    'billing and IP country disagreed and nothing was flagged');
});

check('a buyer VAT number is flagged for reverse-charge review', () => {
  const r = execute(invoice, { trigger: paidOrder({ country: 'DE', vat: 'DE123456789' }), staticData: {} });
  const out = r.outputs['🧮 Apply tax and build the invoice'][0].json;
  assert(out.reviewFlags.some((f) => /reverse charge/i.test(f)),
    'a business VAT number was not flagged for review');
});

check('the invoice email states number, net, tax and total', () => {
  const r = execute(invoice, { trigger: paidOrder({ country: 'DE' }), staticData: {} });
  const html = r.effects.emails[0].html;
  assert(/INV-1000/.test(html), 'invoice number missing from the email');
  assert(/19%/.test(html), 'tax rate missing from the email');
  assert(/119/.test(html), 'total missing from the email');
});

// ═══════════════════════════════════════════════════════════════════════
section('Scheduled branches (previously untested entry points)');

// Both revenue-recovery templates pair a webhook that records events with a
// schedule that acts on them. Every test above entered through the webhook, so
// the follow-up logic these templates exist for had never actually run.

check('dunning: a case past the follow-up day gets its second message', () => {
  const DAY = 86400000;
  const shared = { cases: { 'sub@example.com': {
    email: 'sub@example.com', name: 'Sub', amount: 50, currency: 'USD',
    openedAt: Date.now() - 4 * DAY, lastContactAt: Date.now() - 4 * DAY,
    stage: 0, failures: 1, recovered: false,
  }}};
  const r = execute(dunning, { trigger: {}, staticData: shared, from: 'Daily follow-up run' });
  assert(r.effects.emails.length === 1, `expected one follow-up, got ${r.effects.emails.length}`);
  assert(shared.cases['sub@example.com'].stage === 1, 'the case stage did not advance');
});

check('dunning: the same case is not contacted twice for one stage', () => {
  const DAY = 86400000;
  const shared = { cases: { 'sub@example.com': {
    email: 'sub@example.com', name: 'Sub', amount: 50, currency: 'USD',
    openedAt: Date.now() - 4 * DAY, stage: 0, failures: 1, recovered: false,
  }}};
  const first = execute(dunning, { trigger: {}, staticData: shared, from: 'Daily follow-up run' });
  const second = execute(dunning, { trigger: {}, staticData: shared, from: 'Daily follow-up run' });
  assert(first.effects.emails.length === 1, 'first run should send');
  assert(second.effects.emails.length === 0,
    'the same stage sent twice — a daily schedule would email this customer every day');
});

check('dunning: chasing stops after pauseAfterDays', () => {
  const DAY = 86400000;
  const shared = { cases: { 'old@example.com': {
    email: 'old@example.com', name: 'Old', amount: 50, currency: 'USD',
    openedAt: Date.now() - 30 * DAY, stage: 1, failures: 1, recovered: false,
  }}};
  const r = execute(dunning, { trigger: {}, staticData: shared, from: 'Daily follow-up run' });
  assert(r.effects.emails.length === 0,
    'still chasing a month-old case — past the pause point this only produces complaints');
  assert(shared.cases['old@example.com'].stage === 99, 'the case was not retired');
});

check('dunning: a recovered case is never contacted again', () => {
  const DAY = 86400000;
  const shared = { cases: { 'done@example.com': {
    email: 'done@example.com', amount: 50, openedAt: Date.now() - 5 * DAY,
    stage: 0, recovered: true, recoveredAt: Date.now(),
  }}};
  const r = execute(dunning, { trigger: {}, staticData: shared, from: 'Daily follow-up run' });
  assert(r.effects.emails.length === 0, 'a customer who already paid was chased');
});

check('cart: a cart past the reminder hour gets its first reminder', () => {
  const shared = { carts: { 'shopper@example.com': {
    email: 'shopper@example.com', name: 'Shopper', total: 49, currency: 'USD',
    items: [{ name: 'Course' }], abandonedAt: Date.now() - 2 * 3600000, stage: 0,
  }}};
  const r = execute(cart, { trigger: {}, staticData: shared, from: 'Check carts' });
  assert(r.effects.emails.length === 1, `expected one reminder, got ${r.effects.emails.length}`);
});

check('cart: contact is hard-capped at two messages', () => {
  const shared = { carts: { 'shopper@example.com': {
    email: 'shopper@example.com', total: 49, currency: 'USD', items: [],
    abandonedAt: Date.now() - 48 * 3600000, stage: 1,
  }}};
  const r = execute(cart, { trigger: {}, staticData: shared, from: 'Check carts' });
  assert(r.effects.emails.length === 1, 'the final reminder did not send');
  assert(!shared.carts['shopper@example.com'],
    'the cart survived its final message — a third reminder would follow');
});

check('cart: no discount appears unless explicitly enabled', () => {
  const shared = { carts: { 'shopper@example.com': {
    email: 'shopper@example.com', total: 49, currency: 'USD', items: [],
    abandonedAt: Date.now() - 48 * 3600000, stage: 1,
  }}};
  const r = execute(cart, { trigger: {}, staticData: shared, from: 'Check carts' });
  const body = r.effects.emails[0].body;
  assert(!/COMEBACK10/.test(body),
    'a discount code appeared with enableDiscount off — that trains buyers to always abandon');
});

// ═══════════════════════════════════════════════════════════════════════
section('DCA-A6-01 · AI Product Translation');

const translate = load('a6-content-localization/ai-product-translation/workflow.json');

const product = (o = {}) => ({
  body: { productId: 'book-01', title: 'Trading Masterclass',
          description: 'Learn to trade. Costs $49. Visit https://etqan.example for more. **Bold** text here.', ...o },
  headers: {},
});

const TR_CFG = {
  targetLanguages: ['ar'], sourceLanguage: 'en', protectedTerms: ['Trading Masterclass'],
  rtlLanguages: ['ar', 'he', 'fa', 'ur'], aiEndpoint: 'https://api.test/v1',
  aiModel: 'm', maxTokens: 2000, tone: 't', minLengthRatio: 0.4,
  skipUnchanged: true, historyTtlDays: 90,
};

check('prices, URLs and brand names are replaced with placeholders before translating', () => {
  const r = execute(translate, { trigger: product(), staticData: {}, configOverride: TR_CFG });
  const prepared = r.outputs['🔒 Protect literals and check what changed'][0].json;
  assert(!/\$49/.test(prepared.protectedDescription), 'the price was sent to the model unprotected');
  assert(!/https:\/\//.test(prepared.protectedDescription), 'a URL was sent unprotected');
  assert(!/Trading Masterclass/.test(prepared.protectedTitle), 'the brand name was sent unprotected');
  assert(prepared.protectedMap.length >= 3, `only ${prepared.protectedMap.length} literals protected`);
});

check('RTL languages are marked rtl', () => {
  const r = execute(translate, { trigger: product(), staticData: {}, configOverride: TR_CFG });
  const prepared = r.outputs['🔒 Protect literals and check what changed'][0].json;
  assert(prepared.isRtl === true, 'Arabic was not flagged as RTL');
});

check('a translation that loses a placeholder is NOT published', () => {
  const r = execute(translate, { trigger: product(), staticData: {}, configOverride: TR_CFG });
  const restored = r.outputs['🔓 Restore literals and verify']?.[0]?.json;
  assert(restored, 'restore node produced nothing');
  // The mock model response carries no placeholders, so verification must fail.
  assert(restored.published === false, 'a translation missing its placeholders was published');
  assert(restored.problems.length > 0, 'no problems were reported for a broken translation');
  assert(restored.title === 'Trading Masterclass', 'source text was not preserved on failure');
});

check('unchanged source skips the model entirely', () => {
  const shared = { translations: {} };
  execute(translate, { trigger: product(), staticData: shared, configOverride: TR_CFG });
  // Seed a successful prior translation with the matching hash.
  const prepared = execute(translate, { trigger: product(), staticData: { translations: {} }, configOverride: TR_CFG })
    .outputs['🔒 Protect literals and check what changed'][0].json;
  shared.translations['book-01|ar'] = {
    sourceHash: prepared.sourceHash, title: 'ت', description: 'د', dir: 'rtl', at: Date.now(),
  };
  shared.seen = {};
  const r = execute(translate, { trigger: product(), staticData: shared, configOverride: TR_CFG });
  assert(r.effects.httpCalls.length === 0, 'unchanged content still called the model — that costs money for nothing');
});

check('a product with no title fails loudly', () => {
  const r = execute(translate, { trigger: { body: { productId: 'x' }, headers: {} }, staticData: {}, configOverride: TR_CFG });
  assert(r.effects.errors.length > 0, 'a product with no title passed silently');
});

// ═══════════════════════════════════════════════════════════════════════
section('DCA-A6-02 · AI Sales Page Writer');

const writer = load('a6-content-localization/ai-sales-page-writer/workflow.json');

const facts = (o = {}) => ({
  body: { productName: 'Delivery Template', whatItIs: 'An n8n workflow',
          problemItSolves: 'Buyers not receiving files', price: '$49', ...o },
  headers: {},
});

check('missing facts are reported rather than invented', () => {
  const r = execute(writer, { trigger: facts(), staticData: {} });
  const collected = r.outputs['📥 Collect the facts'][0].json;
  assert(collected.missingFacts.length > 0, 'no missing facts reported despite proof and limits being absent');
  assert(collected.missingFacts.some((m) => /proof/.test(m)), 'absent proof was not reported');
});

check('an unreadable model response does not publish an empty page', () => {
  const r = execute(writer, { trigger: facts(), staticData: {} });
  const rendered = r.outputs['📄 Render the listing'][0].json;
  assert(rendered.ok === false, 'an unreadable response was treated as a valid listing');
  assert(rendered.markdown === null, 'an empty page was rendered for publication');
});

check('a listing with no facts still refuses without productName', () => {
  const r = execute(writer, { trigger: { body: { price: '$1' }, headers: {} }, staticData: {} });
  assert(r.effects.errors.length > 0, 'a listing request with no product name passed silently');
});

// ═══════════════════════════════════════════════════════════════════════
section('DCA-A7-01 · Sales Anomaly Detection');

const anomaly = load('a7-analytics/sales-anomaly-detection/workflow.json');

const AN_CFG = {
  storeName: 'T', alertEmail: 'me@x.test', fromEmail: 'a@x.test', currency: 'USD',
  minDailyOrders: 3, dropThreshold: 0.5, baselineWeeks: 4, minHistoryDays: 14,
  alertCooldownHours: 12,
};

/** Build N days of history ending yesterday, all on the same weekday cadence. */
function seedHistory({ orders = 20, starts = 25, days = 21 } = {}) {
  const stats = {};
  const now = new Date();
  for (let i = 1; i <= days; i++) {
    const d = new Date(now.getTime() - i * 86400000);
    const key = d.toISOString().slice(0, 10);
    stats[key] = { date: key, weekday: d.getUTCDay(), ts: Date.now(),
                   orders, revenue: orders * 50, checkoutStarts: starts, failures: 0 };
  }
  return stats;
}

check('insufficient history reports honestly instead of guessing', () => {
  const r = execute(anomaly, { trigger: {}, staticData: { dailyStats: seedHistory({ days: 3 }) }, configOverride: AN_CFG, from: 'Check every 4 hours' });
  const out = r.outputs['🔬 Compare against the weekday baseline'][0].json;
  assert(out.verdict === 'insufficient_history', `verdict was "${out.verdict}"`);
  assert(out.shouldAlert === false, 'alerted despite having no baseline');
});

check('a normal day does not alert', () => {
  const today = new Date().toISOString().slice(0, 10);
  const stats = seedHistory();
  stats[today] = { date: today, weekday: new Date().getUTCDay(), ts: Date.now(),
                   orders: 20, revenue: 1000, checkoutStarts: 25, failures: 0 };
  const r = execute(anomaly, { trigger: {}, staticData: { dailyStats: stats }, configOverride: AN_CFG, from: 'Check every 4 hours' });
  const out = r.outputs['🔬 Compare against the weekday baseline'][0].json;
  assert(out.verdict === 'normal', `a normal day produced verdict "${out.verdict}"`);
  assert(r.effects.emails.length === 0, 'a normal day sent an alert');
});

check('total silence is diagnosed as BROKEN, never as low demand', () => {
  const r = execute(anomaly, { trigger: {}, staticData: { dailyStats: seedHistory() }, configOverride: AN_CFG, from: 'Check every 4 hours' });
  const out = r.outputs['🔬 Compare against the weekday baseline'][0].json;
  assert(out.verdict === 'anomaly', `no anomaly detected on a zero-order day (verdict ${out.verdict})`);
  assert(out.cause === 'broken', `zero events diagnosed as "${out.cause}" — silence always means broken`);
  assert(out.confidence === 'high', 'confidence should be high when nothing is arriving at all');
});

check('traffic normal but orders down is diagnosed as BROKEN', () => {
  const today = new Date().toISOString().slice(0, 10);
  const stats = seedHistory();
  stats[today] = { date: today, weekday: new Date().getUTCDay(), ts: Date.now(),
                   orders: 1, revenue: 50, checkoutStarts: 24, failures: 0 };
  const r = execute(anomaly, { trigger: {}, staticData: { dailyStats: stats }, configOverride: AN_CFG, from: 'Check every 4 hours' });
  const out = r.outputs['🔬 Compare against the weekday baseline'][0].json;
  assert(out.cause === 'broken',
    `people arrived and could not buy, diagnosed as "${out.cause}" — that is the checkout-broken signature`);
});

check('traffic and orders down together is diagnosed as DEMAND', () => {
  const today = new Date().toISOString().slice(0, 10);
  const stats = seedHistory();
  stats[today] = { date: today, weekday: new Date().getUTCDay(), ts: Date.now(),
                   orders: 2, revenue: 100, checkoutStarts: 3, failures: 0 };
  const r = execute(anomaly, { trigger: {}, staticData: { dailyStats: stats }, configOverride: AN_CFG, from: 'Check every 4 hours' });
  const out = r.outputs['🔬 Compare against the weekday baseline'][0].json;
  assert(out.cause === 'demand',
    `both traffic and orders fell together, diagnosed as "${out.cause}" — that is a marketing signature`);
});

check('failed payments outnumbering successes is diagnosed as BROKEN', () => {
  const today = new Date().toISOString().slice(0, 10);
  const stats = seedHistory();
  stats[today] = { date: today, weekday: new Date().getUTCDay(), ts: Date.now(),
                   orders: 1, revenue: 50, checkoutStarts: 20, failures: 15 };
  const r = execute(anomaly, { trigger: {}, staticData: { dailyStats: stats }, configOverride: AN_CFG, from: 'Check every 4 hours' });
  const out = r.outputs['🔬 Compare against the weekday baseline'][0].json;
  assert(out.cause === 'broken', `payments failing en masse diagnosed as "${out.cause}"`);
  assert(/failed payment/i.test(out.evidence), 'the evidence does not mention the payment failures');
});

check('the alert leads with the diagnosis and a checklist', () => {
  const r = execute(anomaly, { trigger: {}, staticData: { dailyStats: seedHistory() }, configOverride: AN_CFG, from: 'Check every 4 hours' });
  const mail = r.effects.emails[0];
  assert(mail, 'no alert was sent for a total stop');
  assert(/BROKEN/.test(mail.subject), `subject does not lead with the diagnosis: ${mail.subject}`);
  assert(/DO THIS/.test(mail.text), 'the alert has no action checklist');
});

check('an ongoing drop does not re-page inside the cooldown', () => {
  const shared = { dailyStats: seedHistory() };
  const first = execute(anomaly, { trigger: {}, staticData: shared, configOverride: AN_CFG, from: 'Check every 4 hours' });
  const second = execute(anomaly, { trigger: {}, staticData: shared, configOverride: AN_CFG, from: 'Check every 4 hours' });
  assert(first.effects.emails.length === 1, 'first detection should alert');
  assert(second.effects.emails.length === 0,
    'the same ongoing drop paged twice — running every 4h that is 4 pages a day, which gets muted');
});

check('low-volume stores are told there is nothing to detect', () => {
  const r = execute(anomaly, { trigger: {}, staticData: { dailyStats: seedHistory({ orders: 1, starts: 1 }) }, configOverride: AN_CFG, from: 'Check every 4 hours' });
  const out = r.outputs['🔬 Compare against the weekday baseline'][0].json;
  assert(out.verdict === 'volume_too_low', `verdict was "${out.verdict}"`);
  assert(out.shouldAlert === false, 'alerted on a store with no statistical signal');
});

// ═══════════════════════════════════════════════════════════════════════
section('DCA-A3-03 · Leak Detection & Watermarking');

const leak = load('a3-fraud-security/leak-detection-watermarking/workflow.json');

check('stamping issues both a visible and an invisible marker', () => {
  const r = execute(leak, { trigger: { body: { action: 'stamp', orderId: 'o-1', email: 'b@x.test', productId: 'p1', name: 'Buyer' } }, staticData: {} });
  const out = r.outputs['🔖 Create the buyer marker'][0].json;
  assert(out.marker && out.marker.length >= 8, `marker looks too short: ${out.marker}`);
  assert(/Licensed to Buyer/.test(out.visibleMark), 'visible mark does not name the buyer');
  assert(/^DCA-/.test(out.invisibleMark), 'invisible mark is not namespaced');
});

check('the same order always produces the same marker', () => {
  const a = execute(leak, { trigger: { body: { action: 'stamp', orderId: 'o-2', email: 'b@x.test', productId: 'p1' } }, staticData: {} });
  const b = execute(leak, { trigger: { body: { action: 'stamp', orderId: 'o-2', email: 'b@x.test', productId: 'p1' } }, staticData: {} });
  assert(a.outputs['🔖 Create the buyer marker'][0].json.marker ===
         b.outputs['🔖 Create the buyer marker'][0].json.marker,
    'markers are not deterministic — a re-stamped file would not trace');
});

check('different buyers get different markers', () => {
  const a = execute(leak, { trigger: { body: { action: 'stamp', orderId: 'o-3', email: 'a@x.test', productId: 'p1' } }, staticData: {} });
  const b = execute(leak, { trigger: { body: { action: 'stamp', orderId: 'o-4', email: 'b@x.test', productId: 'p1' } }, staticData: {} });
  assert(a.outputs['🔖 Create the buyer marker'][0].json.marker !==
         b.outputs['🔖 Create the buyer marker'][0].json.marker,
    'two buyers share a marker — leaks would be unattributable');
});

check('a found marker traces back to the buyer', () => {
  const shared = {};
  const s = execute(leak, { trigger: { body: { action: 'stamp', orderId: 'o-5', email: 'leaker@x.test', productId: 'p1' } }, staticData: shared });
  const marker = s.outputs['🔖 Create the buyer marker'][0].json.marker;
  shared.seen = {};
  const t = execute(leak, { trigger: { body: { action: 'trace', marker: `DCA-${marker}` } }, staticData: shared });
  const out = t.outputs['🔎 Trace a found marker'][0].json;
  assert(out.action === 'traced', `trace returned "${out.action}"`);
  assert(out.email === 'leaker@x.test', `traced to the wrong buyer: ${out.email}`);
});

check('an unknown marker explains why rather than failing silently', () => {
  const r = execute(leak, { trigger: { body: { action: 'trace', marker: 'NOTREAL12345' } }, staticData: {} });
  const out = r.outputs['🔎 Trace a found marker'][0].json;
  assert(out.action === 'trace_failed', 'an unknown marker was reported as traced');
  assert(/markerSalt|misread/i.test(out.message), 'no explanation of why the trace failed');
});

check('a takedown notice is produced and disclaims legal advice', () => {
  const r = execute(leak, { trigger: { body: { action: 'takedown', url: 'https://pirate.test/file', productName: 'Course' } }, staticData: {} });
  const out = r.outputs['⚖️ Draft the takedown notice'][0].json;
  assert(/DMCA TAKEDOWN NOTICE/.test(out.notice), 'no notice was drafted');
  assert(/https:\/\/pirate\.test\/file/.test(out.notice), 'the infringing URL is missing from the notice');
  assert(/NOT LEGAL ADVICE/.test(out.notice), 'the notice does not disclaim legal advice');
});

check('a takedown without a URL is refused', () => {
  const r = execute(leak, { trigger: { body: { action: 'takedown', marker: 'X' } }, staticData: {} });
  assert(r.effects.errors.length > 0, 'a takedown with no URL was accepted');
});

check('heavy multi-IP sharing is detected from download data', () => {
  const shared = {
    downloads: { 'o-9|p1': { count: 60, ips: Array.from({ length: 25 }, (_, i) => `9.9.9.${i}`), firstAt: Date.now() } },
    markers: { M1: { marker: 'M1', orderId: 'o-9', email: 'sharer@x.test', issuedAt: Date.now() } },
  };
  const r = execute(leak, { trigger: {}, staticData: shared, from: 'Scan download patterns' });
  const out = r.outputs['📊 Find sharing patterns'][0].json;
  assert(out.found === 1, `expected 1 suspect, got ${out.found}`);
  assert(out.suspects[0].severity === 'critical', `25 IPs ranked "${out.suspects[0].severity}"`);
  assert(out.suspects[0].email === 'sharer@x.test', 'the suspect was not linked back to a buyer');
});

check('normal download behaviour raises nothing', () => {
  const shared = { downloads: { 'o-10|p1': { count: 3, ips: ['1.1.1.1', '1.1.1.2'], firstAt: Date.now() } } };
  const r = execute(leak, { trigger: {}, staticData: shared, from: 'Scan download patterns' });
  assert(r.effects.emails.length === 0, 'a normal buyer on two devices triggered a leak alert');
});

// ═══════════════════════════════════════════════════════════════════════
section('DCA-A1-04 · Product Update Broadcast');

const broadcast = load('a1-delivery/product-update-broadcast/workflow.json');
const bcSecrets = { '✍️ Sign fresh links': LINK_SECRET };

const BC_CFG = {
  storeName: 'T', fromEmail: 'u@x.test', supportEmail: 's@x.test',
  downloadBaseUrl: 'https://x.test/download', linkTtlHours: 168, maxDownloads: 5,
  batchSize: 50, historyTtlDays: 730,
  buyers: { 'book-01': [
    { email: 'a@x.test', orderId: 'o-a', name: 'A' },
    { email: 'b@x.test', orderId: 'o-b', name: 'B' },
  ]},
};

const update = (o = {}) => ({
  body: { productId: 'book-01', version: '2.0', significance: 'major', changes: ['New chapter'], ...o },
  headers: {},
});

check('a major update emails every buyer of that product', () => {
  const r = execute(broadcast, { trigger: update(), secrets: bcSecrets, staticData: {}, configOverride: BC_CFG });
  assert(r.effects.emails.length === 2, `expected 2 emails, got ${r.effects.emails.length}`);
  assert(/sig=[a-f0-9]{64}/.test(r.effects.emails[0].html), 'the announcement carries no fresh signed link');
});

check('a patch-level change emails nobody', () => {
  const r = execute(broadcast, { trigger: update({ significance: 'patch', version: '2.0.1' }), secrets: bcSecrets, staticData: {}, configOverride: BC_CFG });
  assert(r.effects.emails.length === 0,
    'a typo fix mailed the whole buyer list — that is how an update becomes an unsubscribe');
});

check('re-running the same update mails nobody twice', () => {
  const shared = {};
  const first = execute(broadcast, { trigger: update(), secrets: bcSecrets, staticData: shared, configOverride: BC_CFG });
  shared.seen = {};
  const second = execute(broadcast, { trigger: update(), secrets: bcSecrets, staticData: shared, configOverride: BC_CFG });
  assert(first.effects.emails.length === 2, 'first run should mail both buyers');
  assert(second.effects.emails.length === 0, 'a re-run mailed everyone a second time');
});

check('buyers of other products are not mailed', () => {
  const r = execute(broadcast, { trigger: update({ productId: 'other-product' }), secrets: bcSecrets, staticData: {}, configOverride: BC_CFG });
  assert(r.effects.emails.length === 0, 'an update mailed buyers who never bought that product');
});

check('a link from the broadcast verifies in A1-02 (four templates, one contract)', () => {
  const r = execute(broadcast, { trigger: update(), secrets: bcSecrets, staticData: {}, configOverride: BC_CFG });
  const url = r.effects.emails[0].html.match(/href="([^"]+download[^"]*)"/)?.[1];
  assert(url, 'no download URL in the announcement');
  const params = Object.fromEntries(new URL(url).searchParams);
  const v = execute(download, { trigger: { query: params, headers: {} }, secrets: dlSecrets, staticData: {} });
  assert(v.effects.responses.some((x) => x.with === 'redirect'),
    'a link from A1-04 was rejected by A1-02 — the URL contract has drifted');
});

// ═══════════════════════════════════════════════════════════════════════
section('DCA-A8-01 · Commission & Affiliate Payouts');

const commission = load('a8-marketplace-ops/commission-affiliate-payouts/workflow.json');

const COM_CFG = {
  storeName: 'T', fromEmail: 'p@x.test', ownerEmail: 'me@x.test', currency: 'USD',
  defaultRate: 20, minimumPayout: 25, holdDays: 30, historyTtlDays: 400,
  partners: { PARTNER_A: { name: 'Partner A', email: 'pa@x.test', rate: 20 } },
};

const sale = (o = {}) => ({ body: { orderId: 'ord-1', partnerId: 'PARTNER_A', amount: 100, currency: 'USD', ...o }, headers: {} });

check('a sale records commission at the configured rate', () => {
  const shared = {};
  const r = execute(commission, { trigger: sale(), staticData: shared, configOverride: COM_CFG });
  const out = r.outputs['📒 Record the earning or reversal'][0].json;
  assert(out.action === 'recorded', `action was "${out.action}"`);
  assert(out.commission === 20, `expected 20 commission on a 100 sale at 20%, got ${out.commission}`);
});

check('a duplicate sale does not double-count commission', () => {
  const shared = {};
  execute(commission, { trigger: sale(), staticData: shared, configOverride: COM_CFG });
  shared.seen = {};
  const r = execute(commission, { trigger: sale(), staticData: shared, configOverride: COM_CFG });
  assert(r.outputs['📒 Record the earning or reversal'][0].json.action === 'duplicate_ignored',
    'the same order was counted twice');
});

check('a refund reverses the commission', () => {
  const shared = {};
  execute(commission, { trigger: sale(), staticData: shared, configOverride: COM_CFG });
  shared.seen = {};
  const r = execute(commission, { trigger: { body: { event: 'refund', orderId: 'ord-1' }, headers: {} }, staticData: shared, configOverride: COM_CFG });
  const out = r.outputs['📒 Record the earning or reversal'][0].json;
  assert(out.action === 'reversed', `refund produced "${out.action}"`);
  assert(shared.earnings['ord-1|reversal'].commission === -20,
    'no negative record was created — the partner would be paid on refunded revenue');
});

check('the rate is frozen at sale time, not recalculated later', () => {
  const shared = {};
  execute(commission, { trigger: sale({ orderId: 'ord-rate' }), staticData: shared, configOverride: COM_CFG });
  // Partner renegotiates to 40% afterwards.
  const raised = { ...COM_CFG, partners: { PARTNER_A: { name: 'Partner A', email: 'pa@x.test', rate: 40 } } };
  shared.seen = {};
  execute(commission, { trigger: sale({ orderId: 'ord-new' }), staticData: shared, configOverride: raised });
  assert(shared.earnings['ord-rate'].commission === 20, 'a historical sale was repriced at the new rate');
  assert(shared.earnings['ord-new'].commission === 40, 'the new rate was not applied to the new sale');
});

check('an unknown partner is flagged rather than silently defaulted', () => {
  const r = execute(commission, { trigger: sale({ partnerId: 'GHOST' }), staticData: {}, configOverride: COM_CFG });
  const out = r.outputs['📒 Record the earning or reversal'][0].json;
  assert(out.warning && /not in your Config/.test(out.warning), 'an unknown partner produced no warning');
});

check('a sale with no partner is recorded as direct, not an error', () => {
  const r = execute(commission, { trigger: sale({ partnerId: '' }), staticData: {}, configOverride: COM_CFG });
  assert(r.outputs['📒 Record the earning or reversal'][0].json.action === 'no_attribution',
    'a direct sale was mishandled');
});

check('payout pays matured earnings above the minimum', () => {
  const old = Date.now() - 40 * 86400000;
  const shared = { earnings: {
    e1: { orderId: 'e1', partnerId: 'PARTNER_A', partnerName: 'Partner A', partnerEmail: 'pa@x.test',
          saleAmount: 200, rate: 20, commission: 40, currency: 'USD', at: old, paid: false, reversed: false },
  }};
  const r = execute(commission, { trigger: {}, staticData: shared, configOverride: COM_CFG, from: 'Payout run' });
  const out = r.outputs['🧮 Calculate what is owed'][0].json;
  assert(out.totalDue === 40, `expected 40 due, got ${out.totalDue}`);
  assert(shared.earnings.e1.paid === true, 'the earning was not marked paid');
});

check('re-running the payout pays nobody twice', () => {
  const old = Date.now() - 40 * 86400000;
  const shared = { earnings: {
    e1: { orderId: 'e1', partnerId: 'PARTNER_A', partnerName: 'P', partnerEmail: 'p@x.test',
          saleAmount: 200, rate: 20, commission: 40, currency: 'USD', at: old, paid: false, reversed: false },
  }};
  const first = execute(commission, { trigger: {}, staticData: shared, configOverride: COM_CFG, from: 'Payout run' });
  const second = execute(commission, { trigger: {}, staticData: shared, configOverride: COM_CFG, from: 'Payout run' });
  assert(first.outputs['🧮 Calculate what is owed'][0].json.totalDue === 40, 'first run should owe 40');
  assert(second.outputs['🧮 Calculate what is owed'][0].json.totalDue === 0,
    'a second payout run paid the same earnings again');
});

check('balances below the minimum carry forward instead of being paid', () => {
  const old = Date.now() - 40 * 86400000;
  const shared = { earnings: {
    e1: { orderId: 'e1', partnerId: 'PARTNER_A', partnerName: 'P', partnerEmail: 'p@x.test',
          saleAmount: 50, rate: 20, commission: 10, currency: 'USD', at: old, paid: false, reversed: false },
  }};
  const r = execute(commission, { trigger: {}, staticData: shared, configOverride: COM_CFG, from: 'Payout run' });
  const out = r.outputs['🧮 Calculate what is owed'][0].json;
  assert(out.totalDue === 0, 'a sub-threshold balance was paid out');
  assert(out.heldCount === 1, 'the balance was not carried forward');
  assert(shared.earnings.e1.paid !== true, 'a carried-forward earning was wrongly marked paid');
});

check('recent earnings are held until the refund window passes', () => {
  const shared = { earnings: {
    e1: { orderId: 'e1', partnerId: 'PARTNER_A', partnerName: 'P', partnerEmail: 'p@x.test',
          saleAmount: 500, rate: 20, commission: 100, currency: 'USD', at: Date.now(), paid: false, reversed: false },
  }};
  const r = execute(commission, { trigger: {}, staticData: shared, configOverride: COM_CFG, from: 'Payout run' });
  assert(r.outputs['🧮 Calculate what is owed'][0].json.totalDue === 0,
    'a sale from today was paid out before its refund window closed');
});

// ═══════════════════════════════════════════════════════════════════════
section('DCA-SYS-02 · Setup Checker');

const setup = load('sys-spine/setup-checker/workflow.json');

// The checker signs a fixed probe with each configured secret, so the harness
// must supply each Crypto node the value the Config declares — exactly as n8n
// would resolve the expression at runtime.
function setupRun(cfgOverride) {
  const c = {
    linkSecret_A1_01: 's1', linkSecret_A1_02: 's1', linkSecret_A4_01: 's1', linkSecret_A1_04: 's1',
    downloadBaseUrl: 'https://real.test/download', fromEmail: 'orders@real.test',
    storeName: 'Real Store', webhookSigningSecret: 'whsec_realvalue',
    testModeStillOn: false, errorWorkflowConfigured: true,
    templatesActivated: ['A1-01', 'A1-02'], aiApiKeyConfigured: true,
    orderLogWired: true, reportEmail: 'me@real.test',
    ...cfgOverride,
  };
  return execute(setup, {
    trigger: {},
    configOverride: c,
    secrets: {
      '🔏 Sign with A1-01 secret': c.linkSecret_A1_01,
      '🔏 Sign with A1-02 secret': c.linkSecret_A1_02,
      '🔏 Sign with A4-01 secret': c.linkSecret_A4_01,
      '🔏 Sign with A1-04 secret': c.linkSecret_A1_04,
    },
    staticData: {},
  });
}

const findingsOf = (r) => r.outputs['🔎 Run every check'][0].json;

check('a correct installation reports ready with no blockers', () => {
  const out = findingsOf(setupRun());
  assert(out.blockers === 0, `a clean install reported ${out.blockers} blocker(s): ` +
    out.findings.filter((f) => f.severity === 'blocker').map((f) => f.title).join(' | '));
  assert(out.readyForCustomers === true, 'a clean install was not marked ready');
});

check('MISMATCHED signing secrets are caught — the check that matters most', () => {
  const out = findingsOf(setupRun({ linkSecret_A1_02: 'DIFFERENT' }));
  const f = out.findings.find((x) => /DO NOT MATCH/.test(x.title));
  assert(f, 'four templates using different secrets was not detected — every download would fail');
  assert(f.severity === 'blocker', `mismatched secrets ranked "${f.severity}"`);
  assert(/A1-02/.test(f.why), 'the report does not name which template disagrees');
});

check('a secret differing only by trailing whitespace is still caught', () => {
  const out = findingsOf(setupRun({ linkSecret_A4_01: 's1 ' }));
  assert(out.findings.some((x) => /DO NOT MATCH/.test(x.title)),
    'a trailing space slipped through — that is invisible on screen and breaks every link');
});

check('testMode left on is a blocker', () => {
  const out = findingsOf(setupRun({ testModeStillOn: true }));
  const f = out.findings.find((x) => /testMode/.test(x.title));
  assert(f && f.severity === 'blocker', 'testMode left on was not flagged as a blocker');
  assert(out.readyForCustomers === false, 'an install with testMode on was marked ready');
});

check('placeholder values are detected', () => {
  const out = findingsOf(setupRun({ downloadBaseUrl: 'https://yourdomain.com/download', storeName: 'YOUR_STORE_NAME' }));
  const f = out.findings.find((x) => /Placeholder/.test(x.title));
  assert(f && f.severity === 'blocker', 'placeholder Config values were not flagged');
  assert(/downloadBaseUrl/.test(f.title), 'the report does not name which values are placeholders');
});

check('a missing webhook secret is flagged as forgeable', () => {
  const out = findingsOf(setupRun({ webhookSigningSecret: 'PASTE_YOUR_GATEWAY_WEBHOOK_SECRET' }));
  const f = out.findings.find((x) => /Webhook signing secret/.test(x.title));
  assert(f && f.severity === 'blocker', 'a missing webhook secret was not a blocker');
  assert(/free orders|forged|anyone/i.test(f.why), 'the report does not explain the actual risk');
});

check('no activated templates is a blocker', () => {
  const out = findingsOf(setupRun({ templatesActivated: [] }));
  const f = out.findings.find((x) => /activated/i.test(x.title));
  assert(f && f.severity === 'blocker', 'an install with nothing activated was not blocked');
  assert(/404/.test(f.why), 'the report does not explain that inactive webhooks return 404');
});

check('a missing Error Workflow is important but not a blocker', () => {
  const out = findingsOf(setupRun({ errorWorkflowConfigured: false }));
  const f = out.findings.find((x) => /Error Workflow/.test(x.title));
  assert(f && f.severity === 'important', `Error Workflow ranked "${f?.severity}"`);
  assert(out.readyForCustomers === true, 'an important-only issue wrongly blocked go-live');
});

check('a missing AI key is only advisable', () => {
  const out = findingsOf(setupRun({ aiApiKeyConfigured: false }));
  const f = out.findings.find((x) => /AI provider/.test(x.title));
  assert(f && f.severity === 'advisable', `a missing AI key ranked "${f?.severity}"`);
});

check('every finding carries a concrete fix', () => {
  const out = findingsOf(setupRun({
    linkSecret_A1_02: 'X', testModeStillOn: true, templatesActivated: [],
    errorWorkflowConfigured: false, orderLogWired: false, aiApiKeyConfigured: false,
    downloadBaseUrl: 'https://yourdomain.com/x', webhookSigningSecret: 'PASTE_ME',
  }));
  const actionable = out.findings.filter((f) => f.severity !== 'passed');
  assert(actionable.length > 0, 'a deliberately broken install produced no findings');
  for (const f of actionable) {
    assert(f.fix && f.fix.length > 30, `finding "${f.title}" has no usable fix instruction`);
  }
});

check('the report leads with whether it is safe to go live', () => {
  const r = setupRun({ testModeStillOn: true });
  const text = r.outputs['📋 Setup report'][0].json.report;
  assert(/NOT READY/.test(text), 'a blocked install does not say so up front');
  assert(text.indexOf('NOT READY') < text.indexOf('MUST FIX'), 'the verdict is buried below the detail');
});

// ═══════════════════════════════════════════════════════════════════════
section('DCA-B3-01 · Sales Pipeline & Follow-Up');

const pipeline = load('b3-sales-crm/sales-pipeline-followup/workflow.json');

const PIPE_CFG = {
  ownerEmail: 'me@x.test', fromEmail: 'p@x.test', businessName: 'B', currency: 'USD',
  staleDays: 4, highValueThreshold: 1000, lowValueThreshold: 100,
  abandonAfterDays: 45, maxDigestItems: 15, historyTtlDays: 180,
};

const DAY = 86400000;
const deal = (o = {}) => ({ dealId: 'd1', contact: 'Alice', email: 'a@x.test',
  value: 500, stage: 'proposal', openedAt: Date.now(), lastContactAt: Date.now(),
  touchCount: 1, status: 'open', currency: 'USD', ...o });

check('recording contact does not wipe the deal details', () => {
  const shared = {};
  execute(pipeline, { trigger: { body: { dealId: 'd1', contact: 'Alice', value: 500, stage: 'proposal' }, headers: {} },
                      staticData: shared, configOverride: PIPE_CFG });
  shared.seen = {};
  execute(pipeline, { trigger: { body: { dealId: 'd1', event: 'contacted' }, headers: {} },
                      staticData: shared, configOverride: PIPE_CFG });
  assert(shared.deals.d1.value === 500, 'a contact event wiped the deal value');
  assert(shared.deals.d1.contact === 'Alice', 'a contact event wiped the contact name');
  assert(shared.deals.d1.touchCount === 1, 'the touch was not counted');
});

check('a high-value deal is chased sooner than a low-value one', () => {
  const silent = Date.now() - 3 * DAY;   // 3 days: past high threshold (2), under normal (4)
  const shared = { deals: {
    big: deal({ dealId: 'big', value: 5000, lastContactAt: silent }),
    small: deal({ dealId: 'small', value: 50, lastContactAt: silent }),
  }};
  const r = execute(pipeline, { trigger: {}, staticData: shared, configOverride: PIPE_CFG, from: 'Daily digest' });
  const out = r.outputs['🔍 Find deals going cold'][0].json;
  const ids = out.needsChasing.map((d) => d.dealId);
  assert(ids.includes('big'), 'a 5000 deal silent for 3 days was not surfaced');
  assert(!ids.includes('small'), 'a 50 deal was chased as urgently as a 5000 one');
});

check('the digest is ordered by deal value', () => {
  const silent = Date.now() - 10 * DAY;
  const shared = { deals: {
    a: deal({ dealId: 'a', value: 200, lastContactAt: silent }),
    b: deal({ dealId: 'b', value: 9000, lastContactAt: silent }),
  }};
  const r = execute(pipeline, { trigger: {}, staticData: shared, configOverride: PIPE_CFG, from: 'Daily digest' });
  const out = r.outputs['🔍 Find deals going cold'][0].json;
  assert(out.needsChasing[0].dealId === 'b', 'the digest is not led by the most valuable deal');
});

check('nothing is ever sent to the prospect', () => {
  const shared = { deals: { d1: deal({ lastContactAt: Date.now() - 10 * DAY }) } };
  const r = execute(pipeline, { trigger: {}, staticData: shared, configOverride: PIPE_CFG, from: 'Daily digest' });
  assert(r.effects.emails.length === 1, 'expected exactly the owner digest');
  assert(r.effects.emails[0].to === 'me@x.test',
    `an email went to ${r.effects.emails[0].to} — this template must never contact the prospect`);
});

check('a recently contacted deal is not chased', () => {
  const shared = { deals: { d1: deal({ lastContactAt: Date.now() }) } };
  const r = execute(pipeline, { trigger: {}, staticData: shared, configOverride: PIPE_CFG, from: 'Daily digest' });
  assert(r.effects.emails.length === 0, 'a deal contacted today was listed as going cold');
});

check('closed deals drop out of the digest', () => {
  const shared = { deals: { d1: deal({ status: 'won', closedAt: Date.now(), lastContactAt: Date.now() - 20 * DAY }) } };
  const r = execute(pipeline, { trigger: {}, staticData: shared, configOverride: PIPE_CFG, from: 'Daily digest' });
  const out = r.outputs['🔍 Find deals going cold'][0].json;
  assert(out.totalStale === 0, 'a won deal was still being chased');
});

check('abandoned deals stop appearing', () => {
  const shared = { deals: { d1: deal({ openedAt: Date.now() - 60 * DAY, lastContactAt: Date.now() - 60 * DAY }) } };
  const r = execute(pipeline, { trigger: {}, staticData: shared, configOverride: PIPE_CFG, from: 'Daily digest' });
  const out = r.outputs['🔍 Find deals going cold'][0].json;
  assert(out.totalStale === 0, 'a two-month-dead deal still appears daily, which trains you to skim the digest');
});

check('every listed deal carries a draft and a stated reason', () => {
  const shared = { deals: { d1: deal({ lastContactAt: Date.now() - 10 * DAY }) } };
  const r = execute(pipeline, { trigger: {}, staticData: shared, configOverride: PIPE_CFG, from: 'Daily digest' });
  const text = r.effects.emails[0].body;
  assert(/DRAFT:/.test(text), 'no draft was written for a stale deal');
  assert(/days silent/.test(text), 'the digest does not say why the deal is listed');
});

// ═══════════════════════════════════════════════════════════════════════
section('DCA-B5-01 · CV Screening & Triage');

const cvs = load('b5-recruitment/cv-screening-triage/workflow.json');

const CV_CFG = {
  roleTitle: 'Engineer', mustHaves: ['3 years Python'], niceToHaves: ['n8n'],
  yearsExperienceExpected: 3, aiEndpoint: 'https://api.test/v1', aiModel: 'm',
  maxTokens: 800, shortlistSize: 20, reviewerEmail: 'me@x.test',
  fromEmail: 'h@x.test', companyName: 'C', historyTtlDays: 90,
};

const application = (o = {}) => ({
  body: { candidateId: 'c1', name: 'Candidate', email: 'c@x.test',
          cvText: 'x'.repeat(400), ...o },
  headers: {},
});

check('an unreadable assessment marks the candidate for review, not zero', () => {
  const shared = {};
  execute(cvs, { trigger: application(), staticData: shared, configOverride: CV_CFG });
  const rec = shared.candidates.c1;
  assert(rec, 'the candidate was not recorded at all');
  assert(rec.score === null, `a failed assessment produced a score of ${rec.score} — that would rank them last`);
  assert(rec.needsManualReview === true, 'a failed assessment did not flag for manual review');
});

check('a very short application is flagged, not discarded', () => {
  const shared = {};
  execute(cvs, { trigger: application({ candidateId: 'c2', cvText: 'See my LinkedIn' }), staticData: shared, configOverride: CV_CFG });
  assert(shared.candidates.c2, 'a short application was discarded');
  assert(shared.candidates.c2.needsManualReview === true, 'a short application was not flagged');
});

check('unscored candidates are listed FIRST in the digest', () => {
  const shared = { candidates: {
    good: { candidateId: 'good', name: 'Scored', email: 'g@x.test', at: Date.now(),
            score: 90, needsManualReview: false, mustHavesMet: [], mustHavesMissing: [],
            strengths: '', questions: [], reasoning: 'strong' },
    unk: { candidateId: 'unk', name: 'Unscored', email: 'u@x.test', at: Date.now(),
           score: null, needsManualReview: true, reviewReason: 'could not be read',
           mustHavesMet: [], mustHavesMissing: [], strengths: '', questions: [], reasoning: '' },
  }};
  const r = execute(cvs, { trigger: {}, staticData: shared, configOverride: CV_CFG, from: 'Daily shortlist' });
  const text = r.effects.emails[0].body;
  assert(text.indexOf('NEEDS A HUMAN') < text.indexOf('RANKED'),
    'unscored candidates were buried below the ranking — those are the ones most likely to be lost');
});

check('the digest states plainly that nobody was rejected', () => {
  const shared = { candidates: {
    a: { candidateId: 'a', name: 'A', email: 'a@x.test', at: Date.now(), score: 40,
         needsManualReview: false, mustHavesMet: [], mustHavesMissing: ['3 years Python'],
         strengths: '', questions: [], reasoning: 'limited evidence' },
  }};
  const r = execute(cvs, { trigger: {}, staticData: shared, configOverride: CV_CFG, from: 'Daily shortlist' });
  const text = r.effects.emails[0].body;
  assert(/Nobody has been rejected/i.test(text), 'the digest does not state that no rejection occurred');
  assert(/reading order, not a decision/i.test(text), 'the digest does not frame itself as a reading order');
});

check('candidates are ranked by score', () => {
  const shared = { candidates: {
    lo: { candidateId: 'lo', name: 'Lo', email: 'l@x.test', at: Date.now(), score: 30,
          needsManualReview: false, mustHavesMet: [], mustHavesMissing: [], strengths: '', questions: [], reasoning: 'r' },
    hi: { candidateId: 'hi', name: 'Hi', email: 'h@x.test', at: Date.now(), score: 95,
          needsManualReview: false, mustHavesMet: [], mustHavesMissing: [], strengths: '', questions: [], reasoning: 'r' },
  }};
  const r = execute(cvs, { trigger: {}, staticData: shared, configOverride: CV_CFG, from: 'Daily shortlist' });
  const out = r.outputs['🏅 Build the shortlist'][0].json;
  assert(out.shortlist[0].candidateId === 'hi', 'the shortlist is not ordered by score');
});

check('no email is ever sent to a candidate', () => {
  const shared = { candidates: {
    a: { candidateId: 'a', name: 'A', email: 'candidate@x.test', at: Date.now(), score: 80,
         needsManualReview: false, mustHavesMet: [], mustHavesMissing: [], strengths: '', questions: [], reasoning: 'r' },
  }};
  const r = execute(cvs, { trigger: {}, staticData: shared, configOverride: CV_CFG, from: 'Daily shortlist' });
  for (const m of r.effects.emails) {
    assert(m.to === 'me@x.test', `an email was addressed to ${m.to} — candidates must never be contacted by this template`);
  }
});

check('an application with no CV text fails loudly', () => {
  const r = execute(cvs, { trigger: { body: { candidateId: 'x' }, headers: {} }, staticData: {}, configOverride: CV_CFG });
  assert(r.effects.errors.length > 0, 'an empty application passed silently');
});

// ═══════════════════════════════════════════════════════════════════════
console.log('\n' + '═'.repeat(64));
console.log(`${passed} passed · ${failed} failed`);
if (failures.length) {
  console.log('\nFailures:');
  for (const f of failures) console.log(`  • ${f.name}\n    ${f.message}`);
}
process.exit(failed ? 1 : 0);
