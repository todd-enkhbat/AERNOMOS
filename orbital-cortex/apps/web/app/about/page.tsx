import type { Metadata } from "next";
import dynamic from "next/dynamic";
import Image from "next/image";
import { OrbitalField } from "@/components/visual/OrbitalField";
import Link from "next/link";

import { DemoBoundary } from "@/components/archive/ArchivePrimitives";
import { AboutContent } from "@/components/about/AboutContent";
import { FadeIn } from "@/components/motion/primitives";
import { LiquidButton } from "@/components/liquid/LiquidButton";

import styles from "./AboutPage.module.css";

export const metadata: Metadata = {
  title: "About",
  description:
    "Why Nomos exists, what role it occupies above space infrastructure, the Golden Record lineage, and what the intelligence layer can do today."
};

const AboutScrollStory = dynamic(
  () =>
    import("@/components/about/AboutScrollStory").then((module) => module.AboutScrollStory),
  {}
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
    <div className={styles.page}>
      <section className={styles.hero} data-cadence="off">
        <div className={styles.heroMedia}>
          <Image
            alt=""
            aria-hidden
            className={styles.heroImage}
            fill
            priority
            sizes="100vw"
            src="/images/archive/nomos-orbital-trails.png"
          />
          <div aria-hidden className={styles.heroScrim} />
        </div>
        <OrbitalField />
        <div className={styles.heroSection}>
          <div className={`page-shell ${styles.heroContent}`}>
            <FadeIn when="mount" y={6}>
              <p className="chart-label text-gold-bright">About / Nomos Orbital</p>
              <h1>
                Order, for the orbital age.
              </h1>
              <p className={styles.heroLead}>
                Nomos Orbital is building the intelligence layer above space
                infrastructure: one place where an objective becomes a routed
                path across satellites, ground systems, and cloud compute.
              </p>
              <div className={styles.heroActions}>
                <LiquidButton href="/plan" variant="primary">
                  Build a mission plan
                </LiquidButton>
                <LiquidButton href="/network" variant="ghost">
                  See the network →
                </LiquidButton>
              </div>
            </FadeIn>
          </div>
        </div>
      </section>

      <section className={`page-shell ${styles.beliefSection}`} data-cadence="off">
        <FadeIn viewportMargin="0px" y={6}>
          <p className="chart-label text-gold">What we believe</p>
          <h2 className={styles.beliefTitle}>
            One request should be able to reach the whole space stack.
          </h2>
        </FadeIn>
        <div className={styles.beliefs}>
          {believe.map((item, index) => (
            <FadeIn delay={0.05 * index} key={item.index} viewportMargin="0px" y={6}>
              <div className={styles.belief}>
                <p className={styles.beliefIndex}>{item.index}</p>
                <div>
                  <h3>{item.title}</h3>
                  <p>{item.detail}</p>
                </div>
              </div>
            </FadeIn>
          ))}
        </div>
        <FadeIn className={styles.beliefClose} delay={0.16} viewportMargin="0px" y={6}>
          <p>
            Nomos is not a satellite operator, a launch company, a ground-station
            provider, or a data reseller. The infrastructure can stay
            heterogeneous. Nomos is the layer that reasons across it, decides how
            it should work together, and keeps every decision explainable.
          </p>
        </FadeIn>
      </section>

      <section className={styles.lineage} data-cadence="off">
        <div className={`page-shell ${styles.lineageIntro}`}>
          <p className="chart-label text-gold">The Golden Record lineage</p>
          <h2 className="display-editorial mt-2 max-w-2xl text-3xl text-cream">
            Meaning, carried across distance.
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

      <section className={`page-shell ${styles.archive}`} data-cadence="off">
        <AboutContent />
      </section>

      <section className={`page-shell ${styles.today}`} data-cadence="off">
        <FadeIn viewportMargin="0px" y={6}>
          <p className="chart-label text-gold">Where the product stands</p>
          <h2 className="display-editorial mt-2 max-w-2xl text-2xl text-cream sm:text-3xl">
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
      </section>

      <section className={`page-shell ${styles.links}`} data-cadence="off">
        <div className="about-archive-links">
          <Link className="about-archive-link" href="/about/final-symposium">
            <p className="chart-label text-gold">ESSAY 01 · THE LONG MISSION</p>
            <h2>The Final Symposium</h2>
            <p>
              A founder-authored inquiry into entropy, memory, and why intelligence
              should remain legible as it moves farther from Earth.
            </p>
          </Link>
          <Link className="about-archive-link" href="/calendar">
            <p className="chart-label text-gold">FIELD REGISTER · CALENDAR</p>
            <h2>Where the work convenes</h2>
            <p>
              A verified public register of industry gatherings, application windows,
              and adjacent open-source work. Presence stays labeled until planned.
            </p>
          </Link>
        </div>
      </section>
    </div>
  );
}
