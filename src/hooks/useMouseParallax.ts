"use client";

import * as React from "react";
import {
  useMotionValue,
  useSpring,
  useReducedMotion,
  type MotionValue,
} from "framer-motion";

interface ParallaxResult {
  /** Normalized pointer position, -0.5 … 0.5, springed. */
  x: MotionValue<number>;
  y: MotionValue<number>;
  bind: {
    onMouseMove: (e: React.MouseEvent) => void;
    onMouseLeave: () => void;
  };
}

/**
 * Tracks the pointer inside an element and returns springed, normalized
 * motion values for parallax effects. No-op under reduced motion.
 */
export function useMouseParallax(stiffness = 120, damping = 18): ParallaxResult {
  const reduce = useReducedMotion();
  const rawX = useMotionValue(0);
  const rawY = useMotionValue(0);
  const x = useSpring(rawX, { stiffness, damping });
  const y = useSpring(rawY, { stiffness, damping });

  const onMouseMove = React.useCallback(
    (e: React.MouseEvent) => {
      if (reduce) return;
      const rect = e.currentTarget.getBoundingClientRect();
      rawX.set((e.clientX - rect.left) / rect.width - 0.5);
      rawY.set((e.clientY - rect.top) / rect.height - 0.5);
    },
    [rawX, rawY, reduce]
  );

  const onMouseLeave = React.useCallback(() => {
    rawX.set(0);
    rawY.set(0);
  }, [rawX, rawY]);

  return { x, y, bind: { onMouseMove, onMouseLeave } };
}
