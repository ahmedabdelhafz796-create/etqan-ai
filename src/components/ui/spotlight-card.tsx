"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

interface SpotlightCardProps extends React.HTMLAttributes<HTMLDivElement> {
  as?: "div" | "article" | "li";
}

/**
 * A glass card whose surface catches a soft gold spotlight that follows
 * the cursor, framed by an animated gradient hairline border.
 * Purely presentational — wraps any content.
 */
export const SpotlightCard = React.forwardRef<HTMLDivElement, SpotlightCardProps>(
  ({ className, children, as = "div", onMouseMove, ...props }, ref) => {
    const Comp = as as "div";

    const handleMove = (e: React.MouseEvent<HTMLDivElement>) => {
      const el = e.currentTarget;
      const rect = el.getBoundingClientRect();
      el.style.setProperty("--mx", `${e.clientX - rect.left}px`);
      el.style.setProperty("--my", `${e.clientY - rect.top}px`);
      onMouseMove?.(e);
    };

    return (
      <Comp
        ref={ref}
        onMouseMove={handleMove}
        className={cn(
          "spotlight gradient-border group relative overflow-hidden rounded-3xl border border-white/10 bg-white/[0.035] backdrop-blur-xl transition-all duration-500",
          className
        )}
        {...props}
      >
        <div className="relative z-[1]">{children}</div>
      </Comp>
    );
  }
);
SpotlightCard.displayName = "SpotlightCard";
