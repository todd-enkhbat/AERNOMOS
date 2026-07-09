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
  className
}: {
  children: ReactNode;
  delay?: number;
  y?: number;
  className?: string;
}) {
  const reduced = useReducedMotion();

  return (
    <motion.div
      className={className}
      initial={reduced ? false : { opacity: 0, y }}
      transition={{ ...springSoft, delay }}
      viewport={{ once: true, margin: "-60px" }}
      whileInView={{ opacity: 1, y: 0 }}
    >
      {children}
    </motion.div>
  );
}

export function Stagger({
  children,
  className,
  gap = 0.06
}: {
  children: ReactNode;
  className?: string;
  gap?: number;
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
      viewport={{ once: true, margin: "-60px" }}
      whileInView="show"
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
