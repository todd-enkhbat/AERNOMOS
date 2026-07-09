"use client";

import { Ship, X } from "lucide-react";

import type { GeoJsonFeature } from "@/lib/types";
import { formatPercent, labelize } from "@/lib/format";

type DetectionPanelProps = {
  feature: GeoJsonFeature | null;
  onClose: () => void;
};

export function DetectionPanel({ feature, onClose }: DetectionPanelProps) {
  if (!feature) {
    return null;
  }

  const props = feature.properties;
  const darkShip = props.dark_ship === true;

  return (
    <aside className="glass-strong absolute bottom-4 left-4 right-4 z-10 max-w-md p-4 md:left-auto">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2">
          <Ship className="text-gold" size={18} strokeWidth={1.8} />
          <h3 className="font-medium text-cream">
            {String(props.detection_id ?? "Detection")}
          </h3>
        </div>
        <button
          aria-label="Close detection panel"
          className="rounded-lg p-1 text-muted transition hover:bg-cream/10 hover:text-cream"
          onClick={onClose}
          type="button"
        >
          <X size={16} />
        </button>
      </div>
      <dl className="mt-3 grid gap-2 text-sm">
        <Row label="Type" value={labelize(String(props.vessel_type ?? props.class ?? "vessel"))} />
        <Row label="Zone" value={String(props.harbor_zone ?? "Harbor")} />
        <Row label="Confidence" value={formatPercent(Number(props.confidence ?? 0))} />
        <Row
          label="AIS status"
          value={darkShip ? "Dark ship (no AIS match)" : "AIS correlated"}
        />
        <Row label="Priority" value={labelize(String(props.priority ?? "monitor"))} />
      </dl>
    </aside>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-4 border-b border-line pb-2">
      <dt className="text-muted-dark">{label}</dt>
      <dd className="font-medium text-cream/90">{value}</dd>
    </div>
  );
}
