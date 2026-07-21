"use client";

import { Suspense, useEffect, useState } from "react";
import { useParams } from "next/navigation";

import { InlineNotice } from "@/components/InlineNotice";
import { LiquidButton } from "@/components/liquid/LiquidButton";
import { MissionBrief } from "@/components/missions/MissionBrief";
import { PageHeader } from "@/components/PageHeader";
import {
  apiErrorMessage,
  exportMissionJson,
  getContactWindows,
  getMission,
  getMissionInfrastructure,
  getMissionPlan,
  listMissionCandidates,
  listMissionPlans,
  resolveShareToken,
  type CatalogCandidate,
  type MissionInfrastructureResponse,
  type MissionPlan,
  type MissionSummary,
} from "@/lib/api";
import type { ContactWindow } from "@/lib/types";

async function loadPlanDetails(
  missionId: string,
  plans: MissionPlan[],
  shareToken: string
): Promise<MissionPlan[]> {
  if (!plans.length) return [];
  const details = await Promise.all(
    plans.map((plan) => getMissionPlan(missionId, plan.id, shareToken))
  );
  return details.map((response) => response.plan);
}

function ShareMissionInner() {
  const params = useParams<{ token: string }>();
  const rawToken = decodeURIComponent(params.token ?? "");
  const [mission, setMission] = useState<MissionSummary | null>(null);
  const [candidates, setCandidates] = useState<CatalogCandidate[]>([]);
  const [infrastructure, setInfrastructure] =
    useState<MissionInfrastructureResponse | null>(null);
  const [plans, setPlans] = useState<MissionPlan[]>([]);
  const [contactWindows, setContactWindows] = useState<ContactWindow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expiresAt, setExpiresAt] = useState<string | null>(null);
  const [exportingJson, setExportingJson] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    (async () => {
      if (!rawToken) {
        setError("This share link is missing a token.");
        setLoading(false);
        return;
      }
      try {
        const resolved = await resolveShareToken(rawToken);
        if (!mounted) return;
        setExpiresAt(resolved.expires_at ?? null);
        const missionId = resolved.mission_id;
        const missionResponse = await getMission(missionId, rawToken);
        if (!mounted) return;
        setMission(missionResponse.mission);

        const [candidateResult, infrastructureResult, plansResult, windowsResult] =
          await Promise.allSettled([
            listMissionCandidates(missionId, rawToken),
            getMissionInfrastructure(missionId, rawToken),
            listMissionPlans(missionId, rawToken),
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
              missionId,
              plansResult.value.plans,
              rawToken
            );
            if (mounted) setPlans(detailed);
          } catch {
            if (mounted) setPlans(plansResult.value.plans);
          }
        }
      } catch (err) {
        if (mounted) {
          setMission(null);
          setError(
            apiErrorMessage(
              err,
              "This share link is invalid, expired, or revoked. No mission data is available."
            )
          );
        }
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => {
      mounted = false;
    };
  }, [rawToken]);

  async function onExportJson() {
    if (!mission) return;
    setNotice(null);
    setExportingJson(true);
    try {
      const document = await exportMissionJson(mission.id, rawToken);
      const blob = new Blob([JSON.stringify(document, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const anchor = window.document.createElement("a");
      anchor.href = url;
      anchor.download = `nomos-mission-${mission.id}.json`;
      anchor.click();
      URL.revokeObjectURL(url);
      setNotice(`JSON export ready (schema_version ${document.schema_version}).`);
    } catch (err) {
      setNotice(apiErrorMessage(err, "Could not export mission JSON."));
    } finally {
      setExportingJson(false);
    }
  }

  return (
    <div className="page-shell pb-16">
      <PageHeader
        action={
          <LiquidButton href="/plan" variant="outline">
            Plan your own mission
          </LiquidButton>
        }
        description={
          expiresAt
            ? `Read-only private share. Link expires ${new Date(expiresAt).toLocaleString()}.`
            : "Read-only private share. Unrelated missions are never exposed by this link."
        }
        eyebrow="Private share · Mission brief"
        title={mission?.title ?? "Shared mission"}
      />

      {notice ? (
        <div className="mb-5">
          <InlineNotice message={notice} />
        </div>
      ) : null}

      {loading ? (
        <p className="text-sm text-muted">Loading shared mission brief…</p>
      ) : error || !mission ? (
        <section className="rounded-xl border border-vermilion/30 bg-vermilion/5 p-6">
          <h2 className="font-serif text-2xl text-cream">Share unavailable</h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-muted">
            {error ??
              "This share link is invalid, expired, or revoked. No mission data is available."}
          </p>
        </section>
      ) : plans.length === 0 ? (
        <section className="rounded-xl border border-white/10 bg-white/[0.02] p-6">
          <h2 className="font-serif text-2xl text-cream">No plan generated yet</h2>
          <p className="mt-2 text-sm text-muted">
            This shared mission does not include generated plans. Ask the owner to generate a
            plan, then share again.
          </p>
        </section>
      ) : (
        <MissionBrief
          canExport
          canShare={false}
          candidates={candidates}
          contactWindows={contactWindows}
          exportingJson={exportingJson}
          infrastructure={infrastructure}
          mission={mission}
          onExportJson={onExportJson}
          onShare={() => undefined}
          plans={plans}
          readOnly
          shareUrl={null}
          sharing={false}
        />
      )}
    </div>
  );
}

export default function ShareMissionPage() {
  return (
    <Suspense
      fallback={<div className="page-shell py-10 text-sm text-muted">Loading shared mission…</div>}
    >
      <ShareMissionInner />
    </Suspense>
  );
}
