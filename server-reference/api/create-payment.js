const crypto = require('crypto');
const { createInvoice } = require('../lib/nowpayments');
const { createOrder } = require('../lib/storage');

const ALLOWED_LANGUAGES = ['ar', 'en', 'tr'];
const PRICE_USD = Number(process.env.PRICE_USD || 19);

// POST /api/create-payment
// body: { name: string, email: string, language: "ar"|"en"|"tr" }
// -> 200 { invoiceUrl, orderId }
module.exports = async function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  const { name, email, language } = req.body || {};

  if (!name || typeof name !== 'string' || name.trim().length < 3) {
    res.status(400).json({ error: 'اسم غير صالح' });
    return;
  }
  if (!email || typeof email !== 'string' || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    res.status(400).json({ error: 'بريد إلكتروني غير صالح' });
    return;
  }
  if (!ALLOWED_LANGUAGES.includes(language)) {
    res.status(400).json({ error: 'لغة غير مدعومة' });
    return;
  }

  const baseUrl = process.env.BASE_URL;
  if (!baseUrl || !process.env.NOWPAYMENTS_API_KEY) {
    res.status(500).json({ error: 'الخادم غير مهيأ بشكل صحيح، حاول لاحقاً' });
    return;
  }

  const orderId = crypto.randomUUID();

  try {
    const invoice = await createInvoice({
      apiKey: process.env.NOWPAYMENTS_API_KEY,
      baseUrl,
      orderId,
      priceUsd: PRICE_USD,
      description: `إتقان AI - حزمة (${language})`
    });

    createOrder({ orderId, name: name.trim(), email: email.trim(), language, priceUsd: PRICE_USD });

    res.status(200).json({ invoiceUrl: invoice.invoice_url, orderId });
  } catch (err) {
    console.error('create-payment failed:', err);
    res.status(502).json({ error: 'تعذر إنشاء فاتورة الدفع، حاول مرة أخرى' });
  }
};
