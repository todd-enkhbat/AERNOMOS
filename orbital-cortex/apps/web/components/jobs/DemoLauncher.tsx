"use client";

import { AnimatePresence, motion } from "framer-motion";
import { ArrowRight, Loader2, RotateCcw } from "lucide-react";
import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";

import { JobStepper } from "@/components/jobs/JobStepper";
import { createJob, getJob, getRouting } from "@/lib/api";
import { DEMO_API_KEY } from "@/lib/constants";
import { defaultJobPayload } from "@/lib/default-job-payload";
import type { Job, JobType, Priority, RoutingDecision } from "@/lib/types";
import { formatCurrency, formatMinutes, labelize } from "@/lib/format";

const jobTypes: JobType[] = ["ship_detection", "crop_health", "disaster_response"];
const priorities: Priority[] = ["fastest", "cheapest", "most_reliable"];

const springIn = { type: "spring" as const, stiffness: 300, damping: 30 };

export function DemoLauncher() {
  const [jobType, setJobType] = useState<JobType>("ship_detection");
  const [priority, setPriority] = useState<Priority>("fastest");
  const [job, setJob] = useState<Job | null>(null);
  const [route, setRoute] = useState<RoutingDecision | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const stopPolling = useCallback(() => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, []);

  useEffect(() => stopPolling, [stopPolling]);

  const poll = useCallback(
    (jobId: string) => {
      stopPolling();
      pollRef.current = setInterval(async () => {
        try {
          const detail = await getJob(jobId);
          setJob(detail.job);
          if (detail.routing_decision) {
            setRoute(detail.routing_decision);
          }
          if (detail.job.status === "complete" || detail.job.status === "failed") {
            stopPolling();
            if (!detail.routing_decision) {
              try {
                const routing = await getRouting(jobId);
                setRoute(routing.routing_decision);
              } catch {
                /* routing optional */
              }
            }
          }
        } catch {
          /* transient poll errors are fine */
        }
      }, 2000);
    },
    [stopPolling]
  );

  async function handleRun() {
    setSubmitting(true);
    setError(null);
    try {
      const response = await createJob(
        { ...defaultJobPayload, job_type: jobType, priority },
        DEMO_API_KEY
      );
      setJob(response.job);
      setRoute(null);
      poll(response.job.id);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "The live API is unreachable right now."
      );
    } finally {
      setSubmitting(false);
    }
  }

  function reset() {
    stopPolling();
    setJob(null);
    setRoute(null);
    setError(null);
  }

  return (
    <div className="aave-glass w-full max-w-md p-6 sm:p-7" id="demo">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="chart-label text-gold">Live demo</p>
          <h2 className="mt-1.5 text-lg font-semibold text-cream">
            Task the network
          </h2>
        </div>
        <span className="flex items-center gap-2 rounded-full border border-line px-3 py-1.5">
          <span className="pulse-dot bg-[#8fd6ab]" />
          <span className="chart-label text-muted">shared queue</span>
        </span>
      </div>

      <AnimatePresence initial={false} mode="wait">
        {!job ? (
          <motion.div
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            initial={{ opacity: 0, y: 8 }}
            key="form"
            transition={springIn}
          >
            <div className="mt-6">
              <p className="chart-label text-muted">Mission</p>
              <div className="mt-2.5 flex flex-wrap gap-2">
                {jobTypes.map((value) => (
                  <button
                    className={`rounded-full border px-3.5 py-1.5 text-sm transition ${
                      jobType === value
                        ? "border-gold/60 bg-gold/15 text-gold-bright"
                        : "border-line text-muted hover:border-cream/25 hover:text-cream"
                    }`}
                    key={value}
                    onClick={() => setJobType(value)}
                    type="button"
                  >
                    {labelize(value)}
                  </button>
                ))}
              </div>
            </div>

            <div className="mt-5">
              <p className="chart-label text-muted">Priority</p>
              <div className="mt-2.5 flex flex-wrap gap-2">
                {priorities.map((value) => (
                  <button
                    className={`rounded-full border px-3.5 py-1.5 text-sm transition ${
                      priority === value
                        ? "border-gold/50 bg-gold/12 text-gold-bright"
                        : "border-line text-muted hover:border-cream/25 hover:text-cream"
                    }`}
                    key={value}
                    onClick={() => setPriority(value)}
                    type="button"
                  >
                    {labelize(value)}
                  </button>
                ))}
              </div>
            </div>

            <div className="mt-5 rounded-xl border border-line bg-void/40 px-4 py-3">
              <p className="chart-label text-muted-dark">Scene</p>
              <p className="metric-value mt-1 text-sm text-cream/85">
                SAR · New York Harbor · bbox −74.3, 40.3, −73.5, 41.0
              </p>
            </div>

            {error ? (
              <p className="mt-4 rounded-xl border border-[#be543c]/40 bg-[#be543c]/10 px-4 py-3 text-sm text-[#e8a08e]">
                {error}
              </p>
            ) : null}

            <motion.button
              className="btn-gold mt-6 flex w-full disabled:cursor-not-allowed disabled:opacity-60"
              disabled={submitting}
              onClick={handleRun}
              type="button"
              whileTap={{ scale: 0.98 }}
            >
              {submitting ? (
                <Loader2 className="animate-spin" size={18} strokeWidth={2} />
              ) : null}
              Run live demo
              {!submitting ? <ArrowRight size={17} strokeWidth={2} /> : null}
            </motion.button>
            <p className="mt-3 text-center text-xs text-muted-dark">
              No account needed. Runs against the real production API.
            </p>
          </motion.div>
        ) : (
          <motion.div
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            initial={{ opacity: 0, y: 8 }}
            key="progress"
            transition={springIn}
          >
            <div className="mt-6">
              <JobStepper status={job.status} />
            </div>

            <div className="mt-6 space-y-2.5">
              <ProgressRow label="Job" value={job.id.slice(0, 20)} />
              <ProgressRow label="Mission" value={labelize(job.job_type)} />
              {route ? (
                <>
                  <ProgressRow accent label="Route" value={route.selected_node_id} />
                  <ProgressRow
                    label="Latency est."
                    value={formatMinutes(route.estimated_latency_minutes)}
                  />
                  <ProgressRow
                    label="Cost est."
                    value={formatCurrency(route.estimated_cost_usd)}
                  />
                </>
              ) : (
                <ProgressRow label="Route" value="scoring candidates…" />
              )}
            </div>

            <div className="mt-6 flex gap-2.5">
              <Link
                className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-gold px-4 py-3 text-sm font-semibold text-void transition-colors hover:bg-gold-bright"
                href={`/jobs/${job.id}`}
              >
                Open mission view
                <ArrowRight size={15} strokeWidth={2} />
              </Link>
              <button
                aria-label="Run another demo"
                className="grid h-11 w-11 place-items-center rounded-xl border border-line text-muted transition hover:border-cream/25 hover:text-cream"
                onClick={reset}
                type="button"
              >
                <RotateCcw size={16} strokeWidth={2} />
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function ProgressRow({
  label,
  value,
  accent = false
}: {
  label: string;
  value: string;
  accent?: boolean;
}) {
  return (
    <div className="flex items-center justify-between gap-4 border-b border-line pb-2">
      <span className="chart-label text-muted-dark">{label}</span>
      <span
        className={`metric-value text-sm ${accent ? "text-gold-bright" : "text-cream/85"}`}
      >
        {value}
      </span>
    </div>
  );
}
