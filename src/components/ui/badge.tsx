import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium tracking-wide transition-colors",
  {
    variants: {
      variant: {
        gold: "border-gold/30 bg-gold/10 text-gold-light",
        emerald: "border-emerald/30 bg-emerald/10 text-emerald-light",
        royal: "border-royal/30 bg-royal/10 text-royal-light",
        loss: "border-loss/30 bg-loss/10 text-loss",
        muted: "border-white/10 bg-white/5 text-soft/70",
      },
    },
    defaultVariants: { variant: "gold" },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <span className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}
