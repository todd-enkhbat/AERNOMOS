import { truthStatusLabel } from "@/components/truth/types";

type FreshnessIndicatorProps = {
  freshness?: string | null;
  className?: string;
};

export function FreshnessIndicator({ freshness, className = "" }: FreshnessIndicatorProps) {
  const value = freshness ?? "unknown";
  const tone =
    value === "fresh"
      ? "freshness-indicator--fresh"
      : value === "stale"
        ? "freshness-indicator--stale"
        : "freshness-indicator--unknown";

  return (
    <span className={`freshness-indicator ${tone} ${className}`.trim()} title={`Data freshness: ${value}`}>
      <span className="freshness-indicator__dot" aria-hidden />
      {value}
    </span>
  );
}

type AssumptionPanelProps = {
  title?: string;
  items: Array<{
    label: string;
    status: string;
    detail?: string;
  }>;
};

export function AssumptionPanel({
  title = "Assumptions & unavailable integrations",
  items,
}: AssumptionPanelProps) {
  if (items.length === 0) return null;

  return (
    <aside className="assumption-panel">
      <p className="chart-label text-gold">{title}</p>
      <ul className="mt-3 space-y-3">
        {items.map((item) => (
          <li className="assumption-panel__item" key={item.label}>
            <div className="flex flex-wrap items-center justify-between gap-2">
              <span className="text-sm text-cream">{item.label}</span>
              <span className="chart-label text-muted">{truthStatusLabel(item.status)}</span>
            </div>
            {item.detail ? (
              <p className="mt-1 text-xs leading-5 text-muted">{item.detail}</p>
            ) : null}
          </li>
        ))}
      </ul>
    </aside>
  );
}
