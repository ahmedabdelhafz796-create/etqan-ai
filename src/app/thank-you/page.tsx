import type { Metadata } from "next";
import Link from "next/link";
import {
  CheckCircle2,
  Clock,
  Download,
  MessageCircle,
  XCircle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { links } from "@/config";
import { getPurchasable } from "@/lib/purchasable";
import { getPaymentStatus } from "@/lib/payment";
import { issueDownloadToken, DOWNLOAD_MAX } from "@/lib/download-token";
import { countGrantsForOrder, createGrant, log } from "@/lib/repositories";
import { isPaidStatus } from "@/lib/nowpayments-webhook";
import { RECEIPT_MAX_ISSUES, verifyReceiptToken } from "@/lib/receipt";

export const metadata: Metadata = {
  title: "Thank You",
  description: "Your order is confirmed.",
  robots: { index: false, follow: false },
};

export const dynamic = "force-dynamic";

/**
 * Two ways in:
 *
 *  - `?NP_id=…` — NOWPayments redirects here right after checkout; the payment
 *    status is verified server-side and, if paid, a secure download link is
 *    minted automatically. No email or database required.
 *  - `?receipt=…` — the durable link from the buyer's delivery email. The
 *    signed receipt is exchanged for a fresh download link, so a buyer can
 *    come back days later without contacting support.
 */
export default async function ThankYouPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const sp = await searchParams;
  const paymentId =
    (typeof sp.NP_id === "string" && sp.NP_id) ||
    (typeof sp.payment_id === "string" && sp.payment_id) ||
    "";

  let state: "paid" | "pending" | "unknown" = "unknown";
  let downloadUrl: string | null = null;
  let bookTitle = "";

  // ── Returning buyer: exchange a signed receipt for a fresh download link ──
  const receipt = typeof sp.receipt === "string" ? sp.receipt : "";
  if (receipt) {
    const verified = verifyReceiptToken(receipt);
    const item = verified.valid ? getPurchasable(verified.productId!) : undefined;
    if (item && verified.orderId) {
      const issuedCount = await countGrantsForOrder(verified.orderId).catch(() => 0);
      if (issuedCount < RECEIPT_MAX_ISSUES) {
        const issued = issueDownloadToken(item.id);
        await createGrant({
          jti: issued.jti,
          orderId: verified.orderId,
          bookId: item.id,
          maxDownloads: DOWNLOAD_MAX,
          expiresAt: issued.expiresAt,
        }).catch(() => {});
        downloadUrl = `/api/download/${item.id}?token=${issued.token}`;
        bookTitle = item.title;
        state = "paid";
      } else {
        await log("warn", "receipt_exhausted", { orderId: verified.orderId }).catch(() => {});
      }
    }
  }

  if (state === "unknown" && paymentId) {
    const status = await getPaymentStatus(paymentId).catch(() => null);
    if (status) {
      const bookId =
        status.order_id?.split("-").slice(0, -1).join("-") || status.order_id;
      const book = getPurchasable(bookId);
      if (isPaidStatus(status.payment_status) && book) {
        const issued = issueDownloadToken(book.id);
        await createGrant({
          jti: issued.jti,
          orderId: status.order_id,
          bookId: book.id,
          maxDownloads: DOWNLOAD_MAX,
          expiresAt: issued.expiresAt,
        }).catch(() => {});
        downloadUrl = `/api/download/${book.id}?token=${issued.token}`;
        bookTitle = book.title;
        state = "paid";
      } else {
        state = "pending";
        bookTitle = book?.title || "";
      }
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-6 py-24">
      <div className="mx-auto max-w-lg text-center">
        {state === "paid" ? (
          <>
            <span className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl border border-emerald/30 bg-emerald/10 text-emerald-light shadow-glow-emerald">
              <CheckCircle2 className="h-8 w-8" />
            </span>
            <h1 className="mt-8 font-display text-3xl font-semibold text-soft sm:text-4xl">
              Payment confirmed — thank you!
            </h1>
            <p className="mt-4 text-base leading-relaxed text-soft/60">
              Your purchase{bookTitle ? ` of ${bookTitle}` : ""} is complete.
              Download your book below. This link is private and expires shortly,
              so save the file to your device.
            </p>
            <div className="mt-8 flex flex-col justify-center gap-3 sm:flex-row">
              <Button asChild variant="gold" size="lg">
                <a href={downloadUrl!}>
                  <Download className="h-5 w-5" />
                  Download your book
                </a>
              </Button>
              <Button asChild variant="glass" size="lg">
                <a href={links.telegramUrl} target="_blank" rel="noopener noreferrer">
                  <MessageCircle className="h-5 w-5" />
                  Join the Telegram
                </a>
              </Button>
            </div>
          </>
        ) : state === "pending" ? (
          <>
            <span className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl border border-gold/30 bg-gold/10 text-gold-light">
              <Clock className="h-8 w-8" />
            </span>
            <h1 className="mt-8 font-display text-3xl font-semibold text-soft sm:text-4xl">
              Confirming your payment…
            </h1>
            <p className="mt-4 text-base leading-relaxed text-soft/60">
              Crypto payments can take a few minutes to confirm on the network.
              Refresh this page in a moment — your download will appear here as
              soon as it clears.
            </p>
            <div className="mt-8">
              <Button asChild variant="gold" size="lg">
                <a href={`/thank-you?NP_id=${paymentId}`}>Refresh</a>
              </Button>
            </div>
          </>
        ) : (
          <>
            <span className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl border border-white/15 bg-white/5 text-soft/60">
              <XCircle className="h-8 w-8" />
            </span>
            <h1 className="mt-8 font-display text-3xl font-semibold text-soft sm:text-4xl">
              Order status unavailable
            </h1>
            <p className="mt-4 text-base leading-relaxed text-soft/60">
              We couldn&apos;t read your payment reference here. If you completed a
              payment, your download link is also sent to the store owner — or
              reach out on Telegram and we&apos;ll deliver it right away.
            </p>
            <div className="mt-8 flex flex-col justify-center gap-3 sm:flex-row">
              <Button asChild variant="gold" size="lg">
                <a href={links.telegramUrl} target="_blank" rel="noopener noreferrer">
                  <MessageCircle className="h-5 w-5" />
                  Contact on Telegram
                </a>
              </Button>
              <Button asChild variant="glass" size="lg">
                <Link href="/">Back to the library</Link>
              </Button>
            </div>
          </>
        )}
      </div>
    </main>
  );
}
