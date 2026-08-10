import type { Metadata } from "next";
import Link from "next/link";

import { NomosMark } from "@/components/brand/NomosMark";
import { FadeIn } from "@/components/motion/primitives";
import { LiquidButton, LiquidCard, LiquidSection } from "@/components/liquid";
import { TruthBadge } from "@/components/truth/TruthBadge";

export const metadata: Metadata = {
  title: "Capabilities",
  description:
    "What Nomos can do today, what still requires provider integration, and the direction ahead. Planning is live. Execution claims stay labeled."
};

type TodayCapability = {
  title: string;
  detail: string;
  mark: { kind: "truth"; status: string } | { kind: "live" };
};

const today: TodayCapability[] = [
  {
    title: "Public catalog search",
    detail:
      "Discover real Sentinel scenes over a drawn area of interest via Microsoft Planetary Computer STAC.",
    mark: { kind: "truth", status: "PROVIDER_REPORTED" }
  },
  {
    title: "Contact opportunity calculation",
    detail:
      "SGP4 / Skyfield pass windows from CelesTrak TLEs, live when fresh and pinned when not.",
    mark: { kind: "truth", status: "CALCULATED" }
  },
  {
    title: "Feasible route comparison",
    detail:
      "Rank satellite, ground, and cloud patterns with explicit feasible, conditional, and rejected plans.",
    mark: { kind: "truth", status: "ESTIMATED" }
  },
  {
    title: "Truth-labeled mission briefs",
    detail:
      "Every headline value carries a truth status. Assumptions and unavailable integrations stay visible.",
    mark: { kind: "live" }
  },
  {
    title: "Private anonymous planning",
    detail:
      "Visitor missions stay in an HttpOnly session. Share links are explicit; missions are not enumerable.",
    mark: { kind: "live" }
  },
  {
    title: "Owner CPU demo",
    detail:
      "Optional fixture GeoTIFF crop and thumbnail on the production worker. Measured durations are observed, not invented.",
    mark: { kind: "truth", status: "OBSERVED" }
  }
];

const requiresProvider = [
  {
    title: "Satellite tasking",
    detail: "Plans that need a tasking API remain conditional until a provider is connected."
  },
  {
    title: "Ground-station reservation",
    detail: "Coordinates may be public. Operational booking is not live."
  },
  {
    title: "Onboard execution",
    detail: "Edge and satellite compute providers are cited from public facts, not claimed as connected."
  },
  {
    title: "Private telemetry",
    detail: "No private fleet feeds. Public TLEs and catalog metadata only."
  },
  {
    title: "Commercial pricing guarantees",
    detail: "Cost fields stay unavailable until a real pricing source exists."
  }
];

const aspire = [
  {
    index: "01",
    title: "Legible orbital decisions",
    detail:
      "Every workload route should remain something a human can direct, audit, and trust as compute moves farther from Earth."
  },
  {
    index: "02",
    title: "Satellites as collaborators",
    detail:
      "Machinery in orbit should become agentic partners on human missions, not opaque schedulers that discard most of what they collect."
  },
  {
    index: "03",
    title: "A planning layer above operators",
    detail:
      "Nomos is not a satellite operator or data reseller. The long product is the verification layer that binds those systems together."
  }
];

const forward = [
  {
    horizon: "Near",
    items: [
      "Provider sandbox and partner connections beyond public-data citations",
      "Live catalog asset download where allowlists and signing permit",
      "Richer ground-track geography when the API can expose coordinates"
    ]
  },
  {
    horizon: "Next",
    items: [
      "Accounts, organizations, and enterprise authentication",
      "Real node adapters for connected cloud and edge providers",
      "Commercial pricing once a verifiable source exists"
    ]
  },
  {
    horizon: "Later",
    items: [
      "Live satellite tasking and station scheduling through partners",
      "Onboard and orbital GPU execution with observed results",
      "Webhooks and cryptographic event signing"
    ]
  }
];

export default function CapabilitiesPage() {
  return (
    <div className="relative pb-6">
      <LiquidSection className="relative overflow-hidden" orbs={false}>
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_78%_18%,rgba(201,162,39,0.1),transparent_42%),radial-gradient(ellipse_at_12%_88%,rgba(0,47,167,0.35),transparent_48%)]"
        />
        <div className="page-shell relative py-10 md:py-12">
          <FadeIn when="mount" y={6}>
            <p className="chart-label flex items-center gap-2 text-gold">
              <NomosMark size={18} />
              Nomos Orbital
            </p>
            <h1 className="display mt-3 max-w-3xl text-3xl leading-[1.08] text-cream sm:text-4xl lg:text-5xl">
              What we can do, what we will not pretend, and where we are going.
            </h1>
            <p className="prose-compact mt-3 max-w-xl text-cream/85">
              Nomos turns a space-data objective into a source-backed
              infrastructure plan. Planning is live. Missing integrations are
              labeled, never invented.
            </p>
            <div className="mt-6 flex flex-wrap items-center gap-3">
              <LiquidButton href="/plan" variant="primary">
                Build a mission plan
              </LiquidButton>
              <LiquidButton href="/examples" variant="ghost">
                View example plan →
              </LiquidButton>
            </div>
          </FadeIn>
        </div>
      </LiquidSection>

      <LiquidSection className="home-band page-shell" orbs={false}>
        <FadeIn viewportMargin="0px" y={6}>
          <div className="flex flex-wrap items-end justify-between gap-4">
            <div>
              <p className="chart-label text-gold">Today</p>
              <h2 className="display mt-2 max-w-2xl text-2xl text-cream sm:text-3xl">
                Live product capabilities
              </h2>
              <p className="prose-compact mt-3 max-w-xl text-muted">
                Safe to claim on customer surfaces. Each capability carries the
                truth class visitors will see on a mission brief.
              </p>
            </div>
            <p className="metric-value text-[11px] text-muted-dark">CAP · 01</p>
          </div>
        </FadeIn>
        <ul className="mt-7 divide-y divide-gold/10 border-y border-gold/10">
          {today.map((item, index) => (
            <FadeIn delay={0.03 * index} key={item.title} viewportMargin="0px" y={6}>
              <li className="grid gap-3 py-5 sm:grid-cols-[minmax(0,1fr)_auto] sm:items-start sm:gap-6">
                <div>
                  <h3 className="text-base font-medium text-cream">{item.title}</h3>
                  <p className="mt-2 max-w-2xl text-sm leading-6 text-muted">
                    {item.detail}
                  </p>
                </div>
                {item.mark.kind === "truth" ? (
                  <TruthBadge className="sm:mt-0.5" compact status={item.mark.status} />
                ) : (
                  <span className="truth-badge truth-badge--grounded truth-badge--compact sm:mt-0.5">
                    Live
                  </span>
                )}
              </li>
            </FadeIn>
          ))}
        </ul>
      </LiquidSection>

      <section className="klein-parchment-band home-band relative overflow-hidden">
        <div aria-hidden className="klein-parchment-band__grain" />
        <div className="page-shell relative py-10 md:py-12">
          <FadeIn viewportMargin="0px" y={6}>
            <div className="flex flex-wrap items-end justify-between gap-4">
              <div>
                <p className="chart-label text-parchment-muted">Boundary</p>
                <h2 className="display mt-2 max-w-2xl text-2xl text-parchment-ink sm:text-3xl">
                  Requires provider integration
                </h2>
                <p className="prose-compact mt-3 max-w-xl text-parchment-muted">
                  These appear on plans as unavailable or conditional. Nomos does
                  not invent tasking, reservations, or prices.
                </p>
              </div>
              <p className="metric-value text-[11px] text-parchment-muted">CAP · 02</p>
            </div>
          </FadeIn>
          <div className="mt-7 grid gap-4 sm:grid-cols-2">
            {requiresProvider.map((item, index) => (
              <FadeIn delay={0.04 * index} key={item.title} viewportMargin="0px" y={6}>
                <div className="klein-parchment-band__plate h-full">
                  <p className="chart-label text-vermilion">Not connected</p>
                  <h3 className="mt-3 text-base font-medium text-parchment-ink">
                    {item.title}
                  </h3>
                  <p className="mt-3 text-sm leading-6 text-parchment-muted">
                    {item.detail}
                  </p>
                </div>
              </FadeIn>
            ))}
          </div>
        </div>
      </section>

      <LiquidSection className="home-band page-shell" orbs={false}>
        <FadeIn viewportMargin="0px" y={6}>
          <div className="flex flex-wrap items-end justify-between gap-4">
            <div>
              <p className="chart-label text-gold">Aspire</p>
              <h2 className="display mt-2 max-w-2xl text-2xl text-cream sm:text-3xl">
                The direction we are building toward
              </h2>
              <p className="prose-compact mt-3 max-w-xl text-muted">
                Aspiration, not a shipped claim. The near-term product earns this
                future by staying useful and honest today.
              </p>
            </div>
            <p className="metric-value text-[11px] text-muted-dark">CAP · 03</p>
          </div>
        </FadeIn>
        <div className="mt-7 space-y-6">
          {aspire.map((item, index) => (
            <FadeIn delay={0.05 * index} key={item.index} viewportMargin="0px" y={6}>
              <div className="grid gap-3 border-l border-gold/25 pl-5 sm:grid-cols-[4rem_minmax(0,1fr)] sm:gap-6">
                <p className="metric-value text-[11px] text-gold">{item.index}</p>
                <div>
                  <h3 className="display text-xl text-cream sm:text-2xl">{item.title}</h3>
                  <p className="prose-compact mt-3 max-w-2xl text-muted">{item.detail}</p>
                </div>
              </div>
            </FadeIn>
          ))}
        </div>
      </LiquidSection>

      <LiquidSection className="home-band page-shell" orbs={false}>
        <FadeIn viewportMargin="0px" y={6}>
          <div className="flex flex-wrap items-end justify-between gap-4">
            <div>
              <p className="chart-label text-cobalt">Forward</p>
              <h2 className="display mt-2 max-w-2xl text-2xl text-cream sm:text-3xl">
                Moving on from here
              </h2>
              <p className="prose-compact mt-3 max-w-xl text-muted">
                Ordered by dependency, not marketing urgency. Nothing below is
                claimed as live until it ships with sources.
              </p>
            </div>
            <p className="metric-value text-[11px] text-muted-dark">CAP · 04</p>
          </div>
        </FadeIn>
        <div className="mt-7 grid gap-4 lg:grid-cols-3">
          {forward.map((column, index) => (
            <FadeIn delay={0.05 * index} key={column.horizon} viewportMargin="0px" y={6}>
              <LiquidCard className="h-full">
                <p className="chart-label text-gold">{column.horizon}</p>
                <ul className="mt-5 space-y-4">
                  {column.items.map((item) => (
                    <li className="flex gap-3 text-sm leading-6 text-cream/90" key={item}>
                      <span
                        aria-hidden
                        className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-gold/70"
                      />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </LiquidCard>
            </FadeIn>
          ))}
        </div>
      </LiquidSection>

      <LiquidSection className="home-band page-shell pb-4" orbs={false}>
        <FadeIn viewportMargin="0px" y={6}>
          <div className="border-t border-gold/12 pt-8">
            <p className="chart-label text-silver">Prove it</p>
            <h2 className="display mt-2 max-w-2xl text-xl text-cream sm:text-2xl">
              See a source-backed plan, or build your own.
            </h2>
            <p className="prose-compact mt-3 max-w-xl text-muted">
              Curated examples disclose what is real, calculated, estimated,
              simulated, and unavailable. The historical job demo remains for
              developers who want routing scores and lifecycle events.
            </p>
            <div className="mt-5 flex flex-wrap gap-3">
              <LiquidButton href="/plan" variant="primary">
                Build a mission plan
              </LiquidButton>
              <LiquidButton href="/examples" variant="outline">
                View example plans
              </LiquidButton>
              <LiquidButton href="/docs" variant="ghost">
                API reference →
              </LiquidButton>
            </div>
            <p className="mt-6 max-w-xl text-xs leading-5 text-muted-dark">
              Prefer the customer path. The{" "}
              <Link className="text-gold hover:underline" href="/jobs">
                historical simulation demo
              </Link>{" "}
              uses a production API with SIMULATED execution and detections.
            </p>
          </div>
        </FadeIn>
      </LiquidSection>
    </div>
  );
}
