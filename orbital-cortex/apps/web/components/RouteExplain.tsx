import type { CandidateScore, RoutingDecision } from "@/lib/types";
import { labelize } from "@/lib/format";

export function RouteExplain({ route }: { route: RoutingDecision }) {
  const eliminated = route.candidate_scores.filter((candidate) => !candidate.eligible);
  const eligible = route.candidate_scores.filter((candidate) => candidate.eligible);

  return (
    <section className="space-y-4">
      <div className="rounded-lg border border-[rgba(86,67,42,0.22)] bg-[#fffaf0]/70 p-4">
        <p className="text-sm font-bold uppercase tracking-wide text-[#6f604c]">
          Audit
        </p>
        <dl className="mt-3 grid gap-2 text-sm sm:grid-cols-2">
          <div>
            <dt className="text-[#6f604c]">Config</dt>
            <dd className="metric-value font-bold">{route.config_version ?? "n/a"}</dd>
          </div>
          <div>
            <dt className="text-[#6f604c]">Decision hash</dt>
            <dd className="metric-value truncate text-xs font-bold">
              {route.decision_hash ?? "n/a"}
            </dd>
          </div>
        </dl>
      </div>

      {eligible.length > 0 ? (
        <div>
          <h3 className="text-lg font-bold text-[#17140f]">Ranked eligible nodes</h3>
          <ul className="mt-2 space-y-2">
            {eligible.map((candidate, index) => (
              <li
                className="rounded-lg bg-[#eadcc8] px-3 py-2 text-sm"
                key={candidate.node_id}
              >
                #{index + 1} {candidate.node_id} — score {candidate.score.toFixed(1)}
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      {eliminated.length > 0 ? (
        <div>
          <h3 className="text-lg font-bold text-[#17140f]">Eliminated nodes</h3>
          <ul className="mt-2 space-y-3">
            {eliminated.map((candidate) => (
              <EliminatedNode candidate={candidate} key={candidate.node_id} />
            ))}
          </ul>
        </div>
      ) : null}
    </section>
  );
}

function EliminatedNode({ candidate }: { candidate: CandidateScore }) {
  const failures = candidate.hard_constraint_failures ?? [];
  const binding = candidate.binding_constraint ?? failures[0]?.constraint;
  return (
    <li className="rounded-lg border border-[rgba(86,67,42,0.22)] bg-[#fffaf0]/70 p-3">
      <p className="font-bold text-[#17140f]">{candidate.node_id}</p>
      {binding ? (
        <p className="mt-1 text-sm text-[#25495a]">
          Binding constraint: {labelize(binding)}
        </p>
      ) : null}
      <ul className="mt-2 space-y-1 text-sm text-[#5d5244]">
        {failures.map((failure) => (
          <li key={`${failure.constraint}-${failure.detail}`}>{failure.detail}</li>
        ))}
      </ul>
    </li>
  );
}
