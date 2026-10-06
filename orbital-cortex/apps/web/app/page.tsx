import Image from "next/image";
import Link from "next/link";
import { ArrowDown, ArrowRight } from "lucide-react";

import { NomosMark } from "@/components/brand/NomosMark";
import { HomeNarrative } from "@/components/home/HomeNarrative";
import { LiquidButton } from "@/components/liquid";
import { FadeIn } from "@/components/motion/primitives";
import { ArchiveImage } from "@/components/visual/ArchiveImage";

import styles from "./HomePage.module.css";

const proofPoints = [
  {
    label: "Search",
    value: "Public satellite catalogs",
    status: "LIVE"
  },
  {
    label: "Calculate",
    value: "Orbital and contact geometry",
    status: "LIVE"
  },
  {
    label: "Recommend",
    value: "Source-backed mission plans",
    status: "LIVE"
  }
];

const networkLayers = [
  {
    index: "01",
    name: "Orbital",
    detail: "Sensors, spacecraft, public catalogs, and contact opportunities."
  },
  {
    index: "02",
    name: "Ground",
    detail: "Reference stations, downlink geometry, and handoff constraints."
  },
  {
    index: "03",
    name: "Cloud",
    detail: "Processing environments, residency requirements, and delivery paths."
  }
];

export default function HomePage() {
  return (
    <div className={styles.page}>
      <section className={styles.hero} aria-labelledby="home-title">
        <Image
          alt="International Space Station solar arrays above Earth"
          className={styles.heroImage}
          fill
          priority
          sizes="100vw"
          src="/images/archive/irosa-hardware.jpg"
        />
        <div className={styles.heroScrim} aria-hidden />
        <div className={styles.heroGrain} aria-hidden />

        <div className={`page-shell ${styles.heroInner}`}>
          <div className={styles.heroCopy}>
            <FadeIn when="mount">
              <p className={styles.eyebrow}>
                <NomosMark size={18} />
                Space intelligence infrastructure
              </p>
            </FadeIn>
            <FadeIn delay={0.06} when="mount">
              <h1 id="home-title">The intelligence layer for space.</h1>
            </FadeIn>
            <FadeIn delay={0.12} when="mount">
              <p className={styles.heroLead}>
                Tell the network what you need. Nomos determines how satellites,
                ground systems, and cloud compute can deliver it.
              </p>
            </FadeIn>
            <FadeIn delay={0.18} when="mount">
              <div className={styles.heroActions}>
                <LiquidButton href="/plan" variant="primary">
                  Run a request
                </LiquidButton>
                <LiquidButton href="/network" variant="ghost">
                  Explore the network
                </LiquidButton>
              </div>
            </FadeIn>
          </div>

          <FadeIn className={styles.proofRail} delay={0.22} when="mount">
            {proofPoints.map((point) => (
              <div className={styles.proofPoint} key={point.label}>
                <span className={styles.proofStatus}>{point.status}</span>
                <strong>{point.value}</strong>
                <span>{point.label}</span>
              </div>
            ))}
          </FadeIn>
        </div>

        <a className={styles.scrollCue} href="#challenge">
          Understand the problem <ArrowDown aria-hidden size={14} />
        </a>
      </section>

      <section className={styles.challenge} id="challenge">
        <div className={`page-shell ${styles.challengeGrid}`}>
          <FadeIn className={styles.challengeStatement} viewportMargin="0px" y={6}>
            <p className={styles.sectionLabel}>The challenge</p>
            <h2>Space capability is fragmented across systems that do not speak the same language.</h2>
          </FadeIn>
          <ArchiveImage
            alt="Children gathered around a terrestrial globe"
            caption="EARTH / THE SHARED OBJECT"
            className={styles.challengeImage}
            objectPosition="center 42%"
            src="/images/archive/children-with-globe.gif"
            tone="gold"
            unoptimized
          />
          <FadeIn className={styles.challengeDetail} delay={0.05} viewportMargin="0px" y={6}>
            <p>
              A single workload can require a satellite operator, orbital data,
              a ground-station window, a processing environment, and a delivery
              path. Teams coordinate every interface and constraint by hand.
            </p>
            <p>
              Nomos sits above that infrastructure. It turns one objective into a
              feasible path and shows the evidence behind the decision.
            </p>
          </FadeIn>
        </div>
      </section>

      <section className={styles.solution} aria-labelledby="solution-title">
        <Image
          alt="A network of orbital infrastructure around Earth"
          className={styles.solutionImage}
          fill
          sizes="100vw"
          src="/images/orbital-circuit-portal-hero.jpg"
        />
        <div className={styles.solutionScrim} aria-hidden />
        <div className={`page-shell ${styles.solutionInner}`}>
          <FadeIn className={styles.solutionCopy} viewportMargin="0px" y={6}>
            <p className={styles.sectionLabel}>The Nomos layer</p>
            <h2 id="solution-title">Different infrastructure. One interface.</h2>
            <p>
              The providers stay independent. Nomos compares their possible role
              in the mission before it recommends a route.
            </p>
          </FadeIn>

          <div className={styles.layerList}>
            {networkLayers.map((layer, index) => {
              return (
                <FadeIn delay={index * 0.04} key={layer.name} viewportMargin="0px" y={6}>
                  <article className={styles.layerRow}>
                    <span className={styles.layerIndex}>{layer.index}</span>
                    <div>
                      <h3>{layer.name}</h3>
                      <p>{layer.detail}</p>
                    </div>
                  </article>
                </FadeIn>
              );
            })}
          </div>

          <Link className={styles.networkLink} href="/network">
            Open the live network atlas <ArrowRight aria-hidden size={16} />
          </Link>
        </div>
      </section>

      <HomeNarrative />
    </div>
  );
}
