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
  const trackPointer = Boolean(finePointer);

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
      onMouseLeave={trackPointer ? onMouseLeave : undefined}
      onMouseMove={trackPointer ? onMouseMove : undefined}
      ref={ref}
      type="button"
      whileHover={
        reduced || !finePointer
          ? undefined
          : {
              transform: "translateY(-2px) scale(1)",
              transition: { duration: 0.2, ease: easeOut }
            }
      }
      whileTap={
        reduced
          ? undefined
          : {
              transform: "translateY(0px) scale(0.97)",
              transition: { duration: 0.12, ease: easeOut }
            }
      }
      transition={spring}
    >
      {trackPointer ? (
        <span aria-hidden className="liquid-glass__specular" data-liquid-specular />
      ) : null}
      <span className="liquid-glass__chip-label">{children}</span>
    </motion.button>
  );
}
