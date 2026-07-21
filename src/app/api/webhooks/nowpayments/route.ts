import { NextResponse } from "next/server";
import {
  verifyIpnSignature,
  isPaidStatus,
} from "@/lib/nowpayments-webhook";
import { createDownloadToken } from "@/lib/download-token";
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
  // order_id is issued as `${bookId}-${timestamp}` by the invoice route.
  const bookId = orderId.split("-").slice(0, -1).join("-") || orderId;

  if (isPaidStatus(status)) {
    const book = getBook(bookId);
    if (book) {
      const token = createDownloadToken(book.id);
      const downloadUrl = `${siteConfig.url}/api/download/${book.id}?token=${token}`;
      // TODO(delivery): persist the order and email `downloadUrl` to the buyer.
      console.info(
        `[nowpayments] paid order=${orderId} book=${book.id} → download link issued`
      );
      // The link is returned for logging/observability; NOWPayments ignores the body.
      return NextResponse.json({ ok: true, delivered: false, downloadUrl });
    }
    console.warn(`[nowpayments] paid but unknown book for order=${orderId}`);
  } else {
    console.info(`[nowpayments] order=${orderId} status=${status}`);
  }

  return NextResponse.json({ ok: true });
}
