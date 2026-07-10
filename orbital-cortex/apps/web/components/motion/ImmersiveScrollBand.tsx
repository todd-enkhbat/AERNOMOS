"use client";

import { motion, useScroll, useTransform } from "framer-motion";
import Image from "next/image";
import type { ReactNode } from "react";
import { useEffect, useRef } from "react";

type ImmersiveScrollBandProps = {
  children: ReactNode;
  /** Total scroll height of the section. */
  scrollHeight?: string;
  /** Background video (preferred when set). */
  videoSrc?: string;
  /** Poster while video loads. */
  posterSrc?: string;
  /** Background image when no video. */
  imageSrc?: string;
  imageAlt?: string;
};

/**
 * Sticky full-viewport band: background media scales and drifts as you scroll.
 */
export function ImmersiveScrollBand({
  children,
  scrollHeight = "170vh",
  videoSrc,
  posterSrc,
  imageSrc,
  imageAlt = ""
}: ImmersiveScrollBandProps) {
  const ref = useRef<HTMLElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start start", "end start"]
  });

  const scale = useTransform(scrollYProgress, [0, 1], [1.02, 1.14]);
  const y = useTransform(scrollYProgress, [0, 1], ["0%", "10%"]);
  const overlay = useTransform(scrollYProgress, [0, 0.35, 1], [0.55, 0.72, 0.88]);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) {
      return;
    }
    video.play().catch(() => {
      /* autoplay may be blocked until interaction */
    });
  }, [videoSrc]);

  return (
    <section className="relative" ref={ref} style={{ height: scrollHeight }}>
      <div className="sticky top-0 h-screen overflow-hidden">
        <motion.div className="absolute inset-0 will-change-transform" style={{ scale, y }}>
          {videoSrc ? (
            <video
              autoPlay
              className="h-full w-full object-cover object-center"
              loop
              muted
              playsInline
              poster={posterSrc}
              preload="auto"
              ref={videoRef}
              src={videoSrc}
            />
          ) : imageSrc ? (
            <Image
              alt={imageAlt}
              className="object-cover object-center"
              fill
              priority
              quality={92}
              sizes="100vw"
              src={imageSrc}
            />
          ) : null}
        </motion.div>

        <motion.div className="absolute inset-0 bg-void" style={{ opacity: overlay }} />
        <div className="absolute inset-0 bg-gradient-to-b from-void/40 via-transparent to-void" />

        <div className="relative z-10 flex h-full items-center py-16">
          <div className="page-shell w-full">{children}</div>
        </div>
      </div>
    </section>
  );
}
