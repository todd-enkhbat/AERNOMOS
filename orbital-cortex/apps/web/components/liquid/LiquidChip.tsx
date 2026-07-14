"use client";

import { motion, useReducedMotion } from "framer-motion";
import type { ReactNode } from "react";

import { useLiquidMouse } from "./useLiquidMouse";
import { useFinePointer } from "./useFinePointer";

type LiquidChipProps = {
  children: ReactNode;
  active?: boolean;
  className?: string;
  onClick?: () => void;
};

const spring = { type: "spring" as const, stiffness: 460, damping: 34 };
const easeOut = [0.23, 1, 0.32, 1] as const;

export function LiquidChip({
  children,
  active = false,
  className = "",
  onClick
}: LiquidChipProps) {
  const reduced = useReducedMotion();
  const finePointer = useFinePointer();
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
      onMouseLeave={finePointer ? onMouseLeave : undefined}
      onMouseMove={finePointer ? onMouseMove : undefined}
      ref={ref}
      type="button"
      whileHover={
        reduced || !finePointer
          ? undefined
          : { y: -2, transition: { duration: 0.2, ease: easeOut } }
      }
      whileTap={
        reduced
          ? undefined
          : { scale: 0.97, transition: { duration: 0.12, ease: easeOut } }
      }
      transition={spring}
    >
      <span className="liquid-glass__chip-label">{children}</span>
    </motion.button>
  );
}
