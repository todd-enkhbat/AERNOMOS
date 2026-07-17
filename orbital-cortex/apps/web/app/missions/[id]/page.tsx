"use client";

import Link from "next/link";
import { useParams, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";

import { InlineNotice } from "@/components/InlineNotice";
import { MissionInfrastructurePanel } from "@/components/missions/MissionInfrastructurePanel";
import { PageHeader } from "@/components/PageHeader";
import { LiquidButton } from "@/components/liquid/LiquidButton";
import { LiquidCard } from "@/components/liquid/LiquidCard";
import { SourcePopover, TruthBadge, asProvenanced } from "@/components/truth";
import {
  apiErrorMessage,
  createShareLink,
  discoverMissionCatalog,
  ensureAnonymousSession,
  generateMissionPlans,
  getMission,
  getMissionInfrastructure,
  listMissionCandidates,
  listMissionPlans,
  type CatalogCandidate,
  type MissionInfrastructureResponse,
  type MissionPlan,
  type MissionSummary
} from "@/lib/api";
import { formatDateTime } from "@/lib/format";

function formatBytes(bytes: number | null | undefined): string {
  if (bytes == null || bytes <= 0) return "unknown";
  const gib = bytes / (1024 * 1024 * 1024);
  if (gib >= 1) return `${gib.toFixed(1)} GiB`;
  const mib = bytes / (1024 * 1024);
  return `${mib.toFixed(0)} MiB`;
}

function MissionDetailInner() {
  const params = useParams<{ id: string }>();
  const searchParams = useSearchParams();
  const shareToken = searchParams.get("share_token") ?? undefined;
  const [mission, setMission] = useState<MissionSummary | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [shareUrl, setShareUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [candidates, setCandidates] = useState<CatalogCandidate[]>([]);
  const [discovering, setDiscovering] = useState(false);
  const [catalogError, setCatalogError] = useState<string | null>(null);
  const [infrastructure, setInfrastructure] = useState<MissionInfrastructureResponse | null>(null);
  const [infraError, setInfraError] = useState<string | null>(null);
  const [plans, setPlans] = useState<MissionPlan[]>([]);
  const [planning, setPlanning] = useState(false);
  const [planError, setPlanError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        if (!shareToken) {
          await ensureAnonymousSession();
        }
        const response = await getMission(params.id, shareToken);
        if (mounted) {
          setMission(response.mission);
          setNotice(null);
        }
        try {
          const listed = await listMissionCandidates(params.id, shareToken);
          if (mounted) setCandidates(listed.candidates);
        } catch {
          // Candidates are optional on first load (e.g. share without prior discover).
        }
        try {
          const infra = await getMissionInfrastructure(params.id, shareToken);
          if (mounted) setInfrastructure(infra);
        } catch {
          if (mounted) setInfraError("Mission infrastructure is unavailable.");
        }
        try {
          const listed = await listMissionPlans(params.id, shareToken);
          if (mounted) setPlans(listed.plans);
        } catch {
          // Plans are optional until generation runs.
        }
      } catch (error) {
        if (mounted) {
          setNotice(apiErrorMessage(error, "This mission is private or unavailable."));
        }
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => {
      mounted = false;
    };
  }, [params.id, shareToken]);

  async function onShare() {
    setNotice(null);
    try {
      await ensureAnonymousSession();
      const response = await createShareLink(params.id);
      const token = response.share_link.token;
      if (!token) {
        setNotice("Share link created, but the token was not returned.");
        return;
      }
      const url = `${window.location.origin}/missions/${params.id}?share_token=${encodeURIComponent(token)}`;
      setShareUrl(url);
    } catch (error) {
      setNotice(apiErrorMessage(error, "Could not create a share link."));
    }
  }

  async function onDiscover() {
    setCatalogError(null);
    setDiscovering(true);
    try {
      await ensureAnonymousSession();
      const response = await discoverMissionCatalog(params.id, { limit: 20 });
      setCandidates(response.candidates);
      if (response.candidates.length === 0) {
        setCatalogError(
          "No catalog scenes matched this AOI and date window. Try a wider date range."
        );
      }
    } catch (error) {
      setCatalogError(
        apiErrorMessage(
          error,
          "Satellite catalog is temporarily unavailable. No scenes were invented."
        )
      );
    } finally {
      setDiscovering(false);
    }
  }

  async function onGeneratePlans() {
    setPlanError(null);
    setPlanning(true);
    try {
      await ensureAnonymousSession();
      const response = await generateMissionPlans(params.id);
      setPlans(response.plans);
      if (response.plans.length === 0) {
        setPlanError("No plans were generated.");
      }
    } catch (error) {
      setPlanError(apiErrorMessage(error, "Could not generate mission plans."));
    } finally {
      setPlanning(false);
    }
  }

  const canDiscover = Boolean(mission && !mission.is_example && !shareToken);
  const canPlan = canDiscover;
  const recommended = plans.find((plan) => plan.recommended) ?? null;

  return (
    <div className="page-shell pb-16">
      <PageHeader
        action={
          <LiquidButton href="/missions" variant="outline">
            Back to missions
          </LiquidButton>
        }
        eyebrow={mission?.is_example ? "Public example" : "Private mission"}
        title={mission?.title ?? "Mission"}
        description="Access requires your anonymous session cookie or a valid private share token."
      />

      {notice ? (
        <div className="mb-4">
          <InlineNotice message={notice} />
        </div>
      ) : null}

      {loading ? (
        <p className="text-sm text-muted">Loading mission…</p>
      ) : mission ? (
        <div className="grid gap-6">
          <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
            <LiquidCard>
              <dl className="space-y-3 text-sm">
                <div>
                  <dt className="chart-label text-muted">Status</dt>
                  <dd className="mt-1 text-cream">{mission.status}</dd>
                </div>
                <div>
                  <dt className="chart-label text-muted">Objective</dt>
                  <dd className="mt-1 text-cream">{mission.objective_type}</dd>
                </div>
                <div>
                  <dt className="chart-label text-muted">Created</dt>
                  <dd className="mt-1 text-cream">{formatDateTime(mission.created_at)}</dd>
                </div>
                {mission.notes ? (
                  <div>
                    <dt className="chart-label text-muted">Notes</dt>
                    <dd className="mt-1 text-cream">{mission.notes}</dd>
                  </div>
                ) : null}
              </dl>
            </LiquidCard>

            <LiquidCard>
              <p className="chart-label text-gold">Sharing</p>
              {mission.is_example ? (
                <p className="mt-3 text-sm text-muted">
                  This is a curated public example. Private share links apply to
                  session-owned missions only.
                </p>
              ) : (
                <>
                  <p className="mt-3 text-sm text-muted">
                    Create a read-only share token. Recipients do not need your session
                    cookie.
                  </p>
                  <LiquidButton className="mt-4" onClick={onShare} variant="primary">
                    Create share link
                  </LiquidButton>
                  {shareUrl ? (
                    <p className="mt-3 break-all text-xs text-gold">{shareUrl}</p>
                  ) : null}
                </>
              )}
              <p className="mt-6 text-xs text-muted">
                Legacy demo jobs remain at{" "}
                <Link className="text-gold hover:underline" href="/jobs">
                  /jobs
                </Link>
                .
              </p>
            </LiquidCard>
          </div>

          <LiquidCard>
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <p className="chart-label text-gold">Catalog data</p>
                <p className="mt-2 max-w-2xl text-sm text-muted">
                  Discover real Sentinel-1 GRD scenes from Microsoft Planetary Computer
                  over this mission AOI. Results are provider-reported — never fabricated.
                </p>
              </div>
              {canDiscover ? (
                <LiquidButton
                  disabled={discovering}
                  onClick={onDiscover}
                  variant="primary"
                >
                  {discovering ? "Searching catalog…" : "Discover catalog data"}
                </LiquidButton>
              ) : null}
            </div>

            {catalogError ? (
              <div className="mt-4">
                <InlineNotice message={catalogError} />
              </div>
            ) : null}

            {candidates.length === 0 && !catalogError ? (
              <p className="mt-4 text-sm text-muted">
                {canDiscover
                  ? "No candidates persisted yet. Run discovery to search the public STAC catalog."
                  : "No catalog candidates for this mission."}
              </p>
            ) : null}

            {candidates.length > 0 ? (
              <ul className="mt-6 space-y-4">
                {candidates.map((candidate) => {
                  const acquisition = asProvenanced(candidate.acquisition_time);
                  const size = asProvenanced(candidate.estimated_size_bytes);
                  return (
                  <li
                    key={candidate.id}
                    className="border-t border-white/10 pt-4 first:border-t-0 first:pt-0"
                  >
                    <div className="flex flex-wrap items-baseline justify-between gap-2">
                      <p className="font-mono text-sm text-cream">
                        {candidate.external_item_id}
                      </p>
                      <TruthBadge status={candidate.truth_status} compact />
                    </div>
                    <dl className="mt-2 grid gap-2 text-xs text-muted sm:grid-cols-2">
                      <div>
                        <dt className="text-muted/80">Collection</dt>
                        <dd className="text-cream">{candidate.collection}</dd>
                      </div>
                      <div>
                        <dt className="text-muted/80">Acquisition</dt>
                        <dd className="mt-0.5 flex flex-wrap items-center gap-2 text-cream">
                          {acquisition ? formatDateTime(String(acquisition.value)) : "—"}
                          {acquisition ? <SourcePopover metric={acquisition} /> : null}
                        </dd>
                      </div>
                      <div>
                        <dt className="text-muted/80">Estimated size</dt>
                        <dd className="mt-0.5 flex flex-wrap items-center gap-2 text-cream">
                          {size ? formatBytes(Number(size.value)) : "unknown"}
                          {size ? <SourcePopover metric={size} /> : null}
                        </dd>
                      </div>
                      <div>
                        <dt className="text-muted/80">Retrieved</dt>
                        <dd className="text-cream">
                          {formatDateTime(candidate.source_timestamp)}
                        </dd>
                      </div>
                      <div className="sm:col-span-2">
                        <dt className="text-muted/80">Assets</dt>
                        <dd className="text-cream">
                          {candidate.available_assets.length
                            ? candidate.available_assets
                                .map(
                                  (asset) =>
                                    `${asset.key ?? "asset"} (${asset.media_type ?? "unknown"}; ${(asset.roles || []).join(",") || "no-role"})`
                                )
                                .join(" · ")
                            : "none listed"}
                        </dd>
                      </div>
                      <div className="sm:col-span-2">
                        <dt className="text-muted/80">Source</dt>
                        <dd className="break-all text-cream">
                          {candidate.source_provider}
                          {candidate.source_url ? (
                            <>
                              {" · "}
                              <a
                                className="text-gold hover:underline"
                                href={candidate.source_url}
                                rel="noreferrer"
                                target="_blank"
                              >
                                STAC item
                              </a>
                            </>
                          ) : null}
                        </dd>
                      </div>
                    </dl>
                  </li>
                  );
                })}
              </ul>
            ) : null}
          </LiquidCard>

          <LiquidCard>
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <p className="chart-label text-gold">Feasibility plans</p>
                <p className="mt-2 max-w-2xl text-sm text-muted">
                  Structured planner output — multiple candidate paths ranked without an LLM.
                  Estimates carry truth status; cost stays unavailable until a real pricing
                  source exists.
                </p>
              </div>
              {canPlan ? (
                <LiquidButton disabled={planning} onClick={onGeneratePlans} variant="primary">
                  {planning ? "Generating plans…" : "Generate plans"}
                </LiquidButton>
              ) : null}
            </div>

            {planError ? (
              <div className="mt-4">
                <InlineNotice message={planError} />
              </div>
            ) : null}

            {plans.length === 0 && !planError ? (
              <p className="mt-4 text-sm text-muted">
                {canPlan
                  ? "No plans yet. Discover catalog data first, then generate feasibility plans."
                  : "No plans for this mission."}
              </p>
            ) : null}

            {recommended ? (
              <div className="mt-6 border-t border-white/10 pt-4">
                <p className="text-xs uppercase tracking-wide text-gold">Recommended</p>
                <p className="mt-1 text-cream">{recommended.summary}</p>
                <p className="mt-2 text-sm text-muted">
                  {recommended.explanation?.why_recommended ?? "Structured scoring selected this path."}
                </p>
                <dl className="mt-3 grid gap-2 text-xs text-muted sm:grid-cols-3">
                  <div>
                    <dt>Status</dt>
                    <dd className="text-cream">{recommended.status}</dd>
                  </div>
                  <div>
                    <dt>Duration</dt>
                    <dd className="mt-0.5 flex flex-wrap items-center gap-2 text-cream">
                      {recommended.estimated_total_time_seconds != null
                        ? `${Math.round(recommended.estimated_total_time_seconds / 60)} min`
                        : "—"}
                      {recommended.estimates?.duration ? (
                        <TruthBadge
                          status={recommended.estimates.duration.truth_status ?? "ESTIMATED"}
                          compact
                        />
                      ) : null}
                    </dd>
                  </div>
                  <div>
                    <dt>Cost</dt>
                    <dd className="mt-0.5 flex flex-wrap items-center gap-2 text-cream">
                      {recommended.estimated_total_cost_usd != null
                        ? `$${recommended.estimated_total_cost_usd.toFixed(2)}`
                        : "unavailable"}
                      <TruthBadge
                        status={recommended.estimates?.cost_usd?.truth_status ?? "UNAVAILABLE"}
                        compact
                      />
                    </dd>
                  </div>
                </dl>
              </div>
            ) : null}

            {plans.length > 0 ? (
              <ul className="mt-6 space-y-3">
                {plans.map((plan) => (
                  <li
                    key={plan.id}
                    className="border-t border-white/10 pt-3 first:border-t-0 first:pt-0"
                  >
                    <div className="flex flex-wrap items-baseline justify-between gap-2">
                      <p className="text-sm text-cream">
                        {plan.summary}
                        {plan.recommended ? (
                          <span className="ml-2 text-xs text-gold">recommended</span>
                        ) : null}
                      </p>
                      <span className="font-mono text-xs text-muted">{plan.status}</span>
                    </div>
                    {plan.explanation?.rejection_reasons?.length ? (
                      <p className="mt-1 text-xs text-muted">
                        {plan.explanation.rejection_reasons
                          .map((reason) => reason.message || reason.code)
                          .filter(Boolean)
                          .join(" · ")}
                      </p>
                    ) : null}
                  </li>
                ))}
              </ul>
            ) : null}
          </LiquidCard>

          <LiquidCard>
            <p className="chart-label text-gold">Mission infrastructure</p>
            <p className="mt-2 max-w-2xl text-sm text-muted">
              Fleet satellites and ground stations scoped to this mission, with source
              labels on every operational number.
            </p>
            {infraError ? (
              <div className="mt-4">
                <InlineNotice message={infraError} />
              </div>
            ) : infrastructure ? (
              <div className="mt-6">
                <MissionInfrastructurePanel infrastructure={infrastructure} />
              </div>
            ) : (
              <p className="mt-4 text-sm text-muted">Loading infrastructure…</p>
            )}
          </LiquidCard>
        </div>
      ) : null}
    </div>
  );
}

export default function MissionDetailPage() {
  return (
    <Suspense fallback={<div className="page-shell py-10 text-sm text-muted">Loading…</div>}>
      <MissionDetailInner />
    </Suspense>
  );
}
