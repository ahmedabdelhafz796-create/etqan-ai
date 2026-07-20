import * as React from "react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Reveal } from "@/components/ui/reveal";

interface SectionHeadingProps {
  eyebrow?: string;
  title: React.ReactNode;
  description?: React.ReactNode;
  align?: "center" | "left";
  className?: string;
}

export function SectionHeading({
  eyebrow,
  title,
  description,
  align = "center",
  className,
}: SectionHeadingProps) {
  return (
    <div
      className={cn(
        "mx-auto max-w-2xl",
        align === "center" ? "text-center" : "text-left mx-0",
        className
      )}
    >
      {eyebrow && (
        <Reveal>
          <Badge variant="gold" className="mb-5 uppercase">
            {eyebrow}
          </Badge>
        </Reveal>
      )}
      <Reveal delay={0.05}>
        <h2 className="font-display text-[2rem] font-semibold leading-[1.1] tracking-tight text-soft sm:text-4xl md:text-[3rem]">
          {title}
        </h2>
      </Reveal>
      {align === "center" && (
        <Reveal delay={0.08}>
          <div className="mx-auto mt-6 h-px w-24 bg-gradient-to-r from-transparent via-gold/60 to-transparent" />
        </Reveal>
      )}
      {description && (
        <Reveal delay={0.1}>
          <p className="mt-5 text-base leading-relaxed text-soft/60 sm:text-lg">
            {description}
          </p>
        </Reveal>
      )}
    </div>
  );
}
