import type { LucideIcon } from "lucide-react";

export function MetricCard({
  label,
  value,
  detail,
  icon: Icon,
  tone = "light"
}: {
  label: string;
  value: string;
  detail?: string;
  icon: LucideIcon;
  tone?: "light" | "dark";
}) {
  const highlight = tone === "dark";

  return (
    <div className={`glass glass-hover p-5 ${highlight ? "border-gold/25" : ""}`}>
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="chart-label text-muted">{label}</p>
          <p className="metric-value mt-3 text-3xl font-medium text-cream">
            {value}
          </p>
        </div>
        <span
          className={`grid h-10 w-10 place-items-center rounded-xl border ${
            highlight
              ? "border-gold/30 bg-gold/10 text-gold-bright"
              : "border-line bg-cream/5 text-silver"
          }`}
        >
          <Icon size={18} strokeWidth={1.8} />
        </span>
      </div>
      {detail ? <p className="mt-4 text-sm text-muted-dark">{detail}</p> : null}
    </div>
  );
}
