"use client";

import { motion, useScroll, useTransform } from "framer-motion";
import { useRef, type ReactNode } from "react";

type OrbitalScrollStageProps = {
  children: ReactNode;
  scrollHeight?: string;
};

/** Sticky orbital canvas stage: content drifts while a 3D layer stays centered. */
export function OrbitalScrollStage({
  children,
  scrollHeight = "140vh"
}: OrbitalScrollStageProps) {
  const ref = useRef<HTMLElement>(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"]
  });
  const y = useTransform(scrollYProgress, [0, 1], [40, -40]);
  const opacity = useTransform(scrollYProgress, [0, 0.2, 0.8, 1], [0.4, 1, 1, 0.4]);

  return (
    <section className="relative" ref={ref} style={{ height: scrollHeight }}>
      <div className="sticky top-[64px] flex h-[min(75vh,680px)] items-center justify-center">
        <motion.div className="absolute inset-0 flex items-center justify-center" style={{ opacity }}>
          {children}
        </motion.div>
        <motion.div
          className="pointer-events-none absolute inset-x-0 bottom-8 flex justify-center"
          style={{ y }}
        >
          <div
            aria-hidden
            className="h-px w-[min(480px,70vw)] bg-gradient-to-r from-transparent via-gold/40 to-transparent"
          />
        </motion.div>
      </div>
    </section>
  );
}
