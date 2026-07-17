"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";

import { InlineNotice } from "@/components/InlineNotice";
import { PageHeader } from "@/components/PageHeader";
import { LiquidButton } from "@/components/liquid/LiquidButton";
import { LiquidCard } from "@/components/liquid/LiquidCard";
import {
  apiErrorMessage,
  createMission,
  ensureAnonymousSession,
  listExampleMissions,
  listMissions,
  type MissionSummary
} from "@/lib/api";
import { formatDateTime } from "@/lib/format";

const DEFAULT_AOI = {
  type: "bbox",
  coordinates: [-74.3, 40.3, -73.5, 41.0]
};

export default function MissionsPage() {
  const [missions, setMissions] = useState<MissionSummary[]>([]);
  const [examples, setExamples] = useState<MissionSummary[]>([]);
  const [title, setTitle] = useState("Maritime awareness draft");
  const [notice, setNotice] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  async function refresh() {
    await ensureAnonymousSession();
    const [mine, publicExamples] = await Promise.all([
      listMissions(),
      listExampleMissions()
    ]);
    setMissions(mine.missions);
    setExamples(publicExamples.missions);
  }

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        await refresh();
        if (mounted) setNotice(null);
      } catch (error) {
        if (mounted) setNotice(apiErrorMessage(error));
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => {
      mounted = false;
    };
  }, []);

  async function onCreate(event: FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    setNotice(null);
    try {
      await ensureAnonymousSession();
      const created = await createMission({
        title: title.trim() || "Untitled mission",
        objective_type: "ship_detection",
        area_of_interest: DEFAULT_AOI,
        notes: "Private session mission"
      });
      setTitle("Maritime awareness draft");
      await refresh();
      setNotice(`Created private mission ${created.mission.id.slice(0, 8)}…`);
    } catch (error) {
      setNotice(apiErrorMessage(error, "Could not create a private mission."));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="page-shell pb-16">
      <PageHeader
        eyebrow="Private workspace"
        title="Your missions"
        description="Missions stay inside this browser’s private anonymous session. Other visitors cannot list or open them without a share token."
      />

      {notice ? (
        <div className="mb-4">
          <InlineNotice message={notice} />
        </div>
      ) : null}

      <div className="grid gap-6 lg:grid-cols-[0.95fr_1.05fr]">
        <LiquidCard>
          <p className="chart-label text-gold">New private mission</p>
          <form className="mt-4 space-y-4" onSubmit={onCreate}>
            <label className="block text-sm text-muted">
              Title
              <input
                className="mt-1.5 w-full rounded-lg border border-white/10 bg-black/30 px-3 py-2 text-cream outline-none focus:border-gold/40"
                onChange={(event) => setTitle(event.target.value)}
                value={title}
              />
            </label>
            <p className="text-xs leading-5 text-muted">
              Uses a default NY Harbor AOI for now. The guided planner form arrives in a
              later phase.
            </p>
            <LiquidButton disabled={submitting} type="submit" variant="primary">
              {submitting ? "Creating…" : "Create private mission"}
            </LiquidButton>
          </form>
        </LiquidCard>

        <LiquidCard>
          <p className="chart-label text-gold">This session</p>
          {loading ? (
            <p className="mt-4 text-sm text-muted">Loading private missions…</p>
          ) : missions.length === 0 ? (
            <p className="mt-4 text-sm text-muted">
              No private missions yet. Create one to keep it scoped to this session only.
            </p>
          ) : (
            <ul className="mt-4 space-y-3">
              {missions.map((mission) => (
                <li key={mission.id}>
                  <Link
                    className="block rounded-xl border border-white/10 px-3 py-3 transition hover:border-gold/30"
                    href={`/missions/${mission.id}`}
                  >
                    <p className="text-sm font-medium text-cream">{mission.title}</p>
                    <p className="mt-1 text-xs text-muted">
                      {mission.objective_type} · {mission.status} ·{" "}
                      {formatDateTime(mission.created_at)}
                    </p>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </LiquidCard>
      </div>

      <section className="mt-8">
        <LiquidCard>
          <p className="chart-label text-gold">Public examples</p>
          <p className="mt-2 text-sm text-muted">
            Curated examples are stored separately and marked <code>is_example</code>. They
            are not private user submissions.
          </p>
          <ul className="mt-4 space-y-3">
            {examples.map((mission) => (
              <li key={mission.id}>
                <Link
                  className="block rounded-xl border border-white/10 px-3 py-3 transition hover:border-gold/30"
                  href={`/missions/${mission.id}`}
                >
                  <p className="text-sm font-medium text-cream">{mission.title}</p>
                  <p className="mt-1 text-xs text-muted">
                    Example · {mission.objective_type} · {formatDateTime(mission.created_at)}
                  </p>
                </Link>
              </li>
            ))}
          </ul>
        </LiquidCard>
      </section>

      <p className="mt-6 text-xs text-muted">
        The legacy simulated job demo remains at{" "}
        <Link className="text-gold hover:underline" href="/jobs">
          /jobs
        </Link>{" "}
        for internal use and is no longer linked from primary navigation.
      </p>
    </div>
  );
}
