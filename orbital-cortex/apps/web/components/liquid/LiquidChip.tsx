"use client";

import { motion, useReducedMotion } from "framer-motion";
import type { ReactNode } from "react";

import { useLiquidMouse } from "./useLiquidMouse";

type LiquidChipProps = {
  children: ReactNode;
  active?: boolean;
  className?: string;
  onClick?: () => void;
};

const spring = { type: "spring" as const, stiffness: 520, damping: 24 };

export function LiquidChip({
  children,
  active = false,
  className = "",
  onClick
}: LiquidChipProps) {
  const reduced = useReducedMotion();
  const { ref, onMouseMove, onMouseLeave } = useLiquidMouse<HTMLButtonElement>();

  return (
    <motion.button
      className={[
        "liquid-glass liquid-glass--chip",
        active && "liquid-glass--chip-active",
        className
      ]
        .filter(Boolean)
        .join(" ")}
      onClick={onClick}
      onMouseLeave={onMouseLeave}
      onMouseMove={onMouseMove}
      ref={ref}
      type="button"
      whileHover={reduced ? undefined : { y: -4, scale: 1.05 }}
      whileTap={reduced ? undefined : { y: 0, scale: 0.96 }}
      transition={spring}
    >
      <span className="liquid-glass__chip-label">{children}</span>
    </motion.button>
  );
}
