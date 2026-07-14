"use client";

import { motion, useReducedMotion } from "framer-motion";
import type { ReactNode } from "react";

import { useLiquidMouse } from "./useLiquidMouse";
import { useFinePointer } from "./useFinePointer";

type LiquidCardProps = {
  children: ReactNode;
  className?: string;
  tone?: "dark" | "light";
  inset?: boolean;
  id?: string;
};

const spring = { type: "spring" as const, stiffness: 420, damping: 34 };
const easeOut = [0.23, 1, 0.32, 1] as const;

export function LiquidCard({
  children,
  className = "",
  tone = "dark",
  inset = false,
  id
}: LiquidCardProps) {
  const reduced = useReducedMotion();
  const finePointer = useFinePointer();
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
      onMouseLeave={finePointer ? onMouseLeave : undefined}
      onMouseMove={finePointer ? onMouseMove : undefined}
      ref={ref}
      whileHover={
        reduced || inset || !finePointer
          ? undefined
          : { y: -2, transition: { duration: 0.2, ease: easeOut } }
      }
      transition={spring}
    >
      <div className="liquid-glass__content relative z-[1]">{children}</div>
    </motion.div>
  );
}
