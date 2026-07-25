"use client";

import * as React from "react";
import { CreditCard, Loader2, Lock, ShoppingCart } from "lucide-react";
import { Button } from "@/components/ui/button";

/**
 * Checkout control for a course page.
 *
 * Crypto (NOWPayments) is always offered; the card/PayPal button only renders
 * when Lemon Squeezy is actually configured on the server, so a buyer is never
 * shown a payment method that cannot complete.
 */
export function CourseBuy({
  productId,
  accent,
  cardEnabled,
}: {
  productId: string;
  accent: "gold" | "emerald";
  cardEnabled: boolean;
}) {
  const [state, setState] = React.useState<"idle" | "crypto" | "card" | "unavailable">("idle");

  async function buy(provider?: "card") {
    if (state === "crypto" || state === "card") return;
    setState(provider === "card" ? "card" : "crypto");
    try {
      const res = await fetch("/api/payment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ bookId: productId, ...(provider ? { provider } : {}) }),
      });
      if (res.ok) {
        const d = (await res.json()) as { checkoutUrl?: string };
        if (d.checkoutUrl) {
          window.location.href = d.checkoutUrl;
          return;
        }
      }
    } catch {
      /* fall through to the honest unavailable state */
    }
    setState("unavailable");
    setTimeout(() => setState("idle"), 3500);
  }

  return (
    <div className="w-full">
      <div className="flex flex-col gap-3 sm:flex-row">
        <Button
          variant={accent}
          size="lg"
          onClick={() => buy()}
          disabled={state === "crypto" || state === "card"}
          className="w-full"
        >
          {state === "crypto" ? (
            <>
              <Loader2 className="h-5 w-5 animate-spin" /> Opening checkout…
            </>
          ) : (
            <>
              <ShoppingCart className="h-5 w-5" /> Get this course
            </>
          )}
        </Button>
        {cardEnabled && (
          <Button
            variant="glass"
            size="lg"
            onClick={() => buy("card")}
            disabled={state === "crypto" || state === "card"}
            className="w-full sm:w-auto"
          >
            {state === "card" ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" /> Opening…
              </>
            ) : (
              <>
                <CreditCard className="h-5 w-5" /> Pay by card
              </>
            )}
          </Button>
        )}
      </div>
      <p className="mt-3 flex items-center gap-1.5 text-[12px] text-soft/50">
        <Lock className="h-3.5 w-3.5" />
        {state === "unavailable"
          ? "Checkout is not available right now — please try again shortly."
          : "Encrypted checkout · instant download · link sent to your email"}
      </p>
    </div>
  );
}
