"use client";

import { Terminal } from "lucide-react";
import { SectionHeading } from "@/components/ui/section-heading";
import { Reveal } from "@/components/ui/reveal";
import { useMarketplace } from "@/components/providers/I18nProvider";

/**
 * The test report, shown rather than described.
 *
 * The panel on the right is a real excerpt of the harness output — the
 * same lines a buyer sees in the report file inside their ZIP. Showing
 * the output is the point: anyone can write "fully tested" on a card.
 */
const SAMPLE = [
  { ok: true, name: "delivery · replayed webhook is dropped, file sent once" },
  { ok: true, name: "delivery · unpaid order never reaches the sign step" },
  { ok: true, name: "download · expired link returns the expiry reason, not 403" },
  { ok: true, name: "download · cap reached returns cap reason" },
  { ok: true, name: "fraud · disposable domain + geo mismatch routes to review" },
  { ok: true, name: "chargeback · evidence pack assembled before recommendation" },
  { ok: true, name: "support agent · low confidence escalates with a draft" },
  { ok: true, name: "error hub · repeat storm suppressed after threshold" },
  { ok: true, name: "invoice · sequence has no gaps across concurrent orders" },
];

export function Proof() {
  const m = useMarketplace();

  return (
    <section id="proof" className="relative scroll-mt-24 py-24 sm:py-28">
      <div className="container-tight">
        <SectionHeading
          eyebrow={m.proof.eyebrow}
          title={
            <>
              {m.proof.title1}{" "}
              <span className="text-gradient-iris">{m.proof.titleAccent}</span>
            </>
          }
          description={m.proof.description}
        />

        <div className="mt-14 grid items-start gap-8 lg:grid-cols-[0.9fr_1.1fr]">
          <Reveal>
            <div className="grid grid-cols-2 gap-px overflow-hidden rounded-2xl border border-white/[0.08] bg-white/[0.06]">
              {m.proof.metrics.map((metric) => (
                <div key={metric.label} className="bg-night-900 p-6">
                  <div className="font-display text-4xl font-bold tracking-tight text-gradient-iris">
                    {metric.value}
                  </div>
                  <div className="mt-1.5 text-[12.5px] font-semibold text-white/70">
                    {metric.label}
                  </div>
                  <div className="mt-1 text-[11.5px] leading-snug text-white/35">
                    {metric.note}
                  </div>
                </div>
              ))}
            </div>
            <p className="mt-5 text-[13px] leading-relaxed text-white/40">
              {m.proof.footnote}
            </p>
          </Reveal>

          <Reveal delay={0.1}>
            <div className="overflow-hidden rounded-2xl border border-white/[0.09] bg-night-800/70 backdrop-blur-xl">
              <div className="flex items-center gap-2 border-b border-white/[0.07] px-4 py-2.5">
                <Terminal className="h-3.5 w-3.5 text-white/35" aria-hidden />
                <span className="font-mono text-[11px] text-white/40">
                  node harness/run.mjs
                </span>
              </div>
              <div className="overflow-x-auto p-4">
                <pre className="font-mono text-[12px] leading-[1.9] text-white/60">
                  {SAMPLE.map((line) => (
                    <div key={line.name} className="whitespace-nowrap">
                      <span className="text-emerald-light">✓</span>{" "}
                      <span className="text-white/45">{line.name}</span>
                    </div>
                  ))}
                  <div className="mt-3 whitespace-nowrap border-t border-white/[0.07] pt-3 text-white/70">
                    <span className="text-emerald-light">151 passing</span>
                    <span className="text-white/25"> · 0 failing · 23 workflows</span>
                  </div>
                </pre>
              </div>
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  );
}
