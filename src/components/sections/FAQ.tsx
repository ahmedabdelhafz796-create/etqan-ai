"use client";

import { SectionHeading } from "@/components/ui/section-heading";
import { Reveal } from "@/components/ui/reveal";
import { useMarketplace } from "@/components/providers/I18nProvider";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

/**
 * FAQ for the automation product line.
 *
 * The trading-library questions that used to live here (formats,
 * signals, "is this financial advice") moved out with the rest of that
 * product; the book section carries its own copy. What is left answers
 * the objections a technical buyer actually raises — what is in the ZIP,
 * whether it runs self-hosted, what "tested" means, and the licence.
 */
export function FAQ() {
  const m = useMarketplace();

  return (
    <section id="faq" className="scroll-mt-24 py-24 sm:py-28">
      <div className="container-tight">
        <SectionHeading
          eyebrow={m.faq.eyebrow}
          title={m.faq.title}
          description={m.faq.description}
        />

        <Reveal className="mx-auto mt-12 max-w-3xl">
          <Accordion type="single" collapsible className="space-y-3">
            {m.faq.items.map((f, i) => (
              <AccordionItem key={f.q} value={`faq-${i}`}>
                <AccordionTrigger>{f.q}</AccordionTrigger>
                <AccordionContent>
                  <p className="leading-relaxed">{f.a}</p>
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </Reveal>
      </div>
    </section>
  );
}
