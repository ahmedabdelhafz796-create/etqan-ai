import type { Metadata } from "next";
import Link from "next/link";
import { CheckCircle2, Download, MessageCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { links } from "@/config";

export const metadata: Metadata = {
  title: "Thank You",
  description: "Your order is confirmed.",
  robots: { index: false, follow: false },
};

export default function ThankYouPage() {
  return (
    <main className="flex min-h-screen items-center justify-center px-6 py-24">
      <div className="mx-auto max-w-lg text-center">
        <span className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl border border-emerald/30 bg-emerald/10 text-emerald-light shadow-glow-emerald">
          <CheckCircle2 className="h-8 w-8" />
        </span>
        <h1 className="mt-8 font-display text-3xl font-semibold text-soft sm:text-4xl">
          Thank you for your order.
        </h1>
        <p className="mt-4 text-base leading-relaxed text-soft/60">
          Your payment is being confirmed. Your download link and access details
          are on their way to your email — check your inbox (and spam) in the
          next few minutes.
        </p>

        <div className="mt-10 flex flex-col justify-center gap-3 sm:flex-row">
          <Button asChild variant="gold" size="lg">
            <a href={links.telegramUrl} target="_blank" rel="noopener noreferrer">
              <MessageCircle className="h-5 w-5" />
              Join the Telegram
            </a>
          </Button>
          <Button asChild variant="glass" size="lg">
            <Link href="/">
              <Download className="h-5 w-5" />
              Back to the library
            </Link>
          </Button>
        </div>
      </div>
    </main>
  );
}
