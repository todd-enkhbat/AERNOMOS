"use client";

import type { ProvenancedMetric, TruthStatus } from "@/components/truth/types";
import { truthStatusLabel } from "@/components/truth/types";

type TruthBadgeProps = {
  status: TruthStatus | string;
  compact?: boolean;
  className?: string;
};

function toneForStatus(status: string): string {
  switch (status) {
    case "SIMULATED":
    case "ESTIMATED":
      return "truth-badge--assumption";
    case "STALE":
    case "UNAVAILABLE":
      return "truth-badge--warning";
    case "OBSERVED":
    case "CALCULATED":
    case "PROVIDER_REPORTED":
    default:
      return "truth-badge--grounded";
  }
}

export function TruthBadge({ status, compact = false, className = "" }: TruthBadgeProps) {
  return (
    <span
      className={`truth-badge ${toneForStatus(status)} ${compact ? "truth-badge--compact" : ""} ${className}`.trim()}
      title={truthStatusLabel(status)}
    >
      {truthStatusLabel(status)}
    </span>
  );
}

export function TruthBadgeForMetric({
  metric,
  compact,
  className,
}: {
  metric: ProvenancedMetric | null | undefined;
  compact?: boolean;
  className?: string;
}) {
  if (!metric) return null;
  return (
    <TruthBadge
      className={className}
      compact={compact}
      status={metric.truth_status}
    />
  );
}
