const crypto = require('crypto');

function sortObject(value) {
  if (Array.isArray(value)) return value.map(sortObject);
  if (value && typeof value === 'object') {
    return Object.keys(value)
      .sort()
      .reduce((acc, key) => {
        acc[key] = sortObject(value[key]);
        return acc;
      }, {});
  }
  return value;
}

// NOWPayments signs IPN callbacks with HMAC-SHA512 over the JSON payload
// with all keys sorted alphabetically (recursively). Compare against the
// `x-nowpayments-sig` header. Never skip this check.
function verifyIpnSignature(payload, signatureHeader, ipnSecret) {
  if (!signatureHeader || !ipnSecret) return false;
  const sorted = sortObject(payload);
  const digest = crypto
    .createHmac('sha512', ipnSecret)
    .update(JSON.stringify(sorted))
    .digest('hex');
  return digest === signatureHeader;
}

async function createInvoice({ apiKey, baseUrl, orderId, priceUsd, description }) {
  const response = await fetch('https://api.nowpayments.io/v1/invoice', {
    method: 'POST',
    headers: {
      'x-api-key': apiKey,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      price_amount: priceUsd,
      price_currency: 'usd',
      order_id: orderId,
      order_description: description,
      ipn_callback_url: `${baseUrl}/api/ipn-webhook`,
      success_url: `${baseUrl}/success.html?order_id=${orderId}`,
      cancel_url: `${baseUrl}/checkout.html?cancelled=1`
    })
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`NOWPayments invoice creation failed: ${response.status} ${text}`);
  }

  return response.json();
}

module.exports = { verifyIpnSignature, createInvoice, sortObject };
