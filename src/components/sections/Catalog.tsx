"use client";

import * as React from "react";
import {
  ArrowUpRight,
  Bot,
  Check,
  ChevronDown,
  Clock,
  Hand,
  Package,
  ShieldAlert,
  Sparkles,
  Target,
  TrendingUp,
  Truck,
  Wallet,
  Webhook,
  Wrench,
  type LucideIcon,
} from "lucide-react";
import { SectionHeading } from "@/components/ui/section-heading";
import { Button } from "@/components/ui/button";
import { Reveal } from "@/components/ui/reveal";
import { BundleDiagram } from "@/components/visuals/BundleDiagram";
import { useMarketplace } from "@/components/providers/I18nProvider";
import {
  automationBundles,
  workflowBySlug,
  type AutomationBundle,
  type WorkflowSpec,
} from "@/config";

/**
 * The primary storefront: AI systems, tools and templates.
 *
 * Each product gets a real presentation rather than a spec line — a
 * diagram, a plain-language summary, the outcomes it produces, the
 * situations people buy it for, and an expandable list of every workflow
 * actually inside it with its node count and trigger type. That list is
 * generated from `config.workflows`, which mirrors `suite/dist`, so the
 * page cannot advertise a workflow the ZIP does not contain.
 *
 * Checkout is Lemon Squeezy for every bundle here. The trading library
 * further down the page uses its own crypto checkout and shares nothing
 * with this section — no components, no payment code, no styling.
 */

const CATEGORY_ICON: Record<WorkflowSpec["category"], LucideIcon> = {
  delivery: Truck,
  protection: ShieldAlert,
  agent: Bot,
  growth: TrendingUp,
  finance: Wallet,
  ops: Wrench,
};

const TRIGGER_ICON: Record<WorkflowSpec["trigger"], LucideIcon> = {
  webhook: Webhook,
  schedule: Clock,
  manual: Hand,
  error: ShieldAlert,
};

export function Catalog() {
  const m = useMarketplace();

  return (
    <section id="catalog" className="relative scroll-mt-24 py-24 sm:py-28">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(ellipse_70%_45%_at_50%_0%,rgba(99,102,241,0.09),transparent_70%)]"
      />

      <div className="container-tight">
        <SectionHeading
          eyebrow={m.catalog.eyebrow}
          title={
            <>
              {m.catalog.title1}{" "}
              <span className="text-gradient-iris">{m.catalog.titleAccent}</span>
            </>
          }
          description={m.catalog.description}
        />

        <div className="mt-14 space-y-6">
          {automationBundles.map((b, i) => (
            <Reveal key={b.id} delay={Math.min(i * 0.05, 0.2)}>
              <BundleCard bundle={b} />
            </Reveal>
          ))}
        </div>

        <p className="mt-10 text-center text-xs leading-relaxed text-white/35">
          {m.catalog.payNote}
        </p>
      </div>
    </section>
  );
}

function BundleCard({ bundle: b }: { bundle: AutomationBundle }) {
  const m = useMarketplace();
  const [open, setOpen] = React.useState(false);
  const copy = m.bundles[b.id as keyof typeof m.bundles];
  const panelId = `wf-${b.id}`;

  return (
    <article
      className={[
        "group relative overflow-hidden rounded-3xl border transition-colors duration-300",
        b.featured
          ? "border-iris/35 bg-gradient-to-br from-iris/[0.10] via-white/[0.015] to-transparent"
          : b.free
            ? "border-dashed border-white/[0.14] bg-white/[0.012] hover:border-white/25"
            : "border-white/[0.08] bg-white/[0.02] hover:border-iris/25",
      ].join(" ")}
    >
      <div className="grid gap-8 p-6 sm:p-8 lg:grid-cols-[1.35fr_1fr] lg:gap-10">
        {/* ── left: the argument ── */}
        <div className="flex flex-col">
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded-md border border-white/10 bg-white/[0.04] px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.14em] text-white/50">
              {m.catalog.kinds[b.kind]}
            </span>
            {b.featured && (
              <span className="inline-flex items-center gap-1 rounded-md bg-iris px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.14em] text-white">
                <Sparkles className="h-3 w-3" aria-hidden />
                {m.catalog.bestValue}
              </span>
            )}
          </div>

          <h3 className="mt-4 font-display text-2xl font-bold tracking-tight sm:text-[1.75rem]">
            {b.name}
          </h3>
          <p className="mt-1.5 text-[15px] text-iris-light/80">{copy.tagline}</p>

          <p className="mt-5 max-w-2xl text-[15px] leading-relaxed text-white/55">
            {copy.summary}
          </p>

          <h4 className="mt-7 text-[11px] font-bold uppercase tracking-[0.14em] text-white/35">
            {m.catalog.outcomesLabel}
          </h4>
          <ul className="mt-3 space-y-2.5">
            {copy.outcomes.map((o) => (
              <li
                key={o}
                className="flex gap-3 text-[14.5px] leading-relaxed text-white/65"
              >
                <Check
                  className="mt-[5px] h-4 w-4 shrink-0 text-iris-mid"
                  aria-hidden
                />
                <span>{o}</span>
              </li>
            ))}
          </ul>

          <h4 className="mt-7 text-[11px] font-bold uppercase tracking-[0.14em] text-white/35">
            {m.catalog.useCasesLabel}
          </h4>
          <ul className="mt-3 flex flex-wrap gap-2">
            {copy.useCases.map((u) => (
              <li
                key={u}
                className="inline-flex items-start gap-2 rounded-lg border border-white/[0.07] bg-white/[0.025] px-3 py-2 text-[13px] leading-snug text-white/55"
              >
                <Target className="mt-[3px] h-3.5 w-3.5 shrink-0 text-aqua/70" aria-hidden />
                {u}
              </li>
            ))}
          </ul>
        </div>

        {/* ── right: the offer ──
            Centred rather than top-aligned: the left column is much taller,
            so anchoring the price block to the top leaves a column of dead
            space beside every card. */}
        <div className="flex flex-col lg:justify-center lg:self-center lg:pl-2">
          <BundleDiagram
            kind={b.kind}
            accent={b.free ? "aqua" : "iris"}
            className="h-36 w-full lg:h-44"
          />

          <div className="mt-6 flex items-baseline gap-3">
            <span className="font-display text-[2.75rem] font-bold leading-none tracking-tight">
              {b.price === null ? m.catalog.free : `$${b.price}`}
            </span>
          </div>
          <p className="mt-2 flex items-center gap-2 font-mono text-[12.5px] text-white/40">
            <Package className="h-3.5 w-3.5" aria-hidden />
            {/* <bdi> so the bidi algorithm cannot merge the two counts
                across the separator when the page renders right-to-left. */}
            <bdi>
              {b.workflowCount} {m.catalog.workflowsLabel}
            </bdi>{" "}
            ·{" "}
            <bdi>
              {b.nodes} {m.catalog.nodesLabel}
            </bdi>
          </p>

          <Button
            asChild
            variant={b.free ? "iris-outline" : "iris"}
            size="lg"
            className="mt-6 w-full"
          >
            <a href={b.checkoutUrl} target="_blank" rel="noopener noreferrer">
              {b.free ? m.catalog.getFree : m.catalog.getBundle}
              <ArrowUpRight className="h-4 w-4" aria-hidden />
            </a>
          </Button>

          <button
            type="button"
            onClick={() => setOpen((v) => !v)}
            aria-expanded={open}
            aria-controls={panelId}
            className="mt-3 flex w-full items-center justify-center gap-1.5 rounded-full px-4 py-2.5 text-[13px] font-medium text-white/45 transition-colors hover:text-white/80"
          >
            {m.catalog.seeInside}
            <ChevronDown
              className={`h-4 w-4 transition-transform duration-300 ${open ? "rotate-180" : ""}`}
              aria-hidden
            />
          </button>
        </div>
      </div>

      {/* ── the manifest: what is actually in the ZIP ── */}
      <div
        id={panelId}
        hidden={!open}
        className="border-t border-white/[0.07] bg-night-900/40 px-6 py-7 sm:px-8"
      >
        <h4 className="text-[11px] font-bold uppercase tracking-[0.14em] text-white/35">
          {m.catalog.includesLabel} · {b.workflows.length}
        </h4>
        <ul className="mt-4 grid gap-2.5 sm:grid-cols-2">
          {b.workflows.map((slug) => {
            const spec = workflowBySlug[slug];
            const Icon = CATEGORY_ICON[spec.category];
            const TrigIcon = TRIGGER_ICON[spec.trigger];
            return (
              <li
                key={slug}
                className="flex gap-3 rounded-xl border border-white/[0.06] bg-white/[0.02] p-3.5"
              >
                <span className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-iris/10 text-iris-light">
                  <Icon className="h-4 w-4" aria-hidden />
                </span>
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
                    <span className="font-mono text-[12.5px] font-semibold text-white/85">
                      {slug}
                    </span>
                    <span className="inline-flex items-center gap-1 rounded border border-white/10 px-1.5 py-px text-[10px] text-white/40">
                      <TrigIcon className="h-2.5 w-2.5" aria-hidden />
                      {m.triggers[spec.trigger]}
                    </span>
                    <span className="rounded border border-white/10 px-1.5 py-px font-mono text-[10px] text-white/40">
                      {spec.nodes} {m.catalog.nodesLabel}
                    </span>
                  </div>
                  <p className="mt-1.5 text-[13px] leading-relaxed text-white/50">
                    {m.workflows[slug as keyof typeof m.workflows]}
                  </p>
                </div>
              </li>
            );
          })}
        </ul>
      </div>
    </article>
  );
}
