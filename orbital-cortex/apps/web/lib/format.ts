export function formatCurrency(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0
  }).format(value);
}

export function formatMinutes(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "0m";
  }
  return `${Math.round(value)}m`;
}

export function formatPercent(value: number): string {
  return `${Math.round(value * 100)}%`;
}

export function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit"
  }).format(new Date(value));
}

export function labelize(value: string): string {
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}
