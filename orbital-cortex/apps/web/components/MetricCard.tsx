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
  const dark = tone === "dark";

  return (
    <div className={dark ? "dark-panel p-5" : "panel p-5"}>
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className={dark ? "text-sm text-[#d8cbb8]" : "text-sm text-[#6f604c]"}>
            {label}
          </p>
          <p className="metric-value mt-3 text-3xl font-semibold">{value}</p>
        </div>
        <span
          className={
            dark
              ? "grid h-10 w-10 place-items-center rounded-lg bg-[#fffaf0]/10 text-[#e0b16f]"
              : "grid h-10 w-10 place-items-center rounded-lg bg-[#eadcc8] text-[#25495a]"
          }
        >
          <Icon size={18} strokeWidth={1.8} />
        </span>
      </div>
      {detail ? (
        <p className={dark ? "mt-5 text-sm text-[#d8cbb8]" : "mt-5 text-sm text-[#6f604c]"}>
          {detail}
        </p>
      ) : null}
    </div>
  );
}
