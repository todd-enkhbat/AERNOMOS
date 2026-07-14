import type { ReactNode } from "react";

type ArchiveHeaderProps = {
  index?: string;
  eyebrow: string;
  title: string;
  description?: string;
  action?: ReactNode;
};

export function ArchiveHeader({
  index,
  eyebrow,
  title,
  description,
  action
}: ArchiveHeaderProps) {
  return (
    <header className="archive-header">
      <div className="archive-header__rule" aria-hidden>
        <span>{index ?? "NOMOS"}</span>
        <span>ORBITAL CONTROL PLANE</span>
      </div>
      <div className="archive-header__body">
        <div>
          <p className="chart-label text-gold">{eyebrow}</p>
          <h2 className="display mt-2 max-w-3xl text-2xl leading-tight text-cream sm:text-3xl">
            {title}
          </h2>
          {description ? (
            <p className="prose-compact mt-3 max-w-2xl text-muted">{description}</p>
          ) : null}
        </div>
        {action ? <div className="shrink-0">{action}</div> : null}
      </div>
    </header>
  );
}

type ProvenancePlateProps = {
  label: string;
  value: string;
  detail?: string;
  tone?: "gold" | "cobalt" | "neutral";
};

export function ProvenancePlate({
  label,
  value,
  detail,
  tone = "neutral"
}: ProvenancePlateProps) {
  return (
    <div className={`provenance-plate provenance-plate--${tone}`}>
      <span className="provenance-plate__mark" aria-hidden />
      <div>
        <p className="chart-label text-[0.62rem] text-muted-dark">{label}</p>
        <p className="metric-value mt-1 text-xs text-cream/90">{value}</p>
        {detail ? <p className="mt-1 text-xs leading-5 text-muted">{detail}</p> : null}
      </div>
    </div>
  );
}

export function DemoBoundary({ compact = false }: { compact?: boolean }) {
  return (
    <aside className={`demo-boundary ${compact ? "demo-boundary--compact" : ""}`}>
      <span className="mission-stamp" aria-hidden>
        DEMO
      </span>
      <div>
        <p className="text-sm font-medium text-cream">What is real here</p>
        <p className="mt-1 text-xs leading-5 text-muted">
          Production API and worker. Real SGP4 orbital math over pinned public data.
          Simulated compute execution and offline reference results.
        </p>
      </div>
    </aside>
  );
}

export function CelestialDivider({ label }: { label?: string }) {
  return (
    <div className="celestial-divider" aria-hidden>
      <span />
      <i />
      {label ? <b>{label}</b> : null}
      <i />
      <span />
    </div>
  );
}
