"use client";

import {
  AssumptionPanel,
  FreshnessIndicator,
  SourcePopover,
  TruthBadge,
  asProvenanced,
  unwrapProvenance,
  type ProvenancedMetric,
} from "@/components/truth";
import { formatDateTime } from "@/lib/format";
import type { components } from "@/lib/generated/api-types";

type MissionInfrastructure = components["schemas"]["MissionInfrastructureResponse"];

function ProvenancedField({
  label,
  metric,
  format,
}: {
  label: string;
  metric: ProvenancedMetric | null;
  format?: (value: unknown) => string;
}) {
  if (!metric) return null;
  const display = format ? format(metric.value) : String(metric.value ?? "—");
  return (
    <div>
      <dt className="text-muted/80">{label}</dt>
      <dd className="mt-0.5 flex flex-wrap items-center gap-2 text-cream">
        <span>{display}</span>
        <SourcePopover metric={metric} />
      </dd>
    </div>
  );
}

export function MissionInfrastructurePanel({
  infrastructure,
}: {
  infrastructure: MissionInfrastructure;
}) {
  const snapshot = infrastructure.orbital_snapshot;
  const groundStations = infrastructure.ground_stations ?? [];
  const satellites = infrastructure.satellites ?? [];
  const assumptions = groundStations.flatMap((station) => [
    {
      label: `${station.name} latency`,
      status: station.latency_minutes.truth_status,
      detail: station.latency_minutes.explanation ?? undefined,
    },
    {
      label: `${station.name} downlink capacity`,
      status: station.downlink_mbps.truth_status,
      detail: station.downlink_mbps.explanation ?? undefined,
    },
  ]);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center gap-3">
        <TruthBadge status={snapshot.truth_status} />
        <FreshnessIndicator freshness={snapshot.freshness} />
        <span className="metric-value text-xs text-muted">
          TLE snapshot {snapshot.snapshot_id}
        </span>
      </div>

      {satellites.length > 0 ? (
        <div>
          <p className="chart-label text-muted-dark">Mission satellites</p>
          <ul className="mt-3 space-y-4">
            {satellites.map((satellite) => {
              const tleEpoch = asProvenanced(satellite.tle_epoch);
              const downlink = asProvenanced(satellite.downlink_rate_mbps);
              return (
                <li
                  key={satellite.id}
                  className="border-t border-white/10 pt-4 first:border-t-0 first:pt-0"
                >
                  <div className="flex flex-wrap items-baseline justify-between gap-2">
                    <p className="text-sm text-cream">{satellite.name}</p>
                    <TruthBadge compact status={satellite.truth_status} />
                  </div>
                  <dl className="mt-2 grid gap-2 text-xs sm:grid-cols-2">
                    <ProvenancedField label="TLE epoch" metric={tleEpoch} />
                    <ProvenancedField
                      format={(value) => `${value} Mbps`}
                      label="Downlink rate"
                      metric={downlink}
                    />
                  </dl>
                </li>
              );
            })}
          </ul>
        </div>
      ) : (
        <p className="text-sm text-muted">
          No fleet satellites matched this mission yet. Run catalog discovery first.
        </p>
      )}

      {groundStations.length > 0 ? (
        <div>
          <p className="chart-label text-muted-dark">Ground stations</p>
          <ul className="mt-3 space-y-4">
            {groundStations.map((station) => (
              <li
                key={station.id}
                className="border-t border-white/10 pt-4 first:border-t-0 first:pt-0"
              >
                <div className="flex flex-wrap items-baseline justify-between gap-2">
                  <p className="text-sm text-cream">
                    {station.name}
                    <span className="ml-2 text-muted">· {station.location}</span>
                  </p>
                  <TruthBadge compact status={station.coordinate_truth_status} />
                </div>
                <dl className="mt-2 grid gap-2 text-xs sm:grid-cols-2">
                  <ProvenancedField
                    format={(value) => `${value}°`}
                    label="Latitude"
                    metric={asProvenanced(station.latitude)}
                  />
                  <ProvenancedField
                    format={(value) => `${value}°`}
                    label="Longitude"
                    metric={asProvenanced(station.longitude)}
                  />
                  <ProvenancedField
                    format={(value) => `${value} min`}
                    label="Latency"
                    metric={asProvenanced(station.latency_minutes)}
                  />
                  <ProvenancedField
                    format={(value) => `${value} Mbps`}
                    label="Downlink"
                    metric={asProvenanced(station.downlink_mbps)}
                  />
                </dl>
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      {snapshot.retrieved_at ? (
        <p className="text-xs text-muted">
          Orbital data retrieved {formatDateTime(snapshot.retrieved_at)}
        </p>
      ) : null}

      <AssumptionPanel items={assumptions} />
    </div>
  );
}

export { unwrapProvenance };
