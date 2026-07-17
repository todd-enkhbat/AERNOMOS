"use client";

import { Suspense, useEffect, useState } from "react";
import { useParams, useSearchParams } from "next/navigation";

import { InlineNotice } from "@/components/InlineNotice";
import { LiquidButton } from "@/components/liquid/LiquidButton";
import { LiquidCard } from "@/components/liquid/LiquidCard";
import { MissionBrief } from "@/components/missions/MissionBrief";
import { PageHeader } from "@/components/PageHeader";
import {
  apiErrorMessage,
  createShareLink,
  discoverMissionCatalog,
  ensureAnonymousSession,
  exportMissionJson,
  generateMissionPlans,
  getContactWindows,
  getMission,
  getMissionInfrastructure,
  getMissionPlan,
  listMissionCandidates,
  listMissionPlans,
  requestMissionPdf,
  revokeShareLink,
  type CatalogCandidate,
  type MissionInfrastructureResponse,
  type MissionPlan,
  type MissionSummary,
} from "@/lib/api";
import { formatDateTime } from "@/lib/format";
import type { ContactWindow } from "@/lib/types";

async function loadPlanDetails(
  missionId: string,
  plans: MissionPlan[],
  shareToken?: string
): Promise<MissionPlan[]> {
  if (!plans.length) return [];
  const details = await Promise.all(
    plans.map((plan) => getMissionPlan(missionId, plan.id, shareToken))
  );
  return details.map((response) => response.plan);
}

function MissionDetailInner() {
  const params = useParams<{ id: string }>();
  const searchParams = useSearchParams();
  const shareToken = searchParams.get("share_token") ?? undefined;
  const [mission, setMission] = useState<MissionSummary | null>(null);
  const [candidates, setCandidates] = useState<CatalogCandidate[]>([]);
  const [infrastructure, setInfrastructure] =
    useState<MissionInfrastructureResponse | null>(null);
  const [plans, setPlans] = useState<MissionPlan[]>([]);
  const [contactWindows, setContactWindows] = useState<ContactWindow[]>([]);
  const [loading, setLoading] = useState(true);
  const [planning, setPlanning] = useState(false);
  const [discovering, setDiscovering] = useState(false);
  const [sharing, setSharing] = useState(false);
  const [revoking, setRevoking] = useState(false);
  const [exportingPdf, setExportingPdf] = useState(false);
  const [exportingJson, setExportingJson] = useState(false);
  const [shareExpiresDays, setShareExpiresDays] = useState(7);
  const [latestShareId, setLatestShareId] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [planError, setPlanError] = useState<string | null>(null);
  const [catalogError, setCatalogError] = useState<string | null>(null);
  const [shareUrl, setShareUrl] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        if (!shareToken) await ensureAnonymousSession();
        const missionResponse = await getMission(params.id, shareToken);
        if (!mounted) return;
        setMission(missionResponse.mission);

        const [candidateResult, infrastructureResult, plansResult, windowsResult] =
          await Promise.allSettled([
            listMissionCandidates(params.id, shareToken),
            getMissionInfrastructure(params.id, shareToken),
            listMissionPlans(params.id, shareToken),
            getContactWindows({ limit: 200 }),
          ]);
        if (!mounted) return;

        if (candidateResult.status === "fulfilled") {
          setCandidates(candidateResult.value.candidates);
        }
        if (infrastructureResult.status === "fulfilled") {
          setInfrastructure(infrastructureResult.value);
        }
        if (windowsResult.status === "fulfilled") {
          setContactWindows(windowsResult.value.contact_windows);
        }
        if (plansResult.status === "fulfilled") {
          try {
            const detailed = await loadPlanDetails(
              params.id,
              plansResult.value.plans,
              shareToken
            );
            if (mounted) setPlans(detailed);
          } catch (error) {
            if (mounted) {
              setPlans(plansResult.value.plans);
              setPlanError(
                apiErrorMessage(
                  error,
                  "Plan summaries loaded, but timeline and source evidence are unavailable."
                )
              );
            }
          }
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

  async function onDiscover() {
    setCatalogError(null);
    setDiscovering(true);
    try {
      await ensureAnonymousSession();
      const response = await discoverMissionCatalog(params.id, { limit: 20 });
      setCandidates(response.candidates);
      if (!response.candidates.length) {
        setCatalogError(
          "No public catalog scenes matched this area and date range. No scenes were invented."
        );
      }
    } catch (error) {
      setCatalogError(
        apiErrorMessage(
          error,
          "The public satellite catalog is temporarily unavailable. No scenes were invented."
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
      if (!response.plans.length) setPlanError("No mission plans were generated.");
    } catch (error) {
      setPlanError(apiErrorMessage(error, "Could not generate mission plans."));
    } finally {
      setPlanning(false);
    }
  }

  async function onShare() {
    setNotice(null);
    setSharing(true);
    try {
      await ensureAnonymousSession();
      const expiresAt = new Date(
        Date.now() + shareExpiresDays * 24 * 60 * 60 * 1000
      ).toISOString();
      const response = await createShareLink(params.id, { expires_at: expiresAt });
      const token = response.share_link.token;
      if (!token) {
        setNotice("A share link was created, but its one-time token was not returned.");
        return;
      }
      setLatestShareId(response.share_link.id);
      setShareUrl(`${window.location.origin}/share/${encodeURIComponent(token)}`);
      setNotice(`Private share link created (expires in ${shareExpiresDays} day${shareExpiresDays === 1 ? "" : "s"}).`);
    } catch (error) {
      setNotice(apiErrorMessage(error, "Could not create a private share link."));
    } finally {
      setSharing(false);
    }
  }

  async function onRevokeShare() {
    if (!latestShareId) {
      setNotice("Create a share link in this session before revoking.");
      return;
    }
    setNotice(null);
    setRevoking(true);
    try {
      await ensureAnonymousSession();
      await revokeShareLink(params.id, latestShareId);
      setShareUrl(null);
      setLatestShareId(null);
      setNotice("Share link revoked. The previous URL no longer works.");
    } catch (error) {
      setNotice(apiErrorMessage(error, "Could not revoke the share link."));
    } finally {
      setRevoking(false);
    }
  }

  async function onExportPdf() {
    setNotice(null);
    setExportingPdf(true);
    try {
      await ensureAnonymousSession();
      const response = await requestMissionPdf(params.id);
      const url = response.export.download_url;
      if (response.export.status !== "ready" || !url) {
        setNotice(
          response.export.error_message ||
            "PDF export did not finish. Try again in a moment."
        );
        return;
      }
      window.open(url, "_blank", "noopener,noreferrer");
      setNotice("PDF mission brief ready.");
    } catch (error) {
      setNotice(apiErrorMessage(error, "Could not generate the PDF brief."));
    } finally {
      setExportingPdf(false);
    }
  }

  async function onExportJson() {
    setNotice(null);
    setExportingJson(true);
    try {
      await ensureAnonymousSession();
      const document = await exportMissionJson(params.id, shareToken);
      const blob = new Blob([JSON.stringify(document, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const anchor = window.document.createElement("a");
      anchor.href = url;
      anchor.download = `nomos-mission-${params.id}.json`;
      anchor.click();
      URL.revokeObjectURL(url);
      setNotice(`JSON export ready (schema_version ${document.schema_version}).`);
    } catch (error) {
      setNotice(apiErrorMessage(error, "Could not export mission JSON."));
    } finally {
      setExportingJson(false);
    }
  }

  const canEdit = Boolean(mission && !mission.is_example && !shareToken);

  return (
    <div className="page-shell pb-16">
      <PageHeader
        action={
          <LiquidButton
            href={mission?.is_example ? "/examples" : "/missions"}
            variant="outline"
          >
            {mission?.is_example ? "Back to examples" : "Back to missions"}
          </LiquidButton>
        }
        description="A source-backed infrastructure recommendation with explicit assumptions, access requirements, and unavailable capabilities."
        eyebrow={mission?.is_example ? "Public example · Mission brief" : "Private workspace · Mission brief"}
        title={mission?.title ?? "Mission brief"}
      />

      {notice ? (
        <div className="mb-5">
          <InlineNotice message={notice} />
        </div>
      ) : null}

      {loading ? (
        <div aria-busy="true" aria-live="polite" className="space-y-4">
          <div className="h-72 animate-pulse rounded-2xl border border-white/10 bg-white/[0.03]" />
          <div className="grid gap-4 sm:grid-cols-4">
            {[0, 1, 2, 3].map((item) => (
              <div className="h-32 animate-pulse rounded-xl border border-white/10 bg-white/[0.025]" key={item} />
            ))}
          </div>
          <span className="sr-only">Loading mission recommendation and evidence.</span>
        </div>
      ) : mission ? (
        <div className="space-y-8">
          <LiquidCard className="!p-4">
            <dl className="grid gap-4 text-xs sm:grid-cols-2 lg:grid-cols-4">
              <div>
                <dt className="chart-label text-muted-dark">Mission status</dt>
                <dd className="mt-1 capitalize text-cream">{mission.status}</dd>
              </div>
              <div>
                <dt className="chart-label text-muted-dark">Objective</dt>
                <dd className="mt-1 text-cream">{mission.objective_type.replaceAll("_", " ")}</dd>
              </div>
              <div>
                <dt className="chart-label text-muted-dark">Deadline</dt>
                <dd className="mt-1 text-cream">
                  {mission.deadline ? formatDateTime(mission.deadline) : "Not specified"}
                </dd>
              </div>
              <div>
                <dt className="chart-label text-muted-dark">Plan version</dt>
                <dd className="mt-1 text-cream">
                  {plans.length ? `v${Math.max(...plans.map((plan) => plan.version))}` : "Not generated"}
                </dd>
              </div>
            </dl>
          </LiquidCard>

          {planError ? <InlineNotice message={planError} /> : null}
          {catalogError ? <InlineNotice message={catalogError} /> : null}

          {!plans.length ? (
            <section className="rounded-2xl border border-gold/25 bg-[radial-gradient(circle_at_80%_0%,rgba(201,162,39,0.12),transparent_48%),rgba(10,10,11,0.82)] p-6 sm:p-9">
              <p className="chart-label text-gold">Recommendation not generated</p>
              <h2 className="mt-4 max-w-2xl font-serif text-4xl leading-tight tracking-[-0.03em] text-cream">
                Generate a source-backed mission plan.
              </h2>
              <p className="mt-4 max-w-2xl text-sm leading-6 text-muted">
                Nomos will compare existing imagery, customer edge, ground-to-cloud, and onboard paths. Missing integrations will remain unavailable instead of being simulated.
              </p>
              {canEdit ? (
                <div className="mt-6 flex flex-wrap gap-3">
                  <LiquidButton disabled={planning} onClick={onGeneratePlans} variant="primary">
                    {planning ? "Generating plan…" : "Generate plan"}
                  </LiquidButton>
                  {!candidates.length ? (
                    <LiquidButton disabled={discovering} onClick={onDiscover} variant="outline">
                      {discovering ? "Searching catalog…" : "Discover public imagery first"}
                    </LiquidButton>
                  ) : null}
                </div>
              ) : (
                <p className="mt-5 text-sm text-muted">
                  This read-only mission does not have generated plans.
                </p>
              )}
            </section>
          ) : (
            <MissionBrief
              canExport={canEdit}
              canShare={canEdit}
              candidates={candidates}
              contactWindows={contactWindows}
              exportingJson={exportingJson}
              exportingPdf={exportingPdf}
              infrastructure={infrastructure}
              mission={mission}
              onExportJson={onExportJson}
              onExportPdf={onExportPdf}
              onRevokeShare={onRevokeShare}
              onShare={onShare}
              onShareExpiresDaysChange={setShareExpiresDays}
              plans={plans}
              revoking={revoking}
              shareExpiresDays={shareExpiresDays}
              shareUrl={shareUrl}
              sharing={sharing}
            />
          )}
        </div>
      ) : (
        <section className="rounded-xl border border-vermilion/30 bg-vermilion/5 p-6">
          <h2 className="font-serif text-2xl text-cream">Mission unavailable</h2>
          <p className="mt-2 text-sm text-muted">
            Return to your private mission list or open a valid share link.
          </p>
        </section>
      )}
    </div>
  );
}

export default function MissionDetailPage() {
  return (
    <Suspense fallback={<div className="page-shell py-10 text-sm text-muted">Loading mission brief…</div>}>
      <MissionDetailInner />
    </Suspense>
  );
}
