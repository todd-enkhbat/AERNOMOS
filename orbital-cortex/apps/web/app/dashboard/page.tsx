"use client";

import {
  Activity,
  Clock3,
  DollarSign,
  RadioTower,
  Satellite,
  Server,
  ShieldCheck
} from "lucide-react";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { InlineNotice } from "@/components/InlineNotice";
import { MetricCard } from "@/components/MetricCard";
import { PageHeader } from "@/components/PageHeader";
import { StatusBadge } from "@/components/StatusBadge";
import { getNodes, getRouting, listJobs } from "@/lib/api";
import { fallbackNodes } from "@/lib/mock-data";
import type { Job, NodesResponse, RoutingDecision } from "@/lib/types";
import { formatCurrency, formatDateTime, formatMinutes, labelize } from "@/lib/format";

export default function DashboardPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [nodes, setNodes] = useState<NodesResponse>(fallbackNodes);
  const [routes, setRoutes] = useState<Record<string, RoutingDecision>>({});
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    async function load() {
      try {
        const [jobsResponse, nodesResponse] = await Promise.all([listJobs(), getNodes()]);
        if (!mounted) {
          return;
        }
        setJobs(jobsResponse.jobs);
        setNodes(nodesResponse);

        const routePairs = await Promise.all(
          jobsResponse.jobs.map(async (job) => {
            try {
              const route = await getRouting(job.id);
              return [job.id, route.routing_decision] as const;
            } catch {
              return null;
            }
          })
        );
        if (mounted) {
          setRoutes(
            Object.fromEntries(routePairs.filter(Boolean) as Array<[string, RoutingDecision]>)
          );
        }
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

  const metrics = useMemo(() => {
    const activeJobs = jobs.filter(
      (job) => job.status !== "complete" && job.status !== "failed"
    ).length;
    const completedToday = jobs.filter((job) => {
      const updated = new Date(job.updated_at);
      const now = new Date();
      return (
        job.status === "complete" &&
        updated.getFullYear() === now.getFullYear() &&
        updated.getMonth() === now.getMonth() &&
        updated.getDate() === now.getDate()
      );
    }).length;
    const routeValues = Object.values(routes);
    const averageLatency =
      routeValues.length > 0
        ? routeValues.reduce((sum, route) => sum + route.estimated_latency_minutes, 0) /
          routeValues.length
        : 0;
    const costSaved = jobs.reduce((sum, job) => {
      const route = routes[job.id];
      if (!route) {
        return sum;
      }
      return sum + Math.max(0, job.max_cost_usd - route.estimated_cost_usd);
    }, 0);

    return {
      activeJobs,
      completedToday,
      averageLatency,
      orbitalNodesOnline: nodes.compute_nodes.filter(
        (node) => node.type === "orbital" && node.power_state === "nominal"
      ).length,
      groundStationsAvailable: nodes.ground_stations.length,
      costSaved
    };
  }, [jobs, nodes, routes]);

  return (
    <div className="page-shell pb-16">
      <PageHeader
        eyebrow="Control plane"
        title="Mission operations dashboard"
        description="Track simulated orbital compute availability, route quality, execution latency, and recent space-data jobs from one local console."
        action={
          <Link
            className="inline-flex items-center gap-2 rounded-lg bg-[#17140f] px-4 py-3 font-bold text-[#fffaf0] transition hover:bg-[#2a241b]"
            href="/jobs"
          >
            <Activity size={18} strokeWidth={1.8} />
            Submit Job
          </Link>
        }
      />

      {notice ? <InlineNotice message={notice} /> : null}

      <section className="mt-5 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <MetricCard
          icon={Activity}
          label="Active Jobs"
          value={String(metrics.activeJobs)}
          detail="Queued, scheduled, or running simulations"
          tone="dark"
        />
        <MetricCard
          icon={ShieldCheck}
          label="Completed Today"
          value={String(metrics.completedToday)}
          detail="Jobs with generated result manifests"
        />
        <MetricCard
          icon={Clock3}
          label="Average Latency"
          value={formatMinutes(metrics.averageLatency)}
          detail="Mean selected-route estimate"
        />
        <MetricCard
          icon={Satellite}
          label="Orbital Nodes Online"
          value={String(metrics.orbitalNodesOnline)}
          detail="Nominal orbital compute candidates"
        />
        <MetricCard
          icon={RadioTower}
          label="Ground Stations Available"
          value={String(metrics.groundStationsAvailable)}
          detail="Simulated downlink partners"
        />
        <MetricCard
          icon={DollarSign}
          label="Estimated Cost Saved"
          value={formatCurrency(metrics.costSaved)}
          detail="Budget headroom across routed jobs"
        />
      </section>

      <section className="mt-8">
        <div className="mb-4 flex items-center justify-between gap-4">
          <h2 className="text-2xl font-bold text-[#17140f]">Recent jobs</h2>
          <Link className="text-sm font-bold text-[#25495a]" href="/jobs">
            View all
          </Link>
        </div>

        <div className="table-shell">
          <table className="data-table">
            <thead>
              <tr>
                <th>Job</th>
                <th>Status</th>
                <th>Route</th>
                <th>Latency</th>
                <th>Cost</th>
                <th>Updated</th>
              </tr>
            </thead>
            <tbody>
              {jobs.length === 0 ? (
                <tr>
                  <td className="text-[#6f604c]" colSpan={6}>
                    No jobs have been submitted.
                  </td>
                </tr>
              ) : (
                jobs.slice(0, 8).map((job) => {
                  const route = routes[job.id];
                  return (
                    <tr key={job.id}>
                      <td>
                        <Link className="font-bold text-[#17140f]" href={`/jobs/${job.id}`}>
                          {labelize(job.job_type)}
                        </Link>
                        <p className="metric-value mt-1 text-xs text-[#6f604c]">
                          {job.id}
                        </p>
                      </td>
                      <td>
                        <StatusBadge status={job.status} />
                      </td>
                      <td className="metric-value text-sm text-[#25495a]">
                        {route?.selected_node_id ?? "pending"}
                      </td>
                      <td className="metric-value text-sm">
                        {route ? formatMinutes(route.estimated_latency_minutes) : "0m"}
                      </td>
                      <td className="metric-value text-sm">
                        {route ? formatCurrency(route.estimated_cost_usd) : "$0"}
                      </td>
                      <td className="text-sm text-[#6f604c]">
                        {formatDateTime(job.updated_at)}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </section>

      <section className="mt-8 grid gap-4 lg:grid-cols-3">
        <div className="dark-panel p-6 lg:col-span-2">
          <div className="flex items-center gap-3">
            <Server className="text-[#e0b16f]" size={20} strokeWidth={1.8} />
            <h2 className="text-2xl font-bold">Routing posture</h2>
          </div>
          <div className="mt-6 grid gap-3 md:grid-cols-3">
            {["Model support", "Contact window", "Fallback path"].map((item) => (
              <div
                className="rounded-lg border border-[#fffaf0]/10 bg-[#fffaf0]/5 p-4"
                key={item}
              >
                <p className="text-sm text-[#d8cbb8]">{item}</p>
                <p className="mt-2 font-bold text-[#fffaf0]">Ready</p>
              </div>
            ))}
          </div>
        </div>
        <div className="panel p-6">
          <h2 className="text-2xl font-bold text-[#17140f]">Network mix</h2>
          <div className="mt-5 space-y-3">
            <p className="flex justify-between text-sm">
              <span className="text-[#6f604c]">Orbital</span>
              <span className="metric-value">
                {nodes.compute_nodes.filter((node) => node.type === "orbital").length}
              </span>
            </p>
            <p className="flex justify-between text-sm">
              <span className="text-[#6f604c]">Cloud</span>
              <span className="metric-value">
                {nodes.compute_nodes.filter((node) => node.type === "ground_cloud").length}
              </span>
            </p>
            <p className="flex justify-between text-sm">
              <span className="text-[#6f604c]">Ground stations</span>
              <span className="metric-value">{nodes.ground_stations.length}</span>
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
