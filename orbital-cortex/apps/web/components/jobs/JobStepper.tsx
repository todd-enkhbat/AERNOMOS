"use client";

import { motion, useReducedMotion } from "framer-motion";
import { Check } from "lucide-react";

import type { JobStatus } from "@/lib/types";

const PHASES: Array<{ key: string; label: string }> = [
  { key: "queued", label: "Queued" },
  { key: "routing", label: "Routing" },
  { key: "executing", label: "Executing" },
  { key: "downlinking", label: "Downlinking" },
  { key: "complete", label: "Complete" }
];

const ORDER: Record<JobStatus, number> = {
  queued: 0,
  routing: 1,
  executing: 2,
  downlinking: 3,
  complete: 4,
  failed: 4
};

export function JobStepper({
  status,
  compact = false
}: {
  status: JobStatus;
  compact?: boolean;
}) {
  const reduced = useReducedMotion();
  const current = ORDER[status];
  const failed = status === "failed";

  return (
    <div className="flex items-center" role="list">
      {PHASES.map((phase, index) => {
        const done = index < current || status === "complete";
        const active = index === current && status !== "complete" && !failed;
        const isLast = index === PHASES.length - 1;

        return (
          <div className={`flex items-center ${isLast ? "" : "flex-1"}`} key={phase.key} role="listitem">
            <div className="flex flex-col items-center gap-1.5">
              <motion.span
                animate={{
                  scale: active && !reduced ? 1.15 : 1,
                  backgroundColor: failed && index === current
                    ? "rgba(190, 84, 60, 0.9)"
                    : done
                      ? "rgba(201, 162, 39, 1)"
                      : active
                        ? "rgba(201, 162, 39, 0.35)"
                        : "rgba(244, 239, 230, 0.08)"
                }}
                className={`grid h-6 w-6 place-items-center rounded-full border ${
                  done || active ? "border-gold/60" : "border-line"
                }`}
                transition={{ type: "spring", stiffness: 380, damping: 26 }}
              >
                {done ? (
                  <Check className="text-void" size={13} strokeWidth={3} />
                ) : active ? (
                  <span className="pulse-dot bg-gold-bright" />
                ) : (
                  <span className="h-1.5 w-1.5 rounded-full bg-cream/20" />
                )}
              </motion.span>
              {!compact ? (
                <span
                  className={`chart-label whitespace-nowrap ${
                    done || active ? "text-gold-bright" : "text-muted-dark"
                  }`}
                >
                  {phase.label}
                </span>
              ) : null}
            </div>
            {!isLast ? (
              <div className={`relative mx-1.5 h-px flex-1 bg-cream/10 ${compact ? "" : "-mt-5"}`}>
                <motion.div
                  animate={{ scaleX: done ? 1 : 0 }}
                  className="absolute inset-y-0 left-0 w-full origin-left bg-gold"
                  initial={false}
                  transition={reduced ? { duration: 0 } : { duration: 0.6, ease: "easeOut" }}
                />
              </div>
            ) : null}
          </div>
        );
      })}
    </div>
  );
}
