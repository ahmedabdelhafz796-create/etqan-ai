import { NextResponse } from "next/server";
import {
  verifyIpnSignature,
  isPaidStatus,
} from "@/lib/nowpayments-webhook";
import { issueDownloadToken, DOWNLOAD_MAX } from "@/lib/download-token";
import {
  recordOrder,
  upsertCustomer,
  createGrant,
  log,
} from "@/lib/repositories";
import { getBook, siteConfig } from "@/config";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/**
 * POST /api/webhooks/nowpayments
 *
 * Receives NOWPayments IPN callbacks, verifies the HMAC-SHA512 signature,
 * and (on a paid status) mints a secure, expiring download link for the
 * purchased book.
 *
 * Delivery of that link to the buyer (email / order record) is the seam that
 * plugs into your database + email provider once configured. Until then the
 * link is logged server-side so nothing is lost.
 */
export async function POST(request: Request) {
  const secret = process.env.NOWPAYMENTS_IPN_SECRET || "";
  if (!secret) {
    return NextResponse.json(
      { error: "ipn_unconfigured", message: "NOWPAYMENTS_IPN_SECRET is not set." },
      { status: 503 }
    );
  }

  // Read the raw body and parse — we must verify against the parsed payload.
  let payload: Record<string, unknown>;
  try {
    payload = (await request.json()) as Record<string, unknown>;
  } catch {
    return NextResponse.json({ error: "bad_json" }, { status: 400 });
  }

  const signature = request.headers.get("x-nowpayments-sig");
  if (!verifyIpnSignature(payload, signature, secret)) {
    return NextResponse.json(
      { error: "invalid_signature" },
      { status: 401 }
    );
  }

  const status = String(payload.payment_status || "");
  const orderId = String(payload.order_id || "");
  const paymentId = payload.payment_id ? String(payload.payment_id) : null;
  const amount = Number(payload.price_amount ?? 0);
  const currency = payload.price_currency ? String(payload.price_currency) : null;
  const email =
    typeof payload.customer_email === "string" ? payload.customer_email : null;
  // order_id is issued as `${bookId}-${timestamp}` by the invoice route.
  const bookId = orderId.split("-").slice(0, -1).join("-") || orderId;
  const book = getBook(bookId);

  // Persist the order + customer regardless of status (idempotent upsert).
  await recordOrder({
    id: orderId || `order-${Date.now()}`,
    paymentId,
    bookId,
    customerEmail: email,
    amount,
    currency,
    status,
  });
  if (email) await upsertCustomer(email);
  await log("info", "nowpayments_ipn", { orderId, status, paymentId });

  if (isPaidStatus(status) && book) {
    const issued = issueDownloadToken(book.id);
    await createGrant({
      jti: issued.jti,
      orderId: orderId || null,
      bookId: book.id,
      maxDownloads: DOWNLOAD_MAX,
      expiresAt: issued.expiresAt,
    });
    const downloadUrl = `${siteConfig.url}/api/download/${book.id}?token=${issued.token}`;
    // TODO(delivery): email `downloadUrl` to the buyer via your ESP.
    await log("info", "download_issued", { orderId, bookId: book.id });
    return NextResponse.json({ ok: true, delivered: false, downloadUrl });
  }

  if (isPaidStatus(status) && !book) {
    await log("warn", "paid_unknown_book", { orderId });
  }

  return NextResponse.json({ ok: true });
}
