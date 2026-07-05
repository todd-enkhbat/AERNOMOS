import type { JobStatus } from "@/lib/types";

const statusClass: Record<JobStatus, string> = {
  queued: "border-[#a86f35]/30 bg-[#a86f35]/10 text-[#6f4d2e]",
  routing: "border-[#25495a]/30 bg-[#25495a]/10 text-[#25495a]",
  executing: "border-[#68735d]/30 bg-[#68735d]/10 text-[#4d5a45]",
  downlinking: "border-[#25495a]/30 bg-[#25495a]/10 text-[#1f3d4d]",
  complete: "border-[#68735d]/30 bg-[#68735d]/10 text-[#3f5137]",
  failed: "border-[#8c3d2e]/30 bg-[#8c3d2e]/10 text-[#8c3d2e]"
};

export function StatusBadge({ status }: { status: JobStatus }) {
  return (
    <span
      className={`inline-flex min-w-[88px] items-center justify-center rounded-lg border px-2.5 py-1 text-xs font-bold uppercase ${statusClass[status]}`}
    >
      {status}
    </span>
  );
}
