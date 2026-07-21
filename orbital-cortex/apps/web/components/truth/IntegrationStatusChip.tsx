"use client";

type IntegrationStatusChipProps = {
  status: string | undefined;
  compact?: boolean;
  className?: string;
};

function labelForStatus(status: string): string {
  switch (status) {
    case "public_data_only":
      return "Public source only";
    case "documented_api":
      return "Documented API";
    case "sandbox_requested":
      return "Sandbox requested";
    case "sandbox_connected":
      return "Sandbox connected";
    case "partner_connected":
      return "Partner connected";
    case "simulated":
      return "Simulated provider";
    case "unavailable":
      return "Unavailable";
    default:
      return status.replace(/_/g, " ");
  }
}

function toneForStatus(status: string): string {
  switch (status) {
    case "simulated":
      return "integration-chip--simulated";
    case "sandbox_connected":
    case "partner_connected":
      return "integration-chip--connected";
    case "sandbox_requested":
      return "integration-chip--pending";
    case "public_data_only":
    case "documented_api":
      return "integration-chip--public";
    default:
      return "integration-chip--neutral";
  }
}

export function IntegrationStatusChip({
  status,
  compact = false,
  className = "",
}: IntegrationStatusChipProps) {
  if (!status) return null;
  return (
    <span
      className={`integration-chip ${toneForStatus(status)} ${
        compact ? "integration-chip--compact" : ""
      } ${className}`.trim()}
      title={`Provider integration status: ${labelForStatus(status)}`}
    >
      {labelForStatus(status)}
    </span>
  );
}

export function integrationStatusFromStep(
  sourceMetadata: Record<string, unknown> | undefined
): string | undefined {
  if (!sourceMetadata) return undefined;
  const value = sourceMetadata.integration_status;
  return typeof value === "string" ? value : undefined;
}
