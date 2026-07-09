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
    <div className="flex flex-col gap-3 py-7 md:flex-row md:items-end md:justify-between">
      <div className="max-w-2xl">
        {eyebrow ? <p className="chart-label mb-2 text-gold">{eyebrow}</p> : null}
        <h1 className="display text-3xl leading-tight text-cream md:text-4xl">
          {title}
        </h1>
        {description ? (
          <p className="prose-compact mt-2 max-w-xl text-muted">{description}</p>
        ) : null}
      </div>
      {action ? <div className="shrink-0">{action}</div> : null}
    </div>
  );
}
