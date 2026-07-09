import { AlertCircle } from "lucide-react";

export function InlineNotice({ message }: { message: string }) {
  return (
    <div className="glass flex items-start gap-3 border-[#be543c]/30 p-4 text-sm text-[#e8a08e]">
      <AlertCircle className="mt-0.5 shrink-0" size={17} strokeWidth={1.8} />
      <p>{message}</p>
    </div>
  );
}
