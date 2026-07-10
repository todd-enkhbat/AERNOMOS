"use client";

import { motion, useReducedMotion, useScroll, useTransform } from "framer-motion";
import { useRef } from "react";

type LiquidOrbProps = {
  className?: string;
};

/** Scroll-reactive decorative glass orb for spatial depth. */
export function LiquidOrb({ className = "" }: LiquidOrbProps) {
  const ref = useRef<HTMLDivElement>(null);
  const reduced = useReducedMotion();
  const { scrollYProgress } = useScroll();
  const y = useTransform(scrollYProgress, [0, 1], [0, reduced ? 0 : 120]);
  const rotate = useTransform(scrollYProgress, [0, 1], [0, reduced ? 0 : 180]);
  const opacity = useTransform(scrollYProgress, [0, 0.12, 0.88, 1], [0, 0.5, 0.5, 0.15]);

  return (
    <motion.div
      aria-hidden
      className={`liquid-orb pointer-events-none fixed right-[8%] top-[18%] z-[4] hidden lg:block ${className}`}
      ref={ref}
      style={{ y, rotate, opacity }}
    >
      <div className="liquid-orb__core" />
      <div className="liquid-orb__glow" />
    </motion.div>
  );
}
