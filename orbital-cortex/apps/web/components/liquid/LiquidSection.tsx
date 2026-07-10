"use client";

import type { ReactNode } from "react";

type LiquidSectionProps = {
  children: ReactNode;
  className?: string;
  id?: string;
  orbs?: boolean;
};

export function LiquidSection({
  children,
  className = "",
  id,
  orbs = true
}: LiquidSectionProps) {
  return (
    <section className={`liquid-section relative ${className}`} id={id}>
      {orbs ? (
        <>
          <div aria-hidden className="liquid-section__orb liquid-section__orb--gold" />
          <div aria-hidden className="liquid-section__orb liquid-section__orb--warm" />
          <div aria-hidden className="liquid-section__noise" />
        </>
      ) : null}
      <div className="liquid-section__inner relative z-[1]">{children}</div>
    </section>
  );
}
