"use client";

import { motion } from "framer-motion";

import { LiquidCard } from "@/components/liquid/LiquidCard";
import type { CandidateScore } from "@/lib/types";

export function ScoreBar({ candidate }: { candidate: CandidateScore }) {
  const width = Math.max(0, Math.min(100, candidate.score));
  const factors = [
    ["Model", candidate.model_support_score],
    ["Latency", candidate.latency_score],
    ["Cost", candidate.cost_score],
    ["Avail", candidate.availability_score],
    ["Contact", candidate.contact_score],
    ["Pref", candidate.preference_score],
    ["Policy", candidate.compliance_score]
  ];

  return (
    <LiquidCard>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="font-medium text-cream">{candidate.node_id}</p>
          <p className="metric-value mt-1 text-xs text-muted">
            {Math.round(candidate.estimated_latency_minutes)}m · $
            {Math.round(candidate.estimated_cost_usd)} ·{" "}
            {candidate.eligible ? "eligible" : "excluded"}
          </p>
        </div>
        <span className="metric-value text-xl text-gold-bright">
          {candidate.score.toFixed(1)}
        </span>
      </div>
      {candidate.binding_constraint ? (
        <p className="chart-label mt-3 text-[#e8a08e]">
          Binding: {candidate.binding_constraint.replaceAll("_", " ")}
        </p>
      ) : null}
      <div className="mt-4 h-1.5 overflow-hidden rounded-full bg-black/40">
        <motion.div
          className="h-full rounded-full bg-gradient-to-r from-brass to-gold-bright"
          initial={{ width: 0 }}
          transition={{ duration: 0.9, ease: [0.32, 0.72, 0, 1] }}
          viewport={{ once: true }}
          whileInView={{ width: `${width}%` }}
        />
      </div>
      <div className="mt-4 grid grid-cols-4 gap-2 lg:grid-cols-7">
        {factors.map(([label, value]) => (
          <div
            className="rounded-lg border border-gold/10 bg-black/30 px-2.5 py-2"
            key={label}
          >
            <p className="chart-label text-[0.58rem] text-muted-dark">{label}</p>
            <p className="metric-value mt-1 text-sm text-cream/90">
              {Number(value).toFixed(1)}
            </p>
          </div>
        ))}
      </div>
      {candidate.reasons.length > 0 ? (
        <div className="mt-4 space-y-1.5">
          {candidate.reasons.slice(0, 4).map((reason) => (
            <p
              className="rounded-lg bg-black/25 px-3 py-2 text-xs leading-snug text-muted"
              key={reason}
            >
              {reason}
            </p>
          ))}
        </div>
      ) : null}
    </LiquidCard>
  );
}
