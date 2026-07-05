import type { ReactNode } from "react";

export function PageHeader({
  eyebrow,
  title,
  description,
  action
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex flex-col gap-5 py-10 md:flex-row md:items-end md:justify-between">
      <div className="max-w-3xl">
        {eyebrow ? (
          <p className="mb-3 text-sm font-bold uppercase text-[#a86f35]">
            {eyebrow}
          </p>
        ) : null}
        <h1 className="text-4xl font-bold leading-tight text-[#17140f] md:text-5xl">
          {title}
        </h1>
        {description ? (
          <p className="mt-4 max-w-2xl text-lg leading-8 text-[#5d5244]">
            {description}
          </p>
        ) : null}
      </div>
      {action ? <div className="shrink-0">{action}</div> : null}
    </div>
  );
}
