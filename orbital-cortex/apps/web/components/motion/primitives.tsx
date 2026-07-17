"use client";

import { motion, useReducedMotion } from "framer-motion";
import type { ReactNode } from "react";

export const spring = {
  type: "spring" as const,
  stiffness: 380,
  damping: 32
};

export const springSoft = {
  type: "spring" as const,
  stiffness: 240,
  damping: 28
};

export function FadeIn({
  children,
  delay = 0,
  y = 12,
  className,
  when = "view"
}: {
  children: ReactNode;
  delay?: number;
  y?: number;
  className?: string;
  /** "view" waits for scroll into viewport; "mount" plays on first paint. */
  when?: "view" | "mount";
}) {
  const reduced = useReducedMotion();
  const visible = { opacity: 1, y: 0 };

  return (
    <motion.div
      className={className}
      initial={reduced ? false : { opacity: 0, y }}
      transition={{ ...springSoft, delay }}
      {...(when === "mount"
        ? { animate: visible }
        : {
            viewport: { once: true, margin: "-40px", amount: 0.15 },
            whileInView: visible
          })}
    >
      {children}
    </motion.div>
  );
}

export function Stagger({
  children,
  className,
  gap = 0.06,
  when = "view"
}: {
  children: ReactNode;
  className?: string;
  gap?: number;
  when?: "view" | "mount";
}) {
  const reduced = useReducedMotion();

  return (
    <motion.div
      className={className}
      initial={reduced ? false : "hidden"}
      variants={{
        hidden: {},
        show: { transition: { staggerChildren: gap } }
      }}
      {...(when === "mount"
        ? { animate: "show" }
        : {
            viewport: { once: true, margin: "-40px", amount: 0.1 },
            whileInView: "show"
          })}
    >
      {children}
    </motion.div>
  );
}

export function StaggerItem({
  children,
  className
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <motion.div
      className={className}
      transition={springSoft}
      variants={{
        hidden: { opacity: 0, y: 14 },
        show: { opacity: 1, y: 0 }
      }}
    >
      {children}
    </motion.div>
  );
}
