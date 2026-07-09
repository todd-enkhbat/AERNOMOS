"use client";

import {
  motion,
  useMotionValue,
  useScroll,
  useSpring,
  useTransform
} from "framer-motion";
import Image from "next/image";
import { useCallback } from "react";

/**
 * Decorative disk fixed to the page edge. Page scroll spins it; wheel or drag
 * on the disk adds extra rotation, like turning a record beside the content.
 */
export function SideScrollDisk() {
  const { scrollYProgress } = useScroll();
  const scrollRotate = useTransform(scrollYProgress, [0, 1], [0, 540]);
  const manualRotate = useMotionValue(0);
  const combined = useTransform(
    [scrollRotate, manualRotate],
    ([scroll, manual]) => (scroll as number) + (manual as number)
  );
  const rotate = useSpring(combined, { stiffness: 90, damping: 22 });
  const opacity = useTransform(scrollYProgress, [0, 0.06, 0.94, 1], [0, 0.62, 0.62, 0.18]);
  const x = useTransform(scrollYProgress, [0, 1], [10, -6]);

  const onWheel = useCallback(
    (event: React.WheelEvent) => {
      manualRotate.set(manualRotate.get() + event.deltaY * 0.45);
    },
    [manualRotate]
  );

  return (
    <motion.div
      aria-hidden
      className="fixed right-[max(0.25rem,calc(50%-640px))] top-1/2 z-[5] hidden -translate-y-1/2 xl:block"
      style={{ opacity, x }}
    >
      <motion.div
        className="group relative cursor-grab touch-none active:cursor-grabbing"
        drag
        dragConstraints={{ top: 0, bottom: 0, left: 0, right: 0 }}
        dragElastic={0}
        dragMomentum={false}
        onDrag={(_, info) => {
          manualRotate.set(manualRotate.get() + info.delta.x * 0.9);
        }}
        onWheel={onWheel}
        style={{ rotate }}
      >
        <div className="relative h-[min(240px,19vw)] w-[min(240px,19vw)]">
          <div className="absolute inset-[-10%] rounded-full bg-gold/10 blur-2xl transition-opacity group-hover:opacity-100 opacity-70" />
          <div className="aave-glass relative h-full w-full overflow-hidden !rounded-full p-[3px]">
            <div className="relative h-full w-full overflow-hidden rounded-full">
              <Image
                alt=""
                className="object-cover"
                draggable={false}
                fill
                sizes="240px"
                src="/images/astronomer-disk.png"
              />
            </div>
          </div>
          <div className="pointer-events-none absolute inset-0 rounded-full ring-1 ring-white/15" />
        </div>
        <p className="chart-label pointer-events-none mt-3 text-center text-[10px] text-muted opacity-0 transition-opacity group-hover:opacity-100">
          Scroll or drag
        </p>
      </motion.div>
    </motion.div>
  );
}
