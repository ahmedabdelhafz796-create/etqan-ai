"use client";

import { SectionHeading } from "@/components/ui/section-heading";
import { useT } from "@/components/providers/I18nProvider";
import { automationBundles, automationProof } from "@/config";
import { Reveal } from "@/components/ui/reveal";
import { Button } from "@/components/ui/button";
import { Check, ArrowUpRight } from "lucide-react";

/**
 * The automation product line.
 *
 * Deliberately quieter than the book store above it. Books are the emotional
 * sell — an institutional edge, a founding-price window. These are bought by
 * people solving an operational problem, and that audience is put off by
 * urgency framing, so there is no countdown and no discount language here.
 *
 * Checkout is external (Lemon Squeezy) rather than going through the site's
 * own NOWPayments flow, which is why these link out instead of using
 * BuyButton. The note under the grid says so plainly rather than surprising
 * someone at the click.
 */
export function AutomationStore() {
  const t = useT();
  const a = t.automation;

  return (
    <section
      id="automation"
      className="relative scroll-mt-24 border-t border-white/[0.06] py-24 sm:py-28"
    >
      {/* Cooler wash than the gold used for books, so the eye registers a
          different product line without needing to read the heading. */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_60%_40%_at_50%_0%,rgba(99,102,241,0.07),transparent_70%)]"
      />

      <div className="container-tight relative">
        <SectionHeading
          eyebrow={a.eyebrow}
          title={
            <>
              {a.title1}{" "}
              <span className="text-gradient-gold">{a.titleGold}</span>
            </>
          }
          description={a.description}
        />

        {/* The proof strip. This is the strongest asset the product line has —
            competitors claim their templates are tested; none publish counts. */}
        <Reveal>
          <div className="mx-auto mt-10 flex max-w-2xl flex-wrap items-center justify-center gap-x-8 gap-y-4 rounded-2xl border border-white/[0.08] bg-white/[0.02] px-6 py-5 text-center">
            <Stat value={automationProof.behaviouralTests} label={`${a.proofLabel} · ${a.proofSuffix}`} />
            <Divider />
            <Stat value={automationProof.workflows} label={a.workflows} />
            <Divider />
            <Stat value={automationProof.nodes} label="nodes" />
          </div>
        </Reveal>

        <div className="mt-14 grid gap-5 sm:grid-cols-2">
          {automationBundles.map((b, i) => {
            const copy = a.bundles[b.id as keyof typeof a.bundles];
            const audience = a[b.audience as keyof typeof a] as string;

            return (
              <Reveal key={b.id} delay={i * 0.05}>
                <article
                  className={[
                    "flex h-full flex-col rounded-2xl border p-6 transition-colors sm:p-7",
                    b.featured
                      ? "border-gold/40 bg-gradient-to-b from-gold/[0.07] to-transparent sm:col-span-2"
                      : b.free
                        ? "border-dashed border-white/15 bg-white/[0.015]"
                        : "border-white/[0.08] bg-white/[0.02] hover:border-white/[0.14]",
                  ].join(" ")}
                >
                  {b.featured && (
                    <span className="mb-4 inline-flex w-fit rounded-full bg-gold px-3 py-1 text-[11px] font-bold uppercase tracking-wider text-black">
                      {a.bestValue}
                    </span>
                  )}

                  <h3 className="text-lg font-bold tracking-tight sm:text-xl">
                    {b.name}
                  </h3>

                  <p className="mt-1.5 text-sm italic text-gold/70">{audience}</p>

                  <div className="mt-4 flex items-baseline gap-2">
                    <span className="text-3xl font-bold tracking-tight">
                      {b.price === null ? a.free : `$${b.price}`}
                    </span>
                    <span className="text-sm text-white/40">
                      · {b.workflowCount} {a.workflows}
                    </span>
                  </div>

                  <ul className="mt-5 flex-1 space-y-2.5">
                    {b.highlights.map((h) => (
                      <li key={h} className="flex gap-2.5 text-sm text-white/60">
                        <Check
                          className="mt-0.5 h-4 w-4 shrink-0 text-gold/60"
                          aria-hidden
                        />
                        <span>{copy[h as keyof typeof copy]}</span>
                      </li>
                    ))}
                  </ul>

                  <Button
                    asChild
                    variant={b.free ? "outline" : "gold"}
                    className="mt-6 w-full"
                  >
                    <a
                      href={b.checkoutUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {b.free ? a.getFree : a.getBundle}
                      <ArrowUpRight className="h-4 w-4" aria-hidden />
                    </a>
                  </Button>
                </article>
              </Reveal>
            );
          })}
        </div>

        <p className="mt-8 text-center text-xs text-white/35">{a.payNote}</p>
      </div>
    </section>
  );
}

function Stat({ value, label }: { value: number; label: string }) {
  return (
    <div>
      <div className="text-2xl font-bold tracking-tight text-gold sm:text-3xl">
        {value}
      </div>
      <div className="mt-0.5 text-[11px] uppercase tracking-wider text-white/40">
        {label}
      </div>
    </div>
  );
}

function Divider() {
  return <div aria-hidden className="hidden h-8 w-px bg-white/10 sm:block" />;
}
