"use client";

import { AnimatePresence, motion } from "framer-motion";
import { ArrowRight, Loader2, RotateCcw } from "lucide-react";
import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";

import { JobStepper } from "@/components/jobs/JobStepper";
import { LiquidButton } from "@/components/liquid/LiquidButton";
import { LiquidCard } from "@/components/liquid/LiquidCard";
import { LiquidChip } from "@/components/liquid/LiquidChip";
import { apiErrorMessage, createJob, getJob, getRouting } from "@/lib/api";
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
      setError(apiErrorMessage(err, "The production API demo is temporarily unavailable."));
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
    <LiquidCard className="w-full max-w-md" id="demo">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="chart-label text-gold">Production API demo</p>
          <h2 className="mt-1.5 text-lg font-semibold text-cream">
            Task the network
          </h2>
        </div>
        <div className="liquid-glass liquid-glass--inset !rounded-full">
          <span className="flex items-center gap-2 px-3 py-1.5">
            <span className="pulse-dot bg-[#8fd6ab]" />
            <span className="chart-label text-muted">shared queue</span>
          </span>
        </div>
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
                  <LiquidChip
                    active={jobType === value}
                    key={value}
                    onClick={() => setJobType(value)}
                  >
                    {labelize(value)}
                  </LiquidChip>
                ))}
              </div>
            </div>

            <div className="mt-5">
              <p className="chart-label text-muted">Priority</p>
              <div className="mt-2.5 flex flex-wrap gap-2">
                {priorities.map((value) => (
                  <LiquidChip
                    active={priority === value}
                    key={value}
                    onClick={() => setPriority(value)}
                  >
                    {labelize(value)}
                  </LiquidChip>
                ))}
              </div>
            </div>

            <LiquidCard className="mt-5" inset>
              <p className="chart-label text-muted-dark">Scene</p>
              <p className="metric-value mt-1 text-sm text-cream/90">
                SAR · New York Harbor · bbox −74.3, 40.3, −73.5, 41.0
              </p>
            </LiquidCard>

            {error ? (
              <p className="mt-4 rounded-xl border border-[#be543c]/40 bg-[#be543c]/10 px-4 py-3 text-sm text-[#e8a08e]">
                {error}
              </p>
            ) : null}

            <div className="mt-6">
              <LiquidButton
                disabled={submitting}
                fullWidth
                onClick={handleRun}
                variant="primary"
              >
                {submitting ? (
                  <Loader2 className="animate-spin" size={18} strokeWidth={2} />
                ) : null}
                Run demo job
                {!submitting ? <ArrowRight size={17} strokeWidth={2} /> : null}
              </LiquidButton>
            </div>
            <p className="mt-3 text-center text-xs text-muted-dark">
              No account needed. Real API and orbital math, simulated execution.
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
              <LiquidButton className="flex-1" href={`/jobs/${job.id}`} variant="primary">
                Open mission view
                <ArrowRight size={15} strokeWidth={2} />
              </LiquidButton>
              <LiquidButton className="!px-3" onClick={reset} variant="outline">
                <RotateCcw size={16} strokeWidth={2} />
              </LiquidButton>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </LiquidCard>
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
    <div className="flex items-center justify-between gap-4 border-b border-white/8 pb-2">
      <span className="chart-label text-muted-dark">{label}</span>
      <span
        className={`metric-value text-sm ${accent ? "text-gold-bright" : "text-cream/90"}`}
      >
        {value}
      </span>
    </div>
  );
}
