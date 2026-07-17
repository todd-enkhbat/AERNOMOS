"use client";

import dynamic from "next/dynamic";
import { Check, CircleAlert, ExternalLink, LockKeyhole } from "lucide-react";

import { ContactWindowTimeline } from "@/components/network/ContactWindowTimeline";
import { ExecutionDemoPanel } from "@/components/missions/ExecutionDemoPanel";
import { MissionFeedbackCapture } from "@/components/missions/MissionFeedbackCapture";
import {
  AssumptionPanel,
  IntegrationStatusChip,
  SourcePopover,
  TruthBadge,
  integrationStatusFromStep,
  type ProvenancedMetric,
  type TruthStatus,
} from "@/components/truth";
import { LiquidButton } from "@/components/liquid/LiquidButton";
import type {
  CatalogCandidate,
  MissionInfrastructureResponse,
  MissionPlan,
  MissionPlanStep,
  MissionSummary,
  SourceEvidence,
} from "@/lib/api";
import { formatDateTime } from "@/lib/format";
import type { ContactWindow } from "@/lib/types";

function asTruthStatus(value: string | null | undefined): TruthStatus {
  switch (value) {
    case "OBSERVED":
    case "CALCULATED":
    case "PROVIDER_REPORTED":
    case "ESTIMATED":
    case "SIMULATED":
    case "STALE":
    case "UNAVAILABLE":
      return value;
    default:
      return "UNAVAILABLE";
  }
}

const MissionGeographyMap = dynamic(
  () =>
    import("@/components/missions/MissionGeographyMap").then(
      (module) => module.MissionGeographyMap
    ),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-[420px] items-center justify-center rounded-2xl border border-white/10 bg-void/60 text-sm text-muted sm:h-[500px]">
        Loading mission geography…
      </div>
    ),
  }
);

function formatDuration(seconds: number | null | undefined): string {
  if (seconds == null) return "Unavailable";
  if (seconds < 60) return `${Math.round(seconds)} sec`;
  const minutes = Math.round(seconds / 60);
  if (minutes < 60) return `${minutes} min`;
  const hours = minutes / 60;
  return `${hours < 10 ? hours.toFixed(1) : Math.round(hours)} hr`;
}

function formatCost(value: number | null | undefined): string {
  return value == null ? "Unavailable" : `$${value.toFixed(2)}`;
}

function formatDataMovement(value: number | null | undefined): string {
  if (value == null) return "Unavailable";
  return value >= 1024 ? `${(value / 1024).toFixed(1)} GiB` : `${Math.round(value)} MiB`;
}

function estimateMetric(
  plan: MissionPlan,
  key: "duration" | "cost_usd" | "data_movement_mb"
): ProvenancedMetric {
  const estimate = plan.estimates?.[key];
  return {
    value: estimate?.value ?? null,
    truth_status: asTruthStatus(estimate?.truth_status),
    source: "Nomos structured planner",
    method: estimate?.method ?? undefined,
    explanation:
      key === "cost_usd" && estimate?.value == null
        ? "No connected provider pricing source is available."
        : "Derived from the mission inputs and persisted source snapshot.",
  };
}

function statusLabel(status: string | null | undefined): string {
  if (status === "feasible") return "Feasible now";
  if (status === "conditional") return "Provider access required";
  return "Unavailable";
}

function statusTruth(status: string | null | undefined): string {
  if (status === "feasible") return "CALCULATED";
  if (status === "conditional") return "ESTIMATED";
  return "UNAVAILABLE";
}

function availabilityForStep(step: MissionPlanStep): string {
  const integration = integrationStatusFromStep(step.source_metadata);
  if (integration === "simulated") {
    return "Simulated registry entry — not live provider access";
  }
  if (integration === "public_data_only" || integration === "sandbox_requested") {
    return "Public provider facts only — live access not verified";
  }
  if (integration === "sandbox_connected" || integration === "partner_connected") {
    return "Connected provider integration";
  }
  if (step.feasibility_status === "feasible" && step.truth_status !== "UNAVAILABLE") {
    return "Available for planning";
  }
  if (step.feasibility_status === "conditional") return "Provider access required";
  return step.rejection_reason || "Unavailable";
}

function selectedCandidateIds(plan: MissionPlan): Set<string> {
  const ids = new Set<string>();
  (plan.steps ?? []).forEach((step) => {
    const id = step.source_metadata?.candidate_id;
    if (typeof id === "string") ids.add(id);
  });
  (plan.assumptions ?? []).forEach((item) => {
    if (
      typeof item === "object" &&
      item !== null &&
      "kind" in item &&
      item.kind === "planner_meta" &&
      "candidate_id" in item &&
      typeof item.candidate_id === "string"
    ) {
      ids.add(item.candidate_id);
    }
  });
  return ids;
}

function planAssumptions(plan: MissionPlan, infrastructure: MissionInfrastructureResponse | null) {
  const items: Array<{ label: string; status: string; detail?: string }> = [];
  (plan.explanation?.top_assumptions ?? []).forEach((detail, index) => {
    items.push({ label: `Planning assumption ${index + 1}`, status: "ESTIMATED", detail });
  });
  (plan.explanation?.missing_integrations ?? []).forEach((integration) => {
    items.push({
      label: integration,
      status: "UNAVAILABLE",
      detail: "This integration is not connected and is not treated as operational access.",
    });
  });
  if (infrastructure?.orbital_snapshot.truth_status === "STALE") {
    items.push({
      label: "Orbital snapshot freshness",
      status: "STALE",
      detail: `Snapshot ${infrastructure.orbital_snapshot.snapshot_id} exceeds the freshness threshold.`,
    });
  }
  return items;
}

function contactWindowIds(plan: MissionPlan): Set<string> {
  const ids = new Set<string>();
  (plan.steps ?? []).forEach((step) => {
    const id = step.source_metadata?.contact_window_id;
    if (typeof id === "string") ids.add(id);
  });
  return ids;
}

function Section({
  index,
  title,
  children,
}: {
  index: string;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section aria-labelledby={`mission-section-${index}`} className="border-t border-white/10 pt-8">
      <div className="mb-5 flex items-baseline gap-3">
        <span className="font-mono text-xs text-vermilion">{index}</span>
        <h2 className="font-serif text-2xl tracking-[-0.02em] text-cream" id={`mission-section-${index}`}>
          {title}
        </h2>
      </div>
      {children}
    </section>
  );
}

function FeasibilitySummary({ plans }: { plans: MissionPlan[] }) {
  const buckets = [
    {
      label: "Feasible now",
      value: plans.filter((plan) => plan.status === "feasible").length,
      detail: "No missing hard constraint in the current source snapshot.",
      status: "CALCULATED",
    },
    {
      label: "Feasible with provider access",
      value: plans.filter((plan) => plan.status === "conditional").length,
      detail: "A provider connection or reservation is still required.",
      status: "ESTIMATED",
    },
    {
      label: "Estimated only",
      value: plans.filter(
        (plan) => plan.estimates?.duration?.truth_status === "ESTIMATED"
      ).length,
      detail: "Duration relies on a disclosed estimate rather than measured execution.",
      status: "ESTIMATED",
    },
    {
      label: "Unavailable",
      value: plans.filter((plan) => plan.status === "rejected").length,
      detail: "At least one hard constraint failed.",
      status: "UNAVAILABLE",
    },
  ];
  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      {buckets.map((bucket) => (
        <article className="rounded-xl border border-white/10 bg-white/[0.025] p-4" key={bucket.label}>
          <div className="flex items-start justify-between gap-3">
            <p className="text-sm text-cream">{bucket.label}</p>
            <SourcePopover
              metric={{
                value: bucket.value,
                truth_status: asTruthStatus(bucket.status),
                source: "Generated mission plans",
                method: "Count grouped by planner feasibility and estimate status",
              }}
            />
          </div>
          <p className="mt-4 font-serif text-4xl text-cream">{bucket.value}</p>
          <p className="mt-2 text-xs leading-5 text-muted">{bucket.detail}</p>
        </article>
      ))}
    </div>
  );
}

function executionStatusLabel(status: string | undefined): string {
  switch (status) {
    case "running":
      return "Running";
    case "executed":
      return "Executed";
    case "failed":
      return "Failed";
    default:
      return "Planned";
  }
}

function executionStatusTone(status: string | undefined): string {
  switch (status) {
    case "executed":
      return "border-cobalt/40 bg-cobalt/10 text-cobalt";
    case "running":
      return "border-gold/40 bg-gold/10 text-gold";
    case "failed":
      return "border-vermilion/40 bg-vermilion/10 text-[#e8a08e]";
    default:
      return "border-white/15 bg-white/[0.04] text-muted";
  }
}

function observedFromStep(step: MissionPlanStep): {
  execution_seconds?: number;
  output_bytes?: number;
  error?: string;
} | null {
  const execution = step.source_metadata?.execution;
  if (!execution || typeof execution !== "object") return null;
  const record = execution as Record<string, unknown>;
  const observed = record.observed;
  if (observed && typeof observed === "object") {
    const metrics = observed as Record<string, unknown>;
    return {
      execution_seconds:
        typeof metrics.execution_seconds === "number"
          ? metrics.execution_seconds
          : undefined,
      output_bytes:
        typeof metrics.output_bytes === "number" ? metrics.output_bytes : undefined,
      error: typeof record.error === "string" ? record.error : undefined,
    };
  }
  if (typeof record.error === "string") {
    return { error: record.error };
  }
  return null;
}

function formatObservedBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  return `${(bytes / 1024).toFixed(1)} KB`;
}

function MissionTimeline({ plan }: { plan: MissionPlan }) {
  const steps = [...(plan.steps ?? [])].sort((a, b) => a.sequence - b.sequence);
  return steps.length ? (
    <ol className="relative space-y-0">
      {steps.map((step, index) => {
        const durationTruth =
          step.duration_seconds == null
            ? "UNAVAILABLE"
            : typeof step.source_metadata?.duration_truth_status === "string"
            ? step.source_metadata.duration_truth_status
            : step.truth_status;
        const execStatus = step.execution_status ?? "planned";
        const observed = observedFromStep(step);
        return (
          <li className="grid gap-4 border-l border-gold/25 pb-7 pl-7 last:pb-0 sm:grid-cols-[minmax(0,0.8fr)_minmax(0,1.2fr)]" key={step.id}>
            <span className="absolute -ml-[2.05rem] mt-0.5 flex h-4 w-4 items-center justify-center rounded-full border border-gold/50 bg-void">
              <span className="h-1.5 w-1.5 rounded-full bg-gold" />
            </span>
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <p className="chart-label text-gold">Step {step.sequence}</p>
                <span
                  className={`rounded-full border px-2 py-0.5 text-[10px] uppercase tracking-wide ${executionStatusTone(execStatus)}`}
                >
                  {executionStatusLabel(execStatus)}
                </span>
              </div>
              <h3 className="mt-1 text-base text-cream">{step.title}</h3>
              <p className="mt-2 text-xs leading-5 text-muted">{step.description}</p>
            </div>
            <dl className="grid grid-cols-2 gap-x-4 gap-y-3 text-xs">
              <div>
                <dt className="text-muted-dark">Start</dt>
                <dd className="mt-1 text-cream">
                  {step.start_time
                    ? formatDateTime(step.start_time)
                    : index === 0
                      ? "At plan start"
                      : `After step ${steps[index - 1].sequence}`}
                </dd>
              </div>
              <div>
                <dt className="text-muted-dark">Duration</dt>
                <dd className="mt-1 flex flex-wrap items-center gap-2 text-cream">
                  {formatDuration(step.duration_seconds)}
                  <TruthBadge compact status={durationTruth} />
                </dd>
                {observed?.execution_seconds != null ? (
                  <dd className="mt-1 flex flex-wrap items-center gap-2 text-xs text-silver">
                    Observed: {observed.execution_seconds.toFixed(3)}s
                    {observed.output_bytes != null
                      ? ` · ${formatObservedBytes(observed.output_bytes)} out`
                      : ""}
                    <TruthBadge compact status="OBSERVED" />
                  </dd>
                ) : null}
                {execStatus === "failed" && observed?.error ? (
                  <dd className="mt-1 text-xs leading-5 text-[#e8a08e]">{observed.error}</dd>
                ) : null}
              </div>
              <div>
                <dt className="text-muted-dark">Provider</dt>
                <dd className="mt-1 break-words text-cream">{step.provider_name}</dd>
              </div>
              <div>
                <dt className="text-muted-dark">Dependency</dt>
                <dd className="mt-1 break-words text-cream">
                  {step.input_artifact || (index ? steps[index - 1].title : "Mission inputs")}
                </dd>
              </div>
              <div className="col-span-2">
                <dt className="text-muted-dark">Current availability</dt>
                <dd className="mt-1 flex flex-wrap items-center gap-2 text-cream">
                  {availabilityForStep(step)}
                  <IntegrationStatusChip
                    compact
                    status={integrationStatusFromStep(step.source_metadata)}
                  />
                  <TruthBadge compact status={step.truth_status} />
                </dd>
              </div>
            </dl>
          </li>
        );
      })}
    </ol>
  ) : (
    <p className="text-sm text-muted">Plan steps are unavailable.</p>
  );
}

function providerIntegrationsForPlan(
  plan: MissionPlan
): Array<{ provider: string; status: string }> {
  const integrations = new Map<string, { provider: string; status: string }>();
  (plan.steps ?? []).forEach((step) => {
    const status = integrationStatusFromStep(step.source_metadata);
    if (!status) return;
    const provider = step.provider_name || "Unknown provider";
    integrations.set(`${provider}:${status}`, { provider, status });
  });
  return Array.from(integrations.values());
}

function AlternativesTable({ plans }: { plans: MissionPlan[] }) {
  return (
    <div className="overflow-x-auto rounded-xl border border-white/10">
      <table className="min-w-[980px] w-full border-collapse text-left text-xs">
        <thead className="bg-white/[0.035] text-muted">
          <tr>
            {["Plan", "Feasibility", "Est. time", "Est. cost", "Data movement", "Access required", "Key reason"].map((label) => (
              <th className="px-4 py-3 font-medium" key={label} scope="col">{label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {plans.map((plan) => {
            const providerIntegrations = providerIntegrationsForPlan(plan);
            const reason =
              plan.recommended
                ? plan.explanation?.why_recommended
                : plan.explanation?.rejection_reasons?.[0]?.message ||
                  plan.explanation?.why_recommended ||
                  "Lower structured preference score.";
            return (
              <tr className="border-t border-white/10 align-top" key={plan.id}>
                <th className="max-w-[220px] px-4 py-4 font-normal text-cream" scope="row">
                  {plan.summary}
                  {plan.recommended ? <span className="mt-1 block text-gold">Recommended</span> : null}
                </th>
                <td className="px-4 py-4">
                  <span className="block text-cream">{statusLabel(plan.status)}</span>
                  <TruthBadge className="mt-2" compact status={statusTruth(plan.status)} />
                </td>
                <td className="px-4 py-4 text-cream">
                  {formatDuration(plan.estimated_total_time_seconds)}
                  <SourcePopover metric={estimateMetric(plan, "duration")} />
                </td>
                <td className="px-4 py-4 text-cream">
                  {formatCost(plan.estimated_total_cost_usd)}
                  <SourcePopover metric={estimateMetric(plan, "cost_usd")} />
                </td>
                <td className="px-4 py-4 text-cream">
                  {formatDataMovement(plan.estimates?.data_movement_mb?.value)}
                  <SourcePopover metric={estimateMetric(plan, "data_movement_mb")} />
                </td>
                <td className="max-w-[180px] px-4 py-4 text-muted">
                  <span className="block">
                    {plan.explanation?.missing_integrations?.join(", ") ||
                      "No provider access flagged"}
                  </span>
                  {providerIntegrations.length ? (
                    <span className="mt-2 flex flex-col items-start gap-1.5">
                      {providerIntegrations.map(({ provider, status }) => (
                        <span
                          className="flex flex-wrap items-center gap-1.5"
                          key={`${provider}:${status}`}
                        >
                          <span className="text-cream">{provider}</span>
                          <IntegrationStatusChip compact status={status} />
                        </span>
                      ))}
                    </span>
                  ) : null}
                </td>
                <td className="max-w-[260px] px-4 py-4 leading-5 text-muted">{reason}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function Sources({
  evidence,
  infrastructure,
}: {
  evidence: SourceEvidence[];
  infrastructure: MissionInfrastructureResponse | null;
}) {
  return (
    <div className="rounded-xl border border-white/10">
      <ul className="divide-y divide-white/10">
        {evidence.map((source) => (
          <li className="flex flex-col gap-3 p-4 sm:flex-row sm:items-start sm:justify-between" key={source.id}>
            <div>
              <p className="text-sm text-cream">{source.source_name}</p>
              <p className="mt-1 text-xs text-muted">
                {source.source_type}
                {source.retrieved_at ? ` · Retrieved ${formatDateTime(source.retrieved_at)}` : ""}
              </p>
              {source.source_url ? (
                <a className="mt-2 inline-flex items-center gap-1 text-xs text-gold hover:underline" href={source.source_url} rel="noreferrer" target="_blank">
                  Open source <ExternalLink aria-hidden size={12} />
                </a>
              ) : null}
            </div>
            <SourcePopover
              metric={{
                value: source.transformed_value ?? source.raw_value ?? source.source_name,
                truth_status: asTruthStatus(source.truth_status),
                source: source.source_name,
                retrieved_at: source.retrieved_at,
                effective_at: source.effective_at,
                method: source.transformation_method,
              }}
            />
          </li>
        ))}
        {infrastructure ? (
          <li className="flex flex-col gap-3 p-4 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <p className="text-sm text-cream">Orbital snapshot {infrastructure.orbital_snapshot.snapshot_id}</p>
              <p className="mt-1 text-xs text-muted">
                Epochs: {infrastructure.orbital_snapshot.epochs?.map(String).join(", ") || "Unavailable"}
                {infrastructure.orbital_snapshot.retrieved_at
                  ? ` · Retrieved ${formatDateTime(infrastructure.orbital_snapshot.retrieved_at)}`
                  : ""}
              </p>
            </div>
            <TruthBadge status={infrastructure.orbital_snapshot.truth_status} />
          </li>
        ) : null}
      </ul>
    </div>
  );
}

export function MissionBrief({
  mission,
  plans,
  candidates,
  infrastructure,
  contactWindows,
  canShare,
  canExport,
  sharing,
  shareUrl,
  shareExpiresDays,
  onShareExpiresDaysChange,
  onShare,
  onRevokeShare,
  revoking,
  exportingPdf,
  exportingJson,
  onExportPdf,
  onExportJson,
  readOnly,
  canExecute,
  onRefreshPlan,
  onExecutionNotice,
}: {
  mission: MissionSummary;
  plans: MissionPlan[];
  candidates: CatalogCandidate[];
  infrastructure: MissionInfrastructureResponse | null;
  contactWindows: ContactWindow[];
  canShare: boolean;
  canExport?: boolean;
  sharing: boolean;
  shareUrl: string | null;
  shareExpiresDays?: number;
  onShareExpiresDaysChange?: (days: number) => void;
  onShare: () => void;
  onRevokeShare?: () => void;
  revoking?: boolean;
  exportingPdf?: boolean;
  exportingJson?: boolean;
  onExportPdf?: () => void;
  onExportJson?: () => void;
  readOnly?: boolean;
  canExecute?: boolean;
  onRefreshPlan?: () => Promise<void>;
  onExecutionNotice?: (message: string | null) => void;
}) {
  const recommended = plans.find((plan) => plan.recommended) ?? null;
  const primary = recommended ?? plans[0];
  if (!primary) return null;
  const chosenIds = selectedCandidateIds(primary);
  const selectedCandidates = candidates.filter((candidate) => chosenIds.has(candidate.id));
  const relevantWindowIds = plans.reduce((ids, plan) => {
    contactWindowIds(plan).forEach((id) => ids.add(id));
    return ids;
  }, new Set<string>());
  const relevantWindows = contactWindows.filter((window) => relevantWindowIds.has(window.id));
  const relevantStationIds = new Set(
    plans.flatMap((plan) =>
      (plan.steps ?? [])
        .filter((step) => step.step_type === "wait_contact" || step.step_type === "downlink")
        .map((step) => step.provider_name)
    )
  );
  const scopedInfrastructure = infrastructure
    ? {
        ...infrastructure,
        ground_stations: (infrastructure.ground_stations ?? []).filter((station) =>
          relevantStationIds.has(station.id)
        ),
      }
    : null;
  const evidence = primary.evidence ?? [];
  const assumptions = planAssumptions(primary, infrastructure);
  const feasibilityStatus =
    primary.status === "feasible"
      ? "Executable for planning now"
      : primary.status === "conditional"
        ? "Provider access required"
        : "No executable path found";
  const missingIntegrations = primary.explanation?.missing_integrations ?? [];

  return (
    <div className="space-y-12">
      <section aria-labelledby="mission-section-01" className="relative overflow-hidden rounded-2xl border border-gold/30 bg-[radial-gradient(circle_at_80%_0%,rgba(201,162,39,0.16),transparent_45%),rgba(10,10,11,0.88)] p-6 shadow-lift sm:p-9">
        <div className="absolute inset-y-0 left-0 w-px bg-gradient-to-b from-transparent via-gold to-transparent" />
        <p className="chart-label text-gold">01 · Executive recommendation</p>
        <h2 className="mt-5 max-w-4xl font-serif text-4xl leading-[1.04] tracking-[-0.035em] text-cream sm:text-6xl" id="mission-section-01">
          {recommended
            ? `Recommended plan: ${primary.summary.toLowerCase()}`
            : "No executable recommendation"}
        </h2>
        <div className="mt-6 flex flex-wrap items-center gap-3">
          <TruthBadge status={statusTruth(primary.status)} />
          <span className="text-sm text-cream">{feasibilityStatus}</span>
        </div>
        <p className="mt-6 max-w-3xl text-base leading-7 text-silver">
          {primary.explanation?.why_recommended ||
            "Every generated path failed at least one hard constraint. Review the unavailable routes below."}
        </p>
        <dl className="mt-8 grid gap-5 border-t border-white/10 pt-6 sm:grid-cols-2 xl:grid-cols-4">
          <div>
            <dt className="chart-label text-muted-dark">Estimated time</dt>
            <dd className="mt-2 flex flex-wrap items-center gap-2 text-lg text-cream">
              {formatDuration(primary.estimated_total_time_seconds)}
              <SourcePopover metric={estimateMetric(primary, "duration")} />
            </dd>
          </div>
          <div>
            <dt className="chart-label text-muted-dark">Estimated cost</dt>
            <dd className="mt-2 flex flex-wrap items-center gap-2 text-lg text-cream">
              {formatCost(primary.estimated_total_cost_usd)}
              <SourcePopover metric={estimateMetric(primary, "cost_usd")} />
            </dd>
          </div>
          <div>
            <dt className="chart-label text-muted-dark">Assumptions used</dt>
            <dd className="mt-2 flex items-center gap-2 text-lg text-cream">
              {primary.explanation?.top_assumptions?.length ?? 0}
              <SourcePopover
                metric={{
                  value: primary.explanation?.top_assumptions?.length ?? 0,
                  truth_status: "CALCULATED",
                  source: "Structured planner explanation",
                  method: "Count of persisted top assumptions",
                }}
              />
            </dd>
          </div>
          <div>
            <dt className="chart-label text-muted-dark">Missing integrations</dt>
            <dd className="mt-2 flex items-center gap-2 text-lg text-cream">
              {missingIntegrations.length}
              <SourcePopover
                metric={{
                  value: missingIntegrations.length,
                  truth_status: "CALCULATED",
                  source: "Structured planner explanation",
                  method: "Count of persisted unavailable integrations",
                }}
              />
            </dd>
          </div>
        </dl>
        <div className="mt-7 grid gap-4 lg:grid-cols-2">
          <div className="rounded-xl border border-cobalt/25 bg-cobalt/5 p-4">
            <p className="chart-label text-cobalt">Executable now</p>
            <ul className="mt-3 space-y-2 text-sm text-silver">
              {(primary.explanation?.executable_now ?? []).map((item) => (
                <li className="flex gap-2" key={item}><Check aria-hidden className="mt-0.5 shrink-0 text-cobalt" size={15} />{item}</li>
              ))}
              {!primary.explanation?.executable_now?.length ? <li>No step is confirmed executable.</li> : null}
            </ul>
          </div>
          <div className="rounded-xl border border-vermilion/25 bg-vermilion/5 p-4">
            <p className="chart-label text-vermilion">Requires access</p>
            <ul className="mt-3 space-y-2 text-sm text-silver">
              {(primary.explanation?.needs_provider ?? []).map((item) => (
                <li className="flex gap-2" key={item}><CircleAlert aria-hidden className="mt-0.5 shrink-0 text-vermilion" size={15} />{item}</li>
              ))}
              {!primary.explanation?.needs_provider?.length ? <li>No provider access blocker identified.</li> : null}
            </ul>
          </div>
        </div>
      </section>

      <Section index="02" title="Feasibility summary">
        <FeasibilitySummary plans={plans} />
      </Section>

      <Section index="03" title="Mission timeline">
        <div className="mb-6">
          <ExecutionDemoPanel
            canExecute={Boolean(canExecute && !readOnly)}
            mission={mission}
            onNotice={onExecutionNotice ?? (() => {})}
            onRefreshPlan={onRefreshPlan ?? (async () => {})}
            plan={primary}
          />
        </div>
        <MissionTimeline plan={primary} />
      </Section>

      <Section index="04" title="Geographic visualization">
        <p className="mb-5 max-w-3xl text-sm leading-6 text-muted">
          Only mission-scoped geography is shown. Public ground-station coordinates do not imply reservation or live capacity.
        </p>
        <MissionGeographyMap candidates={selectedCandidates} infrastructure={scopedInfrastructure} mission={mission} />
        <div className="mt-5 rounded-xl border border-white/10 bg-white/[0.02] p-4">
          <p className="chart-label text-gold">Communication windows</p>
          <div className="mt-4">
            {relevantWindows.length ? (
              <ContactWindowTimeline windows={relevantWindows} />
            ) : (
              <div className="flex flex-wrap items-center gap-2 text-sm text-muted">
                <TruthBadge compact status="UNAVAILABLE" />
                No mission-referenced communication window was returned by the current pass cache.
              </div>
            )}
          </div>
        </div>
      </Section>

      <Section index="05" title="Alternative plans">
        <p className="mb-5 max-w-3xl text-sm leading-6 text-muted">
          The recommended row is included as the comparison baseline. Cost remains unavailable until a sourced pricing integration is connected.
        </p>
        <AlternativesTable plans={plans} />
      </Section>

      <Section index="06" title="Assumptions and sources">
        <div className="grid gap-5 lg:grid-cols-[0.85fr_1.15fr]">
          <AssumptionPanel items={assumptions} title="Assumptions, stale inputs, and unavailable integrations" />
          <Sources evidence={evidence} infrastructure={infrastructure} />
        </div>
      </Section>

      <Section index="07" title="Next actions">
        <div className="grid gap-5 lg:grid-cols-[1fr_auto]">
          <ul className="grid gap-3 sm:grid-cols-2">
            {[
              ...(missingIntegrations.includes("Satellite tasking / reservation API")
                ? ["Connect a satellite tasking provider account", "Request ground-station access"]
                : ["Connect the selected data provider account"]),
              ...(missingIntegrations.includes("Onboard processing provider")
                ? ["Upload payload and onboard compute capabilities"]
                : []),
              "Confirm data residency and destination region",
              "Review the plan with the engineering team",
            ].map((action) => (
              <li className="flex gap-3 rounded-xl border border-white/10 bg-white/[0.025] p-4 text-sm text-cream" key={action}>
                <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full border border-gold/40 text-gold">
                  <Check aria-hidden size={12} />
                </span>
                {action}
              </li>
            ))}
          </ul>
          <div className="flex min-w-52 flex-col gap-3">
            {canExport && onExportPdf ? (
              <LiquidButton disabled={exportingPdf} onClick={onExportPdf} variant="outline">
                {exportingPdf ? "Generating PDF…" : "Export PDF brief"}
              </LiquidButton>
            ) : null}
            {canExport && onExportJson ? (
              <LiquidButton disabled={exportingJson} onClick={onExportJson} variant="outline">
                {exportingJson ? "Preparing JSON…" : "Export JSON"}
              </LiquidButton>
            ) : null}
            {!canExport && !readOnly ? (
              <button className="cursor-not-allowed rounded-xl border border-white/10 px-4 py-3 text-left text-sm text-muted opacity-70" disabled type="button">
                Export mission brief
                <span className="mt-1 block text-xs">Owner session required</span>
              </button>
            ) : null}
            {canShare ? (
              <>
                {onShareExpiresDaysChange ? (
                  <label className="block text-xs text-muted">
                    Link expiry
                    <select
                      className="mt-1 w-full rounded-lg border border-white/15 bg-void px-3 py-2 text-sm text-cream"
                      onChange={(event) => onShareExpiresDaysChange(Number(event.target.value))}
                      value={shareExpiresDays ?? 7}
                    >
                      <option value={1}>1 day</option>
                      <option value={7}>7 days</option>
                      <option value={30}>30 days</option>
                      <option value={90}>90 days</option>
                    </select>
                  </label>
                ) : null}
                <LiquidButton disabled={sharing} onClick={onShare} variant="outline">
                  {sharing ? "Creating link…" : shareUrl ? "Create new share link" : "Create private share link"}
                </LiquidButton>
                {shareUrl && onRevokeShare ? (
                  <LiquidButton disabled={revoking} onClick={onRevokeShare} variant="outline">
                    {revoking ? "Revoking…" : "Revoke latest link"}
                  </LiquidButton>
                ) : null}
              </>
            ) : (
              <button className="cursor-not-allowed rounded-xl border border-white/10 px-4 py-3 text-left text-sm text-muted opacity-70" disabled type="button">
                {readOnly ? "Shared read-only view" : "Read-only mission"}
                <span className="mt-1 block text-xs">
                  {readOnly
                    ? "Exports require the mission owner"
                    : "Only the mission owner can create a link"}
                </span>
              </button>
            )}
            {shareUrl ? (
              <div className="space-y-2">
                <a className="break-all text-xs leading-5 text-gold hover:underline" href={shareUrl}>
                  {shareUrl}
                </a>
                <button
                  className="text-left text-xs text-silver underline-offset-2 hover:underline"
                  onClick={() => {
                    void navigator.clipboard?.writeText(shareUrl);
                  }}
                  type="button"
                >
                  Copy link
                </button>
              </div>
            ) : null}
          </div>
        </div>
      </Section>

      {!readOnly ? (
        <Section index="08" title="Feedback and design partners">
          <MissionFeedbackCapture missionId={mission.id} readOnly={readOnly} />
        </Section>
      ) : null}

      <Section index={readOnly ? "08" : "09"} title="Demo disclosure">
        <aside className="flex gap-4 rounded-xl border border-gold/25 bg-gold/5 p-5 text-sm leading-6 text-silver">
          <LockKeyhole aria-hidden className="mt-0.5 shrink-0 text-gold" size={20} />
          <p>
            This mission plan uses real public orbital and catalog data where available.
            The optional CPU demo runs crop + thumbnail on a fixture GeoTIFF with measured
            OBSERVED durations — not your STAC scene and not GPU inference. Satellite
            tasking, provider reservation, onboard execution, and commercial guarantees
            are not performed unless explicitly marked as connected.
          </p>
        </aside>
      </Section>
    </div>
  );
}
