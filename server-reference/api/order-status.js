const { getOrder } = require('../lib/storage');

// GET /api/order-status?order_id=...
// -> 200 { status: "pending" }
// -> 200 { status: "paid", downloadToken, language }
// -> 404 { status: "unknown" }
module.exports = async function handler(req, res) {
  const orderId = (req.query && req.query.order_id) || '';

  if (!orderId) {
    res.status(400).json({ error: 'order_id required' });
    return;
  }

  const order = getOrder(orderId);

  if (!order) {
    res.status(404).json({ status: 'unknown' });
    return;
  }

  const response = { status: order.status };

  if (order.status === 'paid') {
    response.downloadToken = order.downloadToken;
    response.language = order.language;
  }

  res.status(200).json(response);
};
