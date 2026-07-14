"use client";

import { motion, useReducedMotion } from "framer-motion";

import { CALENDAR_META } from "@/lib/calendar-events";

const EASE_OUT = [0.23, 1, 0.32, 1] as const;

const disks = [
  {
    index: "I",
    label: "Presence",
    value: "You may\nsee us there",
    detail: "Priority labels are signals, not confirmed Nomos RSVPs.",
    ring: "rgba(201, 162, 39, 0.55)"
  },
  {
    index: "II",
    label: "Validity",
    value: "Confirmed\ndates only",
    detail: `Checked ${CALENDAR_META.verifiedAt}. Re-verify before you travel.`,
    ring: "rgba(227, 192, 92, 0.45)"
  },
  {
    index: "III",
    label: "Apply",
    value: "Take it\nwith you",
    detail: "ICS, CSV, and JSON for your own planning stack.",
    ring: "rgba(236, 234, 228, 0.28)"
  }
] as const;

export function CalendarRegisterDisks() {
  const reduced = useReducedMotion();

  return (
    <div className="mt-8 flex flex-wrap items-start justify-center gap-6 md:gap-8 lg:gap-12">
      {disks.map((disk, i) => (
        <motion.article
          animate={reduced ? undefined : { opacity: 1, y: 0, scale: 1 }}
          className="flex w-[11.5rem] flex-col items-center text-center sm:w-[12.5rem]"
          initial={reduced ? undefined : { opacity: 0, y: 10, scale: 0.96 }}
          key={disk.label}
          transition={{ duration: 0.2, ease: EASE_OUT, delay: i * 0.04 }}
        >
          <div
            className="relative flex aspect-square w-full items-center justify-center rounded-full"
            style={{
              background:
                "radial-gradient(circle at 35% 28%, rgba(236,234,228,0.08), rgba(5,5,6,0.92) 62%)",
              boxShadow: `inset 0 0 0 1px ${disk.ring}, inset 0 0 0 8px rgba(5,5,6,0.55), 0 18px 40px rgba(0,0,0,0.45)`
            }}
          >
            <div
              aria-hidden
              className="pointer-events-none absolute inset-[14%] rounded-full border border-dashed border-gold/20"
            />
            <div className="relative z-[1] max-w-[8.5rem] px-3">
              <p className="font-mono text-[10px] tracking-[0.18em] text-gold">{disk.index}</p>
              <p className="chart-label mt-2 text-cream/55">{disk.label}</p>
              <p className="display mt-2 whitespace-pre-line text-[1.05rem] leading-tight text-cream">
                {disk.value}
              </p>
            </div>
          </div>
          <p className="prose-compact mt-4 max-w-[12rem] text-xs text-muted">{disk.detail}</p>
        </motion.article>
      ))}
    </div>
  );
}
