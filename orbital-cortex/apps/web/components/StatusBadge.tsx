import type { JobStatus } from "@/lib/types";

const statusClass: Record<JobStatus, string> = {
  queued: "border-muted/30 bg-muted/10 text-muted",
  routing: "border-gold/40 bg-gold/10 text-gold-bright",
  executing: "border-silver/30 bg-silver/10 text-silver",
  downlinking: "border-gold/35 bg-gold/10 text-gold-bright",
  complete: "border-[#6fbf8f]/40 bg-[#6fbf8f]/10 text-[#8fd6ab]",
  failed: "border-[#be543c]/40 bg-[#be543c]/10 text-[#e8a08e]"
};

const dotClass: Record<JobStatus, string> = {
  queued: "bg-muted",
  routing: "bg-gold-bright",
  executing: "bg-silver",
  downlinking: "bg-gold-bright",
  complete: "bg-[#6fbf8f]",
  failed: "bg-[#be543c]"
};

export function StatusBadge({ status }: { status: JobStatus }) {
  const live = status !== "complete" && status !== "failed";

  return (
    <span
      className={`inline-flex min-w-[96px] items-center justify-center gap-2 rounded-full border px-3 py-1 text-[11px] font-semibold uppercase tracking-wider ${statusClass[status]}`}
    >
      <span className={`${live ? "pulse-dot" : "h-1.5 w-1.5 rounded-full"} ${dotClass[status]}`} />
      {status}
    </span>
  );
}
