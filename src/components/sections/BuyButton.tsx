"use client";

import * as React from "react";
import { Loader2, Lock, ShoppingCart } from "lucide-react";
import { Button, type ButtonProps } from "@/components/ui/button";
import { useSiteConfig } from "@/components/providers/SiteConfigProvider";
import { useT } from "@/components/providers/I18nProvider";
import { type Book } from "@/config";
import { cn } from "@/lib/utils";

const PLACEHOLDER = "PAYMENT_URL_PLACEHOLDER";

interface Props extends Pick<ButtonProps, "variant" | "size" | "className"> {
  book: Book;
  label?: string;
}

/**
 * Buy Now button.
 *
 * Flow (all real, no fake success):
 *  1. Attempts to create a NOWPayments invoice via /api/payment.
 *     If the server has NOWPAYMENTS_API_KEY set, the buyer is
 *     redirected to the hosted crypto checkout.
 *  2. Falls back to NEXT_PUBLIC_PAYMENT_URL (links.paymentUrl) when set
 *     to a real value.
 *  3. If neither is configured yet, shows a graceful "coming soon"
 *     state — nothing is faked.
 *
 * To go live you only replace ONE variable: PAYMENT_URL_PLACEHOLDER
 * (or add the NOWPayments API key in .env.local).
 */
export function BuyButton({
  book,
  label,
  variant,
  size = "lg",
  className,
}: Props) {
  const t = useT();
  const [state, setState] = React.useState<"idle" | "loading" | "unavailable">(
    "idle"
  );
  const { paymentUrl } = useSiteConfig();
  const buyLabel = label ?? t.buy.now;

  const accentVariant =
    variant ?? (book.cover.accent === "emerald" ? "emerald" : "gold");

  async function handleBuy() {
    if (state === "loading") return;
    setState("loading");

    // 1) Try the server-side NOWPayments invoice.
    try {
      const res = await fetch("/api/payment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ bookId: book.id }),
      });
      if (res.ok) {
        const data = (await res.json()) as { checkoutUrl?: string };
        if (data.checkoutUrl) {
          window.location.href = data.checkoutUrl;
          return;
        }
      }
    } catch {
      /* fall through to placeholder */
    }

    // 2) Fall back to a configured direct payment link.
    if (paymentUrl && paymentUrl !== PLACEHOLDER) {
      window.location.href = paymentUrl;
      return;
    }

    // 3) Nothing configured yet — no fake success.
    setState("unavailable");
    setTimeout(() => setState("idle"), 4000);
  }

  return (
    <div className="w-full">
      <Button
        variant={accentVariant}
        size={size}
        onClick={handleBuy}
        disabled={state === "loading"}
        className={cn("w-full", className)}
        aria-label={`${buyLabel} — ${book.title}`}
      >
        {state === "loading" ? (
          <>
            <Loader2 className="h-5 w-5 animate-spin" />
            {t.buy.loading}
          </>
        ) : (
          <>
            <ShoppingCart className="h-5 w-5" />
            {buyLabel}
          </>
        )}
      </Button>

      <p className="mt-2 flex items-center justify-center gap-1.5 text-center text-xs text-soft/45">
        <Lock className="h-3 w-3" />
        {state === "unavailable" ? t.buy.unavailable : t.buy.secure}
      </p>
    </div>
  );
}
