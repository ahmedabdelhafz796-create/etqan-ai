import { NextResponse } from "next/server";
import { verifyLemonSignature } from "@/lib/lemonsqueezy";
import { issueDownloadToken, DOWNLOAD_MAX } from "@/lib/download-token";
import { recordOrder, upsertCustomer, createGrant, log } from "@/lib/repositories";
import { siteConfig } from "@/config";
import { getPurchasable } from "@/lib/purchasable";
import { issueReceiptToken, receiptUrl } from "@/lib/receipt";
import { sendDeliveryEmail } from "@/lib/email";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/**
 * POST /api/webhooks/lemonsqueezy
 *
 * Receives Lemon Squeezy webhooks, verifies the HMAC-SHA256 signature, and on
 * a successful order mints a secure, expiring download grant — mirroring the
 * NOWPayments IPN flow, so card/PayPal buyers get the same instant delivery.
 *
 * Configure a webhook in your Lemon Squeezy dashboard pointing here, with the
 * signing secret set as LEMONSQUEEZY_WEBHOOK_SECRET. Inert until configured.
 */
export async function POST(request: Request) {
  const raw = await request.text();
  const signature = request.headers.get("x-signature");
  if (!verifyLemonSignature(raw, signature)) {
    return NextResponse.json({ error: "invalid_signature" }, { status: 401 });
  }

  let payload: Record<string, unknown>;
  try {
    payload = JSON.parse(raw) as Record<string, unknown>;
  } catch {
    return NextResponse.json({ error: "bad_json" }, { status: 400 });
  }

  const meta = (payload.meta ?? {}) as { event_name?: string; custom_data?: { product_id?: string } };
  const data = (payload.data ?? {}) as { id?: string; attributes?: Record<string, unknown> };
  const attrs = data.attributes ?? {};
  const event = String(meta.event_name || "");
  const status = String(attrs.status || "");
  const email = typeof attrs.user_email === "string" ? attrs.user_email : null;
  const total = Number(attrs.total ?? 0) / 100; // cents → USD
  const productId = meta.custom_data?.product_id || "";
  const orderId = `ls-${data.id || Date.now()}`;

  const item = productId ? getPurchasable(productId) : undefined;
  const paid = event === "order_created" && (status === "paid" || status === "active");

  await recordOrder({
    id: orderId,
    paymentId: data.id ? String(data.id) : null,
    bookId: item?.id || productId,
    customerEmail: email,
    amount: total,
    currency: "USD",
    status: paid ? "finished" : status || event,
  });
  if (email) await upsertCustomer(email);
  await log("info", "lemonsqueezy_webhook", { orderId, event, status });

  if (paid && item) {
    const issued = issueDownloadToken(item.id);
    await createGrant({
      jti: issued.jti,
      orderId,
      bookId: item.id,
      maxDownloads: DOWNLOAD_MAX,
      expiresAt: issued.expiresAt,
    });
    const downloadUrl = `${siteConfig.url}/api/download/${item.id}?token=${issued.token}`;
    await log("info", "download_issued", { orderId, bookId: item.id, via: "lemonsqueezy" });

    let delivered = false;
    if (email) {
      const receipt = issueReceiptToken(orderId, item.id);
      const sent = await sendDeliveryEmail({
        to: email,
        productTitle: item.title,
        orderId,
        receiptUrl: receiptUrl(siteConfig.url, receipt),
        amount: total,
        currency: "USD",
      });
      delivered = sent.sent;
      await log(sent.sent ? "info" : "warn", sent.sent ? "delivery_email_sent" : "delivery_email_skipped", {
        orderId,
        reason: sent.reason,
      });
    }
    return NextResponse.json({ ok: true, delivered, downloadUrl });
  }

  return NextResponse.json({ ok: true });
}
