"use client";

import { motion, useReducedMotion } from "framer-motion";
import Link from "next/link";
import type { ReactNode } from "react";

import { useLiquidMouse } from "./useLiquidMouse";

const MotionLink = motion.create(Link);

type LiquidButtonProps = {
  children: ReactNode;
  href?: string;
  variant?: "primary" | "ghost" | "outline";
  className?: string;
  disabled?: boolean;
  fullWidth?: boolean;
  type?: "button" | "submit" | "reset";
  onClick?: () => void;
};

const spring = { type: "spring" as const, stiffness: 520, damping: 24 };

export function LiquidButton({
  children,
  href,
  variant = "primary",
  className = "",
  disabled,
  fullWidth,
  type = "button",
  onClick
}: LiquidButtonProps) {
  const reduced = useReducedMotion();
  const { onMouseMove, onMouseLeave } = useLiquidMouse<HTMLElement>();

  const classes = [
    "liquid-glass liquid-glass--button",
    variant === "primary" && "liquid-glass--button-primary",
    variant === "outline" && "liquid-glass--button-outline",
    variant === "ghost" && "liquid-glass--button-ghost",
    fullWidth && "liquid-glass--button-block",
    className
  ]
    .filter(Boolean)
    .join(" ");

  const interaction = {
    onMouseLeave,
    onMouseMove,
    whileHover:
      reduced || disabled ? undefined : { y: -5, scale: 1.03, transition: spring },
    whileTap: reduced || disabled ? undefined : { y: 1, scale: 0.97, transition: spring },
    transition: spring
  };

  if (href) {
    return (
      <MotionLink {...interaction} className={classes} href={href}>
        <span className="liquid-glass__inner">{children}</span>
      </MotionLink>
    );
  }

  return (
    <motion.button
      {...interaction}
      className={classes}
      disabled={disabled}
      onClick={onClick}
      type={type}
    >
      <span className="liquid-glass__inner">{children}</span>
    </motion.button>
  );
}
