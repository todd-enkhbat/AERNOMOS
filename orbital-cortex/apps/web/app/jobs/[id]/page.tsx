"use client";

import {
  Activity,
  ChevronLeft,
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
import { JobStepper } from "@/components/jobs/JobStepper";
import { PageHeader } from "@/components/PageHeader";
import { RouteExplain } from "@/components/RouteExplain";
import { ScoreBar } from "@/components/ScoreBar";
import { StatusBadge } from "@/components/StatusBadge";
import { getDetections, getEvents, getJob, getResult, getScene, replayRouting, runSimulation } from "@/lib/api";
import type {
  ArtifactRef,
  GeoJsonFeature,
  Job,
  JobEvent,
  ReplayResponse,
  Result,
  RoutingDecision,
  SceneRecord
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
  const [scene, setScene] = useState<SceneRecord | null>(null);
  const [replayResult, setReplayResult] = useState<ReplayResponse | null>(null);
  const [selectedDetection, setSelectedDetection] = useState<GeoJsonFeature | null>(null);
  const [darkShipsOnly, setDarkShipsOnly] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [replaying, setReplaying] = useState(false);
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
        setRoute(detail.routing_decision ?? null);
        setEvents(eventResponse.events);
        try {
          const sceneResponse = await getScene(jobId);
          setScene((sceneResponse.scene as SceneRecord | null | undefined) ?? null);
        } catch {
          setScene(null);
        }
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

  async function handleReplayRouting() {
    setReplaying(true);
    setNotice(null);
    try {
      const response = await replayRouting(jobId);
      setReplayResult(response);
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Routing replay failed.");
    } finally {
      setReplaying(false);
    }
  }

  async function handleRunSimulation() {
    setRunning(true);
    setNotice(null);
    try {
      const response = await runSimulation(jobId);
      setJob(response.job);
      setResult(response.result ?? null);
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
        eyebrow="Mission"
        title={job ? `${labelize(job.job_type)} run` : "Mission"}
        description={
          job
            ? `${job.sensor} scene over New York Harbor · ${labelize(job.priority)} · ${labelize(
                job.compute_preference
              )}`
            : "Loading mission state."
        }
        action={
          <Link
            className="inline-flex items-center gap-2 rounded-xl border border-line px-4 py-2.5 text-sm text-cream transition hover:border-gold/50 hover:text-gold-bright"
            href="/jobs"
          >
            <ChevronLeft size={17} strokeWidth={2} />
            All missions
          </Link>
        }
      />

      {notice ? <InlineNotice message={notice} /> : null}

      {loading ? (
        <div className="glass mt-5 flex items-center gap-3 p-6 text-muted">
          <Loader2 className="animate-spin" size={18} strokeWidth={1.8} />
          Loading mission detail
        </div>
      ) : job ? (
        <>
          {/* mission phase strip */}
          <section className="glass mt-5 p-6 sm:p-8">
            <div className="flex flex-wrap items-center justify-between gap-4 pb-6">
              <div className="flex items-center gap-4">
                <StatusBadge status={job.status} />
                <span className="metric-value text-xs text-muted-dark">{job.id}</span>
              </div>
              <span className="metric-value text-xs text-muted-dark">
                updated {formatDateTime(job.updated_at)}
              </span>
            </div>
            <JobStepper status={job.status} />
          </section>

          <section className="mt-4 grid gap-4 lg:grid-cols-3">
            <div className="glass glass-hover p-5">
              <p className="chart-label text-muted">Selected route</p>
              <p className="metric-value mt-3 text-xl text-gold-bright">
                {route?.selected_node_id ?? "pending"}
              </p>
            </div>
            <div className="glass glass-hover p-5">
              <p className="chart-label text-muted">Latency estimate</p>
              <p className="metric-value mt-3 text-xl text-cream">
                {formatMinutes(route?.estimated_latency_minutes)}
              </p>
            </div>
            <div className="glass glass-hover p-5">
              <p className="chart-label text-muted">Cost estimate</p>
              <p className="metric-value mt-3 text-xl text-cream">
                {route ? formatCurrency(route.estimated_cost_usd) : "$0"}
              </p>
            </div>
          </section>

          <section className="mt-6 grid gap-6 xl:grid-cols-[0.75fr_1.25fr]">
            <aside className="glass h-fit p-6">
              <div className="flex items-center gap-3">
                <Route className="text-gold" size={18} strokeWidth={1.8} />
                <h2 className="text-lg font-semibold text-cream">Routing decision</h2>
              </div>
              {route ? (
                <div className="mt-5 space-y-4">
                  {route.reasons.map((reason) => (
                    <div
                      className="rounded-xl border border-line bg-void/40 p-4 text-sm leading-6 text-muted"
                      key={reason}
                    >
                      {reason}
                    </div>
                  ))}
                  <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-1">
                    <p className="rounded-xl bg-cream/5 p-4 text-sm">
                      <span className="chart-label block text-muted-dark">Ground station</span>
                      <span className="metric-value mt-2 block text-cream/90">
                        {route.selected_ground_station_id ?? "not required"}
                      </span>
                    </p>
                    <p className="rounded-xl bg-cream/5 p-4 text-sm">
                      <span className="chart-label block text-muted-dark">Fallback</span>
                      <span className="metric-value mt-2 block text-cream/90">
                        {route.fallback_node_id ?? "none"}
                      </span>
                    </p>
                  </div>
                  {scene ? (
                    <div className="rounded-xl border border-line bg-void/40 p-4 text-sm">
                      <p className="chart-label text-muted">Scene metadata</p>
                      <p className="mt-2 text-cream/85">
                        {scene.sensor} · {scene.mode} · {scene.resolution_m}m ·{" "}
                        {scene.provenance}
                      </p>
                      {scene.stac_item_id ? (
                        <p className="metric-value mt-1 text-xs text-muted-dark">
                          STAC: {scene.stac_item_id}
                        </p>
                      ) : null}
                    </div>
                  ) : null}
                  <button
                    className="inline-flex w-full items-center justify-center gap-2 rounded-xl border border-line px-5 py-3 text-sm font-medium text-cream transition hover:border-gold/50 hover:text-gold-bright disabled:cursor-not-allowed disabled:opacity-60"
                    disabled={replaying || !route}
                    onClick={handleReplayRouting}
                    type="button"
                  >
                    {replaying ? (
                      <Loader2 className="animate-spin" size={17} strokeWidth={2} />
                    ) : (
                      <Route size={17} strokeWidth={2} />
                    )}
                    Replay routing
                  </button>
                  {replayResult ? (
                    <div
                      className={`rounded-xl border p-4 text-sm ${
                        replayResult.match
                          ? "border-[#6fbf8f]/40 bg-[#6fbf8f]/10"
                          : "border-[#be543c]/40 bg-[#be543c]/10"
                      }`}
                    >
                      <p className="font-medium text-cream">
                        Audit {replayResult.match ? "match" : "mismatch"}
                      </p>
                      <p className="metric-value mt-2 break-all text-xs text-muted">
                        {replayResult.replay_decision_hash}
                      </p>
                    </div>
                  ) : null}
                  <button
                    className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-gold px-5 py-3 text-sm font-semibold text-void transition-colors hover:bg-gold-bright disabled:cursor-not-allowed disabled:opacity-60"
                    disabled={running || job.status === "complete"}
                    onClick={handleRunSimulation}
                    type="button"
                  >
                    {running ? (
                      <Loader2 className="animate-spin" size={17} strokeWidth={2} />
                    ) : (
                      <Play size={17} strokeWidth={2} />
                    )}
                    {job.status === "complete" ? "Simulation complete" : "Run simulation"}
                  </button>
                </div>
              ) : (
                <p className="mt-5 text-sm text-muted">
                  No route is attached to this job yet.
                </p>
              )}
            </aside>

            <section>
              <div className="mb-4 flex flex-wrap gap-2">
                {detailTabs.map(({ value, label, icon: Icon }) => {
                  return (
                    <button
                      className={`inline-flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-medium transition ${
                        tab === value
                          ? "bg-gold text-void"
                          : "border border-line text-muted hover:border-cream/25 hover:text-cream"
                      }`}
                      key={value}
                      onClick={() => setTab(value)}
                      type="button"
                    >
                      <Icon size={15} strokeWidth={2} />
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
                <div className="glass p-6">
                  <div className="space-y-6">
                    {events.map((event, index) => (
                      <div className="relative flex gap-4" key={event.id}>
                        {index < events.length - 1 ? (
                          <span className="absolute left-[5px] top-5 h-full w-px bg-line" />
                        ) : null}
                        <span className="relative mt-1.5 h-[11px] w-[11px] shrink-0 rounded-full border-2 border-gold bg-void" />
                        <div>
                          <p className="font-medium text-cream">
                            {labelize(event.event_type)}
                          </p>
                          <p className="mt-1 text-sm leading-6 text-muted">
                            {event.message}
                          </p>
                          <p className="metric-value mt-1 text-xs text-muted-dark">
                            {formatDateTime(event.ts_utc)}
                          </p>
                        </div>
                      </div>
                    ))}
                    {events.length === 0 ? (
                      <p className="text-muted">No lifecycle events recorded.</p>
                    ) : null}
                  </div>
                </div>
              ) : null}

              {tab === "result" ? (
                <div className="glass p-6">
                  {result ? (
                    <>
                      <div className="flex flex-wrap items-start justify-between gap-4">
                        <div>
                          <h2 className="text-lg font-semibold text-cream">
                            Inference result
                          </h2>
                          <p className="mt-2 max-w-2xl text-sm leading-6 text-muted">
                            {result.summary}
                          </p>
                        </div>
                        <span className="metric-value rounded-xl border border-gold/30 bg-gold/10 px-3 py-2 text-sm text-gold-bright">
                          {formatPercent(result.confidence)}
                        </span>
                      </div>
                      <div className="mt-6 grid gap-3 md:grid-cols-3">
                        <div className="rounded-xl border border-line bg-void/40 p-4">
                          <p className="chart-label text-muted-dark">Detections</p>
                          <p className="metric-value mt-2 text-2xl text-cream">
                            {result.geojson.features.length}
                          </p>
                        </div>
                        <div className="rounded-xl border border-line bg-void/40 p-4 md:col-span-2">
                          <p className="chart-label text-muted-dark">Output files</p>
                          <div className="mt-2 space-y-1">
                            {result.output_files.map((file) => {
                              const artifact = artifacts.find((a) => a.key === file);
                              return artifact ? (
                                <a
                                  className="metric-value block text-xs text-silver underline decoration-dotted underline-offset-2 transition hover:text-gold-bright"
                                  href={artifact.url}
                                  key={file}
                                  rel="noreferrer"
                                  target="_blank"
                                >
                                  {file}
                                </a>
                              ) : (
                                <p className="metric-value text-xs text-silver" key={file}>
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
                            <MapPinned className="text-gold" size={17} strokeWidth={1.8} />
                            <h3 className="font-semibold text-cream">
                              New York Harbor detection map
                            </h3>
                          </div>
                          <label className="inline-flex items-center gap-2 text-sm text-muted">
                            <input
                              checked={darkShipsOnly}
                              className="h-4 w-4 accent-[#c9a227]"
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
                    <div className="flex items-center gap-3 text-muted">
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
        <div className="glass mt-5 p-6 text-muted">Job not found.</div>
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
        <Table2 className="text-gold" size={17} strokeWidth={1.8} />
        <h3 className="font-semibold text-cream">Detection table</h3>
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
                <td className="metric-value text-sm text-silver">{detection.id}</td>
                <td className="text-sm text-cream/85">{labelize(detection.vesselType)}</td>
                <td className="text-sm text-muted">{detection.zone}</td>
                <td className="metric-value text-sm text-cream/85">
                  {formatPercent(detection.confidence)}
                </td>
                <td className="metric-value text-sm text-cream/85">{detection.lengthMeters} m</td>
                <td className="metric-value text-sm text-cream/85">{detection.headingDegrees} deg</td>
                <td>
                  <span className="chart-label rounded-full border border-gold/30 bg-gold/10 px-2.5 py-1 text-gold-bright">
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
