"use client";

import {
  Activity,
  ChevronLeft,
  Clock3,
  FileJson,
  Loader2,
  MapPinned,
  Play,
  Route,
  Satellite,
  Ship,
  Table2,
  Terminal
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";

import { DetectionPanel } from "@/components/DetectionPanel";
import { HarborMap } from "@/components/HarborMap";
import { InlineNotice } from "@/components/InlineNotice";
import { PageHeader } from "@/components/PageHeader";
import { RouteExplain } from "@/components/RouteExplain";
import { ScoreBar } from "@/components/ScoreBar";
import { StatusBadge } from "@/components/StatusBadge";
import { getDetections, getEvents, getJob, getResult, runSimulation } from "@/lib/api";
import type {
  ArtifactRef,
  GeoJsonFeature,
  Job,
  JobEvent,
  Result,
  RoutingDecision
} from "@/lib/types";
import { formatCurrency, formatDateTime, formatMinutes, formatPercent, labelize } from "@/lib/format";

type DetailTab = "route" | "timeline" | "result" | "api";

type DetectionRow = {
  id: string;
  vesselType: string;
  zone: string;
  confidence: number;
  lengthMeters: number;
  headingDegrees: number;
  priority: string;
  longitude: number;
  latitude: number;
};

const detailTabs: Array<{
  value: DetailTab;
  label: string;
  icon: LucideIcon;
}> = [
  { value: "route", label: "Scores", icon: Satellite },
  { value: "timeline", label: "Timeline", icon: Activity },
  { value: "result", label: "Result", icon: Ship },
  { value: "api", label: "API", icon: Terminal }
];

export default function JobDetailPage() {
  const params = useParams<{ id: string }>();
  const jobId = params.id;
  const [job, setJob] = useState<Job | null>(null);
  const [route, setRoute] = useState<RoutingDecision | null>(null);
  const [events, setEvents] = useState<JobEvent[]>([]);
  const [result, setResult] = useState<Result | null>(null);
  const [artifacts, setArtifacts] = useState<ArtifactRef[]>([]);
  const [detections, setDetections] = useState<GeoJsonFeature[]>([]);
  const [selectedDetection, setSelectedDetection] = useState<GeoJsonFeature | null>(null);
  const [darkShipsOnly, setDarkShipsOnly] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [tab, setTab] = useState<DetailTab>("route");

  const load = useCallback(
    async (silent = false) => {
      if (!silent) {
        setLoading(true);
        setNotice(null);
      }
      try {
        const detail = await getJob(jobId);
        const eventResponse = await getEvents(jobId);
        setJob(detail.job);
        setRoute(detail.routing_decision);
        setEvents(eventResponse.events);
        try {
          const resultResponse = await getResult(jobId);
          setResult(resultResponse.result);
          setArtifacts(resultResponse.artifacts ?? []);
          try {
            const detectionResponse = await getDetections(jobId);
            setDetections(detectionResponse.features);
          } catch {
            setDetections([]);
          }
        } catch {
          setResult(null);
          setArtifacts([]);
          setDetections([]);
        }
      } catch (error) {
        if (!silent) {
          setNotice(error instanceof Error ? error.message : "Job detail is not available.");
        }
      } finally {
        if (!silent) {
          setLoading(false);
        }
      }
    },
    [jobId]
  );

  useEffect(() => {
    load();
  }, [load]);

  // Poll while the async worker is driving the job through its lifecycle.
  useEffect(() => {
    if (!job || job.status === "complete" || job.status === "failed") {
      return;
    }
    const interval = setInterval(() => {
      load(true);
    }, 2500);
    return () => clearInterval(interval);
  }, [job, load]);

  async function handleRunSimulation() {
    setRunning(true);
    setNotice(null);
    try {
      const response = await runSimulation(jobId);
      setJob(response.job);
      setResult(response.result);
      const eventResponse = await getEvents(jobId);
      setEvents(eventResponse.events);
      setTab("result");
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Simulation failed.");
    } finally {
      setRunning(false);
    }
  }

  const apiPreview = useMemo(() => {
    if (!job) {
      return "{}";
    }
    return JSON.stringify(
      {
        job,
        routing_decision: route,
        events,
        result
      },
      null,
      2
    );
  }, [events, job, result, route]);

  return (
    <div className="page-shell pb-16">
      <PageHeader
        eyebrow="Job detail"
        title={job ? `${labelize(job.job_type)} control run` : "Job"}
        description={
          job
            ? `${job.sensor} scene over New York Harbor / ${labelize(job.priority)} / ${labelize(
                job.compute_preference
              )}`
            : "Loading job state."
        }
        action={
          <Link
            className="inline-flex items-center gap-2 rounded-lg border border-[rgba(86,67,42,0.22)] px-4 py-3 font-bold text-[#17140f] transition hover:bg-[#eadcc8]"
            href="/jobs"
          >
            <ChevronLeft size={18} strokeWidth={1.8} />
            Jobs
          </Link>
        }
      />

      {notice ? <InlineNotice message={notice} /> : null}

      {loading ? (
        <div className="panel mt-5 flex items-center gap-3 p-6 text-[#6f604c]">
          <Loader2 className="animate-spin" size={18} strokeWidth={1.8} />
          Loading job detail
        </div>
      ) : job ? (
        <>
          <section className="mt-5 grid gap-4 lg:grid-cols-4">
            <div className="dark-panel p-5">
              <p className="text-sm text-[#d8cbb8]">Status</p>
              <div className="mt-4">
                <StatusBadge status={job.status} />
              </div>
            </div>
            <div className="panel p-5">
              <p className="text-sm text-[#6f604c]">Selected route</p>
              <p className="metric-value mt-3 text-xl font-bold text-[#25495a]">
                {route?.selected_node_id ?? "pending"}
              </p>
            </div>
            <div className="panel p-5">
              <p className="text-sm text-[#6f604c]">Latency</p>
              <p className="metric-value mt-3 text-xl font-bold">
                {formatMinutes(route?.estimated_latency_minutes)}
              </p>
            </div>
            <div className="panel p-5">
              <p className="text-sm text-[#6f604c]">Estimated cost</p>
              <p className="metric-value mt-3 text-xl font-bold">
                {route ? formatCurrency(route.estimated_cost_usd) : "$0"}
              </p>
            </div>
          </section>

          <section className="mt-6 grid gap-6 xl:grid-cols-[0.75fr_1.25fr]">
            <aside className="panel p-6">
              <div className="flex items-center gap-3">
                <Route className="text-[#25495a]" size={20} strokeWidth={1.8} />
                <h2 className="text-2xl font-bold text-[#17140f]">Routing decision</h2>
              </div>
              {route ? (
                <div className="mt-5 space-y-4">
                  {route.reasons.map((reason) => (
                    <div
                      className="rounded-lg border border-[rgba(86,67,42,0.22)] bg-[#fffaf0]/70 p-4 text-sm leading-6 text-[#5d5244]"
                      key={reason}
                    >
                      {reason}
                    </div>
                  ))}
                  <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-1">
                    <p className="rounded-lg bg-[#eadcc8] p-4 text-sm">
                      <span className="block text-[#6f604c]">Ground station</span>
                      <span className="metric-value mt-1 block font-bold text-[#17140f]">
                        {route.selected_ground_station_id ?? "not required"}
                      </span>
                    </p>
                    <p className="rounded-lg bg-[#eadcc8] p-4 text-sm">
                      <span className="block text-[#6f604c]">Fallback</span>
                      <span className="metric-value mt-1 block font-bold text-[#17140f]">
                        {route.fallback_node_id ?? "none"}
                      </span>
                    </p>
                  </div>
                  <button
                    className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-[#17140f] px-5 py-3 font-bold text-[#fffaf0] transition hover:bg-[#2a241b] disabled:cursor-not-allowed disabled:opacity-60"
                    disabled={running || job.status === "complete"}
                    onClick={handleRunSimulation}
                    type="button"
                  >
                    {running ? (
                      <Loader2 className="animate-spin" size={18} strokeWidth={1.8} />
                    ) : (
                      <Play size={18} strokeWidth={1.8} />
                    )}
                    {job.status === "complete" ? "Simulation Complete" : "Run Simulation"}
                  </button>
                </div>
              ) : (
                <p className="mt-5 text-[#6f604c]">
                  No route is attached to this job.
                </p>
              )}
            </aside>

            <section>
              <div className="mb-4 flex flex-wrap gap-2">
                {detailTabs.map(({ value, label, icon: Icon }) => {
                  return (
                    <button
                      className={`inline-flex items-center gap-2 rounded-lg px-4 py-2 font-bold transition ${
                        tab === value
                          ? "bg-[#17140f] text-[#fffaf0]"
                          : "border border-[rgba(86,67,42,0.22)] bg-[#fffaf0]/60 text-[#4f4436] hover:bg-[#eadcc8]"
                      }`}
                      key={value}
                      onClick={() => setTab(value)}
                      type="button"
                    >
                      <Icon size={16} strokeWidth={1.8} />
                      {label}
                    </button>
                  );
                })}
              </div>

              {tab === "route" ? (
                <div className="space-y-4">
                  {route ? <RouteExplain route={route} /> : null}
                  {route?.candidate_scores.map((candidate) => (
                    <ScoreBar candidate={candidate} key={candidate.node_id} />
                  ))}
                </div>
              ) : null}

              {tab === "timeline" ? (
                <div className="panel p-6">
                  <div className="space-y-5">
                    {events.map((event) => (
                      <div className="flex gap-4" key={event.id}>
                        <span className="mt-1 h-3 w-3 shrink-0 rounded-full bg-[#25495a]" />
                        <div>
                          <p className="font-bold text-[#17140f]">
                            {labelize(event.event_type)}
                          </p>
                          <p className="mt-1 text-sm leading-6 text-[#5d5244]">
                            {event.message}
                          </p>
                          <p className="metric-value mt-1 text-xs text-[#6f604c]">
                            {formatDateTime(event.ts_utc)}
                          </p>
                        </div>
                      </div>
                    ))}
                    {events.length === 0 ? (
                      <p className="text-[#6f604c]">No lifecycle events recorded.</p>
                    ) : null}
                  </div>
                </div>
              ) : null}

              {tab === "result" ? (
                <div className="panel p-6">
                  {result ? (
                    <>
                      <div className="flex flex-wrap items-start justify-between gap-4">
                        <div>
                          <h2 className="text-2xl font-bold text-[#17140f]">
                            Mock inference result
                          </h2>
                          <p className="mt-2 max-w-2xl leading-7 text-[#5d5244]">
                            {result.summary}
                          </p>
                        </div>
                        <span className="metric-value rounded-lg bg-[#eadcc8] px-3 py-2 text-sm font-bold text-[#25495a]">
                          {formatPercent(result.confidence)}
                        </span>
                      </div>
                      <div className="mt-6 grid gap-3 md:grid-cols-3">
                        <div className="rounded-lg border border-[rgba(86,67,42,0.22)] bg-[#fffaf0]/70 p-4">
                          <p className="text-sm text-[#6f604c]">Detections</p>
                          <p className="metric-value mt-2 text-2xl font-bold">
                            {result.geojson.features.length}
                          </p>
                        </div>
                        <div className="rounded-lg border border-[rgba(86,67,42,0.22)] bg-[#fffaf0]/70 p-4 md:col-span-2">
                          <p className="text-sm text-[#6f604c]">Output files</p>
                          <div className="mt-2 space-y-1">
                            {result.output_files.map((file) => {
                              const artifact = artifacts.find((a) => a.key === file);
                              return artifact ? (
                                <a
                                  className="metric-value block text-xs text-[#25495a] underline decoration-dotted underline-offset-2 hover:text-[#17140f]"
                                  href={artifact.url}
                                  key={file}
                                  rel="noreferrer"
                                  target="_blank"
                                >
                                  {file}
                                </a>
                              ) : (
                                <p className="metric-value text-xs text-[#25495a]" key={file}>
                                  {file}
                                </p>
                              );
                            })}
                          </div>
                        </div>
                      </div>
                      <div className="relative mt-6">
                        <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
                          <div className="flex items-center gap-2">
                            <MapPinned className="text-[#25495a]" size={18} strokeWidth={1.8} />
                            <h3 className="text-xl font-bold text-[#17140f]">
                              New York Harbor detection map
                            </h3>
                          </div>
                          <label className="inline-flex items-center gap-2 text-sm font-bold text-[#4f4436]">
                            <input
                              checked={darkShipsOnly}
                              className="h-4 w-4"
                              onChange={(event) => setDarkShipsOnly(event.target.checked)}
                              type="checkbox"
                            />
                            Dark ships only (no AIS)
                          </label>
                        </div>
                        <HarborMap
                          darkShipsOnly={darkShipsOnly}
                          features={detections.length > 0 ? detections : mapFeaturesFromResult(result)}
                          onSelect={setSelectedDetection}
                          selectedId={
                            selectedDetection
                              ? String(selectedDetection.properties.detection_id ?? "")
                              : null
                          }
                        />
                        <DetectionPanel
                          feature={selectedDetection}
                          onClose={() => setSelectedDetection(null)}
                        />
                      </div>
                      <DetectionTable result={result} />
                    </>
                  ) : (
                    <div className="flex items-center gap-3 text-[#6f604c]">
                      <FileJson size={18} strokeWidth={1.8} />
                      Result not ready.
                    </div>
                  )}
                </div>
              ) : null}

              {tab === "api" ? (
                <pre className="code-block">{apiPreview}</pre>
              ) : null}
            </section>
          </section>
        </>
      ) : (
        <div className="panel mt-5 p-6 text-[#6f604c]">Job not found.</div>
      )}
    </div>
  );
}

function mapFeaturesFromResult(result: Result): GeoJsonFeature[] {
  return result.geojson.features.flatMap((feature) => {
    if (feature.geometry.type !== "Point" || !Array.isArray(feature.geometry.coordinates)) {
      return [];
    }
    return [
      {
        type: "Feature" as const,
        geometry: {
          type: "Point" as const,
          coordinates: feature.geometry.coordinates as number[]
        },
        properties: {
          ...feature.properties,
          dark_ship: feature.properties.ais_correlated === false
        }
      }
    ];
  });
}

function DetectionTable({ result }: { result: Result }) {
  const detections = extractDetections(result);

  return (
    <section className="mt-6">
      <div className="mb-3 flex items-center gap-2">
        <Table2 className="text-[#25495a]" size={18} strokeWidth={1.8} />
        <h3 className="text-xl font-bold text-[#17140f]">Detection table</h3>
      </div>
      <div className="table-shell">
        <table className="data-table">
          <thead>
            <tr>
              <th>Contact</th>
              <th>Type</th>
              <th>Zone</th>
              <th>Confidence</th>
              <th>Length</th>
              <th>Heading</th>
              <th>Priority</th>
            </tr>
          </thead>
          <tbody>
            {detections.map((detection) => (
              <tr key={detection.id}>
                <td className="metric-value text-sm text-[#25495a]">{detection.id}</td>
                <td>{labelize(detection.vesselType)}</td>
                <td className="text-sm text-[#6f604c]">{detection.zone}</td>
                <td className="metric-value text-sm">
                  {formatPercent(detection.confidence)}
                </td>
                <td className="metric-value text-sm">{detection.lengthMeters} m</td>
                <td className="metric-value text-sm">{detection.headingDegrees} deg</td>
                <td>
                  <span className="rounded-lg bg-[#eadcc8] px-2.5 py-1 text-xs font-bold uppercase text-[#25495a]">
                    {detection.priority}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function extractDetections(result: Result): DetectionRow[] {
  return result.geojson.features.flatMap((feature) => {
    const coordinates = feature.geometry.coordinates;
    if (!isPointCoordinates(coordinates)) {
      return [];
    }
    const properties = feature.properties;
    return [
      {
        id: String(properties.detection_id ?? "contact"),
        vesselType: String(properties.vessel_type ?? properties.class ?? "vessel"),
        zone: String(properties.harbor_zone ?? "Harbor"),
        confidence: Number(properties.confidence ?? 0),
        lengthMeters: Number(properties.length_m_estimate ?? 0),
        headingDegrees: Number(properties.heading_deg_estimate ?? 0),
        priority: String(properties.priority ?? "monitor"),
        longitude: coordinates[0],
        latitude: coordinates[1]
      }
    ];
  });
}

function isPointCoordinates(value: unknown): value is [number, number] {
  return (
    Array.isArray(value) &&
    value.length >= 2 &&
    typeof value[0] === "number" &&
    typeof value[1] === "number"
  );
}
