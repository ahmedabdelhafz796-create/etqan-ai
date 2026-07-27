"use client";

import { SectionHeading } from "@/components/ui/section-heading";
import { useT } from "@/components/providers/I18nProvider";
import { automationBundles, automationProof } from "@/config";
import { Reveal } from "@/components/ui/reveal";
import { Button } from "@/components/ui/button";
import { SystemGlyph } from "@/components/visuals/SystemGlyph";
import { Check, ArrowUpRight, ShieldCheck, Zap, Layers } from "lucide-react";

/**
 * The primary product line: AI systems, tools and templates.
 *
 * Presentation notes worth keeping:
 *
 * · No countdown and no discount language. The trading library below sells on
 *   an offer window; this audience is buying to solve an operational problem
 *   and urgency framing reads as pressure rather than value.
 *
 * · Each card leads with a generated diagram rather than a screenshot. A
 *   workflow canvas photographed at card size is unreadable grey rectangles;
 *   the diagram communicates scale and shape instantly.
 *
 * · Checkout links out to Lemon Squeezy. The trading library uses the site's
 *   own NOWPayments flow. The two never mix, and the note under the grid says
 *   so rather than surprising anyone at the click.
 */
export function AutomationStore() {
  const t = useT();
  const a = t.automation;

  return (
    <section
      id="automation"
      className="relative scroll-mt-24 py-24 sm:py-32"
    >
      {/* Cooler wash than the gold used downstream for books, so the eye
          registers a different product line before reading the heading. */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(ellipse_65%_45%_at_50%_0%,rgba(99,102,241,0.08),transparent_70%)]"
      />

      <div className="container-tight">
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

        {/* Proof strip. The strongest asset this product line has — every
            competitor claims their templates are tested; none publish counts. */}
        <Reveal>
          <div className="mx-auto mt-12 grid max-w-3xl grid-cols-2 gap-px overflow-hidden rounded-2xl border border-white/[0.08] bg-white/[0.06] sm:grid-cols-4">
            <Stat value={automationProof.behaviouralTests} label={a.proofLabel} />
            <Stat value={automationProof.gateProbes} label={a.gateLabel} />
            <Stat value={automationProof.workflows} label={a.workflows} />
            <Stat value={automationProof.nodes} label={a.nodesLabel} />
          </div>
        </Reveal>

        {/* Standards row — the three guarantees that justify the price. */}
        <Reveal delay={0.08}>
          <div className="mx-auto mt-6 flex max-w-3xl flex-wrap items-center justify-center gap-x-7 gap-y-3 text-[13px] text-white/45">
            <Pill icon={ShieldCheck} label={a.stdSecrets} />
            <Pill icon={Zap} label={a.stdRetry} />
            <Pill icon={Layers} label={a.stdErrors} />
          </div>
        </Reveal>

        <div className="mt-16 grid gap-6 lg:grid-cols-2">
          {automationBundles.map((b, i) => {
            const copy = a.bundles[b.id as keyof typeof a.bundles];
            const audience = a[b.audience as keyof typeof a] as string;
            const isWide = !!b.featured;

            return (
              <Reveal
                key={b.id}
                delay={i * 0.05}
                // The grid child is this wrapper, not the article inside it —
                // the column span has to live here or the featured card
                // silently renders at half width with dead space beside it.
                className={b.featured ? "lg:col-span-2" : undefined}
              >
                <article
                  className={[
                    "group relative flex h-full flex-col overflow-hidden rounded-3xl border p-7 transition-all duration-300 sm:p-8",
                    b.featured
                      ? "border-gold/40 bg-gradient-to-b from-gold/[0.08] via-white/[0.02] to-transparent"
                      : b.free
                        ? "border-dashed border-white/[0.14] bg-white/[0.015] hover:border-white/25"
                        : "border-white/[0.08] bg-white/[0.02] hover:-translate-y-0.5 hover:border-gold/30",
                  ].join(" ")}
                >
                  <div
                    className={
                      isWide
                        ? "grid items-center gap-8 lg:grid-cols-[1.15fr_1fr]"
                        : ""
                    }
                  >
                    <div className="flex flex-col">
                      <div className="flex flex-wrap items-center gap-2.5">
                        <span className="rounded-md border border-white/10 bg-white/[0.04] px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.14em] text-white/50">
                          {a.kinds[b.kind]}
                        </span>
                        {b.featured && (
                          <span className="rounded-md bg-gold px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.14em] text-night-900">
                            {a.bestValue}
                          </span>
                        )}
                      </div>

                      <h3 className="mt-4 text-xl font-bold tracking-tight sm:text-2xl">
                        {b.name}
                      </h3>
                      <p className="mt-2 text-sm italic text-gold/70">
                        {audience}
                      </p>

                      {!isWide && (
                        <SystemGlyph
                          kind={b.kind}
                          className="mt-6 h-24 w-full"
                        />
                      )}

                      <div className="mt-6 flex flex-wrap items-baseline gap-x-3 gap-y-1">
                        <span className="text-4xl font-bold tracking-tight">
                          {b.price === null ? a.free : `$${b.price}`}
                        </span>
                        <span className="text-sm text-white/40">
                          {b.workflowCount} {a.workflows} · {b.nodes}{" "}
                          {a.nodesLabel}
                        </span>
                      </div>

                      <ul className="mt-6 flex-1 space-y-3">
                        {b.highlights.map((h) => (
                          <li
                            key={h}
                            className="flex gap-3 text-[14.5px] leading-relaxed text-white/60"
                          >
                            <Check
                              className="mt-1 h-4 w-4 shrink-0 text-gold/60"
                              aria-hidden
                            />
                            <span>{copy[h as keyof typeof copy]}</span>
                          </li>
                        ))}
                      </ul>

                      <Button
                        asChild
                        variant={b.free ? "outline" : "gold"}
                        className="mt-8 w-full"
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
                    </div>

                    {isWide && (
                      <SystemGlyph
                        kind={b.kind}
                        className="hidden h-64 w-full lg:block"
                      />
                    )}
                  </div>
                </article>
              </Reveal>
            );
          })}
        </div>

        <p className="mt-10 text-center text-xs text-white/35">{a.payNote}</p>
      </div>
    </section>
  );
}

function Stat({ value, label }: { value: number; label: string }) {
  return (
    <div className="bg-night-800 px-4 py-6 text-center">
      <div className="text-2xl font-bold tracking-tight text-gold sm:text-3xl">
        {value}
      </div>
      <div className="mt-1 text-[10px] uppercase leading-tight tracking-[0.12em] text-white/40">
        {label}
      </div>
    </div>
  );
}

function Pill({
  icon: Icon,
  label,
}: {
  icon: typeof ShieldCheck;
  label: string;
}) {
  return (
    <span className="inline-flex items-center gap-2">
      <Icon className="h-3.5 w-3.5 text-gold/50" aria-hidden />
      {label}
    </span>
  );
}
