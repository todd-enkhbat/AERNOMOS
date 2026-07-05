"use client";

import { Cloud, RadioTower, Satellite, Server, Signal } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { InlineNotice } from "@/components/InlineNotice";
import { MetricCard } from "@/components/MetricCard";
import { PageHeader } from "@/components/PageHeader";
import { getNodes, listJobs } from "@/lib/api";
import { fallbackNodes } from "@/lib/mock-data";
import type { ComputeNode, GroundStation, NodesResponse } from "@/lib/types";
import { formatMinutes, formatPercent, labelize } from "@/lib/format";

export default function NetworkPage() {
  const [nodes, setNodes] = useState<NodesResponse>(fallbackNodes);
  const [activeJobs, setActiveJobs] = useState(0);
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    async function load() {
      try {
        const [nodeResponse, jobsResponse] = await Promise.all([getNodes(), listJobs()]);
        if (!mounted) {
          return;
        }
        setNodes(nodeResponse);
        setActiveJobs(
          jobsResponse.jobs.filter(
            (job) => job.status !== "completed" && job.status !== "failed"
          ).length
        );
      } catch (error) {
        if (mounted) {
          setNotice(
            error instanceof Error
              ? error.message
              : "Backend data is not available."
          );
          setNodes(fallbackNodes);
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
    <div className="page-shell pb-16">
      <PageHeader
        eyebrow="Network"
        title="Simulated orbital compute fabric"
        description="A local registry of orbital nodes, ground stations, and cloud fallback capacity used by the routing engine."
      />

      {notice ? <InlineNotice message={notice} /> : null}

      <section className="mt-5 grid gap-4 md:grid-cols-4">
        <MetricCard
          detail="Orbital candidates"
          icon={Satellite}
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

      <section className="mt-8 dark-panel overflow-hidden p-6">
        <div className="flex items-center gap-3">
          <Server className="text-[#e0b16f]" size={20} strokeWidth={1.8} />
          <h2 className="text-2xl font-bold">Network route model</h2>
        </div>
        <div className="mt-8 grid gap-4 lg:grid-cols-[1fr_auto_1fr_auto_1fr]">
          <TopologyColumn
            icon={Satellite}
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
      </section>

      <section className="mt-8 grid gap-6 lg:grid-cols-2">
        <NodeGroup title="Orbital nodes" nodes={orbital} />
        <NodeGroup title="Cloud fallback" nodes={cloud} />
      </section>

      <section className="mt-8">
        <h2 className="mb-4 text-2xl font-bold text-[#17140f]">Ground stations</h2>
        <div className="grid gap-4 md:grid-cols-2">
          {nodes.ground_stations.map((station) => (
            <GroundStationCard key={station.id} station={station} />
          ))}
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
  icon: typeof Satellite;
  label: string;
  nodes: string[];
}) {
  return (
    <div className="rounded-lg border border-[#fffaf0]/20 bg-[#fffaf0]/5 p-4">
      <div className="flex items-center gap-2 text-[#e0b16f]">
        <Icon size={18} strokeWidth={1.8} />
        <p className="font-bold text-[#fffaf0]">{label}</p>
      </div>
      <div className="mt-4 space-y-2">
        {nodes.map((node) => (
          <p
            className="metric-value rounded-lg bg-[#fffaf0]/10 px-3 py-2 text-xs text-[#f5eddf]"
            key={node}
          >
            {node}
          </p>
        ))}
      </div>
    </div>
  );
}

function Connector() {
  return (
    <div className="hidden min-w-12 items-center justify-center lg:flex">
      <div className="h-px w-full bg-[#fffaf0]/20" />
    </div>
  );
}

function NodeGroup({ title, nodes }: { title: string; nodes: ComputeNode[] }) {
  return (
    <div>
      <h2 className="mb-4 text-2xl font-bold text-[#17140f]">{title}</h2>
      <div className="grid gap-4">
        {nodes.map((node) => (
          <div className="panel p-5" key={node.id}>
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <h3 className="text-xl font-bold text-[#17140f]">{node.name}</h3>
                <p className="metric-value mt-1 text-xs text-[#6f604c]">{node.id}</p>
              </div>
              <span className="rounded-lg bg-[#eadcc8] px-3 py-2 text-sm font-bold text-[#25495a]">
                {formatPercent(node.availability)}
              </span>
            </div>
            <div className="mt-5 grid gap-3 sm:grid-cols-3">
              <p className="rounded-lg bg-[#fffaf0]/70 p-3 text-sm">
                <span className="block text-[#6f604c]">GPU</span>
                <span className="mt-1 block font-bold text-[#17140f]">
                  {node.gpu_class}
                </span>
              </p>
              <p className="rounded-lg bg-[#fffaf0]/70 p-3 text-sm">
                <span className="block text-[#6f604c]">Latency</span>
                <span className="metric-value mt-1 block font-bold text-[#17140f]">
                  {formatMinutes(node.latency_minutes)}
                </span>
              </p>
              <p className="rounded-lg bg-[#fffaf0]/70 p-3 text-sm">
                <span className="block text-[#6f604c]">Contact</span>
                <span className="metric-value mt-1 block font-bold text-[#17140f]">
                  {formatMinutes(node.next_contact_minutes)}
                </span>
              </p>
            </div>
            <div className="mt-4 flex flex-wrap gap-2">
              {node.supported_models.map((model) => (
                <span
                  className="rounded-lg border border-[rgba(86,67,42,0.22)] px-2.5 py-1 text-xs text-[#4f4436]"
                  key={model}
                >
                  {labelize(model)}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function GroundStationCard({ station }: { station: GroundStation }) {
  return (
    <div className="panel p-5">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h3 className="text-xl font-bold text-[#17140f]">{station.name}</h3>
          <p className="metric-value mt-1 text-xs text-[#6f604c]">{station.id}</p>
        </div>
        <span className="rounded-lg bg-[#eadcc8] px-3 py-2 text-sm font-bold text-[#25495a]">
          {formatPercent(station.availability)}
        </span>
      </div>
      <div className="mt-5 grid gap-3 sm:grid-cols-3">
        <p className="rounded-lg bg-[#fffaf0]/70 p-3 text-sm">
          <span className="block text-[#6f604c]">Location</span>
          <span className="mt-1 block font-bold text-[#17140f]">{station.location}</span>
        </p>
        <p className="rounded-lg bg-[#fffaf0]/70 p-3 text-sm">
          <span className="block text-[#6f604c]">Latency</span>
          <span className="metric-value mt-1 block font-bold text-[#17140f]">
            {formatMinutes(station.latency_minutes)}
          </span>
        </p>
        <p className="rounded-lg bg-[#fffaf0]/70 p-3 text-sm">
          <span className="block text-[#6f604c]">Downlink</span>
          <span className="metric-value mt-1 block font-bold text-[#17140f]">
            {station.downlink_mbps} Mbps
          </span>
        </p>
      </div>
    </div>
  );
}
