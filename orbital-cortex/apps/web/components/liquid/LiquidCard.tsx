"use client";

import { motion, useReducedMotion } from "framer-motion";
import type { ReactNode } from "react";

import { useLiquidMouse } from "./useLiquidMouse";

type LiquidCardProps = {
  children: ReactNode;
  className?: string;
  tone?: "dark" | "light";
  inset?: boolean;
  id?: string;
};

const spring = { type: "spring" as const, stiffness: 460, damping: 28 };

export function LiquidCard({
  children,
  className = "",
  tone = "dark",
  inset = false,
  id
}: LiquidCardProps) {
  const reduced = useReducedMotion();
  const { ref, onMouseMove, onMouseLeave } = useLiquidMouse<HTMLDivElement>();

  return (
    <motion.div
      className={[
        "liquid-glass",
        inset ? "liquid-glass--inset" : "liquid-glass--card",
        tone === "light" && "liquid-glass--light",
        className.includes("overflow-visible") && "liquid-glass--overflow-visible",
        className
      ]
        .filter(Boolean)
        .join(" ")}
      id={id}
      onMouseLeave={onMouseLeave}
      onMouseMove={onMouseMove}
      ref={ref}
      whileHover={reduced || inset ? undefined : { y: -5, scale: 1.008 }}
      transition={spring}
    >
      <div className="liquid-glass__content relative z-[1]">{children}</div>
    </motion.div>
  );
}
