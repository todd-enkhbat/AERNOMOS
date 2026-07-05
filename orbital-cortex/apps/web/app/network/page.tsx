"use client";

import type { LucideIcon } from "lucide-react";
import { Cloud, RadioTower, Satellite as SatelliteIcon, Server, Signal } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { InlineNotice } from "@/components/InlineNotice";
import { MetricCard } from "@/components/MetricCard";
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

      <section className="mt-8 dark-panel overflow-hidden p-6">
        <div className="flex items-center gap-3">
          <Server className="text-[#e0b16f]" size={20} strokeWidth={1.8} />
          <h2 className="text-2xl font-bold">Network route model</h2>
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

      <section className="mt-8">
        <h2 className="mb-4 text-2xl font-bold text-[#17140f]">Ground stations</h2>
        {nodes.ground_stations.length === 0 ? (
          <p className="text-sm text-[#6f604c]">No ground station data available.</p>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {nodes.ground_stations.map((station) => (
              <GroundStationCard key={station.id} station={station} />
            ))}
          </div>
        )}
      </section>

      <section className="mt-8">
        <h2 className="mb-4 text-2xl font-bold text-[#17140f]">Satellites</h2>
        {satellites.length === 0 ? (
          <p className="text-sm text-[#6f604c]">No satellite registry data available.</p>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {satellites.map((satellite) => (
              <SatelliteCard key={satellite.id} satellite={satellite} />
            ))}
          </div>
        )}
      </section>

      <section className="mt-8">
        <h2 className="mb-4 text-2xl font-bold text-[#17140f]">Upcoming contact windows</h2>
        {contactWindows.length === 0 ? (
          <p className="text-sm text-[#6f604c]">No upcoming contact windows in the pass cache.</p>
        ) : (
          <div className="table-shell">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Satellite</th>
                  <th>Ground station</th>
                  <th>AOS (UTC)</th>
                  <th>Max elevation</th>
                  <th>Duration</th>
                </tr>
              </thead>
              <tbody>
                {contactWindows.map((window) => (
                  <tr key={window.id}>
                    <td className="metric-value text-sm">{window.satellite_id}</td>
                    <td className="metric-value text-sm">{window.ground_station_id}</td>
                    <td className="text-sm text-[#6f604c]">{window.aos_utc}</td>
                    <td className="metric-value text-sm">
                      {window.max_elevation_deg.toFixed(1)}°
                    </td>
                    <td className="metric-value text-sm">
                      {Math.round(window.duration_s / 60)}m
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
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
                <span className="block text-[#6f604c]">
                  {node.type === "orbital" ? "Satellite" : "Contact"}
                </span>
                <span className="metric-value mt-1 block font-bold text-[#17140f]">
                  {node.satellite_id ?? "direct"}
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

function SatelliteCard({ satellite }: { satellite: Satellite }) {
  return (
    <div className="panel p-5">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h3 className="text-xl font-bold text-[#17140f]">{satellite.name}</h3>
          <p className="metric-value mt-1 text-xs text-[#6f604c]">{satellite.id}</p>
        </div>
        <span className="rounded-lg bg-[#eadcc8] px-3 py-2 text-sm font-bold text-[#25495a]">
          NORAD {satellite.norad_id}
        </span>
      </div>
      <div className="mt-5 grid gap-3 sm:grid-cols-2">
        <p className="rounded-lg bg-[#fffaf0]/70 p-3 text-sm">
          <span className="block text-[#6f604c]">TLE snapshot</span>
          <span className="metric-value mt-1 block font-bold text-[#17140f]">
            {satellite.snapshot_id}
          </span>
        </p>
        <p className="rounded-lg bg-[#fffaf0]/70 p-3 text-sm">
          <span className="block text-[#6f604c]">Downlink rate</span>
          <span className="metric-value mt-1 block font-bold text-[#17140f]">
            {satellite.downlink_rate_mbps} Mbps
          </span>
        </p>
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
