"use client";

import { motion, useReducedMotion, useScroll, useTransform } from "framer-motion";
import { useRef } from "react";

type ScrollSketchfabProps = {
  title: string;
  src: string;
  className?: string;
  scrollHeight?: string;
};

/** Sticky Sketchfab stage: model drifts and scales as you scroll through the section. */
export function ScrollSketchfab({
  title,
  src,
  className = "",
  scrollHeight = "160vh"
}: ScrollSketchfabProps) {
  const ref = useRef<HTMLElement>(null);
  const reduced = useReducedMotion();
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"]
  });

  const y = useTransform(scrollYProgress, [0, 0.5, 1], [80, 0, -60]);
  const scale = useTransform(scrollYProgress, [0, 0.5, 1], [0.88, 1, 0.92]);
  const rotate = useTransform(scrollYProgress, [0, 1], [-6, 8]);

  if (reduced) {
    return (
      <section className={`relative py-10 ${className}`.trim()}>
        <div className="relative mx-auto h-[min(72vh,640px)] w-full max-w-4xl">
          <iframe
            allow="autoplay; fullscreen; xr-spatial-tracking"
            allowFullScreen
            className="h-full w-full rounded-[28px] border-0"
            loading="lazy"
            src={src}
            title={title}
          />
        </div>
      </section>
    );
  }

  return (
    <section className={`relative ${className}`.trim()} ref={ref} style={{ height: scrollHeight }}>
      <div
        className="sticky flex h-[min(72vh,640px)] items-center justify-center"
        style={{ top: "var(--header-offset)" }}
      >
        <motion.div
          className="relative h-full w-full max-w-4xl"
          style={{ y, scale, rotateZ: rotate }}
        >
          <iframe
            allow="autoplay; fullscreen; xr-spatial-tracking"
            allowFullScreen
            className="h-full w-full rounded-[28px] border-0"
            loading="lazy"
            src={src}
            title={title}
          />
        </motion.div>
      </div>
    </section>
  );
}
