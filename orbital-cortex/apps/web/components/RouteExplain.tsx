import type { CandidateScore, RoutingDecision } from "@/lib/types";
import { labelize } from "@/lib/format";

export function RouteExplain({ route }: { route: RoutingDecision }) {
  const eliminated = route.candidate_scores.filter((candidate) => !candidate.eligible);
  const eligible = route.candidate_scores.filter((candidate) => candidate.eligible);

  return (
    <section className="space-y-4">
      <div className="glass p-5">
        <p className="chart-label text-gold">Audit</p>
        <dl className="mt-3 grid gap-3 text-sm sm:grid-cols-2">
          <div>
            <dt className="text-muted-dark">Config</dt>
            <dd className="metric-value mt-1 text-cream">{route.config_version ?? "n/a"}</dd>
          </div>
          <div>
            <dt className="text-muted-dark">Decision hash</dt>
            <dd className="metric-value mt-1 truncate text-xs text-silver">
              {route.decision_hash ?? "n/a"}
            </dd>
          </div>
        </dl>
      </div>

      {eligible.length > 0 ? (
        <div className="glass p-5">
          <h3 className="chart-label text-muted">Ranked eligible nodes</h3>
          <ul className="mt-3 space-y-2">
            {eligible.map((candidate, index) => (
              <li
                className="flex items-center justify-between gap-3 rounded-lg border border-line bg-void/40 px-3.5 py-2.5 text-sm"
                key={candidate.node_id}
              >
                <span className="text-cream/85">
                  <span className="metric-value mr-2 text-xs text-gold">
                    #{index + 1}
                  </span>
                  {candidate.node_id}
                </span>
                <span className="metric-value text-gold-bright">
                  {candidate.score.toFixed(1)}
                </span>
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      {eliminated.length > 0 ? (
        <div className="glass p-5">
          <h3 className="chart-label text-muted">Eliminated nodes</h3>
          <ul className="mt-3 space-y-3">
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
    <li className="rounded-lg border border-line bg-void/40 p-3.5">
      <p className="font-medium text-cream">{candidate.node_id}</p>
      {binding ? (
        <p className="mt-1 text-sm text-silver">Binding constraint: {labelize(binding)}</p>
      ) : null}
      <ul className="mt-2 space-y-1 text-sm text-muted">
        {failures.map((failure) => (
          <li key={`${failure.constraint}-${failure.detail}`}>{failure.detail}</li>
        ))}
      </ul>
    </li>
  );
}
