import type { Metadata } from "next";
import dynamic from "next/dynamic";
import Image from "next/image";
import Link from "next/link";

import { DemoBoundary } from "@/components/archive/ArchivePrimitives";
import { AboutContent } from "@/components/about/AboutContent";
import { FadeIn } from "@/components/motion/primitives";
import { LiquidButton } from "@/components/liquid/LiquidButton";
import { LiquidCard } from "@/components/liquid/LiquidCard";
import { LiquidSection } from "@/components/liquid/LiquidSection";

export const metadata: Metadata = {
  title: "About",
  description:
    "Why Nomos exists, what role it occupies above space infrastructure, the Golden Record lineage, and what the intelligence layer can do today."
};

const AboutScrollStory = dynamic(
  () =>
    import("@/components/about/AboutScrollStory").then((module) => module.AboutScrollStory),
  { ssr: false }
);

const believe = [
  {
    index: "01",
    title: "Space is becoming an infrastructure layer",
    detail:
      "Orbit is filling with sensors, compute, and communication faster than anyone can coordinate them. What launch did for access to orbit, software must now do for access to its capability."
  },
  {
    index: "02",
    title: "Access today is bespoke",
    detail:
      "Every mission still threads its own path across operators, spacecraft, ground networks, compute environments, and constraints. The coordination work is rebuilt by each team, for each workload."
  },
  {
    index: "03",
    title: "The missing layer is intelligence",
    detail:
      "Someone has to understand the whole network: orbital context, data availability, contact opportunities, compute options, constraints, cost. And use that understanding to determine how an objective gets fulfilled. That is the layer Nomos occupies."
  }
];

const progression = [
  { phase: "Understand", now: true },
  { phase: "Recommend", now: true },
  { phase: "Route", now: true },
  { phase: "Orchestrate", now: false },
  { phase: "Execute", now: false }
];

export default function AboutPage() {
  return (
    <div className="pb-6">
      <section className="relative overflow-hidden">
        <div className="absolute inset-0">
          <Image
            alt=""
            aria-hidden
            className="object-cover object-center opacity-50"
            fill
            priority
            sizes="100vw"
            src="/images/lady-philosophy-circuit-hero.jpg"
            unoptimized
          />
          <div className="absolute inset-0 bg-gradient-to-b from-klein-void/35 via-klein-deep/80 to-klein-void" />
          <div
            aria-hidden
            className="absolute inset-x-0 bottom-0 h-16 bg-gradient-to-b from-transparent to-klein-deep"
          />
        </div>
        <LiquidSection className="relative py-10 md:py-14" orbs={false}>
          <div className="page-shell">
            <FadeIn when="mount" y={6}>
              <p className="chart-label text-gold">About</p>
              <h1 className="display mt-2 max-w-2xl text-3xl leading-tight text-cream md:text-5xl">
                Order, for the orbital age.
              </h1>
              <p className="prose-compact mt-3 max-w-xl text-cream/85">
                Nomos Orbital is building the intelligence layer above space
                infrastructure: one place where an objective becomes a routed
                path across satellites, ground systems, and cloud compute.
              </p>
              <div className="mt-6 flex flex-wrap gap-3">
                <LiquidButton href="/plan" variant="primary">
                  Run a request
                </LiquidButton>
                <LiquidButton href="/network" variant="ghost">
                  See the network →
                </LiquidButton>
              </div>
            </FadeIn>
          </div>
        </LiquidSection>
      </section>

      <LiquidSection className="home-band page-shell">
        <FadeIn viewportMargin="0px" y={6}>
          <p className="chart-label text-gold">What we believe</p>
          <h2 className="display mt-2 max-w-2xl text-2xl text-cream sm:text-3xl">
            One request should be able to reach the whole space stack.
          </h2>
        </FadeIn>
        <div className="mt-7 space-y-6">
          {believe.map((item, index) => (
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
        <FadeIn delay={0.16} viewportMargin="0px" y={6}>
          <p className="prose-compact mt-8 max-w-2xl text-silver">
            Nomos is not a satellite operator, a launch company, a ground-station
            provider, or a data reseller. The infrastructure can stay
            heterogeneous. Nomos is the layer that reasons across it, decides how
            it should work together, and keeps every decision explainable.
          </p>
        </FadeIn>
      </LiquidSection>

      <section className="home-band">
        <div className="page-shell">
          <p className="chart-label text-gold">The Golden Record lineage</p>
          <h2 className="display mt-2 max-w-2xl text-3xl text-cream">
            Scroll to turn the record.
          </h2>
          <p className="prose-compact mt-3 max-w-2xl text-muted">
            In space, distance makes information expensive. Bandwidth is scarce,
            passes are brief, and raw data is not always what should move.
            Intelligence determines what matters, where computation should
            occur, and what deserves to cross the link. The Voyager Golden
            Record is our reminder of that discipline.
          </p>
        </div>
        <AboutScrollStory />
      </section>

      <LiquidSection className="home-band page-shell">
        <AboutContent />
      </LiquidSection>

      <LiquidSection className="home-band page-shell">
        <FadeIn viewportMargin="0px" y={6}>
          <p className="chart-label text-gold">Where the product stands</p>
          <h2 className="display mt-2 max-w-2xl text-2xl text-cream sm:text-3xl">
            Today, and the direction from here
          </h2>
          <p className="prose-compact mt-3 max-w-2xl text-muted">
            Today Nomos reasons over real public orbital and infrastructure
            data, calculates contact opportunities, compares feasible processing
            routes, and exposes its assumptions and sources. Execution against
            commercial providers arrives with integrations, and is labeled until
            it does.
          </p>
        </FadeIn>
        <FadeIn delay={0.05} viewportMargin="0px" y={6}>
          <div className="mt-6 flex flex-wrap items-center gap-x-3 gap-y-4">
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
          <div className="mt-7">
            <DemoBoundary />
          </div>
          <p className="mt-4 text-sm text-muted">
            The full, honest map of what is live, referenced, simulated, and
            planned lives on the{" "}
            <Link className="text-gold hover:underline" href="/capabilities">
              capabilities page
            </Link>
            .
          </p>
        </FadeIn>
      </LiquidSection>

      <LiquidSection className="home-band page-shell">
        <LiquidCard className="relative overflow-hidden">
          <div className="absolute right-5 top-5 font-mono text-[10px] tracking-[0.16em] text-vermilion">
            ESSAY 01
          </div>
          <p className="chart-label text-gold">The long mission</p>
          <h2 className="display mt-2 max-w-2xl text-2xl text-cream">
            The Final Symposium
          </h2>
          <p className="prose-compact mt-4 max-w-2xl text-silver">
            A founder-authored inquiry into entropy, memory, human corrigibility,
            and why intelligence should remain legible as it moves farther from Earth.
            It is a philosophical foundation, not a product roadmap.
          </p>
          <div className="mt-5">
            <LiquidButton href="/about/final-symposium" variant="outline">
              Read the essay
            </LiquidButton>
          </div>
        </LiquidCard>
      </LiquidSection>

      <LiquidSection className="home-band page-shell">
        <LiquidCard>
          <p className="chart-label text-gold">Field register</p>
          <h2 className="display mt-2 max-w-2xl text-2xl text-cream">Calendar</h2>
          <p className="prose-compact mt-4 max-w-2xl text-silver">
            Potential presence, application windows, eligibility research, and live
            GitHub search for adjacent open-source work. Presence is potential until
            marked planned.
          </p>
          <div className="mt-5">
            <LiquidButton href="/calendar" variant="outline">
              Open calendar
            </LiquidButton>
          </div>
        </LiquidCard>
      </LiquidSection>
    </div>
  );
}
