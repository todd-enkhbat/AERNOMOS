import Image from "next/image";
import Link from "next/link";

import { NomosMark } from "@/components/brand/NomosMark";
import { FadeIn } from "@/components/motion/primitives";
import { LiquidButton, LiquidCard, LiquidSection } from "@/components/liquid";

const bespokeChain = [
  "Request",
  "Satellite operator",
  "Flight constraints",
  "Ground provider",
  "Data transfer",
  "Compute environment",
  "Custom pipeline",
  "Result"
];

const nomosChain = ["Request", "Nomos", "Best available path", "Result"];

const loopSteps = [
  {
    step: "01",
    title: "Express the outcome",
    detail:
      "Describe what you need: objective, area, timing, constraints. Not which satellite, which antenna, which cluster.",
    status: null
  },
  {
    step: "02",
    title: "Understand the environment",
    detail:
      "Nomos evaluates orbital geometry, public catalogs, contact opportunities, and the infrastructure represented in the system.",
    status: null
  },
  {
    step: "03",
    title: "Determine the path",
    detail:
      "Nomos compares feasible ways to fulfill the request and explains why a path was selected, with sources and assumptions attached.",
    status: null
  },
  {
    step: "04",
    title: "Execute across the network",
    detail:
      "As providers integrate, recommendations become execution: tasking, downlink, and compute coordinated through one interface.",
    status: "Planned · requires integrations"
  }
];

const availableNow = [
  {
    title: "Intelligence",
    detail: "Search and reason over real public datasets and infrastructure references."
  },
  {
    title: "Orbital geometry",
    detail: "Contact opportunities calculated from real orbital data."
  },
  {
    title: "Routing",
    detail: "Feasible satellite, ground, and cloud processing paths compared and ranked."
  },
  {
    title: "Provenance",
    detail: "Sources, assumptions, constraints, and reasoning exposed on every result."
  },
  {
    title: "Simulation",
    detail:
      "Execution behavior explored with clearly labeled simulated candidates where live integrations do not exist yet."
  }
];

const withIntegrations = [
  "Satellite tasking",
  "Ground-station reservation",
  "Onboard workload execution",
  "Private telemetry",
  "Live commercial availability and pricing",
  "Automated multi-provider execution"
];

const statusKey = [
  { label: "Live", detail: "Working in the product now, on real data." },
  { label: "Reference", detail: "Real public facts represented in the registry, with citations." },
  { label: "Simulated", detail: "Modeled behavior, always labeled as such." },
  { label: "Planned", detail: "Requires provider integration. Never claimed early." }
];

const surfaces = [
  {
    href: "/plan",
    label: "Run a request",
    detail:
      "Describe an objective. Nomos evaluates orbital, data, ground, and compute paths and explains its recommendation."
  },
  {
    href: "/examples",
    label: "Example requests",
    detail:
      "Curated requests with every step labeled: real, calculated, estimated, simulated, or unavailable."
  },
  {
    href: "/network",
    label: "See the network",
    detail:
      "The orbital, ground, and cloud resources Nomos reasons across, with live pass calculations."
  }
];

const progression = [
  { phase: "Understand", now: true },
  { phase: "Recommend", now: true },
  { phase: "Route", now: true },
  { phase: "Orchestrate", now: false },
  { phase: "Execute", now: false }
];

function ChainColumn({
  label,
  items,
  highlight
}: {
  label: string;
  items: string[];
  highlight?: boolean;
}) {
  return (
    <div
      className={[
        "rounded-2xl border p-5 sm:p-6",
        highlight
          ? "border-gold/35 bg-gold/[0.05]"
          : "border-white/10 bg-klein-void/40"
      ].join(" ")}
    >
      <p className={`chart-label ${highlight ? "text-gold" : "text-muted-dark"}`}>
        {label}
      </p>
      <ol className="mt-4 flex flex-col items-start gap-1">
        {items.map((item, index) => (
          <li className="flex flex-col items-start gap-1" key={item}>
            {index > 0 ? (
              <span
                aria-hidden
                className={`ml-3 text-xs leading-none ${
                  highlight ? "text-gold/70" : "text-muted-dark/70"
                }`}
              >
                ↓
              </span>
            ) : null}
            <span
              className={[
                "metric-value rounded-lg border px-2.5 py-1 text-[11px] tracking-[0.08em]",
                item === "Nomos"
                  ? "border-gold/60 bg-gold/15 text-gold-bright"
                  : highlight
                    ? "border-gold/25 text-cream/90"
                    : "border-white/10 text-muted"
              ].join(" ")}
            >
              {item.toUpperCase()}
            </span>
          </li>
        ))}
      </ol>
      <p
        className={`mt-4 text-xs leading-5 ${
          highlight ? "text-cream/70" : "text-muted-dark"
        }`}
      >
        {highlight
          ? "Nomos absorbs the coordination. The request stays simple."
          : "Rebuilt by every team, for every mission."}
      </p>
    </div>
  );
}

function LayerCard({
  name,
  detail
}: {
  name: string;
  detail: string;
}) {
  return (
    <div className="rounded-xl border border-gold/20 bg-klein-void/55 px-2 py-3 text-center sm:px-4 sm:py-4">
      <p className="metric-value text-[10px] tracking-[0.14em] text-gold-bright sm:text-[11px]">
        {name}
      </p>
      <p className="mt-1.5 hidden text-[11px] leading-4 text-muted sm:block">{detail}</p>
    </div>
  );
}

function NetworkDiagram() {
  return (
    <div aria-label="One request enters Nomos. Nomos routes it across orbital nodes, ground networks, and cloud compute, and returns a result." role="img">
      <div className="mx-auto max-w-2xl">
        <div className="mx-auto w-fit rounded-full border border-white/20 bg-klein-void/60 px-4 py-1.5">
          <p className="metric-value text-[11px] tracking-[0.14em] text-cream">
            ONE REQUEST
          </p>
        </div>

        <svg
          aria-hidden
          className="mx-auto block h-8 w-0.5"
          preserveAspectRatio="none"
          viewBox="0 0 2 32"
        >
          <path d="M1 0 V32" fill="none" stroke="rgba(201,162,39,0.35)" strokeWidth="1" vectorEffect="non-scaling-stroke" />
          <path className="route-flow" d="M1 0 V32" fill="none" stroke="#e3c05c" strokeWidth="1.5" vectorEffect="non-scaling-stroke" />
        </svg>

        <div className="mx-auto w-fit rounded-2xl border border-gold/45 bg-gold/[0.07] px-6 py-3.5 text-center">
          <p className="display text-lg leading-none text-cream sm:text-xl">Nomos</p>
          <p className="metric-value mt-1.5 text-[10px] tracking-[0.16em] text-gold">
            INTELLIGENCE · ROUTING
          </p>
        </div>

        <svg
          aria-hidden
          className="block h-10 w-full"
          preserveAspectRatio="none"
          viewBox="0 0 100 40"
        >
          <path
            d="M50 0 L16.7 40 M50 0 V40 M50 0 L83.3 40"
            fill="none"
            stroke="rgba(201,162,39,0.3)"
            strokeWidth="1"
            vectorEffect="non-scaling-stroke"
          />
          <path
            className="route-flow"
            d="M50 0 L16.7 40"
            fill="none"
            stroke="#e3c05c"
            strokeWidth="1.5"
            vectorEffect="non-scaling-stroke"
          />
        </svg>

        <div className="grid grid-cols-3 gap-2 sm:gap-4">
          <LayerCard detail="Spacecraft, payloads, onboard compute" name="ORBITAL NODES" />
          <LayerCard detail="Stations, comms, terrestrial edge" name="GROUND NETWORKS" />
          <LayerCard detail="Elastic processing, storage, models" name="CLOUD COMPUTE" />
        </div>

        <svg
          aria-hidden
          className="block h-10 w-full"
          preserveAspectRatio="none"
          viewBox="0 0 100 40"
        >
          <path
            d="M16.7 0 L50 40 M50 0 V40 M83.3 0 L50 40"
            fill="none"
            stroke="rgba(201,162,39,0.3)"
            strokeWidth="1"
            vectorEffect="non-scaling-stroke"
          />
          <path
            className="route-flow route-flow--late"
            d="M83.3 0 L50 40"
            fill="none"
            stroke="#e3c05c"
            strokeWidth="1.5"
            vectorEffect="non-scaling-stroke"
          />
        </svg>

        <div className="mx-auto w-fit rounded-full border border-gold/40 bg-gold/10 px-4 py-1.5">
          <p className="metric-value text-[11px] tracking-[0.14em] text-gold-bright">
            RESULT
          </p>
        </div>
      </div>
    </div>
  );
}

export default function HomePage() {
  return (
    <div className="relative pb-6">
      <section className="philosophy-hero relative overflow-hidden">
        <div className="philosophy-hero__media" aria-hidden>
          <Image
            alt=""
            className="object-cover object-center"
            fill
            priority
            sizes="100vw"
            src="/images/irosa-solar-array-hero.jpg"
            unoptimized
          />
        </div>
        <div aria-hidden className="philosophy-hero__scrim" />
        <div aria-hidden className="philosophy-hero__grain" />
        <div aria-hidden className="philosophy-hero__bridge" />

        <div className="page-shell relative z-[1]">
          <div className="philosophy-hero__stage">
            <div className="philosophy-hero__portal">
              <div className="philosophy-hero__copy">
                <FadeIn when="mount">
                  <p className="chart-label flex items-center justify-center gap-2 text-gold-bright">
                    <NomosMark size={16} />
                    Space intelligence infrastructure
                  </p>
                </FadeIn>
                <FadeIn delay={0.06} when="mount">
                  <h1 className="philosophy-hero__headline display mt-2.5 text-cream">
                    The intelligence layer for space.
                  </h1>
                </FadeIn>
                <FadeIn delay={0.12} when="mount">
                  <p className="philosophy-hero__lede prose-compact mx-auto mt-2.5 text-cream/88">
                    Tell the network what you need. Nomos determines how
                    satellites, ground systems, and cloud compute deliver it.
                  </p>
                </FadeIn>
                <FadeIn delay={0.18} when="mount">
                  <div className="philosophy-hero__actions">
                    <LiquidButton
                      className="philosophy-hero__cta"
                      href="/plan"
                      variant="primary"
                    >
                      Run a request
                    </LiquidButton>
                    <LiquidButton
                      className="philosophy-hero__cta"
                      href="/network"
                      variant="ghost"
                    >
                      See the network →
                    </LiquidButton>
                  </div>
                </FadeIn>
                <FadeIn delay={0.24} when="mount">
                  <p className="metric-value mt-3 text-[10px] tracking-[0.14em] text-cream/60">
                    EARLY ACCESS · LIVE DEMO
                  </p>
                </FadeIn>
              </div>
            </div>
          </div>
        </div>
      </section>

      <LiquidSection className="home-band page-shell" orbs={false}>
        <FadeIn viewportMargin="0px" y={6}>
          <p className="chart-label text-gold">The problem</p>
          <h2 className="display mt-2 max-w-2xl text-2xl text-cream sm:text-3xl">
            Space is powerful. Access to it is still bespoke.
          </h2>
          <p className="prose-compact mt-3 max-w-2xl text-muted">
            Using space capability today means coordinating separate operators,
            spacecraft, ground networks, compute environments, APIs, and
            constraints by hand. Every team rebuilds the same integration work.
            Nomos is building the abstraction above it.
          </p>
        </FadeIn>
        <div className="mt-7 grid gap-4 md:grid-cols-2">
          <FadeIn viewportMargin="0px" y={6}>
            <ChainColumn items={bespokeChain} label="Today" />
          </FadeIn>
          <FadeIn delay={0.05} viewportMargin="0px" y={6}>
            <ChainColumn highlight items={nomosChain} label="With Nomos" />
          </FadeIn>
        </div>
      </LiquidSection>

      <LiquidSection className="home-band page-shell" orbs={false}>
        <FadeIn viewportMargin="0px" y={6}>
          <p className="chart-label text-gold">The network</p>
          <h2 className="display mt-2 max-w-2xl text-2xl text-cream sm:text-3xl">
            Different infrastructure. One interface.
          </h2>
          <p className="prose-compact mt-3 max-w-2xl text-muted">
            Nomos does not replace satellites, ground stations, or clouds. It
            sits above them: an intelligence layer that reasons across orbital,
            ground, and cloud resources and determines which of them should
            take part in fulfilling each request.
          </p>
        </FadeIn>
        <FadeIn delay={0.05} viewportMargin="0px" y={6}>
          <div className="mt-8">
            <NetworkDiagram />
          </div>
        </FadeIn>
        <FadeIn delay={0.08} viewportMargin="0px" y={6}>
          <p className="display mx-auto mt-8 max-w-xl text-center text-lg italic text-cream/85 sm:text-xl">
            The infrastructure can stay heterogeneous. Access to it should not.
          </p>
        </FadeIn>
      </LiquidSection>

      <LiquidSection className="home-band page-shell" orbs={false}>
        <FadeIn viewportMargin="0px" y={6}>
          <p className="chart-label text-gold">How it works</p>
          <h2 className="display mt-2 max-w-2xl text-2xl text-cream sm:text-3xl">
            The intelligence loop
          </h2>
        </FadeIn>
        <div className="mt-7 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {loopSteps.map((item, index) => (
            <FadeIn
              delay={0.04 * index}
              key={item.step}
              viewportMargin="0px"
              y={6}
            >
              <LiquidCard className="h-full">
                <div className="flex items-center justify-between gap-2">
                  <p className="metric-value text-[11px] text-gold">{item.step}</p>
                  {item.status ? (
                    <span className="truth-badge truth-badge--assumption truth-badge--compact">
                      {item.status}
                    </span>
                  ) : null}
                </div>
                <h3 className="mt-2 text-base font-medium text-cream">
                  {item.title}
                </h3>
                <p className="mt-3 text-sm leading-6 text-muted">{item.detail}</p>
              </LiquidCard>
            </FadeIn>
          ))}
        </div>
      </LiquidSection>

      <section className="klein-parchment-band home-band relative overflow-hidden">
        <div aria-hidden className="klein-parchment-band__grain" />
        <div className="page-shell relative py-10 md:py-12">
          <FadeIn viewportMargin="0px" y={6}>
            <p className="chart-label text-parchment-muted">Product maturity</p>
            <h2 className="display mt-2 max-w-2xl text-2xl text-parchment-ink sm:text-3xl">
              What exists today
            </h2>
            <p className="prose-compact mt-3 max-w-2xl text-parchment-muted">
              The intelligence layer ships first. Execution arrives with
              integrations. The distinction is labeled everywhere it matters.
            </p>
          </FadeIn>
          <div className="mt-7 grid gap-5 lg:grid-cols-2">
            <FadeIn viewportMargin="0px" y={6}>
              <div className="klein-parchment-band__plate h-full">
                <p className="chart-label text-brass">Available now</p>
                <ul className="mt-4 space-y-4">
                  {availableNow.map((item) => (
                    <li className="flex gap-3" key={item.title}>
                      <span
                        aria-hidden
                        className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-brass"
                      />
                      <div>
                        <p className="text-sm font-medium text-parchment-ink">
                          {item.title}
                        </p>
                        <p className="mt-0.5 text-sm leading-6 text-parchment-ink/75">
                          {item.detail}
                        </p>
                      </div>
                    </li>
                  ))}
                </ul>
                <div className="mt-6">
                  <Link
                    className="text-sm text-brass hover:underline"
                    href="/capabilities"
                  >
                    Full capability map →
                  </Link>
                </div>
              </div>
            </FadeIn>
            <FadeIn delay={0.05} viewportMargin="0px" y={6}>
              <div className="klein-parchment-band__plate klein-parchment-band__plate--quiet h-full">
                <p className="chart-label text-parchment-muted">
                  Coming with network integrations
                </p>
                <p className="prose-compact mt-3 text-parchment-muted">
                  These require live provider connections. Nomos labels them on
                  every result instead of inventing them.
                </p>
                <ul className="mt-5 space-y-3">
                  {withIntegrations.map((item) => (
                    <li
                      className="flex gap-3 text-sm leading-6 text-parchment-ink/80"
                      key={item}
                    >
                      <span
                        aria-hidden
                        className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-parchment-muted/60"
                      />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </FadeIn>
          </div>
          <FadeIn delay={0.08} viewportMargin="0px" y={6}>
            <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              {statusKey.map((item) => (
                <div className="flex items-baseline gap-2.5" key={item.label}>
                  <span className="metric-value shrink-0 text-[10px] tracking-[0.14em] text-brass">
                    {item.label.toUpperCase()}
                  </span>
                  <span className="text-xs leading-5 text-parchment-muted">
                    {item.detail}
                  </span>
                </div>
              ))}
            </div>
          </FadeIn>
        </div>
      </section>

      <LiquidSection className="home-band page-shell" orbs={false}>
        <FadeIn viewportMargin="0px" y={6}>
          <p className="chart-label text-gold">Product</p>
          <h2 className="display mt-2 max-w-2xl text-2xl text-cream sm:text-3xl">
            Put a request through the network.
          </h2>
        </FadeIn>
        <div className="mt-7 grid gap-4 md:grid-cols-3">
          {surfaces.map((item, index) => (
            <FadeIn delay={0.04 * index} key={item.href} viewportMargin="0px" y={6}>
              <Link className="block h-full" href={item.href}>
                <LiquidCard className="h-full">
                  <h3 className="text-base font-medium text-cream">
                    {item.label} <span aria-hidden>→</span>
                  </h3>
                  <p className="mt-3 text-sm leading-6 text-muted">{item.detail}</p>
                </LiquidCard>
              </Link>
            </FadeIn>
          ))}
        </div>
        <FadeIn delay={0.1} viewportMargin="0px" y={6}>
          <p className="mt-6 max-w-2xl text-xs leading-5 text-muted-dark">
            Developers: the{" "}
            <Link className="text-gold hover:underline" href="/docs">
              API reference
            </Link>{" "}
            covers the request contract. The legacy{" "}
            <Link className="text-gold hover:underline" href="/jobs">
              historical simulation demo
            </Link>{" "}
            remains available with SIMULATED execution, clearly labeled.
          </p>
        </FadeIn>
      </LiquidSection>

      <LiquidSection className="home-band page-shell pb-8" orbs={false}>
        <FadeIn viewportMargin="0px" y={6}>
          <div className="border-t border-gold/12 pt-8">
            <p className="chart-label text-silver">Where this goes</p>
            <h2 className="display mt-2 max-w-2xl text-2xl text-cream sm:text-3xl">
              One request. The whole space stack.
            </h2>
            <p className="prose-compact mt-3 max-w-2xl text-muted">
              Today, Nomos determines how a space-data workload could move
              through available infrastructure, and shows its reasoning. As
              providers integrate, those decisions become execution. The end
              state is simple: space becomes callable.
            </p>
          </div>
        </FadeIn>
        <FadeIn delay={0.05} viewportMargin="0px" y={6}>
          <div className="mt-7 flex flex-wrap items-center gap-x-3 gap-y-4">
            {progression.map((item, index) => (
              <div className="flex items-center gap-3" key={item.phase}>
                {index > 0 ? (
                  <span aria-hidden className="text-muted-dark">
                    →
                  </span>
                ) : null}
                <div>
                  <p
                    className={`metric-value text-[11px] tracking-[0.14em] ${
                      item.now ? "text-gold-bright" : "text-muted-dark"
                    }`}
                  >
                    {item.phase.toUpperCase()}
                  </p>
                  <p className="mt-1 text-[10px] leading-none text-muted-dark">
                    {item.now ? "today" : "with integrations"}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </FadeIn>
        <FadeIn delay={0.08} viewportMargin="0px" y={6}>
          <div className="mt-7 flex flex-wrap gap-3">
            <LiquidButton href="/plan" variant="primary">
              Run a request
            </LiquidButton>
            <LiquidButton href="/about" variant="ghost">
              Why we exist →
            </LiquidButton>
          </div>
        </FadeIn>
      </LiquidSection>
    </div>
  );
}
