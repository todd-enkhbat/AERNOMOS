"use client";

import type { LucideIcon } from "lucide-react";
import { Cloud, RadioTower, Satellite as SatelliteIcon, Server, Signal } from "lucide-react";
import dynamic from "next/dynamic";
import { useEffect, useMemo, useState } from "react";

import { InlineNotice } from "@/components/InlineNotice";
import { MetricCard } from "@/components/MetricCard";
import { ContactWindowTimeline } from "@/components/network/ContactWindowTimeline";
import { PageHeader } from "@/components/PageHeader";
import { API_BASE_URL, getContactWindows, getNodes, getSatellites, listJobs } from "@/lib/api";
import { EMPTY_NODES } from "@/lib/constants";
import type {
  ComputeNode,
  ContactWindow,
  GroundStation,
  NodesResponse,
  Satellite
} from "@/lib/types";
import { formatMinutes, formatPercent, labelize } from "@/lib/format";

const OrbitalScene = dynamic(
  () => import("@/components/orbital/OrbitalScene"),
  { ssr: false }
);

export default function NetworkPage() {
  const [nodes, setNodes] = useState<NodesResponse>(EMPTY_NODES);
  const [satellites, setSatellites] = useState<Satellite[]>([]);
  const [contactWindows, setContactWindows] = useState<ContactWindow[]>([]);
  const [activeJobs, setActiveJobs] = useState(0);
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    async function load() {
      try {
        const [nodeResponse, jobsResponse, satellitesResponse, windowsResponse] =
          await Promise.all([
            getNodes(),
            listJobs(),
            getSatellites(),
            getContactWindows({ upcoming: true, limit: 20 })
          ]);
        if (!mounted) {
          return;
        }
        setNodes(nodeResponse);
        setSatellites(satellitesResponse.satellites);
        setContactWindows(windowsResponse.contact_windows);
        setActiveJobs(
          jobsResponse.jobs.filter(
            (job) => job.status !== "complete" && job.status !== "failed"
          ).length
        );
      } catch (error) {
        if (mounted) {
          setNotice(
            error instanceof Error
              ? `${error.message} — is the API running at ${API_BASE_URL}?`
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
    <div className="relative pb-16">
      <div className="page-shell">
        <PageHeader
          eyebrow="Network"
          title="The orbital fabric"
          description="Orbital nodes, ground stations, cloud fallback, and the SGP4 contact windows the routing engine schedules against."
        />

        {notice ? <InlineNotice message={notice} /> : null}

        <section className="mt-5 grid gap-4 md:grid-cols-4">
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

        {/* orbital picture + contact windows */}
        <section className="mt-8 grid gap-6 lg:grid-cols-[0.85fr_1.15fr]">
          <div className="glass relative min-h-[380px] overflow-hidden p-6">
            <p className="chart-label relative z-10 text-gold">Constellation</p>
            <h2 className="display relative z-10 mt-2 text-xl text-cream">
              Live pass geometry
            </h2>
            <OrbitalScene className="absolute inset-0 opacity-80" />
          </div>

          <div className="glass p-6">
            <p className="chart-label text-gold">Contact windows</p>
            <h2 className="display mt-2 text-xl text-cream">
              Upcoming passes
            </h2>
            <div className="mt-6">
              <ContactWindowTimeline windows={contactWindows} />
            </div>
          </div>
        </section>

        {/* route model */}
        <section className="glass mt-8 overflow-hidden p-6 sm:p-8">
          <div className="flex items-center gap-3">
            <Server className="text-gold" size={18} strokeWidth={1.8} />
            <h2 className="text-lg font-semibold text-cream">Network route model</h2>
          </div>
          <div className="mt-8 grid gap-4 lg:grid-cols-[1fr_auto_1fr_auto_1fr]">
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
        </section>

        <section className="mt-8 grid gap-6 lg:grid-cols-2">
          <NodeGroup title="Orbital nodes" nodes={orbital} />
          <NodeGroup title="Cloud fallback" nodes={cloud} />
        </section>

        <section className="mt-10">
          <h2 className="mb-4 text-lg font-semibold text-cream">Ground stations</h2>
          {nodes.ground_stations.length === 0 ? (
            <p className="text-sm text-muted">No ground station data available.</p>
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {nodes.ground_stations.map((station) => (
                <GroundStationCard key={station.id} station={station} />
              ))}
            </div>
          )}
        </section>

        <section className="mt-10">
          <h2 className="mb-4 text-lg font-semibold text-cream">Satellites</h2>
          {satellites.length === 0 ? (
            <p className="text-sm text-muted">No satellite registry data available.</p>
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {satellites.map((satellite) => (
                <SatelliteCard key={satellite.id} satellite={satellite} />
              ))}
            </div>
          )}
        </section>
      </div>
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
    <div className="rounded-xl border border-line bg-void/40 p-4">
      <div className="flex items-center gap-2 text-gold">
        <Icon size={17} strokeWidth={1.8} />
        <p className="text-sm font-medium text-cream">{label}</p>
      </div>
      <div className="mt-4 space-y-2">
        {nodes.map((node) => (
          <p
            className="metric-value rounded-lg bg-cream/5 px-3 py-2 text-xs text-cream/80"
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
      <div className="h-px w-full bg-gradient-to-r from-gold/40 via-gold/20 to-gold/40" />
    </div>
  );
}

function NodeGroup({ title, nodes }: { title: string; nodes: ComputeNode[] }) {
  return (
    <div>
      <h2 className="mb-4 text-lg font-semibold text-cream">{title}</h2>
      <div className="grid gap-4">
        {nodes.map((node) => (
          <div className="glass glass-hover p-5" key={node.id}>
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <h3 className="font-medium text-cream">{node.name}</h3>
                <p className="metric-value mt-1 text-xs text-muted-dark">{node.id}</p>
              </div>
              <span className="metric-value rounded-full border border-gold/30 bg-gold/10 px-3 py-1.5 text-xs text-gold-bright">
                {formatPercent(node.availability)}
              </span>
            </div>
            <div className="mt-5 grid gap-3 sm:grid-cols-3">
              <p className="rounded-lg bg-cream/5 p-3 text-sm">
                <span className="chart-label block text-muted-dark">GPU</span>
                <span className="mt-1.5 block font-medium text-cream/90">
                  {node.gpu_class}
                </span>
              </p>
              <p className="rounded-lg bg-cream/5 p-3 text-sm">
                <span className="chart-label block text-muted-dark">Latency</span>
                <span className="metric-value mt-1.5 block text-cream/90">
                  {formatMinutes(node.latency_minutes)}
                </span>
              </p>
              <p className="rounded-lg bg-cream/5 p-3 text-sm">
                <span className="chart-label block text-muted-dark">
                  {node.type === "orbital" ? "Satellite" : "Contact"}
                </span>
                <span className="metric-value mt-1.5 block text-cream/90">
                  {node.satellite_id ?? "direct"}
                </span>
              </p>
            </div>
            <div className="mt-4 flex flex-wrap gap-2">
              {node.supported_models.map((model) => (
                <span
                  className="rounded-full border border-line px-2.5 py-1 text-xs text-muted"
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

function SatelliteCard({ satellite }: { satellite: Satellite }) {
  return (
    <div className="glass glass-hover p-5">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h3 className="font-medium text-cream">{satellite.name}</h3>
          <p className="metric-value mt-1 text-xs text-muted-dark">{satellite.id}</p>
        </div>
        <span className="metric-value rounded-full border border-teal/40 bg-teal/10 px-3 py-1.5 text-xs text-teal">
          NORAD {satellite.norad_id}
        </span>
      </div>
      <div className="mt-5 grid gap-3 sm:grid-cols-2">
        <p className="rounded-lg bg-cream/5 p-3 text-sm">
          <span className="chart-label block text-muted-dark">TLE snapshot</span>
          <span className="metric-value mt-1.5 block text-cream/90">
            {satellite.snapshot_id}
          </span>
        </p>
        <p className="rounded-lg bg-cream/5 p-3 text-sm">
          <span className="chart-label block text-muted-dark">Downlink rate</span>
          <span className="metric-value mt-1.5 block text-cream/90">
            {satellite.downlink_rate_mbps} Mbps
          </span>
        </p>
      </div>
    </div>
  );
}

function GroundStationCard({ station }: { station: GroundStation }) {
  return (
    <div className="glass glass-hover p-5">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h3 className="font-medium text-cream">{station.name}</h3>
          <p className="metric-value mt-1 text-xs text-muted-dark">{station.id}</p>
        </div>
        <span className="metric-value rounded-full border border-gold/30 bg-gold/10 px-3 py-1.5 text-xs text-gold-bright">
          {formatPercent(station.availability)}
        </span>
      </div>
      <div className="mt-5 grid gap-3 sm:grid-cols-3">
        <p className="rounded-lg bg-cream/5 p-3 text-sm">
          <span className="chart-label block text-muted-dark">Location</span>
          <span className="mt-1.5 block font-medium text-cream/90">{station.location}</span>
        </p>
        <p className="rounded-lg bg-cream/5 p-3 text-sm">
          <span className="chart-label block text-muted-dark">Latency</span>
          <span className="metric-value mt-1.5 block text-cream/90">
            {formatMinutes(station.latency_minutes)}
          </span>
        </p>
        <p className="rounded-lg bg-cream/5 p-3 text-sm">
          <span className="chart-label block text-muted-dark">Downlink</span>
          <span className="metric-value mt-1.5 block text-cream/90">
            {station.downlink_mbps} Mbps
          </span>
        </p>
      </div>
    </div>
  );
}
