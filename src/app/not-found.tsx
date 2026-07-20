import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <main className="flex min-h-screen items-center justify-center px-6 py-24 text-center">
      <div>
        <p className="font-mono text-sm uppercase tracking-[0.3em] text-gold-light">
          404 · Off the chart
        </p>
        <h1 className="mt-4 font-display text-4xl font-semibold text-soft sm:text-5xl">
          This page took a stop-loss.
        </h1>
        <p className="mx-auto mt-4 max-w-md text-soft/60">
          The page you&apos;re looking for doesn&apos;t exist or has moved. Let&apos;s
          get you back to the library.
        </p>
        <div className="mt-8">
          <Button asChild variant="gold" size="lg">
            <Link href="/">Back to home</Link>
          </Button>
        </div>
      </div>
    </main>
  );
}
