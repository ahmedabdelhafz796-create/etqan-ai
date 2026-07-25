import { NextResponse } from "next/server";
import { getBook } from "@/config";
import { getProduct } from "@/catalog";
import { getEffectiveConfig } from "@/lib/site-settings";
import { validateCoupon } from "@/lib/repositories";
import { rateLimit, clientIp, tooManyRequests } from "@/lib/rate-limit";
import {
  createInvoice,
  isPaymentConfigured,
  PaymentConfigError,
} from "@/lib/payment";
import { createLemonCheckout, isLemonConfigured } from "@/lib/lemonsqueezy";

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
  // Rate limit checkout creation: 10 requests / minute / IP.
  const rl = rateLimit(`pay:${clientIp(request)}`, 10, 60_000);
  if (!rl.ok) return tooManyRequests(rl.retryAfter);

  let bookId: string | undefined;
  let couponCode: string | undefined;
  let provider: "crypto" | "card" = "crypto";
  try {
    const body = (await request.json()) as { bookId?: string; coupon?: string; provider?: string };
    bookId = body.bookId;
    couponCode = typeof body.coupon === "string" ? body.coupon.slice(0, 40) : undefined;
    if (body.provider === "card") provider = "card";
  } catch {
    return NextResponse.json({ error: "Invalid request body." }, { status: 400 });
  }

  if (!bookId) {
    return NextResponse.json({ error: "Missing bookId." }, { status: 400 });
  }

  const book = getBook(bookId);
  const product = book ? null : getProduct(bookId);
  if (!book && !product) {
    return NextResponse.json({ error: "Unknown product." }, { status: 404 });
  }

  // Offer-aware pricing (server-authoritative), honoring admin overrides for
  // legacy books and the catalog's own prices for courses/bundles.
  const eff = await getEffectiveConfig();
  const offerActive = Date.now() < new Date(eff.offerEndsAt).getTime();

  let priceAmount: number;
  let title: string;
  if (book) {
    const pricing = eff.books[book.id] ?? {
      originalPrice: book.originalPrice,
      offerPrice: book.offerPrice,
    };
    priceAmount =
      offerActive && pricing.offerPrice < pricing.originalPrice
        ? pricing.offerPrice
        : pricing.originalPrice;
    title = book.title;
  } else {
    priceAmount =
      offerActive && product!.offerPrice < product!.originalPrice
        ? product!.offerPrice
        : product!.originalPrice;
    title = product!.title;
  }
  const productId = book ? book.id : product!.id;

  // Server-authoritative coupon: the client can only *suggest* a code; the
  // discount is validated and applied here, never trusted from the browser.
  let appliedCoupon: string | null = null;
  if (couponCode) {
    const percentOff = await validateCoupon(couponCode).catch(() => null);
    if (percentOff && percentOff > 0) {
      priceAmount = Math.max(1, Math.round(priceAmount * (1 - percentOff / 100) * 100) / 100);
      appliedCoupon = couponCode.trim().toUpperCase();
    }
  }

  // Send buyers back to our thank-you page (which auto-issues the download).
  const origin =
    process.env.NEXT_PUBLIC_SITE_URL || new URL(request.url).origin;

  // ── Card / PayPal via Lemon Squeezy ──
  if (provider === "card") {
    if (!isLemonConfigured()) {
      return NextResponse.json(
        {
          error: "checkout_unconfigured",
          message: "Card checkout isn't configured yet. Set LEMONSQUEEZY_API_KEY and LEMONSQUEEZY_STORE_ID.",
        },
        { status: 503 }
      );
    }
    try {
      const checkout = await createLemonCheckout({
        productId,
        title,
        priceAmount,
        redirectUrl: `${origin}/thank-you`,
      });
      if (!checkout) throw new Error("No checkout URL returned.");
      return NextResponse.json({ checkoutUrl: checkout.url, amount: priceAmount, coupon: appliedCoupon, provider: "card" });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to create checkout.";
      return NextResponse.json({ error: "checkout_failed", message }, { status: 502 });
    }
  }

  // ── Crypto via NOWPayments (default) ──
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
      orderId: `${productId}-${Date.now()}`,
      orderDescription: `${title} — E-tqan`,
      successUrl: `${origin}/thank-you`,
      cancelUrl: `${origin}/#courses`,
    });
    return NextResponse.json({
      checkoutUrl: invoice.invoice_url,
      orderId: invoice.order_id,
      amount: priceAmount,
      coupon: appliedCoupon,
      provider: "crypto",
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
