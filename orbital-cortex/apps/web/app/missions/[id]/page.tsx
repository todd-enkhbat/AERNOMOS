"use client";

import Link from "next/link";
import { useParams, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";

import { InlineNotice } from "@/components/InlineNotice";
import { PageHeader } from "@/components/PageHeader";
import { LiquidButton } from "@/components/liquid/LiquidButton";
import { LiquidCard } from "@/components/liquid/LiquidCard";
import {
  apiErrorMessage,
  createShareLink,
  ensureAnonymousSession,
  getMission,
  type MissionSummary
} from "@/lib/api";
import { formatDateTime } from "@/lib/format";

function MissionDetailInner() {
  const params = useParams<{ id: string }>();
  const searchParams = useSearchParams();
  const shareToken = searchParams.get("share_token") ?? undefined;
  const [mission, setMission] = useState<MissionSummary | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [shareUrl, setShareUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

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
