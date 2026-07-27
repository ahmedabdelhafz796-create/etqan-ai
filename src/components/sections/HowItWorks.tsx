"use client";

import { Download, FileCog, Stethoscope, type LucideIcon } from "lucide-react";
import { SectionHeading } from "@/components/ui/section-heading";
import { Reveal } from "@/components/ui/reveal";
import { useMarketplace } from "@/components/providers/I18nProvider";

const ICONS: LucideIcon[] = [Download, FileCog, Stethoscope];

/**
 * Three steps from download to running.
 *
 * The objection this answers is the real one for a template product:
 * "I'll buy it and then spend a weekend failing to install it." Naming
 * the Setup Checker as step three turns that fear into a feature — the
 * install verifies itself.
 */
export function HowItWorks() {
  const m = useMarketplace();

  return (
    <section id="how" className="relative scroll-mt-24 py-24 sm:py-28">
      <div className="container-tight">
        <SectionHeading
          eyebrow={m.how.eyebrow}
          title={
            <>
              {m.how.title1}{" "}
              <span className="text-gradient-iris">{m.how.titleAccent}</span>
            </>
          }
          description={m.how.description}
        />

        <div className="relative mt-14">
          {/* The connecting rail. Decorative, desktop only. */}
          <div
            aria-hidden
            className="pointer-events-none absolute inset-x-[16%] top-[46px] hidden h-px bg-gradient-to-r from-transparent via-iris/30 to-transparent lg:block"
          />

          <ol className="grid gap-6 lg:grid-cols-3">
            {m.how.steps.map((s, i) => {
              const Icon = ICONS[i];
              return (
                <Reveal key={s.n} delay={i * 0.08}>
                  <li className="panel relative h-full p-7">
                    <div className="flex items-center gap-4">
                      <span className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl border border-iris/25 bg-night-900 text-iris-light">
                        <Icon className="h-6 w-6" aria-hidden />
                      </span>
                      <span className="font-mono text-3xl font-bold text-white/12">
                        {s.n}
                      </span>
                    </div>
                    <h3 className="mt-6 text-lg font-bold tracking-tight">
                      {s.title}
                    </h3>
                    <p className="mt-2.5 text-[14.5px] leading-relaxed text-white/55">
                      {s.body}
                    </p>
                  </li>
                </Reveal>
              );
            })}
          </ol>
        </div>
      </div>
    </section>
  );
}
