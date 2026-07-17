"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { FadeIn, Stagger, StaggerItem } from "@/components/motion/primitives";
import { PageHeader } from "@/components/PageHeader";
import { TruthBadge } from "@/components/truth";
import { LiquidButton } from "@/components/liquid/LiquidButton";
import { LiquidCard } from "@/components/liquid/LiquidCard";
import {
  apiErrorMessage,
  getMissionPlan,
  listExampleMissions,
  listMissionPlans
} from "@/lib/api";
import type { MissionPlan, MissionSummary } from "@/lib/api";
import { formatMinutes, labelize } from "@/lib/format";

type ExampleDisclosure = {
  kind: "example_disclosure";
  slug?: string;
  summary?: string;
  real_data?: string[];
  real_calculations?: string[];
  estimated_steps?: string[];
  simulated_steps?: string[];
  unavailable_integrations?: string[];
};

function disclosureFromMission(mission: MissionSummary): ExampleDisclosure | null {
  const systems = Array.isArray(mission.customer_systems)
    ? mission.customer_systems
    : [];
  for (const item of systems) {
    if (
      item &&
      typeof item === "object" &&
      !Array.isArray(item) &&
      (item as { kind?: string }).kind === "example_disclosure"
    ) {
      return item as ExampleDisclosure;
    }
  }
  return null;
}

const disclosureSections: Array<{
  key: keyof ExampleDisclosure;
  label: string;
  simulated?: boolean;
}> = [
  { key: "real_data", label: "Real data" },
  { key: "real_calculations", label: "Real calculations" },
  { key: "estimated_steps", label: "Estimated" },
  { key: "simulated_steps", label: "Simulated", simulated: true },
  { key: "unavailable_integrations", label: "Unavailable", simulated: true }
];

const truthLegend: Array<{ status: string; blurb: string }> = [
  { status: "CALCULATED", blurb: "Orbital math from public TLEs (SGP4)" },
  { status: "ESTIMATED", blurb: "Modeled transfer & processing timing" },
  { status: "SIMULATED", blurb: "Authored reference scene & node ops" },
  { status: "UNAVAILABLE", blurb: "Tasking, booking & pricing not connected" }
];

function feasibilityTone(status?: string | null): string {
  switch (status) {
    case "feasible":
      return "text-emerald-300";
    case "conditional":
      return "text-gold";
    case "rejected":
      return "text-[#e8a08e]";
    default:
      return "text-muted";
  }
}

function pickPlan(plans: MissionPlan[]): MissionPlan | null {
  if (!plans.length) return null;
  return (
    plans.find((plan) => plan.recommended) ??
    plans.find((plan) => plan.status === "feasible") ??
    plans[0]
  );
}

function FeaturedSpecimen({
  mission,
  plan
}: {
  mission: MissionSummary;
  plan: MissionPlan;
}) {
  const steps = (plan.steps ?? []).slice(0, 5);
  const durationSeconds = plan.estimated_total_time_seconds ?? null;
  const durationMinutes =
    durationSeconds != null ? durationSeconds / 60 : null;
  const durationStatus = plan.estimates?.duration?.truth_status ?? "ESTIMATED";
  const costStatus = plan.estimates?.cost_usd?.truth_status ?? "UNAVAILABLE";

  return (
    <FadeIn when="mount">
      <LiquidCard className="overflow-visible">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="chart-label text-gold">Featured example · live planner output</p>
            <h2 className="mt-2 text-xl font-medium text-cream">{mission.title}</h2>
            <p className="mt-1 text-sm text-muted">
              {labelize(mission.objective_type)}
              {mission.preferred_compute_location
                ? ` · ${labelize(mission.preferred_compute_location)}`
                : ""}
            </p>
          </div>
          <div className="flex flex-col items-end gap-2">
            <span
              className={`chart-label ${feasibilityTone(plan.feasibility_status ?? plan.status)}`}
            >
              {labelize(plan.feasibility_status ?? plan.status)}
            </span>
            {plan.recommended ? (
              <span className="rounded-full border border-gold/40 bg-gold/10 px-2.5 py-0.5 text-[0.68rem] uppercase tracking-[0.14em] text-gold">
                Recommended
              </span>
            ) : null}
          </div>
        </div>

        <p className="prose-compact mt-4 text-silver">{plan.summary}</p>
        {plan.explanation?.why_recommended ? (
          <p className="prose-compact mt-2 text-sm text-muted">
            {plan.explanation.why_recommended}
          </p>
        ) : null}

        <div className="mt-5 flex flex-wrap gap-2.5">
          <div className="rounded-xl border border-line bg-void/40 px-3 py-2">
            <p className="chart-label text-muted-dark">Est. duration</p>
            <div className="mt-1 flex items-center gap-2">
              <span className="text-sm text-cream">
                {durationMinutes != null ? formatMinutes(durationMinutes) : "—"}
              </span>
              <TruthBadge compact status={durationStatus} />
            </div>
          </div>
          <div className="rounded-xl border border-line bg-void/40 px-3 py-2">
            <p className="chart-label text-muted-dark">Cost</p>
            <div className="mt-1 flex items-center gap-2">
              <span className="text-sm text-cream">No pricing source</span>
              <TruthBadge compact status={costStatus} />
            </div>
          </div>
          <div className="rounded-xl border border-line bg-void/40 px-3 py-2">
            <p className="chart-label text-muted-dark">Steps</p>
            <p className="mt-1 text-sm text-cream">{plan.steps?.length ?? steps.length}</p>
          </div>
        </div>

        {steps.length ? (
          <ol className="mt-6 space-y-2.5">
            {steps.map((step) => (
              <li
                className="flex items-start gap-3 rounded-xl border border-line/70 bg-void/30 px-3 py-2.5"
                key={step.id}
              >
                <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full border border-gold/30 text-xs text-gold">
                  {step.sequence}
                </span>
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-sm text-cream">{step.title}</span>
                    <TruthBadge compact status={step.truth_status} />
                  </div>
                  <p className="mt-0.5 truncate text-xs text-muted">
                    {step.provider_name}
                    {step.feasibility_status &&
                    step.feasibility_status !== "feasible"
                      ? ` · ${labelize(step.feasibility_status)}`
                      : ""}
                  </p>
                </div>
              </li>
            ))}
          </ol>
        ) : null}

        <div className="mt-6 flex flex-wrap gap-3">
          <LiquidButton href={`/missions/${mission.id}`} variant="primary">
            Open full plan
          </LiquidButton>
          <LiquidButton href="/plan" variant="ghost">
            Build your own
          </LiquidButton>
        </div>
      </LiquidCard>
    </FadeIn>
  );
}

export function ExamplesLibrary() {
  const [missions, setMissions] = useState<MissionSummary[]>([]);
  const [featuredPlan, setFeaturedPlan] = useState<MissionPlan | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    async function load() {
      try {
        const response = await listExampleMissions();
        if (!mounted) return;
        setMissions(response.missions);
        setError(null);

        const featured = response.missions[0];
        if (featured) {
          try {
            const planList = await listMissionPlans(featured.id);
            const chosen = pickPlan(planList.plans);
            if (chosen) {
              const detail = await getMissionPlan(featured.id, chosen.id);
              if (mounted) setFeaturedPlan(detail.plan);
            }
          } catch {
            // Featured specimen is progressive enhancement; the grid still renders.
            if (mounted) setFeaturedPlan(null);
          }
        }
      } catch (err) {
        if (mounted) {
          setError(
            apiErrorMessage(err, "Example missions are temporarily unavailable.")
          );
        }
      } finally {
        if (mounted) setLoading(false);
      }
    }
    load();
    return () => {
      mounted = false;
    };
  }, []);

  const featuredMission = missions[0] ?? null;

  return (
    <div className="page-shell pb-16">
      <PageHeader
        eyebrow="Examples"
        title="See the planner's real output"
        description="Curated public missions that run through the same source-backed planner customers use. Every step carries a truth label — real, calculated, estimated, simulated, or unavailable — so nothing masquerades as live execution."
        action={
          <LiquidButton href="/plan" variant="primary">
            Build a mission plan
          </LiquidButton>
        }
      />

      <aside className="mt-5 rounded-2xl border border-gold/25 bg-gold/8 px-4 py-3">
        <div className="flex flex-wrap items-center gap-2">
          <TruthBadge compact status="SIMULATED" />
          <p className="text-sm text-cream">
            Curated examples ship with an authored reference scene. They are not
            private customer missions and not live execution results.
          </p>
        </div>
      </aside>

      {error ? (
        <p className="mt-5 rounded-xl border border-[#be543c]/40 bg-[#be543c]/10 px-4 py-3 text-sm text-[#e8a08e]">
          {error}
        </p>
      ) : null}

      {loading ? (
        <div className="mt-8 space-y-5">
          <div className="min-h-[280px] animate-pulse rounded-2xl border border-line bg-void/40" />
          <div className="grid gap-4 md:grid-cols-2">
            {[0, 1, 2, 3].map((key) => (
              <div
                className="min-h-[200px] animate-pulse rounded-2xl border border-line bg-void/40"
                key={key}
              />
            ))}
          </div>
        </div>
      ) : (
        <>
          {featuredMission && featuredPlan ? (
            <div className="mt-8">
              <FeaturedSpecimen mission={featuredMission} plan={featuredPlan} />
            </div>
          ) : null}

          <FadeIn delay={0.05} when="mount">
            <div className="mt-8 rounded-2xl border border-line bg-void/30 px-4 py-4">
              <p className="chart-label text-silver">How to read the labels</p>
              <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                {truthLegend.map((entry) => (
                  <div className="flex items-start gap-2" key={entry.status}>
                    <TruthBadge compact status={entry.status} />
                    <span className="text-xs leading-5 text-cream/85">
                      {entry.blurb}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </FadeIn>

          <div className="mt-10">
            <p className="chart-label text-silver">All curated examples</p>
            <Stagger className="mt-4 grid gap-5 lg:grid-cols-2" when="mount">
              {missions.map((mission) => {
                const disclosure = disclosureFromMission(mission);
                return (
                  <StaggerItem className="h-full" key={mission.id}>
                    <LiquidCard className="flex h-full flex-col" interactive={false}>
                      <div className="flex flex-wrap items-start justify-between gap-3">
                        <div>
                          <p className="chart-label text-gold">Public example</p>
                          <h3 className="mt-2 text-lg font-medium text-cream">
                            {mission.title}
                          </h3>
                          <p className="mt-1 text-sm text-muted">
                            {labelize(mission.objective_type)}
                            {mission.preferred_compute_location
                              ? ` · ${labelize(mission.preferred_compute_location)}`
                              : ""}
                          </p>
                        </div>
                        <TruthBadge compact status="SIMULATED" />
                      </div>

                      <p className="prose-compact mt-4 text-silver">
                        {disclosure?.summary ??
                          mission.notes ??
                          "Curated public example mission."}
                      </p>

                      {disclosure ? (
                        <div className="mt-5 space-y-3">
                          {disclosureSections.map((section) => {
                            const items = disclosure[section.key];
                            if (!Array.isArray(items) || items.length === 0) {
                              return null;
                            }
                            return (
                              <div key={section.key}>
                                <p className="chart-label text-muted-dark">
                                  {section.label}
                                </p>
                                <ul className="mt-1.5 space-y-1">
                                  {items.map((item) => (
                                    <li
                                      className="flex gap-2 text-xs leading-5 text-cream/85"
                                      key={item}
                                    >
                                      <span
                                        aria-hidden
                                        className={`mt-1.5 h-1 w-1 shrink-0 rounded-full ${
                                          section.simulated ? "bg-gold" : "bg-cobalt"
                                        }`}
                                      />
                                      <span>{item}</span>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            );
                          })}
                        </div>
                      ) : null}

                      <div className="mt-6 flex flex-wrap gap-3">
                        <LiquidButton
                          href={`/missions/${mission.id}`}
                          variant="outline"
                        >
                          Open example mission
                        </LiquidButton>
                      </div>
                    </LiquidCard>
                  </StaggerItem>
                );
              })}
            </Stagger>
          </div>
        </>
      )}

      {!loading && missions.length === 0 && !error ? (
        <LiquidCard className="mt-8">
          <p className="chart-label text-gold">No examples seeded yet</p>
          <p className="prose-compact mt-3 max-w-2xl text-muted">
            Run the API seed to publish curated example missions, or build your own
            private plan.
          </p>
          <div className="mt-5">
            <LiquidButton href="/plan" variant="primary">
              Build a mission plan
            </LiquidButton>
          </div>
        </LiquidCard>
      ) : null}

      <div className="mt-12 border-t border-gold/12 pt-8">
        <p className="chart-label text-silver">Also available</p>
        <h2 className="display mt-2 text-xl text-cream">Historical simulation demo</h2>
        <p className="prose-compact mt-3 max-w-xl text-muted">
          The legacy Job path at{" "}
          <Link className="text-gold hover:underline" href="/jobs">
            /jobs
          </Link>{" "}
          still runs against the production API with simulated execution and canned
          detections. It is not the primary product path.
        </p>
      </div>
    </div>
  );
}
