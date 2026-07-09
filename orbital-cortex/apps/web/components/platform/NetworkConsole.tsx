"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { ScoreBar } from "@/components/ScoreBar";
import { ContactWindowTimeline } from "@/components/network/ContactWindowTimeline";
import {
  getContactWindows,
  getNodes,
  getRouting,
  getSatellites,
  listJobs
} from "@/lib/api";
import { EMPTY_NODES } from "@/lib/constants";
import type { ContactWindow, Job, NodesResponse, RoutingDecision, Satellite } from "@/lib/types";
import { formatDateTime, formatMinutes, formatPercent } from "@/lib/format";

const NetworkGlobeMap = dynamic(
  () =>
    import("@/components/network/NetworkGlobeMap").then((m) => m.NetworkGlobeMap),
  { ssr: false, loading: () => <div className="min-h-[320px] animate-pulse rounded-[18px] bg-black/40" /> }
);

/** Network console: ground mesh map, passes, routing, registry. Lives on /network. */
export function NetworkConsole() {
  const [nodes, setNodes] = useState<NodesResponse>(EMPTY_NODES);
  const [satellites, setSatellites] = useState<Satellite[]>([]);
  const [windows, setWindows] = useState<ContactWindow[]>([]);
  const [recentJob, setRecentJob] = useState<Job | null>(null);
  const [route, setRoute] = useState<RoutingDecision | null>(null);

  useEffect(() => {
    let mounted = true;
    async function load() {
      try {
        const [nodeRes, satRes, winRes, jobsRes] = await Promise.all([
          getNodes(),
          getSatellites(),
          getContactWindows({ upcoming: true, limit: 24 }),
          listJobs()
        ]);
        if (!mounted) {
          return;
        }
        setNodes(nodeRes);
        setSatellites(satRes.satellites);
        setWindows(winRes.contact_windows);
        const candidate =
          jobsRes.jobs.find((j) => j.status === "complete") ?? jobsRes.jobs[0] ?? null;
        setRecentJob(candidate);
        if (candidate) {
          try {
            const routing = await getRouting(candidate.id);
            if (mounted) {
              setRoute(routing.routing_decision);
            }
          } catch {
            /* optional */
          }
        }
      } catch {
        /* parent shows notice */
      }
    }
    load();
    const timer = setInterval(load, 30_000);
    return () => {
      mounted = false;
      clearInterval(timer);
    };
  }, []);

  const ranked = useMemo(
    () =>
      route?.candidate_scores
        ? [...route.candidate_scores].sort((a, b) => b.score - a.score).slice(0, 3)
        : [],
    [route]
  );

  return (
    <div className="space-y-6">
      <section className="liquid-panel overflow-hidden p-4 sm:p-5">
        <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
          <div>
            <p className="chart-label text-gold">Ground mesh</p>
            <h2 className="display mt-1 text-xl text-cream">Station registry</h2>
            <p className="prose-compact mt-1 text-muted">
              {nodes.ground_stations.length} downlink sites across the production mesh.
            </p>
          </div>
        </div>
        <NetworkGlobeMap stations={nodes.ground_stations} />
        <ul className="mt-4 grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
          {nodes.ground_stations.map((gs) => (
            <li
              className="flex items-center justify-between gap-2 border-t border-gold/10 pt-2 text-sm"
              key={gs.id}
            >
              <span className="text-cream/85">{gs.name}</span>
              <span className="metric-value text-[11px] text-muted">
                {formatPercent(gs.availability)}
              </span>
            </li>
          ))}
        </ul>
      </section>

      <div className="grid gap-4 lg:grid-cols-[1fr_1fr]">
        <section className="liquid-panel p-4 sm:p-5">
          <p className="chart-label text-gold">Contact windows</p>
          <h3 className="display mt-1 text-lg text-cream">SGP4 pass schedule</h3>
          <div className="mt-4">
            <ContactWindowTimeline windows={windows} />
          </div>
        </section>

        <section className="liquid-panel p-4 sm:p-5">
          <p className="chart-label text-gold">Satellite registry</p>
          <div className="mt-3 overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="chart-label text-muted-dark">
                  <th className="pb-2 font-medium">Name</th>
                  <th className="pb-2 font-medium">NORAD</th>
                  <th className="pb-2 font-medium">Mbps</th>
                </tr>
              </thead>
              <tbody>
                {satellites.map((sat) => (
                  <tr className="border-t border-gold/10" key={sat.id}>
                    <td className="py-2 text-cream/85">{sat.name}</td>
                    <td className="metric-value py-2 text-silver">{sat.norad_id}</td>
                    <td className="metric-value py-2 text-muted">{sat.downlink_rate_mbps}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>

      {route && recentJob ? (
        <section className="space-y-3">
          <div className="flex flex-wrap items-end justify-between gap-2">
            <p className="chart-label text-gold">Latest routing decision</p>
            <Link className="text-sm text-muted hover:text-cream" href={`/jobs/${recentJob.id}`}>
              {recentJob.id.slice(0, 18)} →
            </Link>
          </div>
          <div className="grid gap-3 lg:grid-cols-3">
            {ranked.map((c) => (
              <ScoreBar candidate={c} key={c.node_id} />
            ))}
          </div>
          <p className="metric-value text-[11px] text-muted-dark">
            Refreshed · {formatDateTime(new Date().toISOString())} ·{" "}
            {formatMinutes(route.estimated_latency_minutes)} est.
          </p>
        </section>
      ) : null}
    </div>
  );
}
