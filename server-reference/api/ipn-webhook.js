const { verifyIpnSignature } = require('../lib/nowpayments');
const { markOrderPaid } = require('../lib/storage');

const PAID_STATUSES = ['finished', 'confirmed'];

// POST /api/ipn-webhook — called by NOWPayments' servers, not the browser.
// This is the ONLY place payment is actually confirmed. Never mark an
// order paid based on the browser reaching success_url — that redirect
// can be hit by anyone without paying.
module.exports = async function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(405).end();
    return;
  }

  const signature = req.headers['x-nowpayments-sig'];
  const body = req.body;

  if (!verifyIpnSignature(body, signature, process.env.NOWPAYMENTS_IPN_SECRET)) {
    res.status(403).json({ error: 'invalid signature' });
    return;
  }

  const { order_id, payment_status } = body || {};

  if (order_id && PAID_STATUSES.includes(payment_status)) {
    markOrderPaid(order_id);
  }

  // Always 200 once signature is valid, even for intermediate statuses
  // (e.g. "waiting", "confirming") — NOWPayments retries on non-2xx.
  res.status(200).json({ received: true });
};
