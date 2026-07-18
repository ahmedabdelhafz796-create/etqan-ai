const fs = require('fs');
const path = require('path');
const { getOrder, verifyDownloadToken } = require('../lib/storage');

const FILENAMES = {
  ar: 'course-ar.zip',
  en: 'course-en.zip',
  tr: 'course-tr.zip'
};

// GET /api/download?order_id=...&token=...
// Only ever serves the file after verifying the order is paid AND the
// one-time token (issued in markOrderPaid) matches — the token is what
// makes this link unguessable, not the order id alone.
module.exports = async function handler(req, res) {
  const orderId = (req.query && req.query.order_id) || '';
  const token = (req.query && req.query.token) || '';

  if (!orderId || !token || !verifyDownloadToken(orderId, token)) {
    res.status(403).json({ error: 'رابط غير صالح أو منتهي الصلاحية' });
    return;
  }

  const order = getOrder(orderId);
  const filename = FILENAMES[order.language];
  const filePath = path.join(__dirname, '..', '..', 'files', order.language, filename);

  if (!fs.existsSync(filePath)) {
    res.status(404).json({ error: 'الملف غير متاح حالياً، تواصل معنا عبر تليجرام' });
    return;
  }

  res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
  res.setHeader('Content-Type', 'application/zip');
  fs.createReadStream(filePath).pipe(res);
};
