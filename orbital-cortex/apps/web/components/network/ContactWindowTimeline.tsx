"use client";

import { motion } from "framer-motion";
import { useMemo, useState } from "react";

import type { ContactWindow } from "@/lib/types";
import { formatDateTime } from "@/lib/format";

/**
 * Gantt-style visualization of upcoming satellite-to-ground contact windows.
 * One row per satellite, gold bars for passes, hover/tap reveals details.
 */
export function ContactWindowTimeline({ windows }: { windows: ContactWindow[] }) {
  const [selected, setSelected] = useState<ContactWindow | null>(null);

  const model = useMemo(() => {
    if (windows.length === 0) {
      return null;
    }
    const sorted = [...windows].sort(
      (a, b) => new Date(a.aos_utc).getTime() - new Date(b.aos_utc).getTime()
    );
    const start = new Date(sorted[0].aos_utc).getTime();
    const end = Math.max(
      ...sorted.map((w) => new Date(w.aos_utc).getTime() + w.duration_s * 1000)
    );
    const span = Math.max(end - start, 1);

    const satellites = Array.from(new Set(sorted.map((w) => w.satellite_id)));

    return { sorted, start, span, satellites };
  }, [windows]);

  if (!model) {
    return (
      <p className="text-sm text-muted">
        No upcoming contact windows in the pass cache.
      </p>
    );
  }

  const { sorted, start, span, satellites } = model;

  return (
    <div>
      <div className="space-y-3">
        {satellites.map((satelliteId) => {
          const passes = sorted.filter((w) => w.satellite_id === satelliteId);
          return (
            <div className="flex items-center gap-4" key={satelliteId}>
              <span className="metric-value w-28 shrink-0 truncate text-xs text-muted sm:w-36">
                {satelliteId}
              </span>
              <div className="relative h-7 flex-1 overflow-hidden rounded-lg border border-line bg-void/40">
                {passes.map((pass) => {
                  const left =
                    ((new Date(pass.aos_utc).getTime() - start) / span) * 100;
                  const width = Math.max(
                    ((pass.duration_s * 1000) / span) * 100,
                    0.8
                  );
                  const isSelected = selected?.id === pass.id;
                  return (
                    <motion.button
                      animate={{ opacity: 1, scaleX: 1 }}
                      aria-label={`Pass over ${pass.ground_station_id}`}
                      className={`absolute top-1 h-5 origin-left rounded-md transition-colors ${
                        isSelected
                          ? "bg-gold-bright"
                          : "bg-gold/55 hover:bg-gold"
                      }`}
                      initial={{ opacity: 0, scaleX: 0 }}
                      key={pass.id}
                      onClick={() =>
                        setSelected(isSelected ? null : pass)
                      }
                      style={{ left: `${left}%`, width: `${width}%` }}
                      transition={{ duration: 0.5, ease: [0.32, 0.72, 0, 1] }}
                      type="button"
                    />
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-4 flex items-center justify-between">
        <span className="metric-value text-xs text-muted-dark">
          {formatDateTime(new Date(start).toISOString())}
        </span>
        <span className="metric-value text-xs text-muted-dark">
          {formatDateTime(new Date(start + span).toISOString())}
        </span>
      </div>

      {selected ? (
        <motion.div
          animate={{ opacity: 1, y: 0 }}
          className="mt-4 grid gap-3 rounded-xl border border-gold/25 bg-gold/5 p-4 sm:grid-cols-4"
          initial={{ opacity: 0, y: 8 }}
          transition={{ type: "spring", stiffness: 300, damping: 28 }}
        >
          <Detail label="Satellite" value={selected.satellite_id} />
          <Detail label="Ground station" value={selected.ground_station_id} />
          <Detail
            label="AOS"
            value={formatDateTime(selected.aos_utc)}
          />
          <Detail
            label="Duration · elev"
            value={`${Math.round(selected.duration_s / 60)}m · ${selected.max_elevation_deg.toFixed(0)}°`}
          />
        </motion.div>
      ) : (
        <p className="mt-4 text-xs text-muted-dark">
          Click a pass to inspect it.
        </p>
      )}
    </div>
  );
}

function Detail({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="chart-label text-muted-dark">{label}</p>
      <p className="metric-value mt-1 text-sm text-cream/90">{value}</p>
    </div>
  );
}
