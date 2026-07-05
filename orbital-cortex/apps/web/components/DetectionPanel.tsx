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
    <aside className="panel absolute bottom-4 left-4 right-4 z-10 max-w-md p-4 shadow-lg md:left-auto">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2">
          <Ship className="text-[#25495a]" size={18} strokeWidth={1.8} />
          <h3 className="font-bold text-[#17140f]">
            {String(props.detection_id ?? "Detection")}
          </h3>
        </div>
        <button
          aria-label="Close detection panel"
          className="rounded-lg p-1 text-[#6f604c] hover:bg-[#eadcc8]"
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
    <div className="flex justify-between gap-4 border-b border-[rgba(86,67,42,0.12)] pb-2">
      <dt className="text-[#6f604c]">{label}</dt>
      <dd className="font-bold text-[#17140f]">{value}</dd>
    </div>
  );
}
