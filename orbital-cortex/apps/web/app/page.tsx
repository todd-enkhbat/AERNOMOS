import dynamic from "next/dynamic";
import Link from "next/link";

import { NomosMark } from "@/components/brand/NomosMark";
import { FadeIn } from "@/components/motion/primitives";
import { LiquidButton, LiquidCard, LiquidSection } from "@/components/liquid";

const OrbitalScene = dynamic(
  () => import("@/components/orbital/OrbitalScene"),
  {
    ssr: false,
    loading: () => (
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_70%_45%,rgba(201,162,39,0.1),transparent_35%)]" />
    )
  }
);

const steps = [
  {
    step: "01",
    title: "Describe the mission",
    detail:
      "Tell Nomos what you need: objective, area, timing, and constraints in plain language."
  },
  {
    step: "02",
    title: "Nomos evaluates real data and infrastructure",
    detail:
      "It searches public catalogs, calculates contact opportunities, and compares feasible routes."
  },
  {
    step: "03",
    title: "Receive a traceable recommended plan",
    detail:
      "You get a technical mission brief with sources, assumptions, and labeled gaps."
  }
];

const doesToday = [
  "Searches real public data catalogs",
  "Calculates satellite and ground contact opportunities",
  "Compares feasible infrastructure routes",
  "Labels assumptions and unavailable integrations",
  "Generates a technical mission brief"
];

const requiresProvider = [
  "Satellite tasking",
  "Ground-station reservation",
  "Onboard execution",
  "Private telemetry",
  "Commercial pricing guarantees"
];

export default function HomePage() {
  return (
    <div className="relative pb-6">
      <LiquidSection className="relative overflow-hidden">
        <OrbitalScene className="pointer-events-none absolute inset-0 -top-16 h-[calc(100%+4rem)] w-full opacity-40" />
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,rgba(5,5,6,0.88)_0%,rgba(5,5,6,0.72)_42%,rgba(5,5,6,0.35)_70%,rgba(5,5,6,0.2)_100%)]"
        />
        <div className="page-shell relative">
          <div className="flex min-h-[min(78vh,720px)] flex-col justify-center py-14 lg:py-16">
            <FadeIn>
              <p className="chart-label flex items-center gap-2 text-silver">
                <NomosMark size={20} />
                Nomos Orbital
              </p>
            </FadeIn>
            <FadeIn delay={0.06}>
              <h1 className="display mt-5 max-w-3xl text-[2.15rem] leading-[1.08] text-cream sm:text-5xl lg:text-[3.35rem]">
                Plan how your space-data workload should move across satellite,
                ground, and cloud infrastructure.
              </h1>
            </FadeIn>
            <FadeIn delay={0.12}>
              <p className="prose-compact mt-5 max-w-xl text-silver">
                Describe your mission and constraints. Nomos generates a
                source-backed execution plan using real orbital and
                infrastructure data.
              </p>
            </FadeIn>
            <FadeIn delay={0.18}>
              <div className="mt-7 flex flex-wrap items-center gap-3">
                <LiquidButton href="/plan" variant="primary">
                  Build a mission plan
                </LiquidButton>
                <LiquidButton href="/examples" variant="ghost">
                  View example plan →
                </LiquidButton>
              </div>
            </FadeIn>
          </div>
        </div>
      </LiquidSection>

      <LiquidSection className="mt-4 page-shell">
        <FadeIn>
          <p className="chart-label text-gold">How it works</p>
          <h2 className="display mt-2 max-w-2xl text-2xl text-cream sm:text-3xl">
            Three steps to a recommended plan
          </h2>
        </FadeIn>
        <div className="mt-8 grid gap-4 md:grid-cols-3">
          {steps.map((item, index) => (
            <FadeIn delay={0.04 * index} key={item.step}>
              <LiquidCard className="h-full">
                <p className="metric-value text-[11px] text-gold">{item.step}</p>
                <h3 className="mt-2 text-base font-medium text-cream">{item.title}</h3>
                <p className="mt-3 text-sm leading-6 text-muted">{item.detail}</p>
              </LiquidCard>
            </FadeIn>
          ))}
        </div>
      </LiquidSection>

      <LiquidSection className="section-gap page-shell">
        <div className="grid gap-6 lg:grid-cols-2">
          <FadeIn>
            <LiquidCard className="h-full">
              <p className="chart-label text-gold">Capability boundary</p>
              <h2 className="display mt-2 text-2xl text-cream sm:text-3xl">
                What Nomos does today
              </h2>
              <p className="prose-compact mt-3 text-muted">
                Planning and provenance are live. Execution against commercial
                providers is not claimed until those integrations exist.
              </p>
              <ul className="mt-6 space-y-3">
                {doesToday.map((item) => (
                  <li className="flex gap-3 text-sm leading-6 text-cream/90" key={item}>
                    <span aria-hidden className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-gold" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </LiquidCard>
          </FadeIn>
          <FadeIn delay={0.06}>
            <LiquidCard className="h-full">
              <p className="chart-label text-silver">Not yet connected</p>
              <h2 className="display mt-2 text-2xl text-cream sm:text-3xl">
                What requires provider integration
              </h2>
              <p className="prose-compact mt-3 text-muted">
                These capabilities need live provider APIs. Nomos labels them
                honestly on every plan instead of inventing results.
              </p>
              <ul className="mt-6 space-y-3">
                {requiresProvider.map((item) => (
                  <li className="flex gap-3 text-sm leading-6 text-cream/90" key={item}>
                    <span aria-hidden className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-silver/70" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </LiquidCard>
          </FadeIn>
        </div>
      </LiquidSection>

      <LiquidSection className="page-shell pb-8">
        <FadeIn>
          <div className="border-t border-gold/12 pt-8">
            <p className="chart-label text-silver">Also available</p>
            <h2 className="display mt-2 text-xl text-cream sm:text-2xl">
              Historical simulation demo
            </h2>
            <p className="prose-compact mt-3 max-w-xl text-muted">
              The legacy Job path remains for developers who want to inspect
              routing scores and lifecycle events. Execution and detections are
              SIMULATED. Prefer{" "}
              <Link className="text-gold hover:underline" href="/examples">
                curated example plans
              </Link>{" "}
              for the customer path.
            </p>
            <div className="mt-5 flex flex-wrap gap-3">
              <LiquidButton href="/jobs" variant="outline">
                Open historical simulation demo
              </LiquidButton>
              <LiquidButton href="/docs" variant="ghost">
                API reference →
              </LiquidButton>
            </div>
          </div>
        </FadeIn>
      </LiquidSection>
    </div>
  );
}
