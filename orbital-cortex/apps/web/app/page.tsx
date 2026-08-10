import Image from "next/image";
import Link from "next/link";

import { NomosMark } from "@/components/brand/NomosMark";
import { FadeIn } from "@/components/motion/primitives";
import { LiquidButton, LiquidCard, LiquidSection } from "@/components/liquid";

const steps = [
  {
    step: "01",
    title: "Describe the job",
    detail:
      "Tell Nomos what you need: objective, area, timing, and constraints in plain language."
  },
  {
    step: "02",
    title: "Nomos routes across real infrastructure",
    detail:
      "It searches public catalogs, calculates contact opportunities, and compares feasible routes."
  },
  {
    step: "03",
    title: "Run with a traceable record",
    detail:
      "You get an orchestrated execution path with sources, assumptions, and labeled gaps."
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
      <section className="philosophy-hero relative overflow-hidden">
        <div className="philosophy-hero__media" aria-hidden>
          <Image
            alt=""
            className="object-cover object-center"
            fill
            priority
            sizes="100vw"
            src="/images/orbital-circuit-portal-hero.jpg"
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
                    <NomosMark size={18} />
                    Nomos Orbital
                  </p>
                </FadeIn>
                <FadeIn delay={0.06} when="mount">
                  <h1 className="philosophy-hero__headline display mt-2.5 text-cream">
                    Orchestrate space-data jobs across satellite, ground, and
                    cloud.
                  </h1>
                </FadeIn>
                <FadeIn delay={0.12} when="mount">
                  <p className="philosophy-hero__lede prose-compact mx-auto mt-2.5 text-cream/88">
                    Submit the workload. Nomos routes it under real orbital and
                    infrastructure constraints, then runs it with a source-backed
                    audit trail.
                  </p>
                </FadeIn>
                <FadeIn delay={0.18} when="mount">
                  <div className="philosophy-hero__actions">
                    <LiquidButton
                      className="philosophy-hero__cta"
                      href="/plan"
                      variant="primary"
                    >
                      Orchestrate a job
                    </LiquidButton>
                    <LiquidButton
                      className="philosophy-hero__cta"
                      href="/examples"
                      variant="ghost"
                    >
                      See a run →
                    </LiquidButton>
                  </div>
                </FadeIn>
              </div>
            </div>
          </div>
        </div>
      </section>

      <LiquidSection className="home-band page-shell" orbs={false}>
        <FadeIn viewportMargin="0px" y={6}>
          <p className="chart-label text-gold">How it works</p>
          <h2 className="display mt-2 max-w-2xl text-2xl text-cream sm:text-3xl">
            Three steps to a routed job
          </h2>
        </FadeIn>
        <div className="mt-7 grid gap-4 md:grid-cols-3">
          {steps.map((item, index) => (
            <FadeIn
              delay={0.04 * index}
              key={item.step}
              viewportMargin="0px"
              y={6}
            >
              <LiquidCard className="h-full">
                <p className="metric-value text-[11px] text-gold">{item.step}</p>
                <h3 className="mt-2 text-base font-medium text-cream">{item.title}</h3>
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
            <p className="chart-label text-parchment-muted">Capability boundary</p>
            <h2 className="display mt-2 max-w-2xl text-2xl text-parchment-ink sm:text-3xl">
              What Nomos does today
            </h2>
            <p className="prose-compact mt-3 max-w-2xl text-parchment-muted">
              Planning and provenance are live. Execution against commercial
              providers is not claimed until those integrations exist.
            </p>
          </FadeIn>
          <div className="mt-7 grid gap-5 lg:grid-cols-2">
            <FadeIn viewportMargin="0px" y={6}>
              <div className="klein-parchment-band__plate">
                <p className="chart-label text-brass">Live today</p>
                <ul className="mt-4 space-y-3">
                  {doesToday.map((item) => (
                    <li
                      className="flex gap-3 text-sm leading-6 text-parchment-ink/85"
                      key={item}
                    >
                      <span
                        aria-hidden
                        className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-brass"
                      />
                      <span>{item}</span>
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
              <div className="klein-parchment-band__plate klein-parchment-band__plate--quiet">
                <p className="chart-label text-parchment-muted">Not yet connected</p>
                <h3 className="display mt-2 text-xl text-parchment-ink">
                  What requires provider integration
                </h3>
                <p className="prose-compact mt-3 text-parchment-muted">
                  These capabilities need live provider APIs. Nomos labels them
                  honestly on every plan instead of inventing results.
                </p>
                <ul className="mt-5 space-y-3">
                  {requiresProvider.map((item) => (
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
                <div className="mt-6">
                  <Link
                    className="text-sm text-brass hover:underline"
                    href="/capabilities"
                  >
                    See aspirations and roadmap →
                  </Link>
                </div>
              </div>
            </FadeIn>
          </div>
        </div>
      </section>

      <LiquidSection className="home-band page-shell pb-8" orbs={false}>
        <FadeIn viewportMargin="0px" y={6}>
          <div className="border-t border-gold/12 pt-7">
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
