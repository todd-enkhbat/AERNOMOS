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
import { REFERENCE_GROUND_STATIONS } from "@/lib/reference-ground-stations";
import type { ContactWindow, Job, NodesResponse, RoutingDecision, Satellite } from "@/lib/types";
import { formatDateTime, formatMinutes } from "@/lib/format";

const NetworkGlobeMap = dynamic(
  () =>
    import("@/components/network/NetworkGlobeMap").then((m) => m.NetworkGlobeMap),
  { ssr: false, loading: () => <div className="liquid-glass liquid-glass--card min-h-[320px] animate-pulse" /> }
);

/** Network console: ground mesh map, passes, routing, registry. Lives on /network. */
export function NetworkConsole() {
  const [nodes, setNodes] = useState<NodesResponse>(EMPTY_NODES);
  const [satellites, setSatellites] = useState<Satellite[]>([]);
  const [windows, setWindows] = useState<ContactWindow[]>([]);
  const [recentJob, setRecentJob] = useState<Job | null>(null);
  const [route, setRoute] = useState<RoutingDecision | null>(null);
  const [windowsConnected, setWindowsConnected] = useState<boolean | null>(null);
  const [satellitesConnected, setSatellitesConnected] = useState<boolean | null>(null);

  useEffect(() => {
    let mounted = true;
    async function load() {
      try {
        const [nodeResult, satelliteResult, windowResult, jobsResult] = await Promise.allSettled([
          getNodes(),
          getSatellites(),
          getContactWindows({ upcoming: true, limit: 24 }),
          listJobs()
        ]);
        if (!mounted) {
          return;
        }
        if (nodeResult.status === "fulfilled") setNodes(nodeResult.value);
        if (satelliteResult.status === "fulfilled") {
          setSatellites(satelliteResult.value.satellites);
          setSatellitesConnected(true);
        } else {
          setSatellitesConnected(false);
        }
        if (windowResult.status === "fulfilled") {
          setWindows(windowResult.value.contact_windows);
          setWindowsConnected(true);
        } else {
          setWindowsConnected(false);
        }
        if (jobsResult.status !== "fulfilled") return;
        const candidate =
          jobsResult.value.jobs.find((j) => j.status === "complete") ??
          jobsResult.value.jobs[0] ??
          null;
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
        if (mounted) {
          setWindowsConnected(false);
          setSatellitesConnected(false);
        }
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

  const apiGroundStations = useMemo(
    () =>
      nodes.ground_stations.filter(
        (station) =>
          Number.isFinite(station.latitude) &&
          Number.isFinite(station.longitude) &&
          station.latitude >= -90 &&
          station.latitude <= 90 &&
          station.longitude >= -180 &&
          station.longitude <= 180
      ),
    [nodes.ground_stations]
  );

  const groundStations =
    apiGroundStations.length > 0
      ? apiGroundStations
      : REFERENCE_GROUND_STATIONS;
  const registryMode = apiGroundStations.length > 0 ? "api" : "reference";

  return (
    <div>
      <NetworkGlobeMap
        contactWindows={windows}
        registryMode={registryMode}
        stations={groundStations}
      />

      <section className="network-purpose page-shell" aria-labelledby="network-purpose-title">
        <div className="network-purpose__statement">
          <p className="chart-label text-gold">Why the atlas exists</p>
          <h2 id="network-purpose-title">A map becomes useful when it changes the plan.</h2>
          <p>
            Nomos does not show infrastructure as decoration. It uses sourced locations,
            orbital geometry, timing, and constraints to determine which path is feasible
            for a specific objective.
          </p>
        </div>
        <ol className="network-purpose__sequence">
          <li>
            <span>01</span>
            <strong>Start with the objective</strong>
            <p>Area, timing, data product, policy, and delivery constraints.</p>
          </li>
          <li>
            <span>02</span>
            <strong>Calculate the geometry</strong>
            <p>Satellite opportunities and ground contact windows from orbital elements.</p>
          </li>
          <li>
            <span>03</span>
            <strong>Compare feasible paths</strong>
            <p>Orbital, ground, and cloud roles evaluated against the same request.</p>
          </li>
          <li>
            <span>04</span>
            <strong>Return the evidence</strong>
            <p>A recommended route with sources, assumptions, and unavailable steps exposed.</p>
          </li>
        </ol>
      </section>

      <section className="network-evidence page-shell" aria-label="Network calculation evidence">
        <article className="network-evidence__panel">
          <p className="chart-label text-gold">Contact windows</p>
          <h3 className="display mt-1 text-lg text-cream">SGP4 pass schedule</h3>
          <p className="mt-2 text-xs leading-5 text-muted">
            Precomputed from a dated, pinned public TLE snapshot. These are visibility
            estimates, not booked ground-station sessions.
          </p>
          <div className="mt-4">
            {windowsConnected === true ? (
              <ContactWindowTimeline windows={windows} />
            ) : (
              <p className="border-t border-gold/10 pt-4 text-xs leading-5 text-muted">
                {windowsConnected === null
                  ? "Loading calculated contact windows…"
                  : "The calculation API is unavailable. No pass result is shown."}
              </p>
            )}
          </div>
        </article>

        <article className="network-evidence__panel">
          <p className="chart-label text-gold">Satellite registry</p>
          <p className="mt-2 text-xs leading-5 text-muted">
            Real NORAD identities with pinned orbital elements. Downlink rates are
            reference model inputs.
          </p>
          <div className="mt-3 overflow-x-auto">
            {satellitesConnected === true ? <table className="w-full text-left text-sm">
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
            </table> : (
              <p className="border-t border-gold/10 pt-4 text-xs leading-5 text-muted">
                {satellitesConnected === null
                  ? "Loading the satellite registry…"
                  : "The registry API is unavailable. No satellite record is shown."}
              </p>
            )}
          </div>
        </article>
      </section>

      {route && recentJob ? (
        <section className="page-shell mt-6 space-y-3">
          <div className="flex flex-wrap items-end justify-between gap-2">
            <p className="chart-label text-gold">Latest demo routing decision</p>
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
