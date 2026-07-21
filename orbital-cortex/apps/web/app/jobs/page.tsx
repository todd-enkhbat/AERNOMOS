"use client";

import { motion } from "framer-motion";
import { DemoBoundary } from "@/components/archive/ArchivePrimitives";
import { Loader2, SendHorizontal } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useMemo, useState } from "react";

import { InlineNotice } from "@/components/InlineNotice";
import { PageHeader } from "@/components/PageHeader";
import { StatusBadge } from "@/components/StatusBadge";
import { apiErrorMessage, createJob, listJobs } from "@/lib/api";
import { DEMO_API_KEY } from "@/lib/constants";
import { defaultJobPayload } from "@/lib/default-job-payload";
import type {
  ComputePreference,
  Job,
  JobCreatePayload,
  JobType,
  Priority,
  Sensor
} from "@/lib/types";
import { formatDateTime, formatCurrency, labelize } from "@/lib/format";

const jobTypes: JobType[] = ["ship_detection", "crop_health", "disaster_response"];
const sensors: Sensor[] = ["SAR", "optical", "hyperspectral", "any"];
const priorities: Priority[] = ["fastest", "cheapest", "most_reliable"];
const preferences: ComputePreference[] = [
  "orbital_if_available",
  "ground_only",
  "cheapest",
  "fastest"
];

const missionHelp: Record<JobType, string> = {
  ship_detection: "Rich reference flow using an offline New York Harbor SAR scene.",
  crop_health: "Deterministic demo output for testing routing and result retrieval.",
  disaster_response: "Deterministic demo output for testing urgent routing priorities."
};

export default function JobsPage() {
  const router = useRouter();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [jobType, setJobType] = useState<JobType>(defaultJobPayload.job_type);
  const [sensor, setSensor] = useState<Sensor>(defaultJobPayload.sensor);
  const [priority, setPriority] = useState<Priority>(defaultJobPayload.priority);
  const [preference, setPreference] = useState<ComputePreference>(
    defaultJobPayload.compute_preference
  );
  const [maxCost, setMaxCost] = useState(String(defaultJobPayload.max_cost_usd));
  const [aoi, setAoi] = useState(
    JSON.stringify(defaultJobPayload.area_of_interest, null, 2)
  );
  const [notice, setNotice] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    async function loadJobs() {
      try {
        const response = await listJobs();
        if (mounted) {
          setJobs(response.jobs);
          setNotice(null);
        }
      } catch (error) {
        if (mounted) {
          setNotice(apiErrorMessage(error));
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }
    loadJobs();
    return () => {
      mounted = false;
    };
  }, []);

  const payloadPreview = useMemo<JobCreatePayload | null>(() => {
    try {
      return {
        schema_version: 1,
        job_type: jobType,
        area_of_interest: JSON.parse(aoi),
        sensor,
        priority,
        compute_preference: preference,
        max_cost_usd: Number(maxCost)
      };
    } catch {
      return null;
    }
  }, [aoi, jobType, maxCost, preference, priority, sensor]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setNotice(null);

    if (!payloadPreview) {
      setNotice("Area of interest must be valid JSON.");
      return;
    }
    if (!Number.isFinite(payloadPreview.max_cost_usd) || payloadPreview.max_cost_usd <= 0) {
      setNotice("Max cost must be greater than zero.");
      return;
    }

    setSubmitting(true);
    try {
      const response = await createJob(payloadPreview, DEMO_API_KEY);
      // New submissions are not added to the public curated list.
      router.push(`/jobs/${response.job.id}`);
    } catch (error) {
      setNotice(apiErrorMessage(error, "Job submission is temporarily unavailable."));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="page-shell pb-16">
      <PageHeader
        eyebrow="Historical simulation demo"
        title="Run a simulated space-data job"
        description="This path is a labeled historical demo, not the primary product. Submit a job to inspect routing. The board shows curated example jobs only — not every visitor submission. Prefer /plan and /examples for mission planning."
      />

      {notice ? <InlineNotice message={notice} /> : null}
      <div className="mt-5">
        <DemoBoundary compact />
      </div>
      <aside className="mt-3 rounded-2xl border border-gold/25 bg-gold/8 px-4 py-3 text-sm text-cream">
        SIMULATED execution and canned detections. Production API and real orbital
        math; not live vessel intelligence or provider inventory.
      </aside>

      <section className="mt-5 grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
        <form className="glass p-6 sm:p-7" onSubmit={handleSubmit}>
          <div>
            <h2 className="text-lg font-semibold text-cream">New demo job</h2>
            <p className="mt-1 text-sm text-muted">
              {missionHelp[jobType]}
            </p>
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-2">
            <label className="block">
              <span className="chart-label mb-2 block text-muted">Job type</span>
              <select
                className="input-field"
                onChange={(event) => setJobType(event.target.value as JobType)}
                value={jobType}
              >
                {jobTypes.map((value) => (
                  <option key={value} value={value}>
                    {labelize(value)}
                  </option>
                ))}
              </select>
              <span className="mt-1.5 block text-xs leading-5 text-muted-dark">
                The AI task the selected node must support.
              </span>
            </label>
            <label className="block">
              <span className="chart-label mb-2 block text-muted">Sensor</span>
              <select
                className="input-field"
                onChange={(event) => setSensor(event.target.value as Sensor)}
                value={sensor}
              >
                {sensors.map((value) => (
                  <option key={value} value={value}>
                    {labelize(value)}
                  </option>
                ))}
              </select>
              <span className="mt-1.5 block text-xs leading-5 text-muted-dark">
                The requested observation type. SAR is used by the Harbor reference scene.
              </span>
            </label>
            <label className="block">
              <span className="chart-label mb-2 block text-muted">Priority</span>
              <select
                className="input-field"
                onChange={(event) => setPriority(event.target.value as Priority)}
                value={priority}
              >
                {priorities.map((value) => (
                  <option key={value} value={value}>
                    {labelize(value)}
                  </option>
                ))}
              </select>
              <span className="mt-1.5 block text-xs leading-5 text-muted-dark">
                Changes the scoring weights, not the underlying orbital geometry.
              </span>
            </label>
            <label className="block">
              <span className="chart-label mb-2 block text-muted">Max cost USD</span>
              <input
                className="input-field"
                min="1"
                onChange={(event) => setMaxCost(event.target.value)}
                type="number"
                value={maxCost}
              />
              <span className="mt-1.5 block text-xs leading-5 text-muted-dark">
                A hard ceiling used to eliminate routes whose modeled cost is too high.
              </span>
            </label>
            <label className="block md:col-span-2">
              <span className="chart-label mb-2 block text-muted">
                Compute preference
              </span>
              <select
                className="input-field"
                onChange={(event) =>
                  setPreference(event.target.value as ComputePreference)
                }
                value={preference}
              >
                {preferences.map((value) => (
                  <option key={value} value={value}>
                    {labelize(value)}
                  </option>
                ))}
              </select>
              <span className="mt-1.5 block text-xs leading-5 text-muted-dark">
                A routing preference. Hard constraints are always checked first.
              </span>
            </label>
            <label className="block md:col-span-2">
              <span className="chart-label mb-2 block text-muted">
                Area of interest
              </span>
              <textarea
                className="input-field metric-value min-h-[140px] resize-y text-sm"
                onChange={(event) => setAoi(event.target.value)}
                value={aoi}
              />
              <span className="mt-1.5 block text-xs leading-5 text-muted-dark">
                GeoJSON-style bounding box or polygon. The default covers New York Harbor.
              </span>
            </label>
          </div>

          <details className="mt-5 rounded-xl border border-line bg-void/40 p-4">
            <summary className="cursor-pointer text-sm font-medium text-cream">
              Preview API request
            </summary>
            <pre className="code-block mt-3 !text-[11px]">
              {payloadPreview
                ? JSON.stringify(payloadPreview, null, 2)
                : "Area of interest is not valid JSON."}
            </pre>
          </details>

          <motion.button
            className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-gold px-5 py-3.5 font-semibold text-void transition-colors hover:bg-gold-bright disabled:cursor-not-allowed disabled:opacity-60"
            disabled={submitting}
            type="submit"
            whileTap={{ scale: 0.98 }}
          >
            {submitting ? (
              <Loader2 className="animate-spin" size={18} strokeWidth={2} />
            ) : (
              <SendHorizontal size={18} strokeWidth={2} />
            )}
            Submit mission
          </motion.button>
        </form>

        <section>
          <div className="mb-4 flex items-center justify-between gap-4">
            <div>
              <h2 className="text-lg font-semibold text-cream">Curated examples</h2>
              <p className="mt-1 text-xs text-muted">
                A small set of labeled demo jobs. New submissions open on their own detail
                page and are not added to this public list.
              </p>
            </div>
            <span className="metric-value text-sm text-muted">
              {loading ? "loading" : `${jobs.length} examples`}
            </span>
          </div>
          <div className="table-shell">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Job</th>
                  <th>Status</th>
                  <th>Budget</th>
                  <th>Preference</th>
                  <th>Updated</th>
                </tr>
              </thead>
              <tbody>
                {jobs.length === 0 ? (
                  <tr>
                    <td className="text-muted" colSpan={5}>
                      No curated examples yet. Submit a job above to run a private demo
                      detail page; examples are promoted from complete runs on deploy seed.
                    </td>
                  </tr>
                ) : (
                  jobs.map((job) => (
                    <tr key={job.id}>
                      <td>
                        <Link
                          className="font-medium text-cream 	ransition-colors hover:text-gold-bright"
                          href={`/jobs/${job.id}`}
                        >
                          {labelize(job.job_type)}
                        </Link>
                        <p className="metric-value mt-1 text-xs text-muted-dark">
                          {job.id}
                        </p>
                      </td>
                      <td>
                        <StatusBadge status={job.status} />
                      </td>
                      <td className="metric-value text-sm text-cream/85">
                        {formatCurrency(job.max_cost_usd)}
                      </td>
                      <td className="text-sm text-muted">
                        {labelize(job.compute_preference)}
                      </td>
                      <td className="text-sm text-muted">
                        {formatDateTime(job.updated_at)}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </section>
      </section>
    </div>
  );
}
