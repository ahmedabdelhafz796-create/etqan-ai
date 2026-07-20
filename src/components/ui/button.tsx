"use client";

import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-full text-sm font-semibold transition-all duration-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gold/60 focus-visible:ring-offset-2 focus-visible:ring-offset-night disabled:pointer-events-none disabled:opacity-50 select-none",
  {
    variants: {
      variant: {
        gold: "bg-gradient-to-r from-gold-light via-gold to-gold-deep text-night-900 shadow-glow hover:shadow-[0_0_50px_-6px_rgba(233,196,106,0.65)] hover:-translate-y-0.5",
        emerald:
          "bg-gradient-to-r from-emerald-light via-emerald to-emerald-deep text-night-900 shadow-glow-emerald hover:-translate-y-0.5",
        outline:
          "border border-white/15 bg-white/5 text-soft backdrop-blur hover:bg-white/10 hover:border-gold/40",
        ghost: "text-soft/80 hover:text-soft hover:bg-white/5",
        glass:
          "border border-white/10 bg-white/[0.06] text-soft backdrop-blur-md hover:bg-white/10",
      },
      size: {
        sm: "h-9 px-4 text-xs",
        md: "h-11 px-6",
        lg: "h-14 px-8 text-base",
        xl: "h-16 px-10 text-base tracking-wide",
        icon: "h-11 w-11",
      },
    },
    defaultVariants: { variant: "gold", size: "md" },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

export { Button, buttonVariants };
