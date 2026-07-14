"use client";

import { motion, useReducedMotion } from "framer-motion";
import Link from "next/link";
import type { ReactNode } from "react";

import { useLiquidMouse } from "./useLiquidMouse";
import { useFinePointer } from "./useFinePointer";

const MotionLink = motion.create(Link);
const easeOut = [0.23, 1, 0.32, 1] as const;

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

const spring = { type: "spring" as const, stiffness: 460, damping: 34 };

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
  const finePointer = useFinePointer();
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
    onMouseLeave: finePointer ? onMouseLeave : undefined,
    onMouseMove: finePointer ? onMouseMove : undefined,
    whileHover:
      reduced || disabled || !finePointer
        ? undefined
        : {
            y: -3,
            transition: { duration: 0.18, ease: easeOut }
          },
    whileTap:
      reduced || disabled
        ? undefined
        : { scale: 0.97, transition: { duration: 0.12, ease: easeOut } },
    transition: spring
  };

  if (href) {
    const external = /^https?:\/\//i.test(href);
    if (external) {
      return (
        <motion.a
          {...interaction}
          className={classes}
          href={href}
          rel="noreferrer"
          target="_blank"
        >
          <span className="liquid-glass__inner">{children}</span>
        </motion.a>
      );
    }
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
