"use client";

import { useState, type ReactNode } from "react";

import type { ProvenancedMetric } from "@/components/truth/types";
import { TruthBadge } from "@/components/truth/TruthBadge";
import { formatDateTime } from "@/lib/format";

type SourcePopoverProps = {
  metric: ProvenancedMetric;
  label?: string;
  children?: ReactNode;
};

export function SourcePopover({ metric, label, children }: SourcePopoverProps) {
  const [open, setOpen] = useState(false);

  return (
    <span
      className="source-popover"
      onBlur={(event) => {
        if (!event.currentTarget.contains(event.relatedTarget as Node | null)) {
          setOpen(false);
        }
      }}
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
    >
      <button
        className="source-popover__trigger"
        onClick={() => setOpen((value) => !value)}
        type="button"
      >
        {children ?? (
          <span className="inline-flex items-center gap-2">
            {label ? <span className="metric-value text-xs text-cream/90">{label}</span> : null}
            <TruthBadge compact status={metric.truth_status} />
          </span>
        )}
      </button>
      {open ? (
        <span className="source-popover__panel" role="tooltip">
          <span className="source-popover__row">
            <span className="chart-label text-muted-dark">Status</span>
            <TruthBadge compact status={metric.truth_status} />
          </span>
          {metric.source ? (
            <span className="source-popover__row">
              <span className="chart-label text-muted-dark">Source</span>
              <span className="text-xs text-cream/90">{metric.source}</span>
            </span>
          ) : null}
          {metric.retrieved_at ? (
            <span className="source-popover__row">
              <span className="chart-label text-muted-dark">Retrieved</span>
              <span className="metric-value text-xs text-cream/90">
                {formatDateTime(metric.retrieved_at)}
              </span>
            </span>
          ) : null}
          {metric.effective_at ? (
            <span className="source-popover__row">
              <span className="chart-label text-muted-dark">Effective</span>
              <span className="metric-value text-xs text-cream/90">
                {formatDateTime(metric.effective_at)}
              </span>
            </span>
          ) : null}
          {metric.method ? (
            <span className="source-popover__row">
              <span className="chart-label text-muted-dark">Method</span>
              <span className="text-xs text-cream/90">{metric.method}</span>
            </span>
          ) : null}
          {metric.explanation ? (
            <p className="mt-2 text-xs leading-5 text-muted">{metric.explanation}</p>
          ) : null}
        </span>
      ) : null}
    </span>
  );
}
