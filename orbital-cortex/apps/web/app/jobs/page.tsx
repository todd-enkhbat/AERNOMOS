"use client";

import { Loader2, Plus, SendHorizontal } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useMemo, useState } from "react";

import { InlineNotice } from "@/components/InlineNotice";
import { PageHeader } from "@/components/PageHeader";
import { StatusBadge } from "@/components/StatusBadge";
import { createJob, listJobs } from "@/lib/api";
import { defaultJobPayload } from "@/lib/mock-data";
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

export default function JobsPage() {
  const router = useRouter();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [apiKey, setApiKey] = useState("oc_test_123");
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
          setNotice(
            error instanceof Error
              ? error.message
              : "Backend data is not available."
          );
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
      const response = await createJob(payloadPreview, apiKey);
      setJobs((current) => [response.job, ...current]);
      router.push(`/jobs/${response.job.id}`);
    } catch (error) {
      setNotice(
        error instanceof Error ? error.message : "Job submission failed."
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="page-shell pb-16">
      <PageHeader
        eyebrow="Jobs"
        title="Submit a mission job"
        description="Create a deterministic space-data request, route it across simulated orbital and cloud compute, then inspect the operator log and result."
      />

      {notice ? <InlineNotice message={notice} /> : null}

      <section className="mt-5 grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
        <form className="panel p-6" onSubmit={handleSubmit}>
          <div className="flex items-center gap-3">
            <span className="grid h-10 w-10 place-items-center rounded-lg bg-[#17140f] text-[#fffaf0]">
              <Plus size={18} strokeWidth={1.8} />
            </span>
            <div>
              <h2 className="text-2xl font-bold text-[#17140f]">New maritime run</h2>
              <p className="text-sm text-[#6f604c]">
                Default AOI: New York Harbor SAR scene
              </p>
            </div>
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-2">
            <label className="block">
              <span className="mb-2 block text-sm font-bold text-[#4f4436]">API key</span>
              <input
                className="input-field"
                onChange={(event) => setApiKey(event.target.value)}
                value={apiKey}
              />
            </label>
            <label className="block">
              <span className="mb-2 block text-sm font-bold text-[#4f4436]">Job type</span>
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
            </label>
            <label className="block">
              <span className="mb-2 block text-sm font-bold text-[#4f4436]">Sensor</span>
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
            </label>
            <label className="block">
              <span className="mb-2 block text-sm font-bold text-[#4f4436]">Priority</span>
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
            </label>
            <label className="block md:col-span-2">
              <span className="mb-2 block text-sm font-bold text-[#4f4436]">
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
            </label>
            <label className="block md:col-span-2">
              <span className="mb-2 block text-sm font-bold text-[#4f4436]">
                Max cost USD
              </span>
              <input
                className="input-field"
                min="1"
                onChange={(event) => setMaxCost(event.target.value)}
                type="number"
                value={maxCost}
              />
            </label>
            <label className="block md:col-span-2">
              <span className="mb-2 block text-sm font-bold text-[#4f4436]">
                Area of interest
              </span>
              <textarea
                className="input-field min-h-[156px] resize-y font-mono text-sm"
                onChange={(event) => setAoi(event.target.value)}
                value={aoi}
              />
            </label>
          </div>

          <button
            className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-lg bg-[#17140f] px-5 py-3 font-bold text-[#fffaf0] transition hover:bg-[#2a241b] disabled:cursor-not-allowed disabled:opacity-60"
            disabled={submitting}
            type="submit"
          >
            {submitting ? (
              <Loader2 className="animate-spin" size={18} strokeWidth={1.8} />
            ) : (
              <SendHorizontal size={18} strokeWidth={1.8} />
            )}
            Submit Job
          </button>
        </form>

        <section>
          <div className="mb-4 flex items-center justify-between gap-4">
            <h2 className="text-2xl font-bold text-[#17140f]">Job queue</h2>
            <span className="metric-value text-sm text-[#6f604c]">
              {loading ? "loading" : `${jobs.length} jobs`}
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
                    <td className="text-[#6f604c]" colSpan={5}>
                      No jobs have been submitted.
                    </td>
                  </tr>
                ) : (
                  jobs.map((job) => (
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
                      <td className="metric-value text-sm">
                        {formatCurrency(job.max_cost_usd)}
                      </td>
                      <td className="text-sm text-[#6f604c]">
                        {labelize(job.compute_preference)}
                      </td>
                      <td className="text-sm text-[#6f604c]">
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
