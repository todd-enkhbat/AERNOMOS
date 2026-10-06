"use client";

import { FileCheck2, LockKeyhole } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { PageHeader } from "@/components/PageHeader";
import { LiquidButton } from "@/components/liquid/LiquidButton";
import {
  apiErrorMessage,
  ensureAnonymousSession,
  listExampleMissions,
  listMissions,
  type MissionSummary
} from "@/lib/api";
import { formatDateTime } from "@/lib/format";
import { OBJECTIVE_LABELS, type ObjectiveType } from "@/lib/mission-builder";

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
        if (!mounted) return;
        setMissions(mine.missions);
        setExamples(publicExamples.missions);
        setNotice(null);
      } catch (error) {
        if (mounted) {
          setNotice(
            apiErrorMessage(
              error,
              "The private mission workspace is temporarily unavailable. You can still build a new plan or inspect a curated example."
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
  }, []);

  return (
    <div className="page-shell pb-16">
      <PageHeader
        action={
          <LiquidButton href="/plan" variant="primary">
            Build a mission plan
          </LiquidButton>
        }
        description="Plans created here stay private to this browser session until you explicitly make a share link. This is your technical record, not a public activity feed."
        eyebrow="Private workspace"
        title="Your missions"
      />

      <section className="nomos-ledger mt-6" aria-labelledby="private-missions-title">
        <div className="nomos-ledger__header">
          <div>
            <p className="chart-label text-gold">PRIVATE MISSION LEDGER</p>
            <h2 className="mt-1 text-base font-medium text-cream" id="private-missions-title">
              This browser&apos;s mission records
            </h2>
          </div>
          <div className="nomos-ledger__meta">
            <span>anonymous session</span>
            <span>
              {notice
                ? "records unavailable"
                : loading
                ? "loading"
                : missions.length + " record" + (missions.length === 1 ? "" : "s")}
            </span>
          </div>
        </div>

        {loading ? (
          <div className="nomos-empty-state">
            <span className="nomos-empty-state__mark">
              <LockKeyhole aria-hidden size={18} />
            </span>
            <div>
              <h2>Loading your private workspace.</h2>
            </div>
          </div>
        ) : notice ? (
          <div className="nomos-empty-state">
            <span className="nomos-empty-state__mark">
              <LockKeyhole aria-hidden size={18} />
            </span>
            <div>
              <p className="chart-label text-gold">PRIVATE WORKSPACE</p>
              <h2>Mission records are temporarily unavailable.</h2>
              <p>
                Nomos will not represent an unavailable session as an empty one.
                Start a new plan or inspect a clearly labeled public example while
                this workspace reconnects.
              </p>
              <div className="nomos-empty-state__actions">
                <LiquidButton href="/plan" variant="primary">
                  Build a mission plan
                </LiquidButton>
                <LiquidButton href="/examples" variant="outline">
                  Open an example
                </LiquidButton>
              </div>
            </div>
          </div>
        ) : missions.length === 0 ? (
          <div className="nomos-empty-state">
            <span className="nomos-empty-state__mark">
              <FileCheck2 aria-hidden size={18} />
            </span>
            <div>
              <h2>There is no mission record yet.</h2>
              <p>
                Start with an outcome, area, and constraints. Nomos will save the
                resulting plan privately to this browser session.
              </p>
              <div className="nomos-empty-state__actions">
                <LiquidButton href="/plan" variant="primary">
                  Build a mission plan
                </LiquidButton>
                <LiquidButton href="/examples" variant="outline">
                  Open an example
                </LiquidButton>
              </div>
            </div>
          </div>
        ) : (
          <div className="nomos-ledger__body">
            {missions.map((mission, index) => (
              <Link
                className="nomos-ledger__row"
                href={"/missions/" + mission.id}
                key={mission.id}
              >
                <span className="nomos-ledger__index">
                  {String(index + 1).padStart(2, "0")}
                </span>
                <span>
                  <span className="nomos-ledger__row-title">{mission.title}</span>
                  <span className="nomos-ledger__row-detail">
                    {objectiveLabel(mission.objective_type)} · {formatDateTime(mission.created_at)}
                  </span>
                </span>
                <span className="nomos-ledger__status">{mission.status}</span>
              </Link>
            ))}
          </div>
        )}
      </section>

      <section className="mt-10" aria-labelledby="reference-missions-title">
        <div className="flex flex-wrap items-end justify-between gap-4 border-b border-gold/15 pb-4">
          <div>
            <p className="chart-label text-gold">REFERENCE MISSIONS</p>
            <h2 className="display mt-1 text-2xl text-cream" id="reference-missions-title">
              Learn from an explained route.
            </h2>
            <p className="mt-2 max-w-xl text-sm leading-6 text-muted">
              These curated missions are public specimens. Their real, calculated,
              estimated, simulated, and unavailable parts stay labeled.
            </p>
          </div>
          <LiquidButton href="/examples" variant="outline">
            View all examples
          </LiquidButton>
        </div>

        {examples.length ? (
          <div className="nomos-ledger__body">
            {examples.slice(0, 3).map((mission, index) => (
              <Link
                className="nomos-ledger__row"
                href={"/missions/" + mission.id}
                key={mission.id}
              >
                <span className="nomos-ledger__index">R{index + 1}</span>
                <span>
                  <span className="nomos-ledger__row-title">{mission.title}</span>
                  <span className="nomos-ledger__row-detail">
                    {objectiveLabel(mission.objective_type)} · reference mission
                  </span>
                </span>
                <span className="nomos-ledger__status">open plan</span>
              </Link>
            ))}
          </div>
        ) : (
          <p className="mt-4 text-sm text-muted">
            Reference missions are unavailable right now.
          </p>
        )}
      </section>
    </div>
  );
}
