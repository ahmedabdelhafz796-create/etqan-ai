// Reference storage implementation ONLY. A local JSON file works fine for
// testing with `node` or `vercel dev`, but production serverless functions
// run as multiple short-lived, disk-isolated instances — writes here will
// NOT reliably persist or be visible across invocations in that environment.
//
// Before going live with real traffic, swap this module for a real store
// (Vercel KV, Upstash Redis, Supabase/Postgres, etc.) that keeps the same
// five exported functions below so the API handlers don't need to change.

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const DB_PATH = path.join(__dirname, '..', '.data', 'orders.json');

function readAll() {
  try {
    return JSON.parse(fs.readFileSync(DB_PATH, 'utf8'));
  } catch {
    return {};
  }
}

function writeAll(db) {
  fs.mkdirSync(path.dirname(DB_PATH), { recursive: true });
  fs.writeFileSync(DB_PATH, JSON.stringify(db, null, 2));
}

function createOrder({ orderId, name, email, language, priceUsd }) {
  const db = readAll();
  db[orderId] = {
    orderId,
    name,
    email,
    language,
    priceUsd,
    status: 'pending',
    createdAt: new Date().toISOString(),
    downloadToken: null
  };
  writeAll(db);
}

function getOrder(orderId) {
  return readAll()[orderId] || null;
}

// Called only from the IPN webhook handler, after signature verification.
function markOrderPaid(orderId) {
  const db = readAll();
  if (!db[orderId]) return null;
  db[orderId].status = 'paid';
  db[orderId].paidAt = new Date().toISOString();
  db[orderId].downloadToken = crypto.randomBytes(24).toString('hex');
  writeAll(db);
  return db[orderId];
}

function verifyDownloadToken(orderId, token) {
  const order = getOrder(orderId);
  return Boolean(order) && order.status === 'paid' && order.downloadToken === token;
}

module.exports = { createOrder, getOrder, markOrderPaid, verifyDownloadToken };
