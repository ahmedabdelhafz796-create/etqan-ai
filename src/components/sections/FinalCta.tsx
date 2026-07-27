"use client";

import { ArrowUpRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Reveal } from "@/components/ui/reveal";
import { useMarketplace } from "@/components/providers/I18nProvider";
import { automationBundles } from "@/config";

/**
 * Closing offer.
 *
 * It points at the free tool rather than the expensive bundle on
 * purpose. A first-time visitor to an unknown store will not spend $399
 * on a promise; they will spend nothing to read the code, and the code
 * is the argument.
 */
export function FinalCta() {
  const m = useMarketplace();
  const free = automationBundles.find((b) => b.free);

  return (
    <section className="relative py-24 sm:py-28">
      <div className="container-tight">
        <Reveal>
          <div className="relative overflow-hidden rounded-3xl border border-iris/25 bg-gradient-to-br from-iris/[0.12] via-night-800/60 to-transparent px-7 py-14 text-center sm:px-14">
            <div
              aria-hidden
              className="canvas-dots pointer-events-none absolute inset-0 opacity-40"
            />
            <div
              aria-hidden
              className="pointer-events-none absolute left-1/2 top-0 h-64 w-[620px] -translate-x-1/2 bg-[radial-gradient(ellipse,rgba(99,102,241,0.22),transparent_65%)] blur-2xl"
            />

            <div className="relative">
              <h2 className="mx-auto max-w-2xl font-display text-3xl font-bold leading-tight tracking-tight sm:text-[2.5rem]">
                {m.finalCta.title1}{" "}
                <span className="text-gradient-iris">
                  {m.finalCta.titleAccent}
                </span>
              </h2>
              <p className="mx-auto mt-5 max-w-xl text-[15px] leading-relaxed text-white/55">
                {m.finalCta.body}
              </p>

              <div className="mt-9 flex flex-col items-center justify-center gap-3 sm:flex-row">
                {free && (
                  <Button asChild variant="iris" size="xl" className="w-full sm:w-auto">
                    <a
                      href={free.checkoutUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {m.finalCta.primary}
                      <ArrowUpRight className="h-5 w-5" aria-hidden />
                    </a>
                  </Button>
                )}
                <Button asChild variant="glass" size="xl" className="w-full sm:w-auto">
                  <a href="#catalog">{m.finalCta.secondary}</a>
                </Button>
              </div>
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
