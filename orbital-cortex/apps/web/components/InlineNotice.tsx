import { AlertCircle } from "lucide-react";

export function InlineNotice({ message }: { message: string }) {
  return (
    <div className="flex items-start gap-3 rounded-lg border border-[#a86f35]/30 bg-[#fff2dd] p-4 text-sm text-[#6f4d2e]">
      <AlertCircle className="mt-0.5 shrink-0" size={17} strokeWidth={1.8} />
      <p>{message}</p>
    </div>
  );
}
