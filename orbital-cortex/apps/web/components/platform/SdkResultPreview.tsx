"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { useEffect, useState } from "react";

import { LiquidButton } from "@/components/liquid/LiquidButton";
import { LiquidCard } from "@/components/liquid/LiquidCard";
import { ScoreBar } from "@/components/ScoreBar";
import { API_BASE_URL, getDetections, getResult, getRouting, listJobs } from "@/lib/api";
import type { DetectionsGeoJson, Job, ResultResponse, RoutingDecision } from "@/lib/types";
import { formatCurrency, formatMinutes, labelize } from "@/lib/format";

const HarborMap = dynamic(
  () => import("@/components/HarborMap").then((m) => m.HarborMap),
  {
    ssr: false,
    loading: () => <div className="min-h-[260px] animate-pulse rounded-[18px] bg-black/40" />
  }
);

const SDK_SNIPPET = `from orbitalcortex import Client

client = Client(api_key="oc_demo_public")
job = client.jobs.create(job_type="ship_detection", ...)
detections = client.jobs.get_detections(job.id)
manifest = client.jobs.get_result(job.id)`;

/** Latest completed job: GeoJSON detections + SDK result shape. */
export function SdkResultPreview() {
  const [job, setJob] = useState<Job | null>(null);
  const [geojson, setGeojson] = useState<DetectionsGeoJson | null>(null);
  const [result, setResult] = useState<ResultResponse | null>(null);
  const [route, setRoute] = useState<RoutingDecision | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    async function load() {
      try {
        const { jobs } = await listJobs();
        const complete = jobs.find((j) => j.status === "complete");
        if (!complete || !mounted) {
          return;
        }
        setJob(complete);
        const [det, res, routing] = await Promise.all([
          getDetections(complete.id),
          getResult(complete.id),
          getRouting(complete.id)
        ]);
        if (mounted) {
          setGeojson(det);
          setResult(res);
          setRoute(routing.routing_decision);
        }
      } catch (err) {
        if (mounted) {
          setError(err instanceof Error ? err.message : "No SDK results yet");
        }
      }
    }
    load();
  }, []);

  if (error && !job) {
    return (
      <LiquidCard className="text-center">
        <p className="text-sm text-muted">Run a demo job to populate SDK results.</p>
        <div className="mt-4">
          <LiquidButton href="/#demo" variant="primary">
            Run live demo
          </LiquidButton>
        </div>
      </LiquidCard>
    );
  }

  if (!job || !geojson) {
    return <div className="liquid-glass liquid-glass--card min-h-[200px] animate-pulse" />;
  }

  const features = geojson.features ?? [];
  const topCandidate = route?.candidate_scores
    ?.filter((c) => c.eligible)
    .sort((a, b) => b.score - a.score)[0];

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="chart-label text-gold">SDK output</p>
          <h2 className="display mt-2 text-2xl text-cream">
            Detections from the live pipeline.
          </h2>
          <p className="prose-compact mt-1 max-w-lg text-silver">
            GeoJSON features, signed artifact URLs, and routing scores returned by
            the Python SDK against {API_BASE_URL}.
          </p>
        </div>
        <LiquidButton href={`/jobs/${job.id}`} variant="outline">
          Open mission view
        </LiquidButton>
      </div>

      <div className="grid items-start gap-4 lg:grid-cols-[1.15fr_0.85fr]">
        <div className="harbor-map-frame overflow-hidden rounded-[18px] border border-gold/12 bg-[#0a0c10]">
          <HarborMap
            compact
            features={features}
            subtitle={`${features.length} detections · ${route?.selected_node_id ?? "routing"}`}
            title={labelize(job.job_type)}
          />
        </div>

        <div className="space-y-4">
          {topCandidate ? <ScoreBar candidate={topCandidate} /> : null}
          <pre className="code-block !text-[11px]">{SDK_SNIPPET}</pre>
          {result?.artifacts?.length ? (
            <ul className="space-y-2 text-sm">
              {result.artifacts.slice(0, 3).map((artifact) => (
                <li className="metric-value truncate text-[11px] text-muted" key={artifact.key}>
                  {artifact.key}
                </li>
              ))}
            </ul>
          ) : null}
          {route ? (
            <p className="metric-value text-[11px] text-muted-dark">
              {formatMinutes(route.estimated_latency_minutes)} ·{" "}
              {formatCurrency(route.estimated_cost_usd)} · hash{" "}
              {route.decision_hash?.slice(0, 20)}…
            </p>
          ) : null}
        </div>
      </div>
    </div>
  );
}
