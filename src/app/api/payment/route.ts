import { NextResponse } from "next/server";
import { getBook, offerConfig } from "@/config";
import {
  createInvoice,
  isPaymentConfigured,
  PaymentConfigError,
} from "@/lib/payment";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/**
 * POST /api/payment
 * Body: { bookId: string }
 *
 * Creates a NOWPayments hosted invoice for the requested book at the
 * correct (offer-aware) price and returns the checkout URL.
 *
 * When NOWPAYMENTS_API_KEY isn't set yet, responds 503 with a clear
 * message — the client then falls back to the payment URL placeholder.
 * Nothing is faked.
 */
export async function POST(request: Request) {
  let bookId: string | undefined;
  try {
    const body = (await request.json()) as { bookId?: string };
    bookId = body.bookId;
  } catch {
    return NextResponse.json({ error: "Invalid request body." }, { status: 400 });
  }

  if (!bookId) {
    return NextResponse.json({ error: "Missing bookId." }, { status: 400 });
  }

  const book = getBook(bookId);
  if (!book) {
    return NextResponse.json({ error: "Unknown book." }, { status: 404 });
  }

  // Offer-aware pricing (server-authoritative).
  const offerActive = Date.now() < new Date(offerConfig.offerEndsAt).getTime();
  const priceAmount = offerActive ? book.offerPrice : book.originalPrice;

  if (!isPaymentConfigured()) {
    return NextResponse.json(
      {
        error: "checkout_unconfigured",
        message:
          "Payment provider is not configured yet. Set NOWPAYMENTS_API_KEY to enable checkout.",
      },
      { status: 503 }
    );
  }

  try {
    const invoice = await createInvoice({
      priceAmount,
      orderId: `${book.id}-${Date.now()}`,
      orderDescription: `${book.title} — Etqan AI Trading Library`,
    });
    return NextResponse.json({
      checkoutUrl: invoice.invoice_url,
      orderId: invoice.order_id,
      amount: priceAmount,
    });
  } catch (err) {
    if (err instanceof PaymentConfigError) {
      return NextResponse.json(
        { error: "checkout_unconfigured", message: err.message },
        { status: 503 }
      );
    }
    const message =
      err instanceof Error ? err.message : "Failed to create invoice.";
    return NextResponse.json({ error: "checkout_failed", message }, { status: 502 });
  }
}
