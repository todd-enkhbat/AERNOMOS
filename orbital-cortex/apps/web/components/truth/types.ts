import type { components } from "@/lib/generated/api-types";

export type ProvenancedValue = components["schemas"]["ProvenancedValue"];
export type TruthStatus = ProvenancedValue["truth_status"];

export type ProvenancedMetric<T = unknown> = ProvenancedValue & {
  value: T;
};

export function asProvenanced<T>(
  input: T | ProvenancedValue | null | undefined
): ProvenancedMetric<T> | null {
  if (input == null) return null;
  if (typeof input === "object" && input !== null && "truth_status" in input) {
    return input as ProvenancedMetric<T>;
  }
  return {
    value: input as T,
    truth_status: "PROVIDER_REPORTED",
    freshness: "unknown",
  };
}

export function unwrapProvenance<T>(
  input: T | ProvenancedValue | null | undefined
): T | null {
  const provenanced = asProvenanced<T>(input);
  if (!provenanced) return null;
  return provenanced.value as T;
}

export const TRUTH_STATUS_LABELS: Record<TruthStatus, string> = {
  OBSERVED: "Observed",
  CALCULATED: "Calculated",
  PROVIDER_REPORTED: "Provider",
  ESTIMATED: "Estimated",
  SIMULATED: "Simulated",
  STALE: "Stale",
  UNAVAILABLE: "Unavailable",
};

export function truthStatusLabel(status: TruthStatus | string): string {
  return TRUTH_STATUS_LABELS[status as TruthStatus] ?? String(status);
}
