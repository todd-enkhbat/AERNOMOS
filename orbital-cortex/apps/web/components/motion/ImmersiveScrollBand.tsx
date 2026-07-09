"use client";

import { motion, useScroll, useTransform } from "framer-motion";
import Image from "next/image";
import type { ReactNode } from "react";
import { useRef } from "react";

type ImmersiveScrollBandProps = {
  imageSrc: string;
  imageAlt: string;
  children: ReactNode;
  /** Total scroll height of the section. */
  scrollHeight?: string;
};

/**
 * Sticky full-viewport band: background image scales and drifts as you scroll
 * through the section. One immersive scroll moment per band.
 */
export function ImmersiveScrollBand({
  imageSrc,
  imageAlt,
  children,
  scrollHeight = "170vh"
}: ImmersiveScrollBandProps) {
  const ref = useRef<HTMLElement>(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start start", "end start"]
  });

  const scale = useTransform(scrollYProgress, [0, 1], [1.02, 1.14]);
  const y = useTransform(scrollYProgress, [0, 1], ["0%", "10%"]);
  const overlay = useTransform(scrollYProgress, [0, 0.35, 1], [0.55, 0.72, 0.88]);

  return (
    <section className="relative" ref={ref} style={{ height: scrollHeight }}>
      <div className="sticky top-0 h-screen overflow-hidden">
        <motion.div className="absolute inset-0 will-change-transform" style={{ scale, y }}>
          <Image
            alt={imageAlt}
            className="object-cover object-center"
            fill
            priority
            quality={92}
            sizes="100vw"
            src={imageSrc}
          />
        </motion.div>

        <motion.div
          className="absolute inset-0 bg-void"
          style={{ opacity: overlay }}
        />
        <div className="absolute inset-0 bg-gradient-to-b from-void/40 via-transparent to-void" />

        <div className="relative z-10 flex h-full items-center py-16">
          <div className="page-shell w-full">{children}</div>
        </div>
      </div>
    </section>
  );
}
