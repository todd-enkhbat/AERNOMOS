"use client";

import { Activity } from "lucide-react";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { PageHeader } from "@/components/PageHeader";
import { LiquidButton } from "@/components/liquid/LiquidButton";
import { StatusBadge } from "@/components/StatusBadge";
import { apiErrorMessage, getNodes, getRouting, listJobs } from "@/lib/api";
import { EMPTY_NODES } from "@/lib/constants";
import { formatDateTime, formatMinutes, labelize } from "@/lib/format";
import type { Job, NodesResponse, RoutingDecision } from "@/lib/types";

export default function DashboardPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [nodes, setNodes] = useState<NodesResponse>(EMPTY_NODES);
  const [routes, setRoutes] = useState<Record<string, RoutingDecision>>({});
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    async function load() {
      try {
        const [jobsResponse, nodesResponse] = await Promise.all([listJobs(), getNodes()]);
        if (!mounted) return;

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
          setNotice(null);
        }
      } catch (error) {
        if (mounted) setNotice(apiErrorMessage(error));
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
    const routeValues = Object.values(routes);
    const averageLatency =
      routeValues.length > 0
        ? routeValues.reduce((sum, route) => sum + route.estimated_latency_minutes, 0) /
          routeValues.length
        : 0;
    const representedInfrastructure =
      nodes.compute_nodes.length + nodes.ground_stations.length;

    return { activeJobs, averageLatency, representedInfrastructure };
  }, [jobs, nodes, routes]);

  return (
    <div className="page-shell pb-16">
      <PageHeader
        action={
          <LiquidButton href="/missions" variant="primary">
            Open missions
          </LiquidButton>
        }
        description="A reference view of the historical routing demo and the public infrastructure records it evaluates. Private customer missions remain in your mission workspace."
        eyebrow="Nomos reference control"
        title="The system, without invented telemetry."
      />

      {notice ? (
        <>
          <section className="nomos-ledger mt-6" aria-labelledby="control-unavailable-title">
            <div className="nomos-empty-state">
              <span className="nomos-empty-state__mark">
                <Activity aria-hidden size={18} />
              </span>
              <div>
                <p className="chart-label text-gold">REFERENCE STATUS</p>
                <h2 id="control-unavailable-title">Live reference data is unavailable.</h2>
                <p>
                  Nomos does not render unavailable infrastructure as healthy zeroes.
                  Your private mission workspace and the technical documentation remain
                  available while this reference view reconnects.
                </p>
                <div className="nomos-empty-state__actions">
                  <LiquidButton href="/missions" variant="primary">
                    Open missions
                  </LiquidButton>
                  <LiquidButton href="/docs" variant="outline">
                    Read the API reference
                  </LiquidButton>
                </div>
              </div>
            </div>
          </section>
        </>
      ) : (
        <>
          <section className="control-figures" aria-label="Reference control summary">
            <div className="control-figure">
              <span>active reference jobs</span>
              <strong>{metrics.activeJobs}</strong>
              <p>Queued, routing, executing, or downlinking in the historical demo.</p>
            </div>
            <div className="control-figure">
              <span>represented infrastructure</span>
              <strong>{metrics.representedInfrastructure}</strong>
              <p>Public reference stations and clearly labeled compute candidates.</p>
            </div>
            <div className="control-figure">
              <span>mean route estimate</span>
              <strong>{formatMinutes(metrics.averageLatency)}</strong>
              <p>Modeled timing for selected historical-demo routes, not provider telemetry.</p>
            </div>
          </section>

          <section className="mt-10" aria-labelledby="reference-queue-title">
            <div className="flex flex-wrap items-end justify-between gap-4 border-b border-gold/15 pb-4">
              <div>
                <p className="chart-label text-gold">HISTORICAL DEMO</p>
                <h2 className="display mt-1 text-2xl text-cream" id="reference-queue-title">
                  Reference queue
                </h2>
                <p className="mt-2 max-w-xl text-sm leading-6 text-muted">
                  This is a transparent reference system for routing scores and
                  lifecycle events. It is not a live provider operations console.
                </p>
              </div>
              <LiquidButton href="/jobs" variant="outline">
                Open historical demo
              </LiquidButton>
            </div>

            <div className="table-shell mt-5">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Job</th>
                    <th>Status</th>
                    <th>Selected route</th>
                    <th>Estimated latency</th>
                    <th>Updated</th>
                  </tr>
                </thead>
                <tbody>
                  {jobs.length === 0 ? (
                    <tr>
                      <td className="text-muted" colSpan={5}>
                        No reference jobs are represented right now. Use a curated
                        <Link className="text-gold hover:underline" href="/examples">
                          {" "}example mission
                        </Link>
                        {" "}to inspect a source-backed plan instead.
                      </td>
                    </tr>
                  ) : (
                    jobs.slice(0, 8).map((job) => {
                      const route = routes[job.id];
                      return (
                        <tr key={job.id}>
                          <td>
                            <Link
                              className="font-medium text-cream transition-colors hover:text-gold-bright"
                              href={"/jobs/" + job.id}
                            >
                              {labelize(job.job_type)}
                            </Link>
                            <p className="metric-value mt-1 text-xs text-muted-dark">
                              {job.id}
                            </p>
                          </td>
                          <td><StatusBadge status={job.status} /></td>
                          <td className="metric-value text-sm text-silver">
                            {route?.selected_node_id ?? "pending"}
                          </td>
                          <td className="metric-value text-sm text-cream/85">
                            {route ? formatMinutes(route.estimated_latency_minutes) : "pending"}
                          </td>
                          <td className="text-sm text-muted">{formatDateTime(job.updated_at)}</td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          </section>

          <section className="nomos-ledger mt-10" aria-labelledby="control-scope-title">
            <div className="nomos-ledger__header">
              <div>
                <p className="chart-label text-gold">READING THE VIEW</p>
                <h2 className="mt-1 text-base font-medium text-cream" id="control-scope-title">
                  What this reference surface means
                </h2>
              </div>
            </div>
            <div className="nomos-ledger__body">
              {[
                ["01", "Data scope", "Curated public demo records only. Private missions are not listed here."],
                ["02", "Route values", "Latency and route scores are modeled estimates for the historical simulation path."],
                ["03", "Provider boundary", "Public orbital math and references are real. Live tasking, booking, telemetry, and pricing are not connected."]
              ].map(([index, title, detail]) => (
                <div className="nomos-ledger__row" key={index}>
                  <span className="nomos-ledger__index">{index}</span>
                  <span>
                    <span className="nomos-ledger__row-title">{title}</span>
                    <span className="nomos-ledger__row-detail">{detail}</span>
                  </span>
                </div>
              ))}
            </div>
          </section>
        </>
      )}
    </div>
  );
}
