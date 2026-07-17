"use client";

import { Loader2 } from "lucide-react";
import { useCallback, useMemo, useState } from "react";

import { LiquidButton } from "@/components/liquid/LiquidButton";
import { LiquidCard } from "@/components/liquid/LiquidCard";
import { TruthBadge, type ProvenancedMetric } from "@/components/truth";
import {
  apiErrorMessage,
  executePlanStep,
  getExecutionStatus,
  type ExecutionResult,
  type ExecutionStatusResponse,
  type MissionPlan,
  type MissionPlanStep,
  type MissionSummary,
} from "@/lib/api";
import { cropBoundsFromMissionAoi } from "@/lib/missionAoi";

const EXECUTABLE_STEP_TYPES = new Set(["cloud_process", "edge_process"]);
const POLL_MS = 500;
const POLL_MAX_MS = 30_000;

type DemoPhase = "idle" | "crop" | "thumbnail" | "done" | "failed";

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

function findExecutableStep(plan: MissionPlan): MissionPlanStep | null {
  const steps = [...(plan.steps ?? [])].sort((a, b) => a.sequence - b.sequence);
  return (
    steps.find(
      (step) =>
        EXECUTABLE_STEP_TYPES.has(step.step_type) &&
        step.feasibility_status === "feasible"
    ) ?? null
  );
}

async function pollUntilSettled(
  missionId: string,
  planId: string,
  externalJobId: string
): Promise<ExecutionStatusResponse> {
  const deadline = Date.now() + POLL_MAX_MS;
  for (;;) {
    const status = await getExecutionStatus(missionId, planId, externalJobId);
    if (status.job.status === "succeeded" || status.job.status === "failed") {
      return status;
    }
    if (Date.now() >= deadline) {
      throw new Error("Execution timed out while waiting for the worker.");
    }
    await new Promise((resolve) => setTimeout(resolve, POLL_MS));
  }
}

function observedMetric(result: ExecutionResult | null | undefined): ProvenancedMetric | null {
  if (!result?.observed) return null;
  const { execution_seconds, output_bytes } = result.observed;
  return {
    value: execution_seconds,
    truth_status: "OBSERVED",
    source: "local-cpu worker",
    method: "Measured transfer + raster execution on ARQ worker",
    explanation: `Output ${formatBytes(output_bytes)} stored in object storage.`,
  };
}

export function ExecutionDemoPanel({
  mission,
  plan,
  canExecute,
  onRefreshPlan,
  onNotice,
}: {
  mission: MissionSummary;
  plan: MissionPlan;
  canExecute: boolean;
  onRefreshPlan: () => Promise<void>;
  onNotice: (message: string | null) => void;
}) {
  const executableStep = useMemo(() => findExecutableStep(plan), [plan]);
  const cropBounds = useMemo(
    () => cropBoundsFromMissionAoi(mission.area_of_interest as Record<string, unknown>),
    [mission.area_of_interest]
  );

  const [phase, setPhase] = useState<DemoPhase>("idle");
  const [error, setError] = useState<string | null>(null);
  const [cropResult, setCropResult] = useState<ExecutionResult | null>(null);
  const [thumbResult, setThumbResult] = useState<ExecutionResult | null>(null);
  const [thumbnailUrl, setThumbnailUrl] = useState<string | null>(null);
  const [estimateSeconds, setEstimateSeconds] = useState<number | null>(null);

  const running = phase === "crop" || phase === "thumbnail";

  const runDemo = useCallback(async () => {
    if (!executableStep || !canExecute) return;
    setError(null);
    onNotice(null);
    setCropResult(null);
    setThumbResult(null);
    setThumbnailUrl(null);
    setEstimateSeconds(null);

    try {
      setPhase("crop");
      const cropSubmit = await executePlanStep(mission.id, plan.id, {
        step_id: executableStep.id,
        task_type: "crop_geotiff",
        input_ref: "fixture:sample.tif",
        params: { bounds: cropBounds },
      });
      setEstimateSeconds(cropSubmit.estimate.estimated_seconds);

      let cropStatus = await pollUntilSettled(
        mission.id,
        plan.id,
        cropSubmit.job.external_job_id
      );
      if (cropStatus.job.status === "failed") {
        throw new Error(cropStatus.job.error || "Crop task failed.");
      }
      if (!cropStatus.result?.output_ref) {
        throw new Error("Crop succeeded but returned no output reference.");
      }
      setCropResult(cropStatus.result);

      setPhase("thumbnail");
      const thumbSubmit = await executePlanStep(mission.id, plan.id, {
        step_id: executableStep.id,
        task_type: "thumbnail",
        input_ref: cropStatus.result.output_ref,
        params: { max_size: 256 },
      });
      cropStatus = await pollUntilSettled(
        mission.id,
        plan.id,
        thumbSubmit.job.external_job_id
      );
      if (cropStatus.job.status === "failed") {
        throw new Error(cropStatus.job.error || "Thumbnail task failed.");
      }
      if (!cropStatus.result) {
        throw new Error("Thumbnail succeeded but returned no result.");
      }
      setThumbResult(cropStatus.result);
      setThumbnailUrl(cropStatus.download_url ?? null);

      setPhase("done");
      await onRefreshPlan();
      onNotice("CPU demo complete — observed metrics recorded on the plan step.");
    } catch (exc) {
      const message = apiErrorMessage(exc, "CPU demo execution failed.");
      setError(message);
      setPhase("failed");
      onNotice(message);
    }
  }, [
    canExecute,
    cropBounds,
    executableStep,
    mission.id,
    onNotice,
    onRefreshPlan,
    plan.id,
  ]);

  if (!executableStep) {
    return null;
  }

  const plannerDuration = executableStep.duration_seconds;
  const observed = thumbResult?.observed ?? cropResult?.observed;

  return (
    <LiquidCard
      className="!border-gold/30 !bg-[radial-gradient(circle_at_100%_0%,rgba(201,162,39,0.12),transparent_42%),rgba(10,10,11,0.72)]"
      interactive={false}
    >
      <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0 flex-1">
          <p className="chart-label text-gold">Real CPU demo · Phase M</p>
          <h3 className="mt-2 font-serif text-2xl tracking-[-0.02em] text-cream">
            Run a measured crop + thumbnail
          </h3>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-muted">
            Triggers a real worker task on{" "}
            <span className="text-silver">{executableStep.title}</span> using a{" "}
            <strong className="font-normal text-cream">fixture GeoTIFF</strong>, not
            your catalog scene. Durations and byte counts are measured and labeled{" "}
            <TruthBadge compact status="OBSERVED" /> — local CPU, $0 estimate.
          </p>

          <dl className="mt-5 grid gap-4 sm:grid-cols-2">
            <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3">
              <dt className="chart-label text-muted-dark">Planner duration</dt>
              <dd className="mt-2 flex flex-wrap items-center gap-2 text-sm text-cream">
                {plannerDuration != null ? `${plannerDuration.toFixed(0)} sec` : "Unavailable"}
                <TruthBadge compact status="ESTIMATED" />
              </dd>
            </div>
            <div className="rounded-xl border border-gold/20 bg-gold/5 p-3">
              <dt className="chart-label text-gold">Observed execution</dt>
              <dd className="mt-2 flex flex-wrap items-center gap-2 text-sm text-cream">
                {observed ? (
                  <>
                    {observed.execution_seconds.toFixed(3)} sec · out{" "}
                    {formatBytes(observed.output_bytes)}
                    <TruthBadge compact status="OBSERVED" />
                  </>
                ) : (
                  <span className="text-muted">Not run yet</span>
                )}
              </dd>
            </div>
          </dl>

          {estimateSeconds != null && phase !== "idle" ? (
            <p className="mt-3 text-xs text-muted">
              Provider estimate before run: {estimateSeconds.toFixed(2)}s · $0.00 (local CPU)
            </p>
          ) : null}

          {error ? (
            <p className="mt-4 rounded-lg border border-vermilion/30 bg-vermilion/10 px-3 py-2 text-sm text-[#e8a08e]">
              {error}
            </p>
          ) : null}

          {canExecute ? (
            <div className="mt-5 flex flex-wrap gap-3">
              <LiquidButton disabled={running} onClick={() => void runDemo()} variant="primary">
                {running ? (
                  <span className="inline-flex items-center gap-2">
                    <Loader2 aria-hidden className="animate-spin" size={16} />
                    {phase === "crop" ? "Measuring crop…" : "Rendering thumbnail…"}
                  </span>
                ) : phase === "done" ? (
                  "Run CPU demo again"
                ) : (
                  "Run CPU demo"
                )}
              </LiquidButton>
            </div>
          ) : (
            <p className="mt-5 text-sm text-muted">
              Execution is owner-only. Share links can view results after a run, but
              cannot start new jobs.
            </p>
          )}
        </div>

        <div className="w-full shrink-0 lg:w-72">
          <div className="overflow-hidden rounded-xl border border-white/10 bg-void/60">
            {thumbnailUrl ? (
              // eslint-disable-next-line @next/next/no-img-element -- signed artifact URL from API
              <img
                alt="Observed PNG thumbnail from the CPU demo crop"
                className="h-auto w-full object-contain"
                height={256}
                loading="lazy"
                src={thumbnailUrl}
                width={256}
              />
            ) : (
              <div className="flex aspect-square items-center justify-center px-4 text-center text-xs leading-5 text-muted">
                {running
                  ? "Worker is processing the fixture raster…"
                  : "Thumbnail appears here after a successful run."}
              </div>
            )}
          </div>
          {thumbResult && observedMetric(thumbResult) ? (
            <p className="mt-2 text-center text-[11px] text-muted">
              OBSERVED · {thumbResult.observed.execution_seconds.toFixed(3)}s execution
            </p>
          ) : null}
        </div>
      </div>
    </LiquidCard>
  );
}
