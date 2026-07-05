import type { CandidateScore } from "@/lib/types";

export function ScoreBar({ candidate }: { candidate: CandidateScore }) {
  const width = Math.max(0, Math.min(100, candidate.score));
  const factors = [
    ["Model", candidate.model_support_score],
    ["Latency", candidate.latency_score],
    ["Cost", candidate.cost_score],
    ["Availability", candidate.availability_score],
    ["Contact", candidate.contact_score],
    ["Preference", candidate.preference_score],
    ["Policy", candidate.compliance_score]
  ];

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
      <div className="mt-4 grid gap-2 sm:grid-cols-4 lg:grid-cols-7">
        {factors.map(([label, value]) => (
          <div
            className="rounded-lg border border-[rgba(86,67,42,0.16)] bg-[#f5eddf] px-2.5 py-2"
            key={label}
          >
            <p className="text-[0.68rem] font-bold uppercase text-[#6f604c]">
              {label}
            </p>
            <p className="metric-value mt-1 text-sm font-bold text-[#17140f]">
              {Number(value).toFixed(1)}
            </p>
          </div>
        ))}
      </div>
      <div className="mt-4 space-y-2">
        {candidate.reasons.slice(0, 4).map((reason) => (
          <p
            className="rounded-lg bg-[#eadcc8] px-3 py-2 text-sm leading-6 text-[#4f4436]"
            key={reason}
          >
            {reason}
          </p>
        ))}
      </div>
    </div>
  );
}
