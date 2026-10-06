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
    <header className="page-header">
      <div className="page-header__copy">
        {eyebrow ? <p className="chart-label mb-2 text-gold">{eyebrow}</p> : null}
        <h1 className="page-header__title display text-cream">
          {title}
        </h1>
        {description ? (
          <p className="page-header__description prose-compact text-muted">{description}</p>
        ) : null}
      </div>
      {action ? <div className="page-header__action">{action}</div> : null}
    </header>
  );
}
