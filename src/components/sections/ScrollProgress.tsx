"use client";

import { motion, useScroll, useSpring } from "framer-motion";

/** Thin reading-progress bar pinned to the top of the viewport.
 *  Site chrome, so it runs on the AI line's iris/aqua rather than gold. */
export function ScrollProgress() {
  const { scrollYProgress } = useScroll();
  const scaleX = useSpring(scrollYProgress, {
    stiffness: 120,
    damping: 30,
    restDelta: 0.001,
  });

  return (
    <motion.div
      style={{ scaleX }}
      className="fixed inset-x-0 top-0 z-[60] h-0.5 origin-left bg-gradient-to-r from-iris-mid via-iris to-aqua"
      aria-hidden="true"
    />
  );
}
