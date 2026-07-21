"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { InlineNotice } from "@/components/InlineNotice";
import { PageHeader } from "@/components/PageHeader";
import { LiquidButton } from "@/components/liquid/LiquidButton";
import { LiquidCard } from "@/components/liquid/LiquidCard";
import {
  apiErrorMessage,
  ensureAnonymousSession,
  listExampleMissions,
  listMissions,
  type MissionSummary
} from "@/lib/api";
import { OBJECTIVE_LABELS, type ObjectiveType } from "@/lib/mission-builder";
import { formatDateTime } from "@/lib/format";

function objectiveLabel(value: string): string {
  return OBJECTIVE_LABELS[value as ObjectiveType] ?? value;
}

export default function MissionsPage() {
  const [missions, setMissions] = useState<MissionSummary[]>([]);
  const [examples, setExamples] = useState<MissionSummary[]>([]);
  const [notice, setNotice] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        await ensureAnonymousSession();
        const [mine, publicExamples] = await Promise.all([
          listMissions(),
          listExampleMissions()
        ]);
        if (mounted) {
          setMissions(mine.missions);
          setExamples(publicExamples.missions);
          setNotice(null);
        }
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

  return (
    <div className="page-shell pb-16">
      <PageHeader
        eyebrow="Private workspace"
        title="Your missions"
        description="Missions stay inside this browser’s private anonymous session. Other visitors cannot list or open them without a share token."
        action={
          <LiquidButton href="/plan" variant="primary">
            Build a mission plan
          </LiquidButton>
        }
      />

      {notice ? (
        <div className="mb-4">
          <InlineNotice message={notice} />
        </div>
      ) : null}

      <div className="grid gap-6 lg:grid-cols-[0.95fr_1.05fr]">
        <LiquidCard>
          <p className="chart-label text-gold">New mission</p>
          <p className="mt-3 text-sm leading-6 text-muted">
            Use the guided planner to describe your objective, area, and constraints in
            plain language — then save a private mission plan for this session.
          </p>
          <div className="mt-5">
            <LiquidButton href="/plan" variant="primary">
              Build a mission plan
            </LiquidButton>
          </div>
        </LiquidCard>

        <LiquidCard>
          <p className="chart-label text-gold">This session</p>
          {loading ? (
            <p className="mt-4 text-sm text-muted">Loading private missions…</p>
          ) : missions.length === 0 ? (
            <p className="mt-4 text-sm text-muted">
              No private missions yet.{" "}
              <Link className="text-gold hover:underline" href="/plan">
                Build a mission plan
              </Link>{" "}
              to keep one scoped to this session only.
            </p>
          ) : (
            <ul className="mt-4 space-y-3">
              {missions.map((mission) => (
                <li key={mission.id}>
                  <Link
                    className="block rounded-xl border border-white/10 px-3 py-3 	ransition-colors hover:border-gold/30"
                    href={`/missions/${mission.id}`}
                  >
                    <p className="text-sm font-medium text-cream">{mission.title}</p>
                    <p className="mt-1 text-xs text-muted">
                      {objectiveLabel(mission.objective_type)} · {mission.status} ·{" "}
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
                  className="block rounded-xl border border-white/10 px-3 py-3 	ransition-colors hover:border-gold/30"
                  href={`/missions/${mission.id}`}
                >
                  <p className="text-sm font-medium text-cream">{mission.title}</p>
                  <p className="mt-1 text-xs text-muted">
                    Example · {objectiveLabel(mission.objective_type)} ·{" "}
                    {formatDateTime(mission.created_at)}
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
