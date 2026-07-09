"use client";

import type { LucideIcon } from "lucide-react";
import { Cloud, RadioTower, Satellite as SatelliteIcon, Server, Signal } from "lucide-react";
import dynamic from "next/dynamic";
import { useEffect, useMemo, useState } from "react";

import { InlineNotice } from "@/components/InlineNotice";
import { MetricCard } from "@/components/MetricCard";
import { ScrollSketchfab } from "@/components/motion/ScrollSketchfab";
import { OrbitalScrollStage } from "@/components/motion/OrbitalScrollStage";
import { PageHeader } from "@/components/PageHeader";
import { API_BASE_URL, getNodes, listJobs } from "@/lib/api";
import { EMPTY_NODES } from "@/lib/constants";
import type { ComputeNode, NodesResponse } from "@/lib/types";
import { formatMinutes, formatPercent, labelize } from "@/lib/format";

const NetworkConsole = dynamic(
  () =>
    import("@/components/platform/NetworkConsole").then((m) => m.NetworkConsole),
  { ssr: false }
);

const OrbitalScene = dynamic(
  () => import("@/components/orbital/OrbitalScene"),
  { ssr: false }
);

const SKETCHFAB_SATELLITE =
  "https://sketchfab.com/models/f397bb9fe5124a0a9db13b138af516d8/embed?autostart=1&preload=1&ui_theme=dark&ui_infos=0&ui_watermark=0";

export default function NetworkPage() {
  const [nodes, setNodes] = useState<NodesResponse>(EMPTY_NODES);
  const [activeJobs, setActiveJobs] = useState(0);
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    async function load() {
      try {
        const [nodeResponse, jobsResponse] = await Promise.all([
          getNodes(),
          listJobs()
        ]);
        if (!mounted) {
          return;
        }
        setNodes(nodeResponse);
        setActiveJobs(
          jobsResponse.jobs.filter(
            (job) => job.status !== "complete" && job.status !== "failed"
          ).length
        );
      } catch (error) {
        if (mounted) {
          setNotice(
            error instanceof Error
              ? `${error.message}. Is the API running at ${API_BASE_URL}?`
              : `Backend data is not available. Is the API running at ${API_BASE_URL}?`
          );
        }
      }
    }
    load();
    return () => {
      mounted = false;
    };
  }, []);

  const orbital = useMemo(
    () => nodes.compute_nodes.filter((node) => node.type === "orbital"),
    [nodes]
  );
  const cloud = useMemo(
    () => nodes.compute_nodes.filter((node) => node.type === "ground_cloud"),
    [nodes]
  );

  return (
    <div className="relative pb-10">
      <div className="page-shell">
        <PageHeader
          description="Ground mesh, SGP4 passes, orbital nodes, and cloud fallback. Live data from the routing engine."
          eyebrow="Network"
          title="The orbital fabric"
        />
        {notice ? <InlineNotice message={notice} /> : null}

        <section className="grid gap-3 md:grid-cols-4">
          <MetricCard
            detail="Orbital candidates"
            icon={SatelliteIcon}
            label="Orbital Nodes"
            value={String(orbital.length)}
            tone="dark"
          />
          <MetricCard
            detail="Downlink locations"
            icon={RadioTower}
            label="Ground Stations"
            value={String(nodes.ground_stations.length)}
          />
          <MetricCard
            detail="Fallback compute"
            icon={Cloud}
            label="Cloud Nodes"
            value={String(cloud.length)}
          />
          <MetricCard
            detail="Queued or running"
            icon={Signal}
            label="Active Jobs"
            value={String(activeJobs)}
          />
        </section>
      </div>

      <section className="section-gap">
        <div className="page-shell mb-4">
          <p className="chart-label text-gold">Fleet geometry</p>
          <h2 className="display mt-1 text-xl text-cream">Scroll the constellation</h2>
        </div>
        <OrbitalScrollStage scrollHeight="120vh">
          <OrbitalScene className="h-[min(420px,70vw)] w-[min(420px,70vw)]" />
        </OrbitalScrollStage>
      </section>

      <section className="section-gap">
        <div className="page-shell mb-4">
          <p className="chart-label text-gold">Communications satellite</p>
          <p className="prose-compact mt-1 max-w-lg text-muted">
            Interactive model drifts with scroll. Drag to inspect the bus.
          </p>
        </div>
        <ScrollSketchfab scrollHeight="130vh" src={SKETCHFAB_SATELLITE} title="Communications Satellite" />
      </section>

      <section className="section-gap page-shell">
        <NetworkConsole />
      </section>

      <section className="page-shell mt-8">
        <div className="liquid-panel overflow-hidden p-5">
          <div className="flex items-center gap-2.5">
            <Server className="text-gold" size={17} strokeWidth={1.8} />
            <h2 className="text-base font-semibold text-cream">Route model</h2>
          </div>
          <div className="mt-5 grid gap-3 lg:grid-cols-[1fr_auto_1fr_auto_1fr]">
            <TopologyColumn
              icon={SatelliteIcon}
              label="Orbital compute"
              nodes={orbital.map((node) => node.id)}
            />
            <Connector />
            <TopologyColumn
              icon={RadioTower}
              label="Ground stations"
              nodes={nodes.ground_stations.map((station) => station.id)}
            />
            <Connector />
            <TopologyColumn
              icon={Cloud}
              label="Cloud fallback"
              nodes={cloud.map((node) => node.id)}
            />
          </div>
        </div>

        <div className="mt-5 grid gap-4 lg:grid-cols-2">
          <NodeGroup title="Orbital nodes" nodes={orbital} />
          <NodeGroup title="Cloud fallback" nodes={cloud} />
        </div>
      </section>
    </div>
  );
}

function TopologyColumn({
  icon: Icon,
  label,
  nodes
}: {
  icon: LucideIcon;
  label: string;
  nodes: string[];
}) {
  return (
    <div className="rounded-xl border border-gold/10 bg-black/30 p-3.5">
      <div className="flex items-center gap-2 text-gold">
        <Icon size={16} strokeWidth={1.8} />
        <p className="text-sm font-medium text-cream">{label}</p>
      </div>
      <div className="mt-3 space-y-1.5">
        {nodes.length === 0 ? (
          <p className="text-xs text-muted">No nodes registered.</p>
        ) : (
          nodes.map((node) => (
            <p className="metric-value text-[11px] text-cream/75" key={node}>
              {node}
            </p>
          ))
        )}
      </div>
    </div>
  );
}

function Connector() {
  return (
    <div className="hidden min-w-10 items-center justify-center lg:flex">
      <div className="h-px w-full bg-gradient-to-r from-gold/25 via-gold/10 to-gold/25" />
    </div>
  );
}

function NodeGroup({ title, nodes }: { title: string; nodes: ComputeNode[] }) {
  return (
    <div>
      <h2 className="mb-3 text-base font-semibold text-cream">{title}</h2>
      {nodes.length === 0 ? (
        <div className="liquid-panel p-5">
          <p className="text-sm text-muted">No compute nodes in this tier.</p>
        </div>
      ) : (
        <div className="grid gap-3">
          {nodes.map((node) => (
            <div className="liquid-panel p-4" key={node.id}>
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <h3 className="text-sm font-medium text-cream">{node.name}</h3>
                  <p className="metric-value mt-0.5 text-[11px] text-muted-dark">{node.id}</p>
                </div>
                <span className="metric-value text-[11px] text-gold-bright">
                  {formatPercent(node.availability)}
                </span>
              </div>
              <p className="metric-value mt-2 text-[11px] text-muted">
                {node.gpu_class} · {formatMinutes(node.latency_minutes)}
              </p>
              <div className="mt-2 flex flex-wrap gap-1.5">
                {node.supported_models.map((model) => (
                  <span className="text-[11px] text-muted" key={model}>
                    {labelize(model)}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
