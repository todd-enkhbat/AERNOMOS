import type { CandidateScore } from "@/lib/types";

export function ScoreBar({ candidate }: { candidate: CandidateScore }) {
  const width = Math.max(0, Math.min(100, candidate.score));

  return (
    <div className="rounded-lg border border-[rgba(86,67,42,0.22)] bg-[#fffaf0]/70 p-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="font-bold text-[#17140f]">{candidate.node_id}</p>
          <p className="text-sm text-[#6f604c]">
            {Math.round(candidate.estimated_latency_minutes)}m / $
            {Math.round(candidate.estimated_cost_usd)} /{" "}
            {candidate.eligible ? "eligible" : "excluded"}
          </p>
        </div>
        <span className="metric-value text-lg font-bold text-[#25495a]">
          {candidate.score.toFixed(1)}
        </span>
      </div>
      <div className="mt-4 h-2 overflow-hidden rounded-full bg-[#eadcc8]">
        <div
          className="h-full rounded-full bg-[#25495a]"
          style={{ width: `${width}%` }}
        />
      </div>
    </div>
  );
}
